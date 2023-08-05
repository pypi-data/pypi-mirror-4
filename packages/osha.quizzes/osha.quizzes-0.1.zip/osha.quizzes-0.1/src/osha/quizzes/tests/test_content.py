# -*- coding: utf-8 -*-
"""Test custom content types."""

from osha.quizzes.tests.base import IntegrationTestCase
from plone import api
from plone.api.exc import InvalidParameterError
from Products.statusmessages.interfaces import IStatusMessage

import unittest2 as unittest


class TestContent(IntegrationTestCase):
    """Test custom content types."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_create(self):
        """See if we can create custom content types without error."""

        # This should throw an error since this CT is not globally addable
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.portal,
                type='PFGCorrectAnswersAdapter',
                id='correct-answers'
            )

        # So let's create a PFG Folder first
        api.content.create(
            container=self.portal,
            type='FormFolder',
            id='quiz'
        )

        # Now it should work
        api.content.create(
            container=self.portal.quiz,
            type='PFGCorrectAnswersAdapter',
            id='adapter'
        )

        adapter = self.portal.quiz.get('adapter')
        self.assertEqual(adapter.id, 'adapter')
        self.assertEqual(adapter.portal_type, 'PFGCorrectAnswersAdapter')

    def test_points_calculation(self):
        """Test that points are correctly calculated.

        Also confirm that the result is nicely printed to a portal
        message.

        """
        # First, we need a PFG FormFolder
        api.content.create(
            container=self.portal,
            type='FormFolder',
            id='quiz'
        )

        # Now we add a Correct Answers adapter
        api.content.create(
            container=self.portal.quiz,
            type='PFGCorrectAnswersAdapter',
            id='adapter'
        )

        # Followed by two Selection fields
        api.content.create(
            container=self.portal.quiz,
            type='FormSelectionField',
            id='question-1',
            correct_answer='5',
        )
        api.content.create(
            container=self.portal.quiz,
            type='FormSelectionField',
            id='question-2',
            correct_answer='7',
        )

        # set one correct anwser and one incorrect answer
        self.request.form['question-1'] = '5'
        self.request.form['question-2'] = '13'

        # trigger the Correct Answer adapter
        self.portal.quiz.adapter.onSuccess(
            self.portal.quiz.values(),
            self.request
        )

        # assert the portal message
        messages = IStatusMessage(self.request).show()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, u'Your score is: 50%')


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
