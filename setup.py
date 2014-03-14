from distutils.core import setup

setup(
    name='SeleniumDriverWrapper',
    version='0.1dev',
    author='Oskar Karlsson',
    author_email='kontakta@oskarkarlsson.nu',
    url='',
    packages=['seleniumdriverwrapper',],
    license='LICENSE.txt',
    install_requires=[
        "selenium>=2.39.0"
    ],
)
