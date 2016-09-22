#
# Copyright (c) [2014] John Zimmermann
#
# $URL$
# $Date: 2014-11-06$
# $Revision: 1.0$
# $Author: johnz $
#

import os
import re
import sys


class CharacterDetails(object):
    '''
    Collection of character details, including types and library paths,
        found on disk
    '''
    _char_code_pattern = "^([A-Z]{3})"

    def __init__(self):
        '''
        Initialize instance basic details before attempting collect characters
        '''
        self._char_assetlib = r"B:\show\TRUCE\assets\characters"
        self._char_types = ['background', 'hero', 'secondary']
        self._characters = {}

        self._collect_characters()

    def _collect_characters(self):
        '''
        Attempt to collect characters and details from asset library path
        '''
        for char_type in self._char_types:
            tmp_path = os.path.join(self._char_assetlib, char_type)
            char_dirs = os.listdir(tmp_path)

            for char_dir in char_dirs:
                char_code = self._char_code(char_dir)
                if not char_code:
                    continue

                self._characters[char_code] = {'type': char_type,
                                                'long_name': char_dir}

    # def __repr__(self):
    #     '''
    #     Build formatted representation of current instance collection results
    #     '''
    #     if not self._characters:
    #         return None
    #
    #     display_text = ''
    #     char_codes = self._characters.keys()
    #     char_codes.sort()
    #     for schar in char_codes:
    #         display_text += "%s\n" % schar
    #         details = self._characters[schar].keys()
    #         details.sort()
    #         for detail in details:
    #             display_text += "\t%s: %s\n" % (detail,
    #                                             self._characters[schar][detail])
    #
    #     return display_text

    def __repr__(self):
        '''
        Build formatted representation of current instance collection results
        '''
        if not self._characters:
            return None

        display_text = "%s {'_char_assetlib': %s," \
                                    % (self.__class__, self._char_assetlib)\
                       + " '_char_types': %s, '_characters': {" \
                                    % str(self._char_types)

        char_codes = self._characters.keys()
        char_codes.sort()
        for schar in char_codes:
            display_text += "%s: {" % schar
            details = self._characters[schar].keys()
            details.sort()
            for detail in details:
                display_text += "%s: %s" % (detail,
                                                self._characters[schar][detail])
                if detail != details[len(details) - 1]:
                    display_text += ", "
            display_text += "}"
            if schar != char_codes[len(char_codes) - 1]:
                display_text += ", "
        display_text += "}\n"

        return display_text

    def char_code_exists(self, char_code):
        '''
        Determine if specified character code actually exists in
            current character findings from disk

        :type   char_code: C{str}
        :param  char_code: character code to determine if details exist
        '''
        if char_code in self._characters.keys():
            return True

        return False

    def get_char_path(self, char_code):
        '''
        Get the base library path for specified character code

        :type   char_code: C{str}
        :param  char_code: character code to locate path for
        '''
        if self.char_code_exists(char_code):
            return os.path.join(self._char_assetlib,
                                self._characters[char_code]['type'],
                                self._characters[char_code]['long_name'])

    @property
    def hero_chars(self):
        '''
        Get only the hero characters
        '''
        return self._get_character_type('hero')

    @property
    def background_chars(self):
        '''
        Get only the background characters
        '''
        return self._get_character_type('background')

    @property
    def secondary_chars(self):
        '''
        Get only the secondary characters
        '''
        return self._get_character_type('secondary')

    def _get_character_type(self, char_type):
        '''
        Collect only the characters of specified type

        :type   char_type: C{str}
        :param  char_type: character type to look for
        '''
        found_chars = {}
        for char in self._characters.keys():
            if char_type == self._characters[char]['type']:
                found_chars[char] = self._characters[char]

        return found_chars

    @classmethod
    def _char_code(cls, char_dir):
        '''
        Attempt to collect character code from found 'character' directory

        :type   char_dir: C{str}
        :param  char_dir: base directory name to check for character code
        :return:
        '''
        test_code = re.compile(cls._char_code_pattern)
        if test_code.search(char_dir):
            # print 'found'
            char_code = test_code.search(char_dir).groups()[0]
            # print char_code
            return char_code

        return None