from setuptools import setup

VERSION = '0.1'
PACKAGE = 'authzpolicy'

setup(
    name = 'AuthzPolicyPlugin',
    version = VERSION,
    description = "Trac's authz_policy with some improvements.",
    author = 'Mitar',
    author_email = 'mitar.trac@tnode.com',
    url = 'http://mitar.tnode.com/',
    keywords = 'trac plugin',
    license = "GPLv3",
    packages = [PACKAGE],
    include_package_data = True,
    package_data = {},
    install_requires = [],
    zip_safe = False,
    entry_points = {
        'trac.plugins': '%s = %s' % (PACKAGE, PACKAGE),
    },
)
