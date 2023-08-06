"""
Models for the django_highrise app.
"""
import logging

from django.db import models
from django.contrib.auth.models import User

from pyrise import Person

logger = logging.getLogger(__name__)


class HighriseSyncException(Exception):
    """
    Raised whenever syncing issues occur. Typically this is duplicate contacts,
    or missing contacts.
    """
    def __init__(self, message):
        self.message = message

    def __unicode__(self):
        return u'%s' % self.message

    def __str__(self):
        return unicode(self).encode('utf-8')


class HighriseContact(models.Model):
    """
    A record capturing core Highrise properties for a django user.
    """
    highrise_id = models.IntegerField("Highrise ID", unique=True)
    user = models.OneToOneField(
        User, verbose_name="Django user", related_name='highrise')
    company_id = models.IntegerField("Highrise company", null=True)
    # job_title = models.CharField("Highrise job title",
    #     max_length=100, blank=True, null=True)
    # tags = models.CharField("Highrise tags",
    #     max_length=100, blank=True, null=True)
    created_at = models.DateTimeField("First synced at", auto_now_add=True)
    last_synced_at = models.DateTimeField("Last synced at", auto_now=True)

    def __init__(self, *args, **kwargs):
        """
        Initialise the object with a local django user.
        """
        self._person = None
        super(HighriseContact, self).__init__(*args, **kwargs)
        # this property is never stored, but is populated when a sync is
        # done, which makes it available to calling code. It is ephemeral,
        # but useful. It is a pyrise.Person object.

    def __unicode__(self):
        return u"%s = %s" % (self.user, self.highrise_id)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_person(self):
        """
        Lazy instantiation of property - will fetch from Highrise.

        NB This may result in a network API call.
        """
        if self._person is None:
            if self.highrise_id is None:
                return None
            else:
                self._person = Person.get(self.highrise_id)
        return self._person

    def set_person(self, person):
        """
        Setter for person property.
        """
        if person is None:
            self._person = None
        else:
            self._person = person
            self.highrise_id = person.id

    person = property(get_person, set_person)

    # def sync(self):
    #     """
    #     Fetch latest from Highrise, and push updates. NOT IMPLEMENTED.
    #     """
    #     self.person = Person.get(self.highrise_id)
    #     # TODO: update any synced properties
    #     # logging.debug('Highrise API network call: Person.get()')
