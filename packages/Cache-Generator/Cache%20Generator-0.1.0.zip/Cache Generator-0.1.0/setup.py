from distutils.core import setup

setup(
    name='Cache Generator',
    version='0.1.0',
    author='Kendy Menelas',
    author_email='menelaskendy@gmail.com',
    scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='kendymenelas.host22.com/Cache_Generator.zip',
    license='LICENSE.txt',
    description='Useful towel-related stuff.',
    long_description=open('docs/README.txt').read(),
    install_requires=[
        "Django >= 1.1.1",
        "caldav == 0.1.4",
    ],
)
