from setuptools import setup

VERSION = '0.1'
PACKAGE = 'allattachments'

setup(
    name = 'AllAttachmentsMacro',
    version = VERSION,
    description = "A Trac wiki macro that shows all attachments uploaded on a Trac site.",
    author = 'Daan van Etten',
    author_email = 'daan@stuq.nl',
    keywords = 'trac plugin',
    license = "CC-BY-NC-SA",
    packages = [PACKAGE],
    include_package_data = True,
    package_data = {},
    install_requires = [],
    zip_safe = False,
    entry_points = {
        'trac.plugins': '%s = %s' % (PACKAGE, PACKAGE),
    },
)
