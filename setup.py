import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_tm',
    'pyramid_chameleon',
    'pyramid_beaker',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'pymysql',
    'nose',
    'webtest',
    'pillow',
    'redis',
    'geopy',
    'requests_oauthlib',
    'jinja2',
]

setup(name='planevent',
      version='0.111',
      description='planevent',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='planevent',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = planevent:main
      [console_scripts]
      initialize_planevent_db = planevent.scripts.initializedb:main
      """,
      )
