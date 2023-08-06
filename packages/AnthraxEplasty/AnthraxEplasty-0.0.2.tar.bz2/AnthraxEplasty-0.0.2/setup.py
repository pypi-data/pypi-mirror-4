# vim set fileencoding=utf-8
from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()
setup(
    name = 'AnthraxEplasty',
    version = '0.0.2',
    author = 'Szymon Pyżalski',
    author_email = 'zefciu <szymon@pythonista.net>',
    description = 'Anthrax - generating forms from Elephantoplasty objects',
    url = 'http://github.com/zefciu/Anthrax',
    keywords = 'form web orm database',
    long_description = long_description,

    install_requires = ['anthrax', 'Elephantoplasty'],
    tests_require = ['nose>=1.0', 'nose-cov>=1.0'],
    test_suite = 'nose.collector',
    package_dir = {'': 'src'},
    namespace_packages = ['anthrax'],
    packages = [
        'anthrax', 'anthrax.eplasty'
    ],
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points = """[anthrax.reflector]
eplasty = anthrax.eplasty.reflector:EplastyReflector
[anthrax.field_mixins]
eplasty_unique = anthrax.eplasty.field:UniqueMixin
""",
)

