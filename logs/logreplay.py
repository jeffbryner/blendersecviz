#! /usr/bin/python -u
import fileinput
import getopt
import os 
import re 
import string, sys, time,random

printablestringre=re.compile('[\x80-\xFF\x00-\x08\x0A-\x1F]')
def safestring(badstring):
    """only printable range..i.e. upper ascii minus lower junk like line feeds, etc"""
    return printablestringre.sub('',badstring)

def main():
    "The 'heart' of the program, executes all other functions"
    global options
    options = read_options()

    if options["file"] != '':
        fp = open(options['file'], 'r')    
    while 1:
        if options["file"] != '':
            line = safestring(fp.readline().strip())
            if not line:
                break
            else:		
                time.sleep(random.uniform(0.1,1.0))
                sys.stdout.write(line + '\n')



def read_options():
    """Read options from config files and the command line, returns the 
    defaults if no user options are found"""

    # required options
    required = ['file']


    # defaults
    options = {'file'   : ''}


    # read from command line
    helpstr = 'Usage: ' + sys.argv[0] + ' [OPTIONS]' + """\n
Options:
 * -f, --file   <filename>  the log file to replay to stdout
A '*' means this option is required."""

    optlist, args = getopt.getopt(sys.argv[1:], 'f:', ['file='])

    # parse options
    for o, a in optlist:
        if (o == '-h' or o == '--help'):
            print(helpstr)
            sys.exit()
        else:
            for option in options.keys():
                execcode = "if (o == '-%s' or o == '--%s'): options['%s'] = a" % (option[0], option, option)
                exec(execcode)

    for option in required:
        if not options[option]:
            print( "Required option '%s' is not set!" % option)
            sys.exit()

    # return all options
    return options

main()