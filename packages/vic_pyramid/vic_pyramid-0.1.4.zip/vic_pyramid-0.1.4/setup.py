import os

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = '0.1.4'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(
    name='vic_pyramid',
    version=version,
    author='Victor Lin',
    author_email='bornstub@gmail.com',
    description="Victor's Pyramid Scaffold",
    long_description=README + '\n\n' +  CHANGES,
    url='https://bitbucket.org/victorlin/vic_pyramid',
    classifiers=[
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'pyramid>=1.4',
    ], 
    entry_points = """\
    [paste.paster_create_template]
    vic_pyramid=vic_pyramid.scaffolds:VictorPyramidTemplate
    [pyramid.scaffold]
    vic_pyramid=vic_pyramid.scaffolds:VictorPyramidTemplate
    """
)
