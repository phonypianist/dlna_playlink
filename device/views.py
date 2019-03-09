from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

from device.models import DeviceModel, ContentsModel


class DeviceSearchView(TemplateView):
    template_name = 'device_search.html'

    def get(self, request, *args, **kwargs):
        context = super(DeviceSearchView, self).get_context_data(**kwargs)
        devices = DeviceModel().search()
        context['devices'] = devices
        return render(self.request, self.template_name, context)


class ContentsView(TemplateView):
    template_name = 'contents.html'

    def get(self, request, *args, **kwargs):
        context = super(ContentsView, self).get_context_data(**kwargs)
        url = request.GET.get('url')
        service_type = request.GET.get('serviceType')
        container_id = request.GET.get('containerId')
        if not container_id:
            container_id = 0
        containers = ContentsModel().get(url, service_type, container_id)
        context['url'] = url
        context['service_type'] = service_type
        context['containers'] = containers['containers']
        context['items'] = containers['items']
        return render(self.request, self.template_name, context)
