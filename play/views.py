from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class DirectPlayView(TemplateView):
    template_name = 'play.html'

    def post(self, request, *args, **kwargs):
        context = super(DirectPlayView, self).get_context_data(**kwargs)
        print(request.PUT)
        service_type = request.PUT.get('serviceType')
        container_id = request.PUT.get('containerId')
        # return HttpResponseRedirect("/bbs/2/")
        return render(self.request, self.template_name, context)
