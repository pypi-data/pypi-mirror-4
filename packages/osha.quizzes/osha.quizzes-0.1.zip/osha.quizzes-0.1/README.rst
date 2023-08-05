========================
Build quizzes with Plone
========================

`osha.quizzes` is a minimalistic Plone add-on that builds on top of the
`PloneFormGen` product to enable you to build simple quizzes trough-the-web.

* `Source code @ GitHub <http://github.com/syslabcom/osha.quizzes>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/osha.quizzes>`_
* `Continuous Integration @ Travis-CI
  <http://travis-ci.org/syslabcom/osha.quizzes>`_

Installation
============

To install ``osha.quizzes`` you simply add ``osha.quizzes`` to the list of eggs
in your buildout, run buildout and restart Plone. Then, install `osha.quizzes`
using the Add-ons control panel.

Requirements
============

    * `Plone <http://plone.org/>`_ 4.1 or newer
    * `PloneFormGen <http://plone.org/products/ploneformgen>`_ 1.7 or newer

Usage
=====

This package does the following:
 * extends `FormSelectionField` with a ``correct_answer`` field so users can
   specify the correct answer from a list of options,
 * adds a `PFGCorrectAnwserAdapter` that iterates through all
   `FormSelectionFields` on form submit, calculates the percentage of correct
   answers and displays the result as a portal status message.
 * add a `quizzes` view, registered for `Folders`, that lists all FormFolders
   in a Folder, and opens them in an overlay upon clicking on one.

So, to create a quiz, first create a PloneFormGen's FormFolder, add some
FormSelectionFields to it and set the correct answer for each of them.

.. image:: https://github.com/syslabcom/osha.quizzes/raw/master/docs/images/correct_answer_field.png

Then add the `PFGCorrectAnswersAdapter` to the FormFolder, give it some
some arbitrary title and save. No when you fill out the form and click submit,
you'll get your score in a nice status message.

.. image:: https://github.com/syslabcom/osha.quizzes/raw/master/docs/images/result_on_thank_you_page.png

Finally you can choose to use the `quizzes` view on a Folder to list all
quizzes in that folder and open them in overlays.

.. image:: https://github.com/syslabcom/osha.quizzes/raw/master/docs/images/quizzes_view.png

.. image:: https://github.com/syslabcom/osha.quizzes/raw/master/docs/images/quiz_in_overlay.png


