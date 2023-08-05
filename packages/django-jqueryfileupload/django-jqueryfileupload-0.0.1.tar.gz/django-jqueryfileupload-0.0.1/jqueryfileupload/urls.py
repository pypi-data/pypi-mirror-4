from django.conf.urls.defaults import patterns
from .views import UploadFileView, DeleteFileView

urlpatterns = patterns('',
    (r'^upload/$', UploadFileView.as_view(), {}, 'jqueryfileupload_create'),
    (r'^delete/(?P<pk>\d+)/$', DeleteFileView.as_view(), {}, 'jqueryfileupload_delete'),
)
