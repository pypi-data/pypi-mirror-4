from collections import namedtuple
from importlib import import_module

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
# Create your models here.

class Contactable(models.Model):
    address_1 = models.CharField(max_length=255, null=True, blank=True)
    address_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    postcode = models.CharField(max_length=255, null=True, blank=True)
    landline = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    fax = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True

class Company(Contactable):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'{}'.format(self.name)

    class Meta:
        verbose_name_plural = 'companies'


# These are actually classes that are required at run-time.
class Plugin(object):
    def __init__(self, name):
        self.name = name
        self.app = 'luxuryadmin_{}'.format(name)
        self.data = self.submodule('plugin')

    def submodule(self, submodule):
        return import_module('{}.{}'.format(
            self.app,
            submodule
        ))

    @property
    def urls(self):
        return []

    @property
    def sections(self):
        if not hasattr(self.data, 'ADMIN_SECTIONS'):
            return

        for name, title in self.data.ADMIN_SECTIONS:
            yield Section(
                name,
                title,
                reverse('luxuryadmin:{}:{}'.format(
                    self.name,
                    name
                )),
                self
            )
  
    def __repr__(self):
        return '<lux plugin: {}>'.format(self.name)


Section = namedtuple('Section', 'name title url plugin')

def plugins():
    try:
        for plugin_name in settings.LUX_PLUGINS:
            try:
                p = Plugin(plugin_name)
                yield p
                print "Registered plugin", plugin_name
            except ImportError:
                print "Failed to register plugin", plugin_name
                continue

    except AttributeError:
        pass

PLUGINS = list(plugins())