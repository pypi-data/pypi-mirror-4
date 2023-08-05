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

from .errors import Invalid, InvalidList, SchemaError, UNDEFINED


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

        :param schema: Validation schema.
        :param required: Keys defined in the schema must be in the data.
        :param extra: Keys in the data need not have keys in the schema.
        """
        self.schema = schema
        self.required = required
        self.extra = extra

    def __call__(self, data):
        """Validate data against ``self.schema``. This simply is a shortcut for
        ``validate`` method.

        :param data: input data to validate
        :return: validated input
        :raise: :py:class:`~.InvalidList`
        """
        return self.validate([], self.schema, data)

    def validate(self, path, schema, data):
        """Validate data against this ``schema``.

        :param path: (list) current path in the object, Starts as ``[]``
        :param schema: schema to validate agains
        :param data: input data to validate
        :return: validated input
        :raise: :py:class:`~.InvalidList`
        """
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
        # Dirty hack to break circular dependency in import
        from .validators import Required, Optional, Extra

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
                    errors.append(Invalid('extra keys not allowed. Got unknown \'%s\'' % str(key), key_path))
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
            if getattr(key, 'default', UNDEFINED) is not UNDEFINED:
                out[key.schema] = key.default
            else:
                errors.append(Invalid('required keys %s not provided' % repr(required_keys), path + [key]))

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
                errors.append(Invalid('invalid list value (%s)' % (repr(value)), index_path))

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
                raise Invalid('expected value of type %s. Got %s of type %s' % (schema.__name__, repr(data), type(data)), path)

        # function / callable specification ?
        elif callable(schema):
            try:
                data = schema(data)
            except ValueError, e:
                raise Invalid('%s does not match condition %s()' % (repr(data), schema.__name__), path)
            except Invalid, e:
                raise Invalid(e.msg, path + e.path)

        # when everything failed, re-read the manual
        else:
            raise Invalid('%s is not a valid scalar value' % (repr(data)) , path)

        return data
