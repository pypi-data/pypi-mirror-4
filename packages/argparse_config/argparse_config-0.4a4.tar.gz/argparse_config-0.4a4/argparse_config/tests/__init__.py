from ConfigParser import SafeConfigParser
from StringIO import StringIO
from argparse import ArgumentParser
import functools
import tempfile
import textwrap
from unittest import TestCase
from .. import set_defaults, read_config

__author__ = 'tikitu'

def with_config_file():
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self):
            config_file = textwrap.dedent(f.__doc__.lstrip('\n'))
            config_parser = SafeConfigParser()
            config_parser.readfp(StringIO(config_file))
            return f(self, config_parser)
        return wrapper
    return decorator

class DefaultsTest(TestCase):

    @with_config_file()
    def test_types(self, config_parser):
        '''
        [default]
        int_v: 1
        string_v: s
        false_bool_v:
        true_bool_v: 1
        float_v: 1.5
        '''

        arg_parser = ArgumentParser()
        arg_parser.add_argument('--int-v', default=2, type=int)
        arg_parser.add_argument('--string-v', default='z', type=str)
        arg_parser.add_argument('--false-bool-v', default=True, type=bool)
        arg_parser.add_argument('--true-bool-v', default=False, type=bool)
        arg_parser.add_argument('--float-v', default=2.0, type=float)

        set_defaults(arg_parser, config_parser)

        parsed_args = arg_parser.parse_args([])
        self.assertEqual(parsed_args.int_v, 1)
        self.assertEqual(parsed_args.string_v, 's')
        self.assertEqual(parsed_args.false_bool_v, False)
        self.assertEqual(parsed_args.true_bool_v, True)
        self.assertEqual(parsed_args.float_v, 1.5)

    @with_config_file()
    def test_subcommands(self, config_parser):
        """
        [default]
        repository: https://tikitu@bitbucket.org/tikitu/argparse_config

        [merge]
        tool: meld

        [commit]
        user: Tikitu de Jager <tikitu@logophile.org>
        """

        arg_parser = ArgumentParser('hg')
        arg_parser.add_argument('--repository')
        sub_parsers = arg_parser.add_subparsers()

        merge_parser = sub_parsers.add_parser('merge')
        merge_parser.add_argument('--tool')

        commit_parser = sub_parsers.add_parser('commit')
        commit_parser.add_argument('--user')

        set_defaults(arg_parser, config_parser)

        parsed_args = arg_parser.parse_args(['merge'])
        self.assertEqual(parsed_args.repository, 'https://tikitu@bitbucket.org/tikitu/argparse_config')
        self.assertEqual(parsed_args.tool, 'meld')

        parsed_args = arg_parser.parse_args(['commit'])
        self.assertEqual(parsed_args.user, 'Tikitu de Jager <tikitu@logophile.org>')

    @with_config_file()
    def test_required(self, config_parser):
        """
        [default]
        required_arg: provided
        """
        arg_parser = ArgumentParser()
        arg_parser.add_argument('--required-arg', required=True)

        set_defaults(arg_parser, config_parser)

        parsed_args = arg_parser.parse_args([])

        self.assertEqual(parsed_args.required_arg, 'provided')

    @with_config_file()
    def test_store_const(self, config_parser):
        """
        [default]
        flag: 1
        inverted_flag: 1
        value_ignored_flag: ignored
        no_value_flag:
        """
        arg_parser = ArgumentParser()
        arg_parser.add_argument('--flag', action='store_const', const=True, default=False)
        arg_parser.add_argument('--inverted-flag', action='store_const', const=False, default=True)
        arg_parser.add_argument('--unused-flag', action='store_const', const=True, default=False)
        arg_parser.add_argument('--value-ignored-flag', action='store_const', const='used', default=None)
        arg_parser.add_argument('--no-value-flag', action='store_const', const=True, default=False)

        set_defaults(arg_parser, config_parser)

        parsed_args = arg_parser.parse_args([])

        self.assertEqual(parsed_args.flag, True)
        self.assertEqual(parsed_args.inverted_flag, False, "Effect should be the same as commandline")
        self.assertEqual(parsed_args.value_ignored_flag, 'used', "Not what is in the config file")
        self.assertEqual(parsed_args.no_value_flag, True, "Indeed, no value in the config file is actually needed")

    def test_file_shortcut(self):
        arg_parser = ArgumentParser()
        arg_parser.add_argument('--verbose', action='store_const', const=True)
        file_contents = textwrap.dedent("""
        [default]
        verbose:
        """.lstrip('\n'))
        temp_file = tempfile.NamedTemporaryFile()
        with temp_file.file as f:
            f.write(file_contents)
            f.flush()
            read_config(arg_parser, temp_file.name)
        parsed_args = arg_parser.parse_args([])
        self.assertTrue(parsed_args.verbose)
        