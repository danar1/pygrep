#!/usr/bin/env python3

import argparse
import re
import sys
from typing import List

from abc import ABC, abstractmethod


class IFormatter(ABC):

    @staticmethod
    @abstractmethod
    def format_string(matches, file_name, line_number, line):
        """
        Interface method
        """
        pass


class UnderlineFormatter(IFormatter):

    @staticmethod
    def format_string(matches, file_name, line_number, line):
        """
        Format a string:
        "file_name line_number line"
        such that for each match object index range,
        the corresponding portion of the line in this index range is underlined with '^'
        :param matches: re.Match objects iterator
        :param file_name: file name
        :param line_number: line number of "line" in the provided file_name
        :param line: line from the provided file_name
        :return: returns the formatted string, or empty string if no match
        """
        formatted_string = ''
        start_index = 0
        ansi_caret = f'\u005e'
        caret_string = ''

        for match in matches:
            match_start_index, match_end_index = match.span()
            substring_before_match = line[start_index:match_start_index]
            match_string_caret = line[match_start_index:match_end_index]
            caret_string += ' ' * len(substring_before_match) + ansi_caret + ' ' * len(match_string_caret[:-1])
            start_index = match_end_index
        if len(caret_string) > 0:
            caret_string += " " * len(line[start_index:])
            formatted_string = f'{file_name} {line_number} {line}' \
                               f'{" " * len(file_name)} {" " * len(str(line_number))} {caret_string}\n'
        return formatted_string


class StandardFormatter(IFormatter):

    @staticmethod
    def format_string(matches, file_name: str, line_number: int, line: str):
        """
        Format a string:
        "file_name line_number line"
        :param matches: re.Match objects iterator
        :param file_name: file name
        :param line_number: line number of "line" in the provided file_name
        :param line: line from the provided file_name
        :return: returns the formatted string, or empty string if no match
        """
        formatted_string = ''
        matches_list = list(matches)
        if len(matches_list) > 0:
            formatted_string = f'{file_name} {line_number} {line}'
        return formatted_string


class MachineFormatter(IFormatter):

    @staticmethod
    def format_string(matches, file_name, line_number, line):
        """
        Format a string:
        "file_name:line_number:start_position:matched_text"
        such that start position and matched text of first occurrence (in the line) are displayed
        :param matches: re.Match objects iterator
        :param file_name: file name
        :param line_number: line number of "line" in the provided file_name
        :param line: line from the provided file_name
        :return: returns the formatted string, or empty string if no match
        """
        formatted_string = ''
        matches_list = list(matches)
        if len(matches_list) > 0:
            first_match = matches_list[0]
            start_index, end_index = first_match.span()
            formatted_string = f'{file_name}:{line_number}:{start_index}:{line[start_index:end_index]}\n'
        return formatted_string


class ColorFormatter(IFormatter):

    @staticmethod
    def format_string(matches, file_name: str, line_number: int, line: str):
        """
        Format a string:
        "file_name line_number line"
        such that for each match object index range,
        the corresponding portion of the line in this index range is colored in red
        :param matches: re.Match objects iterator
        :param file_name: file name
        :param line_number: line number of "line" in the provided file_name
        :param line: line from the provided file_name
        :return: returns the formatted string, or empty string if no match
        """
        colored_line = ''
        formatted_string = ''
        start_index = 0
        ansi_red = '\u001b[31m'
        ansi_reset = '\u001b[0m'

        for match in matches:
            match_start_index, match_end_index = match.span()
            substring_before_match = line[start_index:match_start_index]
            match_string_colored = ansi_red + line[match_start_index:match_end_index] + ansi_reset
            colored_line += substring_before_match + match_string_colored
            start_index = match_end_index
        if len(colored_line) > 0:
            colored_line += line[start_index:]
            formatted_string = f'{file_name} {line_number} {colored_line}'
        return formatted_string


class FormatterFactory:
    """
    Formatter factory
    Returns at runtime the desired formatter,
    based on requested format_style
    """

    # formats style
    COLOR = 'color'
    MACHINE = 'machine'
    UNDERLINE = 'underline'
    STANDARD = 'standard'

    @classmethod
    def get_formatter(cls, format_style: str = None):
        if format_style == cls.STANDARD:
            formatter_obj = StandardFormatter()
        elif format_style == cls.COLOR:
            formatter_obj = ColorFormatter()
        elif format_style == cls.MACHINE:
            formatter_obj = MachineFormatter()
        elif format_style == cls.UNDERLINE:
            formatter_obj = UnderlineFormatter()
        else:
            raise ValueError(f"format_style must be one of: "
                             f"'{cls.STANDARD}', '{cls.COLOR}', '{cls.MACHINE}', '{cls.UNDERLINE}'")

        return formatter_obj


class PatternMatcher:

    def __init__(self, regex: str, formatter: IFormatter):
        self.regex = regex
        self.formatter = formatter

    def print_matches_from_files(self, files_list: List[str]) -> None:
        for file_name in files_list:
            with open(file_name, 'r') as f:
                self._print_matches(self.regex, self.formatter, f, file_name)

    def print_matches_from_strings(self, strings_list: List[str]) -> None:
        self._print_matches(self.regex, self.formatter, strings_list)

    @staticmethod
    def _print_matches(regex: str, formatter: IFormatter, iterable, file_name: str = 'STDIN') -> None:
        try:
            raw_regex_string = r'{}'.format(regex)
            pattern = re.compile(raw_regex_string)
        except re.error as ex:
            print(f'Bad regex, {ex}, regex: "{raw_regex_string}"')
            raise SystemExit(1)

        for line_number, line in enumerate(iterable, 1):
            matches = pattern.finditer(line)
            formatted_line = formatter.format_string(matches, file_name, line_number, line)
            if formatted_line:
                print(formatted_line, end='')


def read_from_stdin() -> List[str]:
    """
    Read input from stdin until encounter 'q' character
    :return: returns a list of lines read from stdin
    """
    stdin_lines = []
    for line in sys.stdin:
        if 'q' == line.rstrip():
            break
        stdin_lines.append(line)
    return stdin_lines


def parse_args():
    """
    Parse command line arguments
    :return: argparse.Namespace object
    """
    parser = argparse.ArgumentParser(prog='pygrep',
                                     description='Searches for a pattern using a regular expression in lines of text, '
                                                 'and prints the lines which contain matching text')
    parser.add_argument('-r', '--regex',
                        dest='regex',
                        action='store',
                        required=True,
                        help='The regular expression to search for')
    parser.add_argument('-f', '--files',
                        dest='files',
                        nargs='+',
                        action='store',
                        help='A list of files to search in. '
                             'If this parameter is omitted, the script expects text input from STDIN')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--underline',
                       dest='underline',
                       action='store_true',
                       help='"^" is printed underneath the matched text')
    group.add_argument('-c', '--color',
                       dest='color',
                       action='store_true',
                       help='The matched text is highlighted in color')
    group.add_argument('-m', '--machine',
                       dest='machine',
                       action='store_true',
                       help='Print the output in the format: '
                            'file_name:line_number:start_position:matched_text"')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if args.color:
        format_style = FormatterFactory.COLOR
    elif args.machine:
        format_style = FormatterFactory.MACHINE
    elif args.underline:
        format_style = FormatterFactory.UNDERLINE
    else:
        format_style = FormatterFactory.STANDARD

    formatter = FormatterFactory.get_formatter(format_style=format_style)
    pattern_matcher = PatternMatcher(regex=args.regex, formatter=formatter)

    if args.files is not None:
        pattern_matcher.print_matches_from_files(files_list=args.files)
    else:
        stdin_input_list = read_from_stdin()
        pattern_matcher.print_matches_from_strings(strings_list=stdin_input_list)


if __name__ == '__main__':
    main()
