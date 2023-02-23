import argparse
import sys
import os 

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def parse_args():
    parser= MyParser(description='This script does XXX')
    parser.add_argument('--oldpath',required=True default="", type=str, help='path to the old file', metavar='')
    parser.add_argument('--newpath',required=True default="", type=str, help='path to the new file', metavar='')
    config = parser.parse_args()
    return config

config = vars(parse_args())

oldpath = config['oldpath']
newpath = config['newpath']

os.rename(oldpath, newpath)