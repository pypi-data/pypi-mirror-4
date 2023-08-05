# -*- coding: utf-8 -*-
"""Definition of the PFGCorrectAnswersAdapter content type"""

from AccessControl import ClassSecurityInfo
from osha.quizzes.config import PROJECTNAME
from osha.quizzes.interfaces import IPFGCorrectAnswersAdapter
from plone import api
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.CMFCore.permissions import View
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter
from Products.PloneFormGen.content.actionAdapter import FormAdapterSchema
from zope.interface import implements

PFGCorrectAnswersAdapterSchema = FormAdapterSchema.copy() + atapi.Schema((
    # -*- Your Archetypes field definitions here ... -*-
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PFGCorrectAnswersAdapterSchema['title'].storage = atapi.AnnotationStorage()
PFGCorrectAnswersAdapterSchema['description'].storage = \
    atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    PFGCorrectAnswersAdapterSchema, moveDiscussion=False)


class PFGCorrectAnswersAdapter(FormActionAdapter):
    """Calculate the percentage of correct answers."""
    implements(IPFGCorrectAnswersAdapter)

    meta_type = "PFGCorrectAnswersAdapter"
    schema = PFGCorrectAnswersAdapterSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security.declareProtected(View, 'onSuccess')

    def onSuccess(self, fields, REQUEST=None):
        """The essential method of a PloneFormGen Adapter."""

        max_points = 0
        points = 0

        # iterate through FormSelectionFields and count correct answers
        for field in fields:
            if field.portal_type != 'FormSelectionField':
                continue

            max_points += 1
            if  (REQUEST.form.get(field.id) and
                 field.correct_answer.strip() == REQUEST.form[field.id]):
                points += 1

        if max_points > 0:
            result = round(float(points) / float(max_points) * 100)

            api.portal.show_message(
                request=REQUEST,
                type='info',
                message="Your score is: %i%%" % result)

atapi.registerType(PFGCorrectAnswersAdapter, PROJECTNAME)
