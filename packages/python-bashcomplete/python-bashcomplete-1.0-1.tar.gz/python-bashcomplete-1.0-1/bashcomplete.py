#!/usr/bin/env python

import os
import re
import sys

bash_template = '''
_endCompletion()
{
    if [[ ${cur} == -* || ${COMP_CWORD} -eq $1 ]] ; then
        _clearCompletion
        COMPLETED=1
    fi
}

_clearCompletion()
{
    COMPREPLY=()
}

_setCompletion()
{
    if [[ $COMPLETED -eq 0 ]] ; then
        COMPREPLY=( $( compgen -W "$use" -- $cur ) )
        COMPLETED=1
    fi
}

_%s()
{
    # Reset previous array
    COMPLETED=0
    _clearCompletion
    cur="${COMP_WORDS[COMP_CWORD]}"

%s

%s
}
complete %s -F _%s %s
'''

level_template = '%slevel%s="${COMP_WORDS[%s]}"'

space_increment = '    '

class BashComplete:


    def append_begin_case(self, spaces, level):
        '''Helper method for duplicate code'''

        self.bash_append('case "${level%s}" in', spaces, level)

    def append_switch_case(self, spaces, key):
        '''Helper method for duplicate code'''

        self.bash_append('%s)', spaces, key)

    def append_terminal_case(self, spaces, level):
        '''Helper method for duplicate code'''

        self.bash_append('*)', spaces + 1)
        self.bash_append('_endCompletion %s', spaces + 2, level + 1)
        self.bash_append(';;', spaces + 2)

    def append_end_case(self, spaces, uses, first_level=False):
        '''Helper method for duplicate code'''

        self.bash_append('esac', spaces)
        if uses:
            self.bash_append('use="%s"', spaces, ' '.join(uses))
        else:
            self.bash_append('use=""', spaces)
        self.bash_append('_setCompletion', spaces)

        if not first_level:
            self.bash_append(';;', spaces)

    def process_next_level(self, parent_level, these_keys, spaces, level):
        '''Helper method for duplicate code'''

        # Cycle through all keys on this level
        for this_key in these_keys:
            # Create this level
            self.append_switch_case(spaces + 1, this_key)

            # go one level deeper
            self.generate_bash_complete(parent_level[this_key], spaces + 2, level + 1)


    def __init__(self, incoming, constrain=False):
        # Internal variables
        self.constrain = constrain
        self.bash_array = []
        self.max_level = 1

        # Start bashcomplete generation
        self.generate_bash_complete(incoming, spaces=1, level=1, first_level=True)

        # Write to file
        self.output()


    def generate_bash_complete(self, parent_level, spaces, level, first_level=False):
        '''Generates most of the bashcomplete code.'''

        # Keep count of max_level for code generation
        if level > self.max_level:
            self.max_level = level

        # Create the cases for this level
        self.append_begin_case(spaces, level)

        if isinstance(parent_level, list):
            # Check lists of strings and dicts

            these_keys = []
            next_level = {}

            for key in parent_level:
                if isinstance(key, dict):
                    # Keep subkeys as options for this level
                    # Queue for further investigation
                    for subkey in key:
                        these_keys.append(subkey)
                        next_level.update(key)
                else:
                    # Keep all strings as options for this level
                    these_keys.append(key)

            if next_level:
                # Sort all keys for readability
                next_keys = next_level.keys()
                next_keys.sort()

                # Process the next level
                self.process_next_level(next_level, next_keys, spaces, level)

            # If no subkeys, end bashcomplete
            self.append_terminal_case(spaces, level)

        if isinstance(parent_level, dict):
            # Sort all keys for readability
            these_keys = parent_level.keys()
            these_keys.sort()

            # Process the next level
            self.process_next_level(parent_level, these_keys, spaces, level)

        if isinstance(parent_level, list) or isinstance(parent_level, dict):
            # End this level's case
            self.append_end_case(spaces, these_keys, first_level)
        else:
            # If no subkeys, end bashcomplete
            self.append_terminal_case(spaces, level)
            # End this level's case
            self.append_end_case(spaces, '', first_level)

    def bash_append(self, text, spaces, string_formatting=None):
        '''Helper method for keeping track of the bash_complete code'''

        # Do all `string % (replacements)`
        if string_formatting:
            text = text % string_formatting

        # Do all `%stext % (space)` replacements
        if spaces:
            text = '%s%s' % (spaces * space_increment, text)

        self.bash_array.append(text)

    def bash(self):
        '''Converts the bash_array to a proper bash script'''

        # Grab filenames
        filename, clean_filename = self.get_filenames()

        # Generate the proper amount of bash levels
        bash_levels = []
        for i in range(self.max_level):
            bash_levels.append(level_template % (space_increment, i + 1, i + 1))

        constraint = ''
        if self.constrain:
            constraint = '-o default'

        # Do the final generation
        return bash_template % (
                clean_filename,
                '\n'.join(bash_levels),
                '\n'.join(self.bash_array),
                constraint,
                clean_filename,
                filename)


    def get_filenames(self):
        '''Find filenames for .bash_complete filename and bash functions'''

        # Get caller's filename
        filename = os.path.basename(sys.argv[0])

        # Ensure alphanumeric variable for bash code
        clean_filename = re.sub('[\W_]+', '_', filename)

        return filename, clean_filename

    def output(self):
        '''Saves the bash script to filename.bash_complete'''

        # Grab filename
        filename, clean_filename = self.get_filenames()

        # Write file
        with open('%s.bash_complete' % clean_filename, 'w') as f:
            f.write(self.bash())



def test():
    test = {
        'level1a':{
            'a'
        },
        'level1b':{
            'b'
        }
    }
    test = {'level1a': 'does not show', 'level1b': 'does not show'}
    test = ['level1a', 'level1b']
    test = [{'level1a': ['1', '2', '3']}, {'level1b': ['4', '5', '6']}, 'level1c']
    test = {'level1a': ['1', '2', '3'], 'level1b': ['4', '5', '6']}
    test = {
        'files': ['`ls -1`'],
        'devices': ['`ls -1 /dev`']
    }
    bc = BashComplete(test)

if __name__ == "__main__":
    test()
