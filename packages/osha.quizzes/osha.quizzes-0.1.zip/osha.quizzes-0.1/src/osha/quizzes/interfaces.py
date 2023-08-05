# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from Products.PloneFormGen.interfaces.actionAdapter import \
    IPloneFormGenActionAdapter


class IPFGCorrectAnswersAdapter(IPloneFormGenActionAdapter):
    """Calculate the percentage of correct answers"""
