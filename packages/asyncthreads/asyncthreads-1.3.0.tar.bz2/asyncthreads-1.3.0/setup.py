import os, sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def main():
    setup(
        name='asyncthreads',
        version= '1.3.0',
        author='Andrew Gillis',
        author_email='gillis.andrewj@gmail.com',
        url='http://bitbucket.org/agillis/asyncthreads',
        description='asyncthreads: asynchronous thread utility objects',
        long_description = open('README.txt').read(),
        license='http://www.opensource.org/licenses/mit-license.php',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
        keywords='threads threadpool reactor',
        classifiers=['Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: POSIX',
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: MacOS :: MacOS X',
                     'Topic :: Software Development :: Libraries',
                     'Topic :: Utilities',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3'],
        packages=['asyncthreads'],
        zip_safe=True,
        )


if __name__ == '__main__':
    main()
