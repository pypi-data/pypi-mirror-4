"""
Models for the django_highrise app.
"""
import logging
from pyrise import Person, Highrise
from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


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
        # this property is never stored, but is populated when a sync is
        # done, which makes it available to calling code. It is ephemeral,
        # but useful. It is a pyrise.Person object.
        self._person = None
        super(HighriseContact, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"%s = %s" % (self.user, self.highrise_id)

    def __str__(self):
        return unicode(self).encode('utf-8')

    @property
    def url(self):
        """
        Return the URL to the person on Highrise.

        If the underlying Highrise._server is not set, or the highrise_id
        property is not set then return empty string.
        """
        if Highrise._server and self.highrise_id:
            return ("%s/people/%s"
                % (Highrise._server, self.highrise_id))
        else:
            return ''

    def save(self):
        """
        Saves person property to Highrise as well as saving local model.
        """
        if self._person:
            self._person.save()
        super(HighriseContact, self).save()

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
            self.highrise_id = None
        else:
            self._person = person
            self.highrise_id = person.id

    person = property(get_person, set_person)
