#############################
Getting started with Onctuous
#############################

.. include:: ../_include/intro.rst

Installation
============

::

    $ pip install onctuous


Example usage
=============

Validate a scalar
-----------------

::

    from onctuous import Schema

    validate_is_int = Schema(int)

    # Validate 42 (this will run fine)
    validated = validate_is_int(42)

    # Validate "toto" (this will raise ``InvalidList`` containing a list of errors)
    validated = validate_is_int("toto")


Validate a list
---------------

Using the same idea, you can validate a list of ``int``

::

    from onctuous import Schema

    validate_is_int_list = Schema([int])

    # This will run fine
    validated = validate_is_int_list([42, 2, 7])

    # This will raise ``InvalidList`` containing a list of errors
    validated = validate_is_int_list([2, 7, "toto"])


But we can also use on of the bundled validators and check the URL looks to
be valid for example and even supply a custom error message!

::

    from onctuous import Schema, Url

    validate_is_urls = Schema([Url(msg="Ooops, this is *not* a valid URL")])

    # This will run fine
    validated = validate_is_urls(["www.example.com", "ftp://user:pass@ftp.example.com:42/toto?weird/path"])

    # This will raise ``InvalidList`` containing a list of errors
    validated = validate_is_urls([2, 7, "toto"])


Validate a dictionary
---------------------

Again, this is the same concept with some more niceties. For example, here is a
basic user schema:

::

    from onctuous import Schema, Url

    validate_user = Schema({
        'firstname': unicode,
        'lastname': unicode,
        'age': int,
        'website': Url(msg="Ooops, this is *not* a valid URL"),
    })

    # use it...

But wait, I don't want megative ages, do I ?

::

    from onctuous import Schema, Url, InRange, All

    validate_user = Schema({
        'firstname': unicode,
        'lastname': unicode,
        'age': All(int, InRange(min=0, msg="Uh, ages can not be negative...")),
        'website': Url(msg="Ooops, this is *not* a valid URL"),
    })

    # use it...

Have you noticed how this uses ``All`` to specify that both ``int`` and ``range``
conditions must ne met ?

What if I want to make the "Website" field optional ? Let me introduce ``Markers``

::

    from onctuous import Schema, Url, InRange, All, Optional

    validate_user = Schema({
        'firstname': unicode,
        'lastname': unicode,
        'age': All(int, InRange(min=0, msg="Uh, ages can not be negative...")),
        Optional('website'): Url(msg="Ooops, this is *not* a valid URL"),
    })

    # use it...

You could also have used the 'Required' Marker with a default value. This is very
usefull if you do not want to spend your whole time writing ``if key in data...``.

::

    from onctuous import Schema, Url, InRange, All, Required

    validate_user = Schema({
        'firstname': unicode,
        'lastname': unicode,
        'age': All(int, InRange(min=0, msg="Uh, ages can not be negative...")),
        Required('website', "#"): Url(msg="Ooops, this is *not* a valid URL"),
    })

    # use it...


It is worth noting that that the provided default value does *not* need to pass
validations. You can use it as a "Marker" further in you application.

Nested and advanced validations
-------------------------------

You can nest shemas. You actually did it in the previous example where scalars
are nested into a dict or a list. But you can arbitrarily nest lists into dict
and the other way around, as you need.

For example, let's say you are writing a blog post which obviously has an author
and maybe some tags whose len are between 3 and 20 chars included.

::

    from onctuous import Schema, All, Required, Length, InRange

    # Same schema as user above. I just removed the Schema instanciation but
    # could have kept it. It's just more natural
    user = {
        'firstname': unicode,
        'lastname': unicode,
        'age': All(int, InRange(min=0, msg="Uh, ages can not be negative...")),
        Required('website', "#"): Url(msg="Ooops, this is *not* a valid URL"),
    }

    validate_post = Schema({
        'title': unicode,
        'body': unicode,
        'author': user,  # look how you can split a schema into re-usable chunks!
        Optional('tags'): [All(unicode, Length(min=3, max=20))],
        Required('website', "#"): Url(msg="Ooops, this is *not* a valid URL"),
    })

    # use it...

That's all for nesting.

You could also use the ``Extra`` special key to allow extra fields to be present
while still being valid.

When instanciating the schema, there are also a global ``required`` and ``extra``
parameters that can optionally be set. They both default to ``False``

Going further
=============

There are tons of bundled validators, :ref:`see the full API documentation <validator-list>`
for a full list.
