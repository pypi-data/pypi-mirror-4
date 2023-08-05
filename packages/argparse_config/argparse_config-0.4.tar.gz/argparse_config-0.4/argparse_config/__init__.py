"""
Author: tikitu
"""
import ConfigParser
from argparse import _SubParsersAction, _StoreAction, _StoreConstAction

__version__ = '0.4'

def read_config_file(arg_parser, filename):
    config_parser = ConfigParser.SafeConfigParser(allow_no_value=True)
    config_parser.read([filename])
    read_config_parser(arg_parser, config_parser)

def read_config_parser(arg_parser, config_parser):
    ReadConfig(config_parser=config_parser).walk_parser(arg_parser)

def generate_config(arg_parser, parsed_args, only_non_defaults=False):
    action = GenerateConfig(parsed_args, only_non_defaults=only_non_defaults)
    action.walk_parser(arg_parser)
    return action.contents

class ArgParserWalker(object):

    def start_section(self, section_name):
        raise NotImplementedError()
    def end_section(self):
        raise NotImplementedError()
    def process_parser_action(self, action, is_store_const=False):
        raise NotImplementedError()

    def walk_parser(self, arg_parser):
        try:
            self.start_section('default')
            for action in arg_parser._actions:
                if isinstance(action, _StoreAction):
                    self.process_parser_action(action)
                elif isinstance(action, _StoreConstAction):
                    self.process_parser_action(action, is_store_const=True)
                elif isinstance(action, _SubParsersAction):
                    for command, sub_parser in action.choices.items():
                        self.start_section(command)
                        for sub_action in sub_parser._actions:
                            self.process_parser_action(sub_action)
                        self.end_section()
            self.end_section()
        except DefaultError as e:
            arg_parser.error(u'[{section_name}] config option "{option_string}" must be {type_transformer}() value, got: {value}'.format(
                section_name=e.section_name,
                option_string = e.option_string,
                type_transformer=e.type_transformer.__name__,
                value=e.value
            ))

class GenerateConfig(ArgParserWalker):

    def __init__(self, parsed_args, only_non_defaults=False):
        self.parsed_args = parsed_args
        self._contents = []
        self._only_non_defaults = only_non_defaults

    def start_section(self, section_name):
        if self._contents:
            self._contents.append(u'')
        self._contents.append(u'[{0}]'.format(section_name))

    def end_section(self):
        pass

    @property
    def contents(self):
        return u'\n'.join(self._contents + [u''])

    def process_parser_action(self, action, is_store_const=False):
        # take the longest string, since that is likely the most informative
        action_name = list(action.option_strings)
        action_name.sort(key=lambda s: len(s), reverse=True)
        action_name = _convert_option_string(action_name[0])

        action_value = getattr(self.parsed_args, action.dest, None)
        if self._only_non_defaults and action_value == action.default:
            action_value = None
        if action_value is not None:
            if is_store_const:
                self._contents.append(action_name)
            else:
                self._contents.append(u'{action_name}: {default_value}'.format(
                    action_name=action_name,
                    default_value=action_value, # and hope it prints the way we want it to...
                ))


class ReadConfig(ArgParserWalker):

    def __init__(self, config_parser=None):
        self.sections = []
        self.config_parser = config_parser

    def start_section(self, section_name):
        self.sections.append(section_name)

    def end_section(self):
        self.sections.pop()

    @property
    def current_section(self):
        return self.sections[-1] if self.sections else None

    def process_parser_action(self, action, is_store_const=False):
        for option_string in action.option_strings:
            option_string = _convert_option_string(option_string)
            if self.config_parser.has_option(self.current_section, option_string):
                if is_store_const:
                    action.default = action.const
                else:
                    value = self.config_parser.get(self.current_section, option_string)
                    type_transformer = action.type if action.type is not None else lambda x:x
                    try:
                        action.default = type_transformer(value)
                    except:
                        raise DefaultError(self.current_section, option_string, value, type_transformer)
                action.required = False

class DefaultError(Exception):
    def __init__(self, section_name, option_string, value, type_transformer):
        self.section_name = section_name
        self.option_string = option_string
        self.value = value
        self.type_transformer = type_transformer

def _convert_option_string(op_s):
    return op_s.lstrip('-').replace('-', '_')

