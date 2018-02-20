from distutils.core import setup

setup(
    name='prodict',
    packages=['prodict'],  # this must be the same as the name above
    version='0.8',
    description='Prodict = Pro Dictionary with IDE friendly(auto code completion), dot-accessible attributes and more.',
    long_description='Ever wanted to use a <strong>dict</strong> like a class and access keys as attributes? '
                     '<strong>Prodict</strong> does exactly this.'
                     'Although there are number of modules doing this, Prodict does a little bit more. You can '
                     'provide type hints and get auto-complete!',
    author='Ramazan Polat',
    author_email='ramazanpolat@gmail.com',
    url='https://github.com/ramazanpolat/prodict',
    download_url='https://pypi.python.org/pypi/prodict/0.7',
    keywords=['prodict', 'python3', 'typehinting', 'dynamic-props', 'dict', 'dictionary', 'auto-complete',
              'auto-code-complete'],
    classifiers=[],
)
