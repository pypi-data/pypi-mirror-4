from django.conf import settings as settings_module


def settings(request):
    settings_names = ['FAVICON_PREFIX', 'ADMIN_JQUERY_ADDITIONAL_VERSION', 'STATIC_URL']
    settings_names.extend(getattr(settings_module, 'CONTEXT_SETTINGS', []))
    result = {'SETTING_%s' % name: getattr(settings_module, name, None) for name in settings_names}
    result['SETTING_ADMIN_TOOLS_USAGE'] = 'admin_tools.dashboard' in settings_module.INSTALLED_APPS
    return result
