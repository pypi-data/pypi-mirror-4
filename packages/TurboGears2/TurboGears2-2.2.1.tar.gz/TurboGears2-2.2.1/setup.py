import os
here = os.path.abspath(os.path.dirname(__file__))
execfile(os.path.join(here, 'tg', 'release.py'))

from setuptools import find_packages, setup

import sys

test_requirements = ['coverage',
                    'nose',
                    'TurboKid >= 1.0.4',
                    'zope.sqlalchemy >= 0.4',
                    'jinja2',
                    'Chameleon < 2.0a',
                    'simplegeneric',
                    'repoze.who',
                    'repoze.who.plugins.sa >= 1.0.1',
                    "repoze.who-friendlyform >=1.0.4",
                    'repoze.tm2 >= 1.0a4',
                    'wsgiref',
                    'tw.forms',
                    'tw2.forms',
                    'Kajiki>=0.2.2',
                    'Genshi >= 0.5.1',
                    'TurboKid >= 1.0.4',
                    'Mako',
                    'TurboJson >= 1.3',
                    'Babel >=0.9.4',
                    'tgext.admin>=0.3.9',
                    ]

install_requires=[
    'WebOb == 1.1.1',
    'Pylons',# == 1.0',
    'WebFlash >= 0.1a8',
    'WebError >= 0.10.1',
    'Babel',
    'crank >= 0.6.2'
    ]

setup(
    name='TurboGears2',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[],
    keywords='turbogears pylons',
    author=author,
    author_email=email,
    url=url,
    license=license,
    packages=find_packages(exclude=['ez_setup', 'examples']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        #XXX: Perhaps this 'core-testing' extras_require can be removed
        #     since tests_require takes care of that as long as TG is tested
        #     with 'python setup.py test' (which we should IMHO so setuptools
        #     can take care of these details for us)
        'core-testing':test_requirements,
    },
    test_suite='nose.collector',
    tests_require = test_requirements,
    entry_points='''
        [paste.global_paster_command]
        tginfo = tg.commands.info:InfoCommand
        [turbogears2.command]
        serve = paste.script.serve:ServeCommand [Config]
        shell = pylons.commands:ShellCommand
    ''',
    dependency_links=[
        "http://tg.gy/220"
        ]
)
