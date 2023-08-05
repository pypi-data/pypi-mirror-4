"""Implement base class for handlers. This can be used to simply inherit from
this class instead of directly registering new handler.

"""
from __future__ import absolute_import

from thriftpool import thriftpool
from thriftpool.exceptions import RegistrationError
from thriftpool.utils.structures import AttributeDict

__all__ = ['BaseHandler']


class Options(AttributeDict):
    """Holder for handler options."""


class OptionsMeta(type):
    """Create options for class."""

    def __new__(mcs, name, bases, attrs):
        # Create default options for new class.
        attrs['meta'] = meta = Options(abstract=False)
        # Try to inherit from parent class.
        for base in bases[::-1]:
            try:
                meta.update(base.meta)
            except AttributeError:
                pass
        meta.abstract = False
        # Fill options.
        try:
            options = attrs['options']
        except KeyError:
            pass
        else:
            meta.update({key: getattr(options, key)
                         for key in dir(options)
                         if not key.startswith('_')})
        # Create new class itself.
        return super(OptionsMeta, mcs).__new__(mcs, name, bases, attrs)


class HandlerMeta(OptionsMeta):
    """Register new classes as handlers."""

    def __new__(mcs, name, bases, attrs):
        if 'options' not in attrs:
            raise RegistrationError('Class {0!r} missed "options" attribute.'.
                                    format(name))
        klass = super(HandlerMeta, mcs).__new__(mcs, name, bases, attrs)
        if klass.meta.abstract:
            # Don't register abstract classes.
            return klass
        return thriftpool.register(**klass.meta)(klass)


class BaseHandler(object):
    """Base class for handler."""

    __metaclass__ = HandlerMeta

    class options:
        abstract = True
