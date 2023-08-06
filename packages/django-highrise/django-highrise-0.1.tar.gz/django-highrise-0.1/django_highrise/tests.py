"""
Django test for django-highrise app.
"""
from pyrise import Person, EmailAddress
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from . import sync_user as sync
from . import init, test_me
from .models import HighriseSyncException


class HighriseIntegrationTestCase(TestCase):
    """
    Tests for django_highrise app.
    """

    def setUp(self):
        """
        Initialise pyrise connection settings, and test connectivity.
        """
        init(settings.HIGHRISE_SERVER, settings.HIGHRISE_API_KEY)
        test_me()
        self.test_user = User.objects.create_user('john',
            'lennon@thebeatles.com', 'johnpassword')
        self.test_user.firstname = 'john'
        self.test_user.lastname = 'lennon'

    def tearDown(self):
        pass

    def test_sync_new_user(self):
        """Test syncing a user who is not already in Highrise."""
        user = self.test_user
        contact = sync(user)
        cp = contact.person
        self.assertIsNotNone(cp)
        self.assertEqual(cp.id, contact.highrise_id)
        self.assertEqual(cp.first_name, user.firstname)
        self.assertEqual(cp.last_name, user.lastname)
        self.assertEqual(len(cp.contact_data.email_addresses), 1)
        self.assertEqual(cp.contact_data.email_addresses[0].address, user.email)
        self.assertIsNone(contact.company_id)
        # always clean up after yourself.
        contact.person.delete()

    def test_sync_existing_user(self):
        """ Test syncing a user a second time."""
        user = self.test_user
        contact1 = sync(user)
        contact2 = sync(user)
        self.assertEqual(contact1.person.id, contact2.person.id)
        self.assertEqual(contact1.highrise_id, contact2.highrise_id)
        self.assertEqual(contact1.created_at, contact2.created_at)
        self.assertEqual(contact1.last_synced_at, contact2.last_synced_at)
        self.assertNotEqual(contact1.company_id, contact2.last_synced_at)
        contact1.person.delete()

    def test_duplicate_highrise_contacts(self):
        """
        Test that duplicate highrise contacts (same email) will raise an exception.
        """
        user = self.test_user
        p1 = self._create_highrise_contact_from_user(user)
        p2 = self._create_highrise_contact_from_user(user)
        with self.assertRaises(HighriseSyncException):
            sync(user)
        p1.delete()
        p2.delete()

    def _create_highrise_contact_from_user(self, user):
        """
        Helper method that creates a Highrise contact in the 'raw' using pyrise.

        This method does not sync the contact, it just creates them directly.

        Args:
            user: the django user from which to create the person.

        Returns:
            a reference to the created contact as a pyrise.Person object
        """
        p = Person()
        p.first_name = user.firstname
        p.last_name = user.lastname
        email = EmailAddress(address=user.email)
        p.contact_data.email_addresses.append(email)
        p.save()  # network API call
        return p
