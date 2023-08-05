import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
]

setup(
    name='pyramid_foundation',
    version='0.2.4',
    author='Parker Pinette',
    author_email='parker@parkerpinette.com',
    url='https://github.com/ppinette/pyramid_foundation',
    license='LICENSE.txt',
    description='Pyramid scaffold to extend project with Foundation support',
    long_description=README + '\n\n' + CHANGES,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    entry_points="""\
        [pyramid.scaffold]
        pyramid_foundation=pyramid_foundation.scaffolds:PyramidFoundationTemplate
    """,
)
