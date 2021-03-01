from distutils.core import setup

version = '0.8.15'

setup(
    name='prodict',
    packages=['prodict'],  # this must be the same as the name above
    version=version,
    description='Prodict = Pro Dictionary with IDE friendly(auto code completion), dot-accessible attributes and more.',
    long_description='Ever wanted to use a dict like a class and access keys as attributes? '
                     'Prodict does exactly this.'
                     'Although there are number of modules doing this, Prodict does a little bit more. You can '
                     'provide type hints and get auto-complete!',
    author='Ramazan Polat',
    author_email='ramazanpolat@gmail.com',
    url='https://github.com/ramazanpolat/prodict',
    download_url='https://pypi.python.org/pypi/prodict/' + version,
    keywords=['prodict', 'python3', 'typehinting', 'dynamic-props', 'dict', 'dictionary', 'auto-complete',
              'auto-code-complete'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Software Development :: Libraries :: Python Modules'],
)
