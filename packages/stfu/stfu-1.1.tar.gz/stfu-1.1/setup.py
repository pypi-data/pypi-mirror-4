# coding: utf-8
from distutils.core import setup
import stfu

setup(
    name = 'stfu',
    version = '1.1',
    license = 'BSD',
    author = 'João Bernardo Oliveira',
    author_email = 'jbvsmo@example.com',
    description = 'STFU those exceptions (explicitly)',
    py_modules = ['stfu'],
    long_description = stfu.__doc__,
    keywords = ['stfu', 'exception', 'silence'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
