============
Config Store
============

- Stores configurations and are retrievable as a dictionary
- Configurations are lazily loaded and are cached per request
- Configurations can have a Setup action to run a setup function. Configforms will follow HttpRequests returned from that function.
- Configuration is defined as a django form
- Configurations can be encrypted by subclassing EncryptedConfigurationForm

Installation
============

#. Add the 'configstore' directory to your Python path

#. Add 'configstore' to your INSTALLED_APPS in your settings file

Usage
=====

Define your configuration form somewhere::

    from django import forms
    from django.contrib.auth.models import User
    
    from configstore.configs import ConfigurationInstance, register
    from configstore.forms import ConfigurationForm

    class ExampleConfigurationForm(ConfigurationForm):
        amount = forms.DecimalField()
        message = forms.CharField()
        user = forms.ModelChoiceField(queryset=User.objects.all())

        def config_task(self):
            return "Yay, you've accomplished nothing!"

Register the form::

    complex_instance = ConfigurationInstance('example', 'Example Config', ExampleConfigurationForm)
    register(complex_instance)

Somewhere else in your code retrieve the config and use it::

    from configstore.configs import get_config
    config = get_config('example')
    print config['amount']


You can also encrypt the data in your configstore data section. Configstore uses AES keyed on your django secret::

    from django import forms
    from django.contrib.auth.models import User

    from configstore.configs import ConfigurationInstance, register
    from configstore.forms import EncryptedConfigurationForm

    class ExampleConfigurationForm(EncryptedConfigurationForm):
        amount = forms.DecimalField()
        message = forms.CharField()
        user = forms.ModelChoiceField(queryset=User.objects.all())

        def config_task(self):
            return "Yay, you've accomplished nothing!"
