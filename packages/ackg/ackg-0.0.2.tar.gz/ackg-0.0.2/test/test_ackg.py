import os
import imp
from mock import Mock

imp.load_source('ackg', os.path.join(os.path.dirname(__file__), '..', 'bin', 'ackg'))
import ackg

import unittest

def get_args(args=None):
    return ackg.get_arg_parser().parse_args(args)


class TestAckg(unittest.TestCase):


    def test_get_arg_parser(self):
        parser = ackg.get_arg_parser()


    def test_create_find_cmd(self):
        args = get_args()
        result = ackg.create_find_cmd(args)
        self.assertTrue(result.startswith('find'), result)
        self.assertTrue(' -type f ' in result, result)
        self.assertTrue(result.endswith('print0'), result)
        
    def test_create_defer_cmd(self):
        args = get_args()
        result = ackg.create_defer_cmd(args)
        self.assertTrue(result.startswith('xargs'), result)
        self.assertTrue(' -0 ' in result, result)
        self.assertTrue(' -n 100' in result, result)

    def test_create_grep_cmd(self):
        args = get_args(['foo'])
        result = ackg.create_grep_cmd(args)
        self.assertTrue(result.startswith('grep'), result)
        self.assertTrue(' --binary-files=without-match ' in result, result)
        self.assertTrue(' --color ' in result, result)
        self.assertTrue(' --ignore-case ' in result, result)
        self.assertTrue(' --line-number ' in result, result)
        self.assertTrue(' --with-filename ' in result, result)
