# Django-Highrise

This app provides integration between Django and Highrise, which is used to
provide CRM capabilities.

Currently this supports only one operation - pushing a user to Highrise.

It uses the [pyrise](https://github.com/feedmagnet/pyrise) library.

## Why bother?

Django is a great web app framework, it's not such a good CRM tool. Sometimes
you need a little bit extra. Highrise is a simple CRM product from the guys
behind Basecamp. It allows you to keep tabs on contacts (amongst a lot of
other sales-related stuff), and has a great email integration feature. You can
read more about it at [http://highrisehq.com/signup](http://highrisehq.com/signup).

## Tell me more

This app simplifies the process of integrating with Highrise. It provides the
API hooks to allow you to push django user records into Highrise, and to read
a Highrise contact's feed (notes, emails, comments) back out. Where and when
you use these hooks is up to you. It could be at the point of user registration,
it could be through the Django admin site, it could even be from the command
line, run as a batch job overnight.

Under the hood django-highrise is a wrapper around pyrise, and so the objects
returned are standard pyrise Person, Note, Email objects. This allows you to
use them in your own code, for instance for adding additional attributes
beyond just the core User attributes.

The app comes with a single model - HighriseContact. This is used to track
the fact that a User has been synced with Highrise, and to contain some basic
utility attributes that make further integration easier.

## Network considerations

It is very important to bear in mind that this app makes a number of calls
across the public internet, and is therefore neither highly performant, nor
immune to standard network connectivity issues. It should *not* therefore be
integrated in any area of your application where an unexpected 30s network
timeout would cause a problem. i.e. do not include this as a synchronous call
in your registration process.

When you sync a User to Highrise two network calls take place: first, a GET is
issued to the API to fetch any possible matches, then, if none are found, a
POST is issued to push the new contact to the API. If you wanted to add further
attributes to the Person and save those back to Highrise, that would be three
network calls. **Caveat emptor**.

## Configuration

The underlying `pyrise` library requires a server URL and a valid API key. These
are set by the app when calling the `init()` function.

The server setting is the URL to your instance of Highrise - e.g. **example.highrisehq.com**.
Highrise API keys are specific to an individual user - and are available in
your account under the 'My info' section.

You can use the `test_me()` method to validate your credentials:

    >>> from django_highrise import init, test_me
    >>> init('example.highrisehq.com', '1234567890')
    >>> test_me()
    True
    >>>

NB You must call `init()` before using the `sync_user()` function; an exception
of type HighriseSyncException will be raised if you do not do so.

Easiest option is to call `init()` in your `settings.py` file.

## Show me some code

Initialise Highrise connection:

    >>> from django.conf import settings
    >>> from django_highrise import init, test_me
    >>> init(settings.HIGHRISE_SERVER, settings.HIGHRISE_API_KEY)
    >>> test_me()
    True
    >>>

Push a django user to Highrise:

    >>> from django.contrib.auth.models import User
    >>> user = User.objects.create_user('bob', 'bob@example.com', 'password')
    >>> from django_highrise import sync_user
    >>> contact = sync(user)
    >>> contact
    <HighriseContact: bob = 1234567>
    >>>

Update a person in Highrise from django:

    >>> contact.person.title = "CEO"
    >>> contact.save()

Fetch the notes about a contact from Highrise:

    >>> for note in contact.person.notes:
    ...   print note.body
    ...
    This is a note
    This is another note
    >>>

Get the Highrise URL for the contact:

    >>> print contact.url
    'https://example.highrisehq.com/people/1234567'
    >>>

## Tests

There is a test suite, please bear in mind that it will only run within the
context of a django app.