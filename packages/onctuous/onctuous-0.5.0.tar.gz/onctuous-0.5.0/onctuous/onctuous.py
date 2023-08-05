# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Alec Thomas <alec@swapoff.org>
# Copyright (C) 2012 Ludia Inc.
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Alec Thomas <alec@swapoff.org>
# Maintainers: Jean-Tiare Le Bigot <jtlebigot@socialludia.com>,

"""Schema validation for Python data structures.
"""

import os
import re
import types
import urlparse


class Undefined(object):
    def __nonzero__(self):
        return False

    def __repr__(self):
        return '...'


UNDEFINED = Undefined()


class Error(Exception):
    """Base validation exception."""


class SchemaError(Error):
    """An error was encountered in the schema."""


class Invalid(Error):
    """The data was invalid.

    :attr msg: The error message.
    :attr path: The path to the error, as a list of keys in the source data.
    """

    def __init__(self, message, path=None):
        Exception.__init__(self, message)
        self.path = path or []

    @property
    def msg(self):
        return self.args[0]

    def __str__(self):
        error_string = Exception.__str__(self)

        if self.path:
            error_string += ' @ data[%s]' % ']['.join(map(repr, self.path))

        return error_string


class InvalidList(Invalid):
    def __init__(self, errors):
        if not errors:
            raise ValueError("'errors' array can *not* be empty")
        self.errors = errors[:]

    @property
    def msg(self):
        return self.errors[0].msg

    @property
    def path(self):
        return self.errors[0].path

    def add(self, error):
        self.errors.append(error)

    def __str__(self):
        return str(self.errors[0])


class Schema(object):
    """A validation schema.

    The schema is a Python tree-like structure where nodes are pattern
    matched against corresponding trees of values.

    Nodes can be values, in which case a direct comparison is used, types,
    in which case an isinstance() check is performed, or callables, which will
    validate and optionally convert the value.
    """

    def __init__(self, schema, required=False, extra=False):
        """Create a new Schema.

        :param schema: Validation schema. See :module:`onctuous` for details.
        :param required: Keys defined in the schema must be in the data.
        :param extra: Keys in the data need not have keys in the schema.
        """
        self.schema = schema
        self.required = required
        self.extra = extra

    def __call__(self, data):
        """Validate data against this schema."""
        return self.validate([], self.schema, data)

    def validate(self, path, schema, data):
        try:
            if isinstance(schema, dict):
                return self._validate_dict(path, schema, data)
            elif isinstance(schema, list):
                return self._validate_list(path, schema, data)
            return self._validate_scalar(path, schema, data)
        except InvalidList:
            raise
        except Invalid, e:
            raise InvalidList([e])

    def _validate_dict(self, path, schema, data):
        """Validates ``data`` dictionnary. If the schema is empty and extra keys
        are explicitely allowed, ``data`` is returned immediately.

        This handles the ``Required``, ``Optional`` and ``Extra`` markers.
        It has also support for default values if provided in ``default``
        attribute
        """
        # Empty schema when extra allowed, allow any data list.
        if (not schema and self.extra):
            return data # shortcut

        out = type(data)()

        required_keys = set()
        error = None
        errors = []
        extra = self.extra

        # load required key list
        for skey in schema:
            if (isinstance(skey, Required)
            or self.required and not isinstance(skey, Optional)):
                required_keys.add(skey)

        # loop over data to validate
        for key, value in data.iteritems():
            key_path = path + [key]

            # First, select a validator key by trying to match data key against it
            for skey, rule in schema.iteritems():
                if skey is Extra:
                    # "Extra" is a "match all". Use it in last resort
                    extra = True
                else:
                    try:
                        new_key = self.validate(key_path, skey, key)
                        break  # Match found !
                    except Invalid, e:
                        error = e
            # No matching rule ?
            else:
                if extra:
                    out[key] = value
                else:
                    errors.append(Invalid('extra keys not allowed', key_path))
                # go to next key
                continue  # pragma: no coverage (coverage bug...)

            # Second, validate data against the rule we just found
            try:
                out[new_key] = self.validate(key_path, rule, value)
            except Invalid, e:
                if len(e.path) > len(key_path):
                    errors.append(e)
                else:
                    errors.append(Invalid(e.msg + ' for dictionary value', e.path))
                break

            # Last, mark any required() fields as found.
            required_keys.discard(skey)

        # Check that all required keys are supplied or have default values
        for key in required_keys:
            if getattr(key, 'default', None) is not None:
                out[key.schema] = key.default
            else:
                errors.append(Invalid('required key not provided', path + [key]))

        # handle errors and return
        if errors:
            raise InvalidList(errors)

        return out

    def _validate_list(self, path, schema, data):
        """Validate a list by trying to match each value from ``data`` agains
        values of the schema. All values nust match but all rules in schema are
        optional. This means that an empty input will always match

        if the schema is empty, the input is considered valid
        """
        # Empty list schema, allow any data list.
        if not schema or not data:
            return data

        out = type(data)()
        errors = []

        for i, value in enumerate(data):
            index_path = path + [i]

            # Attempt a validation agains each condition in the schema
            for s in schema:
                try:
                    validated = self.validate(index_path, s, value)
                    out.append(validated)
                    break
                except Invalid, e:
                    if len(e.path) > len(index_path):
                        raise

            # no condition matches => error
            else:
                errors.append(Invalid('invalid list value', index_path))

        # handle errors and return
        if errors:
            raise InvalidList(errors)

        return out

    @staticmethod
    def _validate_scalar(path, schema, data):
        """Validate a scalar value. The schema can be:
         - a value
         - a type
         - a callable (function or objects)
        """
        # value specification ?
        if data == schema:
            pass

        # type specification ?
        elif type(schema) is type:
            if not isinstance(data, schema):
                raise Invalid('expected %s' % schema.__name__, path)

        # object / callable specification ?
        elif callable(schema):
            try:
                data = schema(data)
            except ValueError, e:
                raise Invalid('not a valid value', path)
            except Invalid, e:
                raise Invalid(e.msg, path + e.path)

        # when everything failed, re-read the manual
        else:
            raise Invalid('not a valid value', path)

        return data


class Marker(object):
    """Mark nodes for special treatment."""

    def __init__(self, schema, msg=None):
        self.schema = schema
        self._schema = Schema(schema)
        self.msg = msg

    def __call__(self, v):
        try:
            return self._schema(v)
        except Invalid, e:
            if not self.msg or len(e.path) > 1:
                raise
            raise Invalid(self.msg)

    def __str__(self):
        return str(self.schema)

    def __repr__(self):
        return repr(self.schema)


class Optional(Marker):
    """Mark a node in the schema as optional."""


class Required(Marker):
    """Mark a node in the schema as being required."""

    def __init__(self, schema, default=None, msg=None):
        super(Required, self).__init__(schema, msg)
        self.default = default


def Extra(_):
    """Allow keys in the data that are not present in the schema."""
    raise SchemaError('"extra" should never be called')


def Msg(schema, msg):
    """Report a user-friendly message if a schema fails to validate.
    Messages are only applied to invalid direct descendants of the schema.
    """
    schema = Schema(schema)
    def f(v):
        try:
            return schema(v)
        except Invalid, e:
            if len(e.path) > 1:
                raise e
            else:
                raise Invalid(msg)
    return f


def Coerce(type, msg=None):
    """Coerce a value to a type.

    If the type constructor throws a ValueError, the value will be marked as
    Invalid.
    """
    def f(v):
        try:
            return type(v)
        except ValueError:
            raise Invalid(msg or ('expected %s' % type.__name__))
    return f


def IsTrue(msg=None):
    """Assert that a value is true, in the Python sense.
    "In the Python sense" means that implicitly false values, such as empty
    lists, dictionaries, etc. are treated as "false":
    """
    def f(v):
        if v:
            return v
        raise Invalid(msg or 'value was not true')
    return f


def IsFalse(msg=None):
    """Assert that a value is false, in the Python sense.
    """
    def f(v):
        if not v:
            return v
        raise Invalid(msg or 'value was not false')
    return f


def Boolean(msg=None):
    """Convert human-readable boolean values to a bool.

    Accepted values are 1, true, yes, on, enable, and their negatives.
    Non-string values are cast to bool.
    """
    def f(v):
        try:
            if isinstance(v, basestring):
                v = v.lower()
                if v in ('1', 'true', 'yes', 'on', 'enable'):
                    return True
                if v in ('0', 'false', 'no', 'off', 'disable'):
                    return False
                raise Invalid(msg or 'expected boolean')
            return bool(v)
        except ValueError:
            raise Invalid(msg or 'expected boolean')
    return f


def Any(*validators, **kwargs):
    """Use the first validated value.

    :param msg: Message to deliver to user if validation fails.
    :returns: Return value of the first validator that passes.
    """
    msg = kwargs.pop('msg', None)
    schemas = [Schema(val) for val in validators]

    def f(v):
        for schema in schemas:
            try:
                return schema(v)
            except Invalid, e:
                if len(e.path) > 1:
                    raise
                pass  # pragma: no coverage (still and again a coverage bug)
        else:
            raise Invalid(msg or 'no valid value found')
    return f


def All(*validators, **kwargs):
    """Value must pass all validators.

    The output of each validator is passed as input to the next.

    :param msg: Message to deliver to user if validation fails.
    """
    msg = kwargs.pop('msg', None)
    schemas = [Schema(val) for val in validators]

    def f(v):
        try:
            for schema in schemas:
                v = schema(v)
        except Invalid, e:
            raise Invalid(msg or e.msg)
        return v
    return f


def Match(pattern, msg=None):
    """Value must match the regular expression.

    Pattern may also be a compiled regular expression:
    """
    if isinstance(pattern, basestring):
        pattern = re.compile(pattern)

    def f(v):
        if not pattern.match(v):
            raise Invalid(msg or 'does not match regular expression')
        return v
    return f


def Sub(pattern, substitution, msg=None):
    """Regex substitution.
    """
    if isinstance(pattern, basestring):
        pattern = re.compile(pattern)

    def f(v):
        return pattern.sub(substitution, v)
    return f


def Url(msg=None):
    """Verify that the value is a URL."""
    def f(v):
        try:
            urlparse.urlparse(v)
            return v
        except:
            raise Invalid(msg or 'expected a URL')
    return f


def IsFile(msg=None):
    """Verify the file exists."""
    def f(v):
        if os.path.isfile(v):
            return v
        else:
            raise Invalid(msg or 'not a file')
    return f


def IsDir(msg=None):
    """Verify the directory exists."""
    def f(v):
        if os.path.isdir(v):
            return v
        else:
            raise Invalid(msg or 'not a directory')
    return f


def PathExists(msg=None):
    """Verify the path exists, regardless of its type."""
    def f(v):
        if os.path.exists(v):
            return v
        else:
            raise Invalid(msg or 'path does not exist')
    return f


def InRange(min=None, max=None, msg=None):
    """Limit a value to a range.

    Either min or max may be omitted.

    :raises Invalid: If the value is outside the range and clamp=False.
    """
    def f(v):
        if min is not None and v < min:
            raise Invalid(msg or 'value must be at least %s' % min)
        if max is not None and v > max:
            raise Invalid(msg or 'value must be at most %s' % max)
        return v
    return f


def Clamp(min=None, max=None, msg=None):
    """Clamp a value to a range.

    Either min or max may be omitted.
    """
    def f(v):
        if min is not None and v < min:
            v = min
        if max is not None and v > max:
            v = max
        return v
    return f


def Length(min=None, max=None, msg=None):
    """The length of a value must be in a certain range."""
    def f(v):
        if min is not None and len(v) < min:
            raise Invalid(msg or 'length of value must be at least %s' % min)
        if max is not None and len(v) > max:
            raise Invalid(msg or 'length of value must be at most %s' % max)
        return v
    return f

# weird calling convention...
def ToLower(v):
    """Transform a string to lower case.
    """
    return str(v).lower()


def ToUpper(v):
    """Transform a string to upper case.
    """
    return str(v).upper()


def Capitalize(v):
    """Capitalise a string.
    """
    return str(v).capitalize()


def Title(v):
    """Title case a string.
    """
    return str(v).title()

