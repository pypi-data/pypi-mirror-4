from setuptools import setup

setup(
    name='appsettings',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    version='0.2',
    url='http://bits.btubbs.com/appsettings/',
    py_modules=['appsettings'],
    description=('A tiny helper to read the yaml file specified in the '
                 'APP_SETTINGS_YAML env var and return an object with '
                 'the parsed contents'),
    long_description=open('README.rst').read(),
    install_requires=[
        'pyyaml>=3.0',
    ],
    zip_safe=False,
)
