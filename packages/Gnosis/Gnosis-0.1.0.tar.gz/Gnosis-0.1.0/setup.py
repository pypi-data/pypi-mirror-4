from distutils.core import setup

setup(
    name='Gnosis',
    version='0.1.0',
    author='David Mertz, Mark Wallsgrove',
    author_email='mark.wallsgrove@gmail.com',
    packages=[
        'gnosis',
        'gnosis.util',
        'gnosis.util.convert',
        'gnosis.util.test',
        'gnosis.anon',
        'gnosis.xml',
        'gnosis.xml.relax',
        'gnosis.xml.objectify',
        'gnosis.xml.objectify.doc',
        'gnosis.xml.objectify.test',
        'gnosis.xml.validity',
        'gnosis.xml.pickle',
        'gnosis.xml.pickle.util',
        'gnosis.xml.pickle.doc',
        'gnosis.xml.pickle.parsers',
        'gnosis.xml.pickle.ext',
        'gnosis.xml.pickle.test',
        'gnosis.magic'
    ],
    url='http://github.com/smokedice/Objectify',
    license='LICENSE.txt',
    description='Parses XML into Python object representation',
#    long_description=open('README.txt').read(),
#    install_requires=[
#        "Django >= 1.1.1",
#        "caldav == 0.1.4",
#    ],
)
