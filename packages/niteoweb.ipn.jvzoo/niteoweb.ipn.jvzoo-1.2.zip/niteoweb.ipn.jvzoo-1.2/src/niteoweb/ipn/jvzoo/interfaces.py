# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from niteoweb.ipn.jvzoo import JVZooMessageFactory as _
from zope import schema
from zope.interface import Interface


class IJVZooSettings(Interface):
    """Definition of fields for niteoweb.ipn.jvzoo configuration form."""

    secretkey = schema.Password(
        title=_(u"JVZoo Secret Key"),
        description=_(
            u"help_secretkey",
            default=u"Enter the Secret Key you got from JVZoo to access "
                    "their API."),
        required=True,
    )


# exceptions
class JVZooError(Exception):
    """Base class for niteoweb.ipn.jvzoo exception."""


class SecretKeyNotSet(JVZooError):
    """Exception thrown when secret-key for @@jvzoo is not set."""


class UnknownTransactionType(JVZooError):
    """Exception through when Transaction Type is not known."""
