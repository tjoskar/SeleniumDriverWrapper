from distutils.core import setup

setup(
    name='SeleniumDriverWrapper',
    version='0.2dev',
    author='Oskar Karlsson',
    author_email='kontakta@oskarkarlsson.nu',
    url='https://github.com/tjoskar/SeleniumDriverWrapper',
    packages=['seleniumdriverwrapper',],
    license='LICENSE.txt',
    install_requires=[
        "selenium>=2.39.0"
    ],
)
