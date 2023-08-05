from setuptools import setup, find_packages
from gpolyline import __version__

setup(
    name = 'gpolyline',
    version = __version__,
    description = "Converts a series of latitude/longitude points to an encoded string for use with Google Maps",
    long_description = """Converts a series of latitude/longitude points to an encoded string for use with Google Maps""",
    keywords = ['googlemaps'],
    author = 'Wyatt Baldwin',
    author_email = 'wyatt.lee.baldwin@gmail.com',
    maintainer = 'Rodrigo Machado',
    maintainer_email = 'rcmachado@gmail.com',
    url = 'http://github.com/rcmachado/gpolyline',
    license = 'OSI',
    classifiers = ['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.6',
                   'Topic :: Software Development :: Libraries :: Application Frameworks',
                   ],
    packages = find_packages(),
    package_dir = {"gpolyline": "gpolyline"},
    include_package_data = True,
)

