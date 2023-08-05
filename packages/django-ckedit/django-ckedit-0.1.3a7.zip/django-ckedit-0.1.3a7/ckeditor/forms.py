from __future__ import division
from django import forms
from django.core.files.storage import default_storage
from django.core.files import temp
try:
    from PIL import Image
except ImportError:
    import Image
import os
from django.conf import settings


MAX_RESOLUTION = (1920, 1080)
UPLOAD_DIRECTORY = getattr(settings, 'CKEDITOR_UPLOAD_DIRECTORY', 'ckeditor')


class CKEditorUploadForm(forms.Form):
    upload = forms.ImageField()

    def save(self):
        try:
            upload = self.cleaned_data['upload']
            image = Image.open(upload.file)
            if image.size[0] > MAX_RESOLUTION[0] or image.size[1] > MAX_RESOLUTION[1]:
                ratio = max(image.size[0] / MAX_RESOLUTION[0], image.size[1] / MAX_RESOLUTION[1])
                width = int(image.size[0] / ratio)
                height = int(image.size[1] / ratio)
                image = image.resize((width, height), Image.ANTIALIAS)
                upload.file = temp.NamedTemporaryFile(suffix='.upload')
                name, ext = os.path.splitext(upload.name)
                format = Image.EXTENSION.get(ext, 'JPEG')
                image.save(upload.file, format)
            path = default_storage.save(UPLOAD_DIRECTORY + '/' + upload.name, upload)
            url = default_storage.url(path)
            return url
        except KeyError:
            return ''
