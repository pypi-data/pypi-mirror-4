# vim set fileencoding=utf-8
from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

with open('entry_points.ini') as f:
    entry_points = f.read()

setup(
    name = 'AnthraxHTMLInput',
    version = '0.0.4',
    author = 'Szymon Pyżalski',
    author_email = 'zefciu <szymon@pythonista.net>',
    description = 'Anthrax - tools for HTML input',
    keywords = 'form web html',
    long_description = long_description,

    install_requires = ['lxml'],
    tests_require = ['nose>=1.0', 'nose-cov>=1.0'],
    test_suite = 'nose.collector',
    package_dir = {'': 'src'},
    namespace_packages = ['anthrax'],
    packages = find_packages('src'),
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points = entry_points,

)

