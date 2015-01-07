#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_prompt
--------------

Tests for `cookiecutter.prompt` module.
"""
import os
import platform
import sys

from cookiecutter.compat import patch, unittest, OrderedDict
from cookiecutter import prompt

if 'windows' in platform.platform().lower():
    old_stdin = sys.stdin

    class X(object):
        def readline(self):
            return '\n'
    sys.stdin = X()


class TestPrompt(unittest.TestCase):

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'Audrey Roy')
    def test_prompt_for_config_simple(self):
        context = {"cookiecutter": {"full_name": "Your Name"}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        self.assertEqual(cookiecutter_dict, {"full_name": u"Audrey Roy"})

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'Pizzä ïs Gööd')
    def test_prompt_for_config_unicode(self):
        context = {"cookiecutter": {"full_name": "Your Name"}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        self.assertEqual(cookiecutter_dict, {"full_name": u"Pizzä ïs Gööd"})

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'Pizzä ïs Gööd')
    def test_unicode_prompt_for_config_unicode(self):
        context = {"cookiecutter": {"full_name": u"Řekni či napiš své jméno"}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        self.assertEqual(cookiecutter_dict, {"full_name": u"Pizzä ïs Gööd"})

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'\n')
    def test_unicode_prompt_for_default_config_unicode(self):
        context = {"cookiecutter": {"full_name": u"Řekni či napiš své jméno"}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        self.assertEqual(cookiecutter_dict, {"full_name": u"Řekni či napiš své jméno"})

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'\n')
    def test_unicode_prompt_for_templated_config(self):
        context = {"cookiecutter": OrderedDict([
            ("project_name", u"A New Project"),
            ("pkg_name", u"{{ cookiecutter.project_name|lower|replace(' ', '') }}")
        ])}

        cookiecutter_dict = prompt.prompt_for_config(context)
        self.assertEqual(cookiecutter_dict, {"project_name": u"A New Project",
             "pkg_name": u"anewproject"})

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'\n')
    def test_prompt_for_config_with_dict_context_entry(self):
        context = {'cookiecutter': OrderedDict([
            (
                'project_name', {
                    'default': u'A New Project',
                    'prompt': u'Your project name',
                },
            ),
            (
                'include_extras', {
                    'default': u'no',
                    'prompt':  u'Include extra things?',
                    'type': 'boolean',
                },
            ),
            (
                 'include_tests', {
                    'default': u'yes',
                    'prompt':  u'Include some test files?',
                    'type': 'boolean',
                },
            ),
        ])}
        context = prompt.prompt_for_config(context)
        self.assertEqual(context, {
            'project_name': u'A New Project',
            'include_extras': False,
            'include_tests': True,
        })

    def test_prompt_with_environment_defailt(self):
        context = {'cookiecutter': {'repo_name': 'something'}}
        with patch.dict(os.environ):
            os.environ['COOKIECUTTER_REPO_NAME'] = expected = 'better'
            context = prompt.prompt_for_config(context, no_input=True)

        self.assertEqual(context, {'repo_name': expected})

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'\n')
    def test_prompt_with_environment_defailt_and_context_entry(self):
        context = {'cookiecutter': OrderedDict([
            (
                'include_extras', {
                    'default': u'no',
                    'prompt':  u'Include extra things?',
                    'type': 'boolean',
                },
            ),
        ])}
        with patch.dict(os.environ):
            os.environ['COOKIECUTTER_INCLUDE_EXTRAS'] = 'yes'
            context = prompt.prompt_for_config(context)
        self.assertEqual(context, {
            'include_extras': True,
        })


class TestPromptNoInput(unittest.TestCase):

    def test_prompt_no_input(self):
        orig_context = {"cookiecutter": {"project_name": u"A New Project"}}
        context = prompt.prompt_for_config(orig_context, no_input=True)
        self.assertEqual(context, orig_context['cookiecutter'])

    def test_prompt_no_input_with_rich_context_type(self):
        context = {'cookiecutter': OrderedDict([
            (
                 'include_tests', {
                    'default': u'yes',
                    'prompt':  u'Include some test files?',
                    'type': 'boolean',
                },
            ),
        ])}
        context = prompt.prompt_for_config(context, no_input=True)
        self.assertEqual(context, {'include_tests': True})


class TestQueryAnswers(unittest.TestCase):

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'y')
    def test_query_y(self):
        answer = prompt.query_yes_no("Blah?")
        self.assertTrue(answer)

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'ye')
    def test_query_ye(self):
        answer = prompt.query_yes_no("Blah?")
        self.assertTrue(answer)

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'yes')
    def test_query_yes(self):
        answer = prompt.query_yes_no("Blah?")
        self.assertTrue(answer)

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'n')
    def test_query_n(self):
        answer = prompt.query_yes_no("Blah?")
        self.assertFalse(answer)


class TestQueryDefaults(unittest.TestCase):

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'y')
    def test_query_y_none_default(self):
        answer = prompt.query_yes_no("Blah?", default=None)
        self.assertTrue(answer)

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'n')
    def test_query_n_none_default(self):
        answer = prompt.query_yes_no("Blah?", default=None)
        self.assertFalse(answer)

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'')
    def test_query_no_default(self):
        answer = prompt.query_yes_no("Blah?", default='no')
        self.assertFalse(answer)

    @patch('cookiecutter.prompt.read_response', lambda x=u'': u'junk')
    def test_query_bad_default(self):
        self.assertRaises(ValueError, prompt.query_yes_no, "Blah?", default='yn')
