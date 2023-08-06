import os

from setuptools import setup, find_packages

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '1.11.0-1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = '\n'.join(
    [read('README.txt'),
     "\n",
     read('CHANGES.txt'),
     "\n",
     read('js', 'jquery_validate', 'test_jquery-validate.txt'),
     ])

setup(
    name='js.jquery_validate',
    version=version,
    description="Fanstatic packaging of validate for jQuery (jquery.validate.js)",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Nikolai Sevostjanov',
    author_email='nikolai.sevostjanov@gmail.com',
    url='https://bitbucket.org/s_nikolai/js.jquery_validate',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        'js.jquery',
    ],
    entry_points={
        'fanstatic.libraries': [
            'jquery_validate = js.jquery_validate:library',
            ],
        },
    )