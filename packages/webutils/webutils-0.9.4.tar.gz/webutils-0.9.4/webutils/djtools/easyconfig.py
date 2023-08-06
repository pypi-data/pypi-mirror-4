from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


class EasyConfig(object):
    def __init__(self, default_module, setting_name):
        self.default_module = default_module
        self.setting_name = setting_name

    def _get_config(self):
        ''' Get the config as defined in the settings
        '''
        config = self._get_config_name()
        try:
            package = import_module(config)
        except ImportError:
            path = '.'.join(config.split('.')[:-1])
            pkg = config.split('.')[-1]
            try:
                tmp_package = import_module(path, package=pkg)
                package = getattr(tmp_package, pkg)
            except (ImportError, AttributeError):
                raise ImproperlyConfigured(
                    'The %s setting refers to a non-existing package.' % \
                                                            self.setting_name
                )
        
        if callable(package):
            package = package()
        return package

    def _get_config_name(self):
        ''' Returns the name of the support config (either the setting value, 
            if it exists, or the default).
        '''
        return getattr(settings, self.setting_name, self.default_module)


    def get_object(self, method, default_obj):
        ''' Check that the support config is custom, and if so, that the 
            right methods exist. If not, return the default_obj
        '''
        if self._get_config_name() != self.default_module:
            config = self._get_config()
            if hasattr(config, method):
                return getattr(config, method)()

        return default_obj