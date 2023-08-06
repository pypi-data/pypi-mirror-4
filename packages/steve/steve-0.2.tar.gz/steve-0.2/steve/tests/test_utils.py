#######################################################################
# This file is part of steve.
#
# Copyright (C) 2012, 2013 Will Kahn-Greene
# Licensed under the Simplified BSD License. See LICENSE for full
# license.
#######################################################################

import datetime
from unittest import TestCase

from nose.tools import eq_

from steve.util import verify_video_data, html_to_markdown


class TestVerifyVideoData(TestCase):
    default = {
        'title': 'Foo',
        'category': 'Test Category',
        'language': 'English',
        'added': datetime.datetime.now().isoformat()
        }

    def test_default_minimum(self):
        """Verify that default verifies"""
        # Note: This is dependent on video_reqs.json data.

        data = dict(self.default)

        eq_(len(verify_video_data(data)), 0)

    def test_category(self):
        """Test category variations"""
        # category is none, no data['category']
        data = dict(self.default)
        del data['category']
        eq_(len(verify_video_data(data, None)), 1)

        # category is something, no data['category']
        eq_(len(verify_video_data(data, 'Test Category')), 0)

        # category is none, data['category'] = something
        data = dict(self.default)
        eq_(len(verify_video_data(data, None)), 0)

        # category is something, data['category'] = same something
        eq_(len(verify_video_data(data, data['category'])), 0)

        # category is something, data['category'] = different something
        eq_(len(verify_video_data(data, data['category'] + 'abc')), 1)

    def test_minimum_requirements(self):
        """Tests verifying required fields"""
        # Note: This is dependent on video_reqs.json data.

        data = dict(self.default)
        del data['title']
        eq_(len(verify_video_data(data)), 1)

        data = dict(self.default)
        del data['category']
        eq_(len(verify_video_data(data)), 1)

        data = dict(self.default)
        del data['language']
        eq_(len(verify_video_data(data)), 1)

        data = dict(self.default)
        del data['added']
        eq_(len(verify_video_data(data)), 1)

        # Four errors if we pass in an empty dict
        eq_(len(verify_video_data({})), 4)

    def test_speakers(self):
        """Tests speakers which is a TextArrayField"""
        # Note: This is dependent on video_reqs.json data.

        data = dict(self.default)

        data['speakers'] = []
        eq_(len(verify_video_data(data)), 0)

        data['speakers'] = ['']
        eq_(len(verify_video_data(data)), 1)

        data['speakers'] = ['Jimmy Discotheque']
        eq_(len(verify_video_data(data)), 0)

    def test_state(self):
        """Test verifying state (IntegerField with choices)"""
        # Note: This is dependent on video_reqs.json data.

        data = dict(self.default)

        data['state'] = 0
        eq_(len(verify_video_data(data)), 1)

        data['state'] = 1
        eq_(len(verify_video_data(data)), 0)

        data['state'] = 2
        eq_(len(verify_video_data(data)), 0)

        data['state'] = 3
        eq_(len(verify_video_data(data)), 1)

    def test_video_ogv_download_only(self):
        """Test BooleanField"""
        # Note: This is dependent on video_reqs.json data.

        data = dict(self.default)

        data['video_ogv_download_only'] = True
        eq_(len(verify_video_data(data)), 0)

        data['video_ogv_download_only'] = False
        eq_(len(verify_video_data(data)), 0)

        data['video_ogv_download_only'] = 'True'
        eq_(len(verify_video_data(data)), 1)


def test_html_to_markdown():
    """Test html_to_markdown"""
    eq_(html_to_markdown('<p>this is <b>html</b>!</p>'),
        u'this is **html**!')
