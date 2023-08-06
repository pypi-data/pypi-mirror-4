from importlib import import_module

from django.conf.urls import patterns, url
from django.contrib import admin
from django.conf import settings


def get_signed_methods(cls, inst=None):
    provider = inst or cls
    return [getattr(provider, x) for x in dir(cls) if hasattr(getattr(cls, x), 'extra_admin_url')]


def get_admin_classes(app):
    result = []
    try:
        module = import_module('%s.admin' % app)
        for node in dir(module):
            if admin.ModelAdmin in getattr(getattr(module, node), '__mro__', []):
                result.append(getattr(module, node))
    except ImportError:
        pass
    return result


def get_site_registered_info(cls):
    try:
        return [(k, v) for k, v in admin.site._registry.items() if isinstance(v, cls)][0]
    except IndexError:
        return (None, None)


def get_link(method, model):
    return r'^%s/%s/' % (model._meta.app_label, model._meta.module_name) + method.extra_admin_url


def make_extra_admin_urls():
    urls = ['']
    for app in [app for app in settings.INSTALLED_APPS if not app.startswith('django.contrib')]:
        admin_classes = get_admin_classes(app)
        for admin_cls in admin_classes:
            model, admin_inst = get_site_registered_info(admin_cls)
            if model:
                methods = get_signed_methods(admin_cls, admin_inst)
                for method in methods:
                    urls.append(url(get_link(method, model), method))

                for inline in getattr(admin_cls, 'inlines', []):
                    methods = get_signed_methods(inline)
                    for method in methods:
                        model = inline.model if method.use_inline_data else model
                        urls.append(url(get_link(method, model), method))
    return patterns(*urls)


urlpatterns = make_extra_admin_urls()
