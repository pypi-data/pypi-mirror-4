from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(
    name = 'dictionary',
    version = '1.0',
    description = 'Python dictionary module',
    author = 'Saswat Raj',
    author_email = 'saswatrj2010@gmail.com',
    url='https://github.com/saswatraj/dictionary.git',
    py_modules = ['dictionary'],
    data_files = [(get_python_lib(),['dict.txt'])]
    )
