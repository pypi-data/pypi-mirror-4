from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.files import File
from django.utils import simplejson
from django.conf import settings

from .models import UploadedFile


class DeleteFileViewTest(TestCase):
    def setUp(self):
        self.file = UploadedFile.objects.create()
        self.url = reverse('jqueryfileupload_delete', kwargs={'pk': self.file.pk})

    def test_delete_file(self):
        response = self.client.delete(self.url, HTTP_ACCEPT='application/json')

        self.assertEqual(0, UploadedFile.objects.count())
        self.assertEqual(response['Content-Disposition'], 'inline; filename=files.json')
        self.assertIn('application/json', response['Content-Type'])

    def test_delete_inexistent_file(self):
        url = reverse('jqueryfileupload_delete', kwargs={'pk': 0})
        response = self.client.delete(url, HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, 404)


class CreateFileViewTest(TestCase):
    def setUp(self):
        self.file = open('README.md')
        self.url = reverse('jqueryfileupload_create')

    def tearDown(self):
        self.file.close()

    def test_post_file(self):
        response = self.client.post(self.url, {'file': self.file}, HTTP_ACCEPT='application/json')

        self.assertEqual(1, UploadedFile.objects.count())
        uploaded_file = UploadedFile.objects.get()

        self.assertEqual(response['Content-Disposition'], 'inline; filename=files.json')
        self.assertIn('application/json', response['Content-Type'])

        body = simplejson.loads(response.content)

        self.assertIsInstance(body, list)
        self.assertEqual(1, len(body))
        self.assertIsInstance(body[0], dict)
        file = body[0]

        self.assertIn('name', file)
        self.assertIn('size', file)
        self.assertIn('url', file)
        self.assertIn('thumbnail_url', file)
        self.assertIn('delete_url', file)
        self.assertIn('delete_type', file)
        self.assertIn('README', file['name'])
        self.file.seek(0)
        self.assertEqual(len(self.file.read()), file['size'])
        self.assertEqual(uploaded_file.file.url, file['url'])
        self.assertIsNone(file['thumbnail_url'])
        self.assertEqual(reverse('jqueryfileupload_delete', kwargs={'pk': uploaded_file.pk}), file['delete_url'])
        self.assertEqual('DELETE', file['delete_type'])


