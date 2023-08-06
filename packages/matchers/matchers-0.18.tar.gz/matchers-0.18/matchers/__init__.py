# -*- coding: utf-8 -*-
"""
This file is part of matchers.

matchers is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

matchers is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with matchers.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import json
from lxml import etree
from collections import Iterable
from exceptions import StopIteration
from contextlib import contextmanager

from hamcrest import *
from hamcrest.core.base_matcher import BaseMatcher


class matches_re(BaseMatcher):
    """Custom hamcrest matcher for regular expressions"""

    def __init__(self, regex):
        self.regex_text = regex
        self.regex = re.compile(regex)

    def _matches(self, item):
        if not isinstance(item, str) and not isinstance(item, unicode):
            return False

        return any(self.regex.finditer(item))

    def describe_to(self, description):
        description.append_text(u" string that matches regex: '{}'".format(self.regex_text))

    def describe_mismatch(self, actual, description):
        description.append_text(u" string '{}' does not match regex: '{}'"
                                .format(actual, self.regex_text))


class edi_document(matches_re):
    """Custom hamcrest matcher to pseudo-validate EDI"""
    def __init__(self):
        super(edi_document, self).__init__(
            u'UNB\+UNOA:1\+[^:]+:ZZ\+AEATADUE:ZZ\+\d{8}:\d{4}\+\d+\+\+&EE'
        )


class date_iso(matches_re):
    fmt = dict(
        year=ur'(\d{4})',
        month=ur'((0[1-9])|(1[0-2]))',
        day=ur'([0-3]\d)',
        hours=ur'(([01]\d)|(2[0-3]))',
        minutes=ur'([0-5]\d)',
        seconds=ur'([0-5]\d)',
        miliseconds=ur'(\d+)',
        sep=ur'[/-]',
    )

    def __init__(self):
        "1988-10-04T06:15:00.230943Z"
        super(date_iso, self).__init__(
            u'^{year}{sep}{month}{sep}{day}([T ]{hours}:{minutes}:{seconds}(.{miliseconds})?)?$'
            .format(**self.fmt)
        )

    def describe_to(self, description):
        description.append_text(u' an ISO 8601 formatted date string ')


class xml_document(BaseMatcher):
    """Custom hamcrest matcher for XML documents"""
    def __init__(self, matcher=None):
        self.matcher = matcher

    def _matches(self, item):
        try:
            doc = etree.fromstring(item)
        except ValueError, err:
            # try again at ValueError: Unicode strings with encoding declaration are not supported.
            item = item.encode('utf-8')
            doc = etree.fromstring(item)

        except etree.Error, err:
            self.error = err
            return False

        if self.matcher:
            return self.matcher.matches(doc)

        return True

    def describe_to(self, description):
        description.append_text(u"string conforming a valid XML document")

    def describe_mismatch(self, actual, description):
        description.append_text(u"failed to load xml document {} due to following errors: '{}'"
                                .format(actual, self.error))


class xml_element(BaseMatcher):
    """Checks for a xml element with a certain name"""
    def __init__(self, tag, matcher=None, ns=None):
        self.tag = tag if ns is None else "{{{ns}}}{tag}".format(ns=ns, tag=tag)
        self.matcher = matcher

    def _matches(self, item):
        if not item.tag == self.tag:
            return False

        if self.matcher:
            return self.matcher.matches(item)

        return True

    def describe_to(self, description):
        description.append_text(u" xml element with tag named '{0}'".format(self.tag))


# A etree xml document is the root element also.
# This may change in other implementation.
xml_root = xml_element


class xml_contains_element(xml_element):
    def _matches(self, item):
        try:
            item = item.find(".//" + self.tag)
        except:
            return False

        if item is None:
            return False

        return super(xml_contains_element, self)._matches(item)

    def describe_to(self, description):
        description.append_text(u" xml element has a children: '{0}'".format(self.tag))
        if self.matcher:
            description.append_text(u" matching {}".format(self.matcher))


class xml_namespaced(BaseMatcher):
    def __init__(self, ns_url):
        self.url = ns_url

    def _matches(self, item):
        return self.url in item.nsmap.values()

    def describe_to(self, description):
        description.append_text(u"xml document wich is namespaced with the url '{0}'".format(self.url))

    def describe_mismatch(self, actual, description):
        description.append_text(u"url '{}' is not within the namespaces of the xml element {}".format(self.url, actual.nsmap))


class soap_document(xml_document):
    """Checks for a well constructed soap document. xml_document with extra checking"""

    ns_url = "http://schemas.xmlsoap.org/soap/envelope/"

    def __init__(self, matcher=None):
        default_matcher = all_of(xml_root('Envelope', ns=self.ns_url))
        if matcher:
            default_matcher = all_of(default_matcher, matcher)

        super(soap_document, self).__init__(default_matcher)

    def describe_to(self, description):
        description.append_text(u"SOA xml document envelope")

    def describe_mismatch(self, actual, description):
        description.append_text(u"is not a valid xml document or does not have namespace '{0}'"
                                .format(self.ns_url))


class soap_message(soap_document):
    def __init__(self, matcher=None):
        super(soap_message, self).__init__(xml_contains_element('Body', ns=self.ns_url, matcher=matcher))

    def describe_to(self, description):
        description.append_text(u"xml document within a SOA envelope")

    def describe_mismatch(self, actual, description):
        description.append_text(u" soap message {} should containg a 'Body' element ".format(actual))


class json_(BaseMatcher):
    def __init__(self, matcher=None):
        self.matcher = matcher
        self.response = None

    def _matches(self, response):
        self.response = response
        try:
            self.response = json.loads(response)
        except:
            return False

        if self.matcher:
            return self.matcher.matches(self.response)

        return True

    def describe_to(self, description):
        description.append_text(u'a JSON object that ').append_description_of(self.matcher)

    def describe_mismatch(self, response, description):
        description.append_text(u'was ').append_value(self.response)
        if self.matcher:
            self.matcher.describe_mismatch(self.response, description)


class callable_(BaseMatcher):
    def _matches(self, item):
        return callable(item)

    def describe_to(self, description):
        description.append_text(u'callable object')

    def describe_mismatch(self, actual, description):
        description.append_text(u' the object {} was not a callable object'.format(actual))


class has_properties(BaseMatcher):
    def __init__(self, *args, **kwargs):
        """ has_properties(dict) or has_properties(a=1, b=2) """
        if args:
            kwargs.update(args[0])

        self.entries = dict(kwargs)

    def _matches(self, obj):
        return has_entries(self.entries).matches(self._properties(obj))

    def _properties(self, obj):
        return {k: getattr(obj, k, None) for k in self.entries.iterkeys()}

    def describe_to(self, description):
        description.append_text(u'an object with all this properties: {}'.format(self.entries))

    def describe_mismatch(self, actual, description):
        properties = self._properties(actual)
        description.append_text(u' but found instead a {} object with this properties: {}'
                                .format(actual, properties))
        difference = set(properties.items()) - set(self.entries.items())
        description.append_text(u' which differs in {}'.format(difference))


class empty(BaseMatcher):
    def _matches(self, obj):
        try:
            iter(obj).next()
        except StopIteration:
            return True
        except TypeError:
            return not bool(obj)
        else:
            return False

    def describe_to(self, description):
        description.append_text(u' an empty object ')


class has_keys(BaseMatcher):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Iterable):
            args = args[0]

        self.entries = set(args)

    def _matches(self, obj):
        return not bool(self.entries - set(dict(obj).keys()))

    def describe_to(self, description):
        description.append_text(u'a dictionary contains all this keys: {}'.format(self.entries))

    def describe_mismatch(self, actual, description):
        description.append_text(u' but found instead: {}'.format(actual))
        description.append_text(u' which misses keys: {}'.format(self.entries - set(actual.keys())))


class iterable(BaseMatcher):
    def _matches(self, obj):
        return isinstance(obj, Iterable)

    def describe_to(self, description):
        description.append_text(u'an iterable object ')

    def describe_mismatch(self, actual, description):
        description.append_text(u' but found instead a {} object, which is not iterable'.format(actual))


class _setmatcher(BaseMatcher):
    def __init__(self, sequence):
        self.sequence = set(sequence)

    def describe_mismatch(self, actual, description):
        description.append_text(u' but found instead {}, wich differs of the target in {}'
                                .format(self.other_sequence, self.sequence.difference(self.other_sequence)))


class subset_of(_setmatcher):
    def _matches(self, other_sequence):
        self.other_sequence = set(other_sequence)
        return self.other_sequence.issubset(self.sequence)

    def describe_to(self, description):
        description.append_text(u'a set of which {} is a subset'.format(self.sequence))


class superset_of(_setmatcher):
    def _matches(self, other_sequence):
        self.other_sequence = set(other_sequence)
        return self.other_sequence.issuperset(self.sequence)

    def describe_to(self, description):
        description.append_text('a set of which {} is superset'.format(self.sequence))


class disjoint_with(_setmatcher):
    def _matches(self, other_sequence):
        self.other_sequence = set(other_sequence)
        return self.other_sequence.isdisjoint(self.sequence)

    def describe_to(self, description):
        description.append_text('a set disjoint of {}'.format(self.sequence))


class as_unicode(BaseMatcher):
    def __init__(self, matcher=None):
        self.matcher = matcher

    def _matches(self, obj):
        try:
            uobj = unicode(obj)
        except UnicodeDecodeError:
            raise AssertionError(u'object "{}" is not unicode codificable'.format(obj))
        else:
            return matcher.matches(unicode(uobj))


@contextmanager
def assert_that_raises(matcher_or_exception):
    exception, matcher = ((matcher_or_exception, None)
                          if isinstance(matcher_or_exception, Exception)
                          else (Exception, matcher_or_exception))

    catched = {'exception': None}
    try:
        yield catched
    except exception as raised:
        catched['exception'] = raised
        if matcher is not None:
            assert_that(raised, matcher)
    else:
        raise AssertionError(u'no {} raised'.format(exception.__name__))
