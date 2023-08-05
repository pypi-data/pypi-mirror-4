##################
Extending Onctuous
##################

Folder structure
================

::

    Onctuous
    +-- onctuous            => the real code
    |   +-- tests
    |       +-- unit        => all individual validators and low level logic
    |       `-- functional  => global behovior
    +-- docs
        `-- pages           => what you are reading


Adding a custom validator
=========================

If you want to contribute to ``Onctuous`` (we would love it btw), you will need
to add your custom validator into ``ddmock.validators`` module. Otherwise, put it
wherever you want, there are no restrictions.

By convention, validators are:

 - Callable
 - Returns the validated value on success, even unmodified. This ensures chainability
 - Raises ``Invalid`` on failure

All validators will look like this:

::

    # Parent function: loads the parameters
    def ValidatorName(param1, param2, msg=None):
        # this 'inner' function does the real job and is called by ``Onctuous``
        def f(v):
            if some condition:
                return v  # All changes done to the value will be reflected in the validated object
            raise Invalid(msg or 'Ooops: "Some Condition" was not met!')
        return f

For example, here is the ``Url`` validator:


::

    def Url(msg=None):
        """Verify that the value is a URL."""
        def f(v):
            try:
                urlparse.urlparse(v)
                return v
            except:
                raise Invalid(msg or 'expected a URL')
        return f

That's all you need to do!

Adding a custom marker
======================

Sadly, this is quite more invasive to do and will probably require you to patch
the heart of ``Onctuous``.

Markers lives in the same module as Validators: ``ddmock.validators`` and are
also callable.

The most simple Marker you can do is the "Optional" marker:

::

    class Optional(Marker):
        """Mark a node in the schema as optional."""

But you could override ``__init__`` or ``__call__`` for instance.

Then, Marker presence is detected in ``Schema._validate_dict`` in module
``ddmock.schema``, that is to say, the heart of ``Onctuous``
