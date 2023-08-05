import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

required = ['pyramid >= 1.0',
            'pyramid_jinja2 >= 0.6',
            'Khufu-Script',
            'Khufu-SQLAHelper']

setup(name='Spitter',
      version='0.4',
      description=('Spitter is a microblogging web app written '
                   'using the pyramid web framework'),
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://src.serverzen.com/spitter',
      keywords='web wsgi bfg pylons pyramid khufu',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=required,
      tests_require=required,
      test_suite="spitter",
      entry_points="""
      [paste.app_factory]
      app = spitter.main:make_app
      [console_scripts]
      spitter = spitter.main:main
      """
      )
