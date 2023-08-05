# -*- coding: utf-8 -*-
"""Extending existing Archetypes content types."""

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.PloneFormGen.content.fields import FGSelectionField
from zope.component import adapts
from zope.interface import implements


class CorrectAnswerField(ExtensionField, StringField):
    """Field to specify the correct answer."""


class FGSelectionFieldExtender(object):
    adapts(FGSelectionField)
    implements(IOrderableSchemaExtender)

    fields = [
        CorrectAnswerField(
            "correct_answer",
            widget=StringWidget(
                label="Correct answer")),
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        """Manipulate the order in which fields appear.

        @param schematas: Dictonary of schemata name -> field lists
        @return: Dictionary of reordered field lists per schemata.

        """
        new_schemata = schematas.copy()
        new_schemata['default'].remove('correct_answer')
        new_schemata['default'].insert(
            new_schemata['default'].index('fgVocabulary') + 1,
            'correct_answer')
        return new_schemata

    def getFields(self):
        return self.fields
