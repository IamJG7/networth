'''
main module is the entry point for the application
'''

import sys
from internal import networth

def main():
    '''
    main function is the entry point for the application
    '''
    try:
        app = networth.Application()
        app.start()
    except Exception as err:
        print(f"Failed to start the application: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
