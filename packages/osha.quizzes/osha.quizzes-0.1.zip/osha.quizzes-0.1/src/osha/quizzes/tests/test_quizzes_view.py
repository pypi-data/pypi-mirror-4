# -*- coding: utf-8 -*-
"""Test @@todo BrowserView."""

from osha.quizzes.tests.base import IntegrationTestCase
from DateTime import DateTime
from plone import api

import unittest2 as unittest


class TestView(IntegrationTestCase):
    """Test the @@quizzes BrowserView."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.folder = self.portal.folder

        # Set @@quizzes as default display view for folder
        self.folder.setLayout("quizzes")

        # get the view
        self.view = api.content.get_view(
            name='quizzes',
            context=self.folder,
            request=self.request
        )

    def test_no_quizzes(self):
        """Test HTML output when there are no Quizzes in a folder."""
        output = self.view()
        self.assertIn('No quizzes found', output)
        self.assertNotIn('<table class="listing"', output)

    def test_listing_table(self):
        """Test HTML listing table output."""

        # create a Quiz item
        api.content.create(
            container=self.folder,
            type="FormFolder",
            title=u"Ein Über Quiz",
            description="An advanced and difficult quiz.",
            comments="The quiz is not recommended for beginners."
        )

        # set the modification date to a known value so we can test its
        # presence in the view output
        date = DateTime('2012/10/18')
        self.folder['ein-uber-quiz'].setModificationDate(date)
        self.folder['ein-uber-quiz'].reindexObject(idxs=['modified'])

        # get view output
        output = self.view()

        # check that the 'no items found' msg is not shown
        self.assertNotIn('No quizzes found', output)

        # clickable title
        self.assertIn('class="quiz-link"', output)
        self.assertIn('href="http://nohost/plone/folder/ein-uber-quiz"', output)
        self.assertIn(u'>Ein Über Quiz</a>', output)

        # modification date
        self.assertIn('<td>Oct 18, 2012 12:00 AM</td>', output)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
