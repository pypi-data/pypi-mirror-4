================
Django WYMEditor
================

A Django application that contains a widget to render a form field with a
WYMEditor_ interface.

 .. _WYMEditor: http://www.wymeditor.org/

Requirements
============

Currently integration with django-filebrowser or django-bfm is hard-coded in.
This will be fixed in a future version. For now, make sure you have django-
filebrowser installed and included in your ``INSTALLED_APPS``, and that one of
the following is in your URLconf::

    # For django-filebrowser

    urlpatterns += patterns('',
        (r'^admin/filebrowser/', include('filebrowser.urls'))
    )


    # For django-bfm

    # Hack for WYMEditor hardcoded link URL... :-(
    from django.views.generic import RedirectView
    urlpatterns += patterns('',
        url(r'^admin/filebrowser/browse/', RedirectView.as_view(url="/admin/files/")),
        url(r'^admin/files/', include('django_bfm.urls'))
    )


With that, you should have full filebrowser integration w/ WYMEditor.
