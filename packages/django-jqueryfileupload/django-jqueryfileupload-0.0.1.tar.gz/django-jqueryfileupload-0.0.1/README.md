django-jqueryfileupload
=======================

Django app for handle multiple file uploads via jquery-file-upload plugin.

## Requirements

* Django>=1.3

## Testing

    python setup.py test

## Configuration

    INSTALLED_APPS += ('jqueryfileupload',)

    urlpatterns += (r'^fileuploader/', include('jqueryfileupload.urls'))
