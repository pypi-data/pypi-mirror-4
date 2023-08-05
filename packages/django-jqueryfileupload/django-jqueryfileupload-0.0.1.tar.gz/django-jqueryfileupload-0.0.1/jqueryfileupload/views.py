from django.core.urlresolvers import reverse
from django.views.generic import DeleteView, CreateView
from django.http import HttpResponse
from django.forms import models as forms_models
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson

from .models import UploadedFile


def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

def get_delete_url(object):
    return reverse('jqueryfileupload_delete', kwargs={'pk': object.pk})


class DeleteFileView(DeleteView):
    model = UploadedFile
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JSONResponse(True, mimetype=response_mimetype(self.request), 
                            content_disposition='inline; filename=files.json')


class UploadFileView(CreateView):
    model = UploadedFile
    file_field = 'file'

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        return super(UploadFileView, self).dispatch(request)

    def form_valid(self, form):
        self.object = form.save()
        return self.success_response()

    def form_invalid(self, form):
        return self.error_response()

    def success_response(self):
        response = [{
            "name": self.get_file_field(self.object).name,
            "size": self.get_file_field(self.object).size,
            "url": self.get_file_field(self.object).url,
            "thumbnail_url": self.get_thumbnail_url(self.object),
            "delete_url": get_delete_url(self.object),
            "delete_type": "DELETE"
        }]
        return JSONResponse(response, mimetype=response_mimetype(self.request), content_disposition='inline; filename=files.json')

    def error_response(self):
        return JSONResponse(False, mimetype=response_mimetype(self.request), 
                            content_disposition='inline; filename=files.json')

    def get_thumbnail_url(self, object):
        return None

    def get_file_field(self, object):
        return getattr(object, self.file_field)



class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', json_opts={}, mimetype="application/json", content_disposition=None, *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse,self).__init__(content, mimetype, *args, **kwargs)
        if content_disposition is not None:
            self['Content-Disposition'] = content_disposition
