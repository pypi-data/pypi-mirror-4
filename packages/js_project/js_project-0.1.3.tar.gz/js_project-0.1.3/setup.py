import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'fanstatic',
]

setup(
    name='js_project',
    version='0.1.3',
    author='Parker Pinette',
    author_email='parker@parkerpinette.com',
    url='https://github.com/ppinette/pyramid_foundation',
    license='LICENSE.txt',
    description='pcreate scaffold for fanstatic resource library projects',
    long_description=README + '\n\n' + CHANGES,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    entry_points="""\
        [pyramid.scaffold]
        js_project=js_project.scaffolds:JSProjectTemplate
    """,
)
