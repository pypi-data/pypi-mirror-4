# vim set fileencoding=utf-8
from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

with open('entry_points.ini') as f:
    entry_points = f.read()

setup(
    name = 'AnthraxDojoFrontend',
    version = '0.0.2',
    author = 'Szymon Pyżalski',
    author_email = 'zefciu <szymon@pythonista.net>',
    description = 'Anthrax frontend for using dojo toolkit',
    url = 'http://github.com/zefciu/Anthrax',
    keywords = 'form web javascript ajax validation wysiwyg',
    long_description = long_description,

    install_requires = ['Anthrax>=0.0.1', 'Mako>=0.6.2'],
    tests_require = ['nose>=1.0', 'nose-cov>=1.0', 'lxml', 'AnthraxHTMLInput'],
    test_suite = 'nose.collector',
    package_dir = {'': 'src'},
    namespace_packages = ['anthrax'],
    packages = [
        'anthrax', 'anthrax.dojo',
    ],
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

