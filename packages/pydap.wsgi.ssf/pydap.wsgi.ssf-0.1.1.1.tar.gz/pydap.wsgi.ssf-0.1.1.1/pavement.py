import string

from paver.easy import *
from paver.setuputils import setup, find_packages, find_package_data
import paver.doctools
import paver.virtual
from paver.release import setup_meta

__version__ = (0,1,1,1)

options = environment.options
setup(**setup_meta)

options(
    setup=Bunch(
        name='pydap.wsgi.ssf',
        version='.'.join(str(d) for d in __version__),
        description='WSGI middleware implementing Opendap server-side functions on the Pydap server.',
        long_description='''
This module brings a WSGI middleware that allows the Pydap Opendap
server to process calls to server-side functions.
        ''',
        keywords='opendap dods dap data science climate oceanography meteorology',
        classifiers=filter(None, map(string.strip, '''
            Development Status :: 5 - Production/Stable
            Environment :: Console
            Environment :: Web Environment
            Framework :: Paste
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: MIT License
            Operating System :: OS Independent
            Programming Language :: Python
            Topic :: Internet
            Topic :: Internet :: WWW/HTTP :: WSGI
            Topic :: Scientific/Engineering
            Topic :: Software Development :: Libraries :: Python Modules
        '''.split('\n'))),
        author='Roberto De Almeida',
        author_email='rob@pydap.org',
        url='http://pydap.org/',
        license='MIT',

        packages=find_packages(),
        package_data=find_package_data("pydap", package="pydap",
                only_in_packages=False),
        include_package_data=True,
        zip_safe=False,
        namespace_packages=['pydap', 'pydap.wsgi'],

        test_suite='nose.collector',

        dependency_links=[],
        install_requires=[
            'Pydap',
            'WebOb',
        ],
        entry_points="""
            [pydap.function]
            bounds = pydap.wsgi.ssf.functions:bounds
            geogrid = pydap.wsgi.ssf.functions:geogrid
            mean = pydap.wsgi.ssf.functions:mean

            [paste.filter_app_factory]
            main = pydap.wsgi.ssf:make_middleware
        """,
    ),
    minilib=Bunch(
        extra_files=['doctools', 'virtual']
    ), 
)


@task
@needs(['generate_setup', 'minilib', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
