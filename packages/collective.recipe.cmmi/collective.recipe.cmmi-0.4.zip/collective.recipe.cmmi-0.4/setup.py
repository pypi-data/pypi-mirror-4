from setuptools import setup
import os

version = '0.4'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
HISTORY = open(os.path.join(here, 'HISTORY.rst')).read()

setup(
    name='collective.recipe.cmmi',
    version=version,
    description="Adds small features to zc.recipe.cmmi",
    long_description=README + "\n\n" + HISTORY,
    license="ZPL 2.1",
    include_package_data=True,
    author='Florian Schulze',
    author_email='florian.schulze@gmx.net',
    url='http://github.com/collective/collective.recipe.cmmi',
    packages=['collective', 'collective.recipe', 'collective.recipe.cmmi'],
    namespace_packages=['collective', 'collective.recipe'],
    zip_safe=False,
    install_requires=[
        'zc.recipe.cmmi<=1.4.0'],
    entry_points={
        'zc.buildout':
            ['default = collective.recipe.cmmi:Recipe']})
