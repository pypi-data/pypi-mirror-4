"""
Django-Highrise app.

Setup:

Install the app from PyPI:

    $ pip install django-highrise

Add the app to your django settings.py INSTALLED_APPS:

    INSTALLED_APPS = (
        ...
        'django_highrise',
    )

Run syncdb to create the underlying database tables:

    $ python manage.py syncdb

You can now import the django_highrise package and start using the app.

NB you must call 'init(server, key)' to initialise the Highrise API settings
before using any other methods.

"""
import logging

from pyrise import Highrise, ElevatorError, Person, EmailAddress
from .models import HighriseContact, HighriseSyncException

logger = logging.getLogger(__name__)


def init(server, api_key):
    """
    Initialises pyrise with server and api_key info.

    Args:
        server: the Highrise account domain, e.g. acme.highrisehq.com

        api_key: a valid Highrise API key - keys are locked to users,
            and so you will need to get a key from your account on Highrise.
    """
    Highrise.set_server(server)
    Highrise.auth(api_key)


def test_me():
    """
    Test the connection to Highrise by called the /me.xml endpoint.

    If the server and api_key settings are correct, then this should return
    so valid XML.

    Returns:
        True if the connection works, else False.
    """
    try:
        Highrise.request('me.xml')
        return True
    except ElevatorError:
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
    try:
        # HAPPY PATH
        hc = HighriseContact.objects.get(user=user)
        hc.get_person()  # this forces lazy instantiation to happen now.
        return hc

    except HighriseContact.DoesNotExist:
        # There's no local HighriseContact, so we need to work out whether
        # this user exists at all in Highrise. If they do not, then we go
        # the whole hog, and create a new Person in Highrise. If they do
        # exist, then we create a new local contact, and link it to the
        # existing remote Person. If multiple matches (by email) are
        # returned from Highrise, they there is no implicit solution, so
        # raise an exception and let the client code handle it.
        try:
            pp = Person.filter(email=user.email)
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

        except ElevatorError:
            logger.error("Highrise API exception.", exc_info=True)


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
    p = Person()
    p.first_name = user.firstname
    p.last_name = user.lastname
    email = EmailAddress(address=user.email)
    p.contact_data.email_addresses.append(email)
    p.save()  # network API call
    return p
