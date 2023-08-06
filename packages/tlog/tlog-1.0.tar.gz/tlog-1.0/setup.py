from distutils.core import setup, Extension

setup(name="tlog",
    version="1.0",
    packages=['tlog'],
    ext_package="tlog",
    ext_modules=[Extension("pktparser", ["tlog/pktparser.c"])],
    description='Traffic monitoring utilities',
    url='http://bitbucket.org/wroniasty/tlog',
    author='Jakub Wroniecki',
    author_email='wroniasty@gmail.com',
    license="BSD",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    long_description=open('README.md', 'r').read()
)
