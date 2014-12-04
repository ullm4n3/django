# coding: utf-8
from __future__ import unicode_literals
import warnings

from django.conf import settings
from django.template.base import TemplateSyntaxError
from django.template.loader import get_template
from django.test import SimpleTestCase
from django.utils.deprecation import RemovedInDjango20Warning

from ..utils import render, setup, SomeClass, SomeOtherException, UTF8Class


class FilterSyntaxTests(SimpleTestCase):

    @setup({'filter-syntax01': '{{ var|upper }}'})
    def test_filter_syntax01(self):
        """
        Basic filter usage
        """
        output = render('filter-syntax01', {"var": "Django is the greatest!"})
        self.assertEqual(output, "DJANGO IS THE GREATEST!")

    @setup({'filter-syntax02': '{{ var|upper|lower }}'})
    def test_filter_syntax02(self):
        """
        Chained filters
        """
        output = render('filter-syntax02', {"var": "Django is the greatest!"})
        self.assertEqual(output, "django is the greatest!")

    @setup({'filter-syntax03': '{{ var |upper }}'})
    def test_filter_syntax03(self):
        """
        Allow spaces before the filter pipe
        """
        output = render('filter-syntax03', {'var': 'Django is the greatest!'})
        self.assertEqual(output, 'DJANGO IS THE GREATEST!')

    @setup({'filter-syntax04': '{{ var| upper }}'})
    def test_filter_syntax04(self):
        """
        Allow spaces after the filter pipe
        """
        output = render('filter-syntax04', {'var': 'Django is the greatest!'})
        self.assertEqual(output, 'DJANGO IS THE GREATEST!')

    @setup({'filter-syntax05': '{{ var|does_not_exist }}'})
    def test_filter_syntax05(self):
        """
        Raise TemplateSyntaxError for a nonexistent filter
        """
        with self.assertRaises(TemplateSyntaxError):
            get_template('filter-syntax05')

    @setup({'filter-syntax06': '{{ var|fil(ter) }}'})
    def test_filter_syntax06(self):
        """
        Raise TemplateSyntaxError when trying to access a filter containing
        an illegal character
        """
        with self.assertRaises(TemplateSyntaxError):
            get_template('filter-syntax06')

    @setup({'filter-syntax07': "{% nothing_to_see_here %}"})
    def test_filter_syntax07(self):
        """
        Raise TemplateSyntaxError for invalid block tags
        """
        with self.assertRaises(TemplateSyntaxError):
            get_template('filter-syntax07')

    @setup({'filter-syntax08': "{% %}"})
    def test_filter_syntax08(self):
        """
        Raise TemplateSyntaxError for empty block tags
        """
        with self.assertRaises(TemplateSyntaxError):
            get_template('filter-syntax08')

    @setup({'filter-syntax09': '{{ var|removetags:"b i"|upper|lower }}'})
    def test_filter_syntax09(self):
        """
        Chained filters, with an argument to the first one
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RemovedInDjango20Warning)
            output = render('filter-syntax09', {'var': '<b><i>Yes</i></b>'})
        self.assertEqual(output, 'yes')

    @setup({'filter-syntax10': r'{{ var|default_if_none:" endquote\" hah" }}'})
    def test_filter_syntax10(self):
        """
        Literal string as argument is always "safe" from auto-escaping.
        """
        output = render('filter-syntax10', {"var": None})
        self.assertEqual(output, ' endquote" hah')

    @setup({'filter-syntax11': r'{{ var|default_if_none:var2 }}'})
    def test_filter_syntax11(self):
        """
        Variable as argument
        """
        output = render('filter-syntax11', {"var": None, "var2": "happy"})
        self.assertEqual(output, 'happy')

    @setup({'filter-syntax12': r'{{ var|yesno:"yup,nup,mup" }} {{ var|yesno }}'})
    def test_filter_syntax12(self):
        """
        Default argument testing
        """
        output = render('filter-syntax12', {"var": True})
        self.assertEqual(output, 'yup yes')

    @setup({'filter-syntax13': r'1{{ var.method3 }}2'})
    def test_filter_syntax13(self):
        """
        Fail silently for methods that raise an exception with a
        `silent_variable_failure` attribute
        """
        output = render('filter-syntax13', {"var": SomeClass()})
        if settings.TEMPLATE_STRING_IF_INVALID:
            self.assertEqual(output, "1INVALID2")
        else:
            self.assertEqual(output, "12")

    @setup({'filter-syntax14': r'1{{ var.method4 }}2'})
    def test_filter_syntax14(self):
        """
        In methods that raise an exception without a
        `silent_variable_attribute` set to True, the exception propagates
        """
        with self.assertRaises(SomeOtherException):
            render('filter-syntax14', {"var": SomeClass()})

    @setup({'filter-syntax15': r'{{ var|default_if_none:"foo\bar" }}'})
    def test_filter_syntax15(self):
        """
        Escaped backslash in argument
        """
        output = render('filter-syntax15', {"var": None})
        self.assertEqual(output, r'foo\bar')

    @setup({'filter-syntax16': r'{{ var|default_if_none:"foo\now" }}'})
    def test_filter_syntax16(self):
        """
        Escaped backslash using known escape char
        """
        output = render('filter-syntax16', {"var": None})
        self.assertEqual(output, r'foo\now')

    @setup({'filter-syntax17': r'{{ var|join:"" }}'})
    def test_filter_syntax17(self):
        """
        Empty strings can be passed as arguments to filters
        """
        output = render('filter-syntax17', {'var': ['a', 'b', 'c']})
        self.assertEqual(output, 'abc')

    @setup({'filter-syntax18': r'{{ var }}'})
    def test_filter_syntax18(self):
        """
        Make sure that any unicode strings are converted to bytestrings
        in the final output.
        """
        output = render('filter-syntax18', {'var': UTF8Class()})
        self.assertEqual(output, '\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111')

    @setup({'filter-syntax19': '{{ var|truncatewords:1 }}'})
    def test_filter_syntax19(self):
        """
        Numbers as filter arguments should work
        """
        output = render('filter-syntax19', {"var": "hello world"})
        self.assertEqual(output, "hello ...")

    @setup({'filter-syntax20': '{{ ""|default_if_none:"was none" }}'})
    def test_filter_syntax20(self):
        """
        Filters should accept empty string constants
        """
        output = render('filter-syntax20')
        self.assertEqual(output, "")

    @setup({'filter-syntax21': r'1{{ var.silent_fail_key }}2'})
    def test_filter_syntax21(self):
        """
        Fail silently for non-callable attribute and dict lookups which
        raise an exception with a "silent_variable_failure" attribute
        """
        output = render('filter-syntax21', {"var": SomeClass()})
        if settings.TEMPLATE_STRING_IF_INVALID:
            self.assertEqual(output, "1INVALID2")
        else:
            self.assertEqual(output, "12")

    @setup({'filter-syntax22': r'1{{ var.silent_fail_attribute }}2'})
    def test_filter_syntax22(self):
        """
        Fail silently for non-callable attribute and dict lookups which
        raise an exception with a `silent_variable_failure` attribute
        """
        output = render('filter-syntax22', {"var": SomeClass()})
        if settings.TEMPLATE_STRING_IF_INVALID:
            self.assertEqual(output, "1INVALID2")
        else:
            self.assertEqual(output, "12")

    @setup({'filter-syntax23': r'1{{ var.noisy_fail_key }}2'})
    def test_filter_syntax23(self):
        """
        In attribute and dict lookups that raise an unexpected exception
        without a `silent_variable_attribute` set to True, the exception
        propagates
        """
        with self.assertRaises(SomeOtherException):
            render('filter-syntax23', {"var": SomeClass()})

    @setup({'filter-syntax24': r'1{{ var.noisy_fail_attribute }}2'})
    def test_filter_syntax24(self):
        """
        In attribute and dict lookups that raise an unexpected exception
        without a `silent_variable_attribute` set to True, the exception
        propagates
        """
        with self.assertRaises(SomeOtherException):
            render('filter-syntax24', {"var": SomeClass()})

    @setup({'filter-syntax25': '{{ var.attribute_error_attribute }}'})
    def test_filter_syntax25(self):
        """
        #16383 - Attribute errors from an @property value should be
        reraised.
        """
        with self.assertRaises(AttributeError):
            render('filter-syntax25', {'var': SomeClass()})
