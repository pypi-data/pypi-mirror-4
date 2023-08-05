from setuptools import setup, find_packages


setup(
    name='unittest-utils',
    version='0.1.2',
    description='Some custom utils for unittest2',
    long_description=open('README.rst').read(-1),
    author='',
    author_email='',
    url='',
    install_requires=[
        "unittest2",
        "termcolor",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts':
            ['unittest-utils=unittest_utils.main:_main']
    }
)
