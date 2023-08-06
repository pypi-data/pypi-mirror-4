from setuptools import setup


install_requires = ['requests==1.1.0', 'termcolor==1.1.0']


setup(
    name='hoard',
    version='1.0',
    description='',
    long_description=open('README.rst').read() + '\n\n' +
                     open('CHANGELOG.rst').read(),
    author='George Hickman',
    author_email='george@ghickman.co.uk',
    url='http://github.com/ghickman/hoard-cli',
    license=open('LICENSE').read(),
    packages=['hoard'],
    entry_points={'console_scripts': ['hoard = hoard.main:run']},
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ),
    install_requires=install_requires,
)

