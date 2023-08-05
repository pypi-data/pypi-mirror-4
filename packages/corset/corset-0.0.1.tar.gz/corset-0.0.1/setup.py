from distutils.core import setup
setup(
    name = 'corset',
    packages = ['corset', 'corset.management', 'corset.management.commands'],
    package_dir = {'management' : 'management/', 'commands' : 'management/commands/'},
    version = '0.0.1',
    description = 'Django JS/CSS compiler',
    author = 'Chad Masso',
    author_email = 'chad.m.masso@gmail.com',
    maintainer = 'Chad Masso',
    maintainer_email = 'chad.m.masso@gmail.com',
)
