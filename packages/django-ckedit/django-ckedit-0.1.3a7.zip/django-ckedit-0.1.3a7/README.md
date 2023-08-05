Django CKEditor
===============

Django CKEditor contains the JavaScript WYSIWYG editor, [CKEditor](http://ckeditor.com/) and functionality for uploading and browsing files on your server.

Installation
------------

Run `pip install django-ckedit`

Add `ckeditor` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = (
    ...
    'ckeditor',
)
```

To your sites `url.py` add:

```python
urlpatterns = patterns('',
    ...
    url(r'^ckeditor/', include('ckeditor.urls')),
)
```

Views
-----

###upload
Uploads a file from the CKEditor insert image dialog's upload section to a user-specified path using the [default storage](https://docs.djangoproject.com/en/dev/topics/files/#the-built-in-filesystem-storage-class).

##browse
Displays image thumbnails from the CKEditor insert image dialog's browse section.

Settings
--------

`CKEDTIOR_UPLOAD_DIRECTORY (default 'ckeditor')`

The directory the uploads are saved to and files are browsed from.