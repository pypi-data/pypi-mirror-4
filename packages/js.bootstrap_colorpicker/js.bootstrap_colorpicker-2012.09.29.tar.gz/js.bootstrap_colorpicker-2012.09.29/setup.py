import os

from setuptools import setup, find_packages

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '2012.09.29'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = '\n'.join(
    [read('README.txt'),
     "\n",
     read('CHANGES.txt'),
     "\n",
     read('js', 'bootstrap_colorpicker', 'test_bootstrap-colorpicker.txt'),
     ])

setup(
    name='js.bootstrap_colorpicker',
    version=version,
    description="Fanstatic packaging of Colorpicker for Bootstrap (bootstrap-colorpicker.js)",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Nikolai Sevostjanov',
    author_email='nikolai.sevostjanov@gmail.com',
    url='https://bitbucket.org/s_nikolai/js.bootstrap_colorpicker',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        'js.bootstrap',
        ],
    entry_points={
        'fanstatic.libraries': [
            'bootstrap_colorpicker = js.bootstrap_colorpicker:library',
            ],
        },
    )