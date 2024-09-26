'''
main module is the entry point for the application
'''

import argparse
import sys
from internal import networth

def main():
    '''
    main function is the entry point for the application
    '''
    try:
        parser = argparse.ArgumentParser(
            prog='eFinance',
            description='Application analyzes Networth and Opportunities',
            epilog='Developed by JGLab Co')
        parser.add_argument('-s', '--service', type=str, help='Specify: api | core | ingest')
        args = parser.parse_args()

        app = networth.Application()
        app.start(cmd_input=args)
    except Exception as err:
        print(f"Failed to start the application: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
