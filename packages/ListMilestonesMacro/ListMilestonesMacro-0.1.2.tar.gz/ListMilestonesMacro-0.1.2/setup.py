from setuptools import setup

VERSION = '0.1.2'
PACKAGE = 'listmilestones'

setup(
    name = 'ListMilestonesMacro',
    version = VERSION,
    description = "Lists milestones based on a name.",
    author = 'Mitar',
    author_email = 'mitar.trac@tnode.com',
    url = 'http://mitar.tnode.com/',
    keywords = 'trac plugin',
    license = "AGPLv3",
    packages = [PACKAGE],
    include_package_data = True,
    package_data = {
        PACKAGE: ['templates/*.html'],
    },
    install_requires = [],
    zip_safe = False,
    entry_points = {
        'trac.plugins': '%s = %s' % (PACKAGE, PACKAGE),
    },
)
