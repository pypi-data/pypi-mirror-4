#!D:\programming\Python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'ss==0.2','console_scripts','ss'
__requires__ = 'ss==0.2'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('ss==0.2', 'console_scripts', 'ss')()
    )
