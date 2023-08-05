from ConfigParser import SafeConfigParser
from StringIO import StringIO
from argparse import ArgumentParser
import functools
import tempfile
import textwrap
from unittest import TestCase
from .. import read_config_parser, read_config_file, generate_config

__author__ = 'tikitu'

def with_config_file():
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self):
            config_file = textwrap.dedent(f.__doc__.lstrip('\n'))
            config_parser = SafeConfigParser(allow_no_value=True)
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

        read_config_parser(arg_parser, config_parser)

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

        read_config_parser(arg_parser, config_parser)

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

        read_config_parser(arg_parser, config_parser)

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
        no_value_flag_without_colon
        """
        arg_parser = ArgumentParser()
        arg_parser.add_argument('--flag', action='store_const', const=True, default=False)
        arg_parser.add_argument('--inverted-flag', action='store_const', const=False, default=True)
        arg_parser.add_argument('--unused-flag', action='store_const', const=True, default=False)
        arg_parser.add_argument('--value-ignored-flag', action='store_const', const='used', default=None)
        arg_parser.add_argument('--no-value-flag', action='store_const', const=True, default=False)
        arg_parser.add_argument('--no-value-flag-without-colon', action='store_true')

        read_config_parser(arg_parser, config_parser)

        parsed_args = arg_parser.parse_args([])

        self.assertEqual(parsed_args.flag, True)
        self.assertIs(parsed_args.inverted_flag, False, "Effect should be the same as commandline")
        self.assertEqual(parsed_args.value_ignored_flag, 'used', "Not what is in the config file")
        self.assertEqual(parsed_args.no_value_flag, True, "Indeed, no value in the config file is actually needed")
        self.assertIs(parsed_args.no_value_flag_without_colon, True)

    @with_config_file()
    def test_store_true_false(self, config_parser):
        """
        [default]
        flag:
        flag_false:
        """
        arg_parser = ArgumentParser()
        arg_parser.add_argument('--flag', action='store_true')
        arg_parser.add_argument('--flag-false', action='store_false')

        read_config_parser(arg_parser, config_parser)

        parsed_args = arg_parser.parse_args([])

        self.assertIsNotNone(parsed_args.flag)
        self.assertIs(parsed_args.flag, True)
        self.assertIsNotNone(parsed_args.flag_false)
        self.assertIs(parsed_args.flag_false, False)

    def test_file_shortcut(self):
        arg_parser = ArgumentParser()
        arg_parser.add_argument('--verbose', action='store_const', const=True)
        file_contents = textwrap.dedent("""
        [default]
        verbose
        """.lstrip('\n'))
        temp_file = tempfile.NamedTemporaryFile()
        with temp_file.file as f:
            f.write(file_contents)
            f.flush()
            read_config_file(arg_parser, temp_file.name)
        parsed_args = arg_parser.parse_args([])
        self.assertTrue(parsed_args.verbose)

class DefaultsOutputTest(TestCase):

    @with_config_file()
    def test_everything(self, config_parser):
        """
        [default]
        int_value: 3
        flag
        """
        arg_parser = ArgumentParser()
        arg_parser.add_argument('--int-value', type=int)
        arg_parser.add_argument('--flag', action='store_true')

        sub_parsers = arg_parser.add_subparsers()
        subcommand_parser = sub_parsers.add_parser('subcommand')
        subcommand_parser.add_argument('--tool', default='hammer')
        subcommand_parser.add_argument('--object', default='nail')

        parsed_args = arg_parser.parse_args(['subcommand'])
        new_config_file = generate_config(arg_parser, parsed_args)
        self.assertEquals(new_config_file, textwrap.dedent("""
        [default]

        [subcommand]
        tool: hammer
        object: nail
        """.lstrip('\n')))

        read_config_parser(arg_parser, config_parser)
        parsed_args = arg_parser.parse_args(['subcommand', '--object', 'thumb'])
        new_config_file = generate_config(arg_parser, parsed_args)
        self.assertEquals(new_config_file, textwrap.dedent("""
        [default]
        int_value: 3
        flag:

        [subcommand]
        tool: hammer
        object: thumb
        """.lstrip('\n')))

    @with_config_file()
    def test_everything(self, config_parser):
        """
        [default]
        flag
        """
        def check_round_trip(arg_parser):
            read_config_parser(arg_parser, config_parser)
            parsed_args = arg_parser.parse_args([])
            new_config_file = generate_config(arg_parser, parsed_args)
            self.assertEquals(new_config_file, textwrap.dedent("""
            [default]
            flag
            """.lstrip('\n')))

        arg_parser = ArgumentParser()
        arg_parser.add_argument('--flag', action='store_true')
        check_round_trip(arg_parser)

        arg_parser = ArgumentParser()
        arg_parser.add_argument('--flag', action='store_false')
        check_round_trip(arg_parser)

    @with_config_file()
    def test_only_new(self, config_parser):
        """
        [default]
        flag
        int_value: 3
        """
        arg_parser = ArgumentParser()
        arg_parser.add_argument('--flag', action='store_true')
        arg_parser.add_argument('--int-value', default=1)
        arg_parser.add_argument('--str-value')

        parsed_args = arg_parser.parse_args(['--str-value', 'ssss'])
        new_config_file = generate_config(arg_parser, parsed_args, only_non_defaults=True)
        self.assertEquals(new_config_file, textwrap.dedent("""
        [default]
        str_value: ssss
        """.lstrip('\n')))
