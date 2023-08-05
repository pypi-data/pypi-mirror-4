import sys
from distutils.core import setup, Extension

include = '/usr/include/cairo' if 'linux' in sys.platform else '/opt/local/include/cairo/'
lib_dir = '/usr/lib/x86_64-linux-gnu/' if 'linux' in sys.platform else '/opt/local/lib/'


charting_module = Extension('_charting',
                    include_dirs = [include],
                    libraries = ['cairo'],
                    library_dirs = [lib_dir],
                    sources = ['extensions/charting.c']
                    )


setup (name = 'BeautifulCharts',
       version = '0.6.5',
       description = '',
       ext_modules = [charting_module],
       py_modules = ['BeautifulCharts/converters', 'BeautifulCharts/charting', 'BeautifulCharts/tests', 'BeautifulCharts/__init__']
       )
