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
        "Django >= 1.1.1",
        "caldav == 0.1.4",
    ],
)

setup(
    name='TowelStuff',
    version='0.1.0',
    author='J. Random Hacker',
    author_email='jrh@example.com',
    packages=['towelstuff', 'towelstuff.test'],
    scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='Useful towel-related stuff.',
    long_description=open('README.txt').read(),
    install_requires=[
        "selenium>=2.39.0"
    ],
)
