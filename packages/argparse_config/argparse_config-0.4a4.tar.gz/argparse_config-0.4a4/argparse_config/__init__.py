"""
Author: tikitu
"""
import ConfigParser
from argparse import _SubParsersAction, _StoreAction, _StoreConstAction

__version__ = '0.4a4'

def read_config(arg_parser, filename):
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read([filename])
    set_defaults(arg_parser, config_parser)

def set_defaults(argparser, config_parser):
    try:
        for action in argparser._actions:
            if isinstance(action, _StoreAction):
                _process_parser_action(action, config_parser)
            elif isinstance(action, _StoreConstAction):
                _process_parser_action(action, config_parser, is_store_const=True)
            elif isinstance(action, _SubParsersAction):
                for command, sub_parser in action.choices.items():
                    if config_parser.has_section(command):
                        for sub_action in sub_parser._actions:
                            _process_parser_action(sub_action, config_parser, section_name=command)
    except DefaultError as e:
        argparser.error(u'[{section_name}] config option "{option_string}" must be {type_transformer}() value, got: {value}'.format(
            section_name=e.section_name,
            option_string = e.option_string,
            type_transformer=e.type_transformer.__name__,
            value=e.value
        ))

class DefaultError(Exception):
    def __init__(self, section_name, option_string, value, type_transformer):
        self.section_name = section_name
        self.option_string = option_string
        self.value = value
        self.type_transformer = type_transformer

def _convert_option_string(op_s):
    return op_s.lstrip('-').replace('-', '_')

def _process_parser_action(action, config_parser, section_name='default', is_store_const=False):
    for option_string in action.option_strings:
        option_string = _convert_option_string(option_string)
        if config_parser.has_option(section_name, option_string):
            if is_store_const:
                action.default = action.const
            else:
                value = config_parser.get(section_name, option_string)
                type_transformer = action.type if action.type is not None else lambda x:x
                try:
                    action.default = type_transformer(value)
                except:
                    raise DefaultError(section_name, option_string, value, type_transformer)
            action.required = False

