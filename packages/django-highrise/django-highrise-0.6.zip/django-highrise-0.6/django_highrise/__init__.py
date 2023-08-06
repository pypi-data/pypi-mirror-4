"""
Django-Highrise is a simple django app used to assist in synchronising django
users with Highrise CRM contacts.

Setup:

1. Install the app from PyPI
2. Add `django_highrise` to your django INSTALLED_APPS in settings.py
3. Run syncdb to create the underlying database tables

NB you must call `init(server, api_key)` to initialise the Highrise API
settings before attempting to sync a user to Highrise.
"""

__title__ = 'django-highrise'
__version__ = '0.6'
__author__ = 'Hugo Rodger-Brown'
__license__ = 'Simplified BSD License'
__copyright__ = 'Copyright 2013 Hugo Rodger-Brown'
__description__ = 'Highrise CRM integration for Django projects.'

import logging
import pyrise


logger = logging.getLogger(__name__)


def init(server, api_key):
    """
    Initialises pyrise with server and api_key info.

    Args:
        server: the Highrise account domain, e.g. acme.highrisehq.com

        api_key: a valid Highrise API key - keys are locked to users,
            and so you will need to get a key from your account on Highrise.
    """
    pyrise.Highrise.set_server(server)
    pyrise.Highrise.auth(api_key)


def test_me():
    """
    Test the connection to Highrise by called the /me.xml endpoint.

    If the server and api_key settings are correct, then this should return
    so valid XML.

    Returns:
        True if the connection works, else False.
    """
    try:
        pyrise.Highrise.request('me.xml')
        return True
    except pyrise.ElevatorError:
        return False


def sync_user(user):
    """
    Syncs the user to Highrise, and returns the HighriseContact object, which
    has a reference to the pyrise Person and the django user.

    Args:
        user: the django user to sync. only user attributes (name, email)
            are synced by this method - to sync anything else please use
            the returned Person object reference, and its properties and
            methods (add_note, add_tag etc.)
    """
    # imported here to allow setuptools to import django_highrise
    # outside of a django project.
    from .models import HighriseContact

    if pyrise.Highrise._server is None:
        raise HighriseSyncException(
            "Highrise connection is not initialised. Please call init() "
            "with the server and api_key arguments.")
    try:
        # HAPPY PATH
        hc = HighriseContact.objects.get(user=user)
        hc.get_person()  # this forces lazy instantiation to happen now.
        return hc

    except pyrise.NotFound:
        # hmm. we have a local HighriseContact record with a Highrise ID
        # that doesn't match anything in Highrise itself. Add some context
        # and re-raise
        raise HighriseSyncException(
            "Not matching Highrise contact found for %s at %s"
            % (hc.highrise_id, pyrise.Highrise._server)
        )

    except HighriseContact.DoesNotExist:
        # There's no local HighriseContact, so we need to work out whether
        # this user exists at all in Highrise. If they do not, then we go
        # the whole hog, and create a new Person in Highrise. If they do
        # exist, then we create a new local contact, and link it to the
        # existing remote Person. If multiple matches (by email) are
        # returned from Highrise, they there is no implicit solution, so
        # raise an exception and let the client code handle it.
        try:
            pp = pyrise.Person.filter(email=user.email)
            # logging.debug('Highrise API network call: Person.filter()')

            if len(pp) == 0:
                p = create_new_contact(user)

            elif len(pp) == 1:
                p = pp[0]

            else:
                raise HighriseSyncException(
                    "Multiple contacts found matching <%s>." % user.email
                )

            contact = HighriseContact(user=user, person=p)
            contact.save()
            return contact

        except pyrise.ElevatorError:
            logger.error("Highrise API exception.", exc_info=True)
            raise


def create_new_contact(user):
    """
    Creates a new contact in Highrise from a django user. No duplicate checking.

    This is invoked by the sync process if no mathing contact exists. It
    shouldn't really be called directly. Use sync_user instead.

    Args:
        user: the django user to use as the base.

    Returns:
        The created pyrise.Person object.

    NB This requires a network API call.
    """
    p = pyrise.Person()
    p.first_name = user.first_name
    p.last_name = user.last_name
    email = pyrise.EmailAddress(address=user.email)
    p.contact_data.email_addresses.append(email)
    p.save()  # network API call
    return p


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
