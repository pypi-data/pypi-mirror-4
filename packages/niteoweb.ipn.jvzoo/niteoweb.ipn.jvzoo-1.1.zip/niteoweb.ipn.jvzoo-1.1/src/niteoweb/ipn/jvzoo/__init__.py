# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

JVZooMessageFactory = MessageFactory('niteoweb.ipn.jvzoo')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
