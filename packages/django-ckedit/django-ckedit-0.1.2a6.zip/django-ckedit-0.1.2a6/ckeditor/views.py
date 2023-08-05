from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from ckeditor.forms import CKEditorUploadForm
from django.core.files.storage import default_storage
from os.path import splitext
from mimetypes import guess_type
from easy_thumbnails.files import get_thumbnailer
from django.conf import settings


UPLOAD_DIRECTORY = getattr(settings, 'CKEDITOR_UPLOAD_DIRECTORY', 'ckeditor')


@csrf_exempt
@login_required
def upload(request):
    if request.method == 'POST':
        form = CKEditorUploadForm(request.POST, request.FILES)
        if form.is_valid():
            url = form.save()
            return HttpResponse("""
                <script type="text/javascript">
                    window.parent.CKEDITOR.tools.callFunction(%s, "%s");
                </script>
            """ % (request.GET['CKEditorFuncNum'], url))
    return HttpResponseBadRequest('Please upload a file')


@login_required
def browse(request):
    def get_type(file_name):
        type_string, encoding = guess_type(file_name)
        if not type_string:
            return
        file_type, extension = type_string.split('/')
        return file_type

    dirs, file_names = default_storage.listdir(UPLOAD_DIRECTORY)
    files = {}
    for file_name in file_names:
        if get_type(file_name) == 'image':
            name, ext = splitext(file_name)
            files[name] = get_thumbnailer(default_storage, UPLOAD_DIRECTORY + '/' + file_name)
    return render(request, 'ckeditor/browse.html', {
        'files': files,
    })
