from setuptools import setup
import os

version = '0.3'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
HISTORY = open(os.path.join(here, 'HISTORY.rst')).read()

setup(
    name='collective.recipe.cmmi',
    version=version,
    description="Plugins and utilities for supervisor",
    long_description=README + "\n\n" + HISTORY,
    license="ZPL 2.1",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'zc.recipe.cmmi<=1.4.0'],
    entry_points={
        'zc.buildout':
            ['default = collective.recipe.cmmi:Recipe']})
