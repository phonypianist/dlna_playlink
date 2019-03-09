import io
import re
import socket
import urllib
import urllib.request
import xml.etree.ElementTree as ET


class DeviceModel:

    def search(self):

        timeout = 4

        msearch_request_lines = (
            'M-SEARCH * HTTP/1.1',
            'HOST: 239.255.255.250:1900',
            'MAN: "ssdp:discover"',
            f'MX: {timeout}',
            # 'ST:upnp:rootdevice',
            'ST:ssdp:all',
            '',
            ''
        )

        devices = []
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            msearch_request_body = '\r\n'.join(msearch_request_lines)
            sock.sendto(msearch_request_body.encode('utf-8'), ('239.255.255.250', 1900))
            while True:
                try:
                    response, device = sock.recvfrom(4096)
                    response = response.decode('utf-8')
                    if re.compile(r'ST: .*ContentDirectory', re.MULTILINE).search(response):
                        location_match = re.compile(r'LOCATION: (.*)', re.MULTILINE).search(response)
                        if location_match:
                            device = self.search_into_location(location_match.group(1))
                            devices.extend(device)

                except socket.timeout:
                    break

        return devices

    @staticmethod
    def search_into_location(location):
        request = urllib.request.Request(location)
        with urllib.request.urlopen(request) as response:
            response_body = response.read()
            root = parse_xml_without_namespace(response_body.decode('utf-8'))

        name = root.find('device/friendlyName').text
        # TODO imageの取得
        image = ''
        udn = root.find('device/UDN').text.lstrip('uuid:')
        services = root.find('device/serviceList')
        devices = []
        for service in services:
            service_type = service.find('serviceType').text
            if service_type.find('ContentDirectory') >= 0:
                location = service.find('controlURL').text
                devices.append(Device(udn, service_type, name, location, image))

        return devices


class Device:

    udn = ''
    service_type = ''
    name = ''
    location = ''
    image = ''

    def __init__(self, udn, service_type, name, location, image):
        self.udn = udn
        self.service_type = service_type
        self.name = name
        self.location = location
        self.image = image


class ContentsModel:

    __BLANK_IMAGE_URI = '/static/images/blank.png'

    def get(self, url, service_type, object_id):
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"'
        }

        containers = []
        items = []
        starting_index = 0
        while True:
            body = f'''<?xml version="1.0"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
              <s:Body>
                <u:Browse xmlns:u="{service_type}">
                  <ObjectID>{object_id}</ObjectID>
                  <BrowseFlag>BrowseDirectChildren</BrowseFlag>
                  <Filter>*</Filter>
                  <StartingIndex>{starting_index}</StartingIndex>
                  <RequestedCount>0</RequestedCount>
                  <SortCriteria></SortCriteria>
                </u:Browse>
              </s:Body>
            </s:Envelope>
            '''

            req = urllib.request.Request(url, body.encode('utf-8'), headers)
            with urllib.request.urlopen(req) as response:
                response_body = response.read().decode('utf-8')

            print(response_body)
            root = ET.fromstring(response_body)
            result = root.find('.//Result').text
            if result:

                didl_root = parse_xml_without_namespace(result)
                for container in didl_root.findall('.//container'):
                    container_id = container.get('id')
                    title_element = container.find('title')
                    if title_element is not None:
                        title = title_element.text
                    else:
                        title = container_id
                    album_art_uri = container.find('albumArtURI')
                    if album_art_uri is not None:
                        image_uri = album_art_uri.text
                    else:
                        image_uri = self.__BLANK_IMAGE_URI
                    containers.append(Container(container_id, title, image_uri))

                for item in didl_root.findall('.//item'):
                    item_id = item.get('id')
                    title_element = item.find('title')
                    res_element = item.find('res')
                    items.append(Item(item_id, title_element.text, res_element.text))

            total = int(root.find('.//TotalMatches').text)
            starting_index += int(root.find('.//NumberReturned').text)
            if starting_index >= total:
                break

        return {
            'containers': containers,
            'items': items
        }


class Container:

    container_id = ''
    title = ''
    image_uri = ''

    def __init__(self, container_id, title, image_uri):
        self.container_id = container_id
        self.title = title
        self.image_uri = image_uri


class Item:

    item_id = ''
    title = ''
    uri = ''

    def __init__(self, item_id, title, uri):
        self.item_id = item_id
        self.title = title
        self.uri = uri


def parse_xml_without_namespace(xml_text):
    it = ET.iterparse(io.StringIO(xml_text))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
    return it.root

