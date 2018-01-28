from distutils.core import setup

setup(
    name='prodict',
    packages=['prodict'],  # this must be the same as the name above
    version='0.6',
    description='Dictionary with IDE friendly(auto code completion), dot-accessible attributes and more.',
    long_description='Ever wanted to use a dict like a class and access keys as attributes? Prodict does exactly '
                     'this. Although there are number of modules doing this, Prodict does a little bit more. You can '
                     'provide type hints and get auto-complete!',
    author='Ramazan Polat',
    author_email='ramazanpolat@gmail.com',
    url='https://github.com/ramazanpolat/prodict',
    download_url='https://pypi.python.org/pypi/prodict/0.6',
    keywords=['python3', 'typehinting', 'dynamic-props', 'dict', 'dictionary', 'auto-complete', 'auto-code-complete'],
    classifiers=[],
)
