#!/usr/bin/python3.2 -tt

# passgen generates a randomized password
# Copyright (C) 2012 Ryan Porterfield

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from randstring import StringGenerator
import sys

"""
Author: Ryan Porterfield

This program generates a password for the user based on the users specified
requirements
"""

version = '1.0.0'

def main():
    # Print a blank line for readability
    print( '' )
    args = parse_args()
    generator = StringGenerator(verbose=args['verbose'])
    passwords = generator.create_string(args['lengths'],
                                     string_type=args['command'])

    if not passwords:
        print('No passwords created', file=sys.stderr)
        sys.exit(1)

    print_pass(passwords)
    # Print another blank line at the end of the program
    print( '' )
    sys.exit( 0 )


def parse_args():
    args = { 'command' : 'all', 'lengths' : [], 'verbose' : False }
    commands = ['all', 'alphabetic', 'alpha-numeric', 'numeric', 'symbolic', ]
    options = { '-h' : 'help', '--help' : 'help', '-v' : 'verbose',
                '--verbose' : 'verbose', '--version' : 'version', }
 
    for arg in sys.argv[1:]:
        if ( arg in commands ) and ( not args['command'] ):
            args['command'] = arg
        elif ( arg in commands )  and ( args['command'] ):
            print_usage( None, exit=True )
        elif arg in options.keys():
            args[options[arg]] = True
        else:
            try:
                args['lengths'].append( int( arg ) )
            except ValueError:
                print_usage( 'ERROR: ' + arg + ' is not a valid option',
                            exit=True ) 

    if len( args['lengths'] ) < 1:
        print_usage( 'ERROR: No password lengths provided.', exit=True )

    return args


def print_usage( message, exit=False, exit_code=1 ):
    usage = """
usage: ./passgen.py [--help] [--version] [options] [character set] length...
options
        -h, --help          prints the help documentation
        -v, --verbose       verbose mode; program prints extra debug info
        --version           prints the version number
character set
        all                 All characters are valid
        alphabetic          Only A-Z and a-z
        alpha-numeric       A-Z, a-z, and 0-9
        numeric             0-9 only
        symbolic            ASCII symbols
length
        A list of length(s) of the passwords to be generated
"""
    if message:
        print( message )
    print( usage )

    if exit:
        sys.exit( exit_code )


def print_pass( passwords ):
    """
    DOCSTRING
    """
    # The string that will help the user remember their password
    mnemonic = '\t'
    # String constant that maps letters of the alphabet to it's military 
    # (phonetic) alphabet counterpart
    phonetic_alphabet = {
        'A' : 'ALPHA', 'a' : 'alpha',
        'B' : 'BRAVO', 'b' : 'bravo',
        'C' : 'CHARLIE', 'c' : 'charlie',
        'D' : 'DELTA', 'd' : 'delta',
        'E' : 'ECHO', 'e' : 'echo',
        'F' : 'FOXTROT', 'f' : 'foxtrot',
        'G' : 'GOLF', 'g' : 'golf',
        'H' : 'HOTEL', 'h' : 'hotel',
        'I' : 'INDIA', 'i' : 'india',
        'J' : 'JULIETE', 'j' : 'juliet',
        'K' : 'KILO', 'k' : 'kilo',
        'L' : 'LIMA', 'l' : 'lima',
        'M' : 'MIKE', 'm' : 'mike',
        'N' : 'NOVEMBER', 'n' : 'november',
        'O' : 'OSCAR', 'o' : 'oscar',
        'P' : 'PAPA', 'p' : 'papa',
        'Q' : 'QUEBEC', 'q' : 'quebec',
        'R' : 'ROMEO', 'r' : 'romeo',
        'S' : 'SIERRA', 's' : 'sierra',
        'T' : 'TANGO', 't' : 'tango',
        'U' : 'UNIFORM', 'u' : 'uniform',
        'V' : 'VICTOR', 'v' : 'victor',
        'W' : 'WHISKEY', 'w' : 'whiskey',
        'X' : 'X-RAY', 'x' : 'x-ray',
        'Y' : 'YO-YO', 'y' : 'yo-yo',
        'Z' : 'ZULU', 'z' : 'zulu'
    }

    for password in passwords:
        for char in password:
            if char in phonetic_alphabet:
                mnemonic = mnemonic + phonetic_alphabet[char] + ' '
            else:
                mnemonic = mnemonic + char + ' '

        print( 'Password:', password )
        print( 'Here\'s a mnemonic to help you remember your password:\n\t',
               mnemonic )


# Boilerplate syntax to call main function
# Because it's conventional
if __name__ == '__main__':
  main()
