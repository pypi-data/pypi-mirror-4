# Django-Highrise

This app provides integration between Django and Highrise, which is used to
provide CRM capabilities.

Currently this supports only one operation - syncing a user to Highrise.

It uses the (pyrise)[https://github.com/feedmagnet/pyrise] library.

## Why bother?

Django is a great web app framework, it's not such a good CRM tool. Sometimes
you need a little bit extra. Highrise is a simple CRM product from the guys
behind Basecamp. It allows you to keep tabs on contacts (amongst a lot of
other sales-related stuff), and has a great email integration feature. You can
read more about it [here](http://highrisehq.com/signup).

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

The app does come with a single model - HighriseContact. This is used to track
the fact that a User has been synced with Highrise, and to contain some basic
utility attributes that make further integration easier.

## Network considerations

It is very important to bear in mind that this app makes a number of calls
across the public internet, and is therefore neither highly performant, nor
immune to standard network connectivity issues. It should *not* therefore be
integrated in any area of your application where an unexpected 30s network time-
out would cause a problem. e.g. do not include this as a synchronous call in
your registration process.

When you sync a User to Highrise two network calls take place: first, a GET is
issued to the API to fetch any possible matches, then, if none are found, a
POST is issued to push the new contact to the API.
If you wanted to add further attributes to the Person and save those back to
Highrise, that would be three network calls. Caveat emptor.

## Show me some code

Push a django user to Highrise

    >>> user = User.objects.create_user('bob', 'bob@example.com', 'password')
    >>> from django_highrise import sync_to_highrise as sync
    >>> contact = sync(user)

Update a person in Highrise from django

    >>> contact = HighriseContact.get(user=user)
    >>> contact.fetch()  # fetches the latest Person from Highrise
    >>> contact.person.title = "CEO"
    >>> contact.person.save()

Fetch the notes about a contact from Highrise

    >>> contact = sync(user)
    >>> len(contact.person.notes)
    2
