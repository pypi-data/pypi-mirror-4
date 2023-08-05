from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

install_requires = [
    'Kotti >= 0.7',
]

setup(name='kotti_site_gallery',
      version='0.1.0b2',
      description="Event collection for Kotti sites",
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='kotti site gallery',
      author='Christian Neumann',
      author_email='cneumann@datenkarussell.de',
      url='http://pypi.python.org/pypi/kotti_site_gallery',
      license='BSD-2-Clause',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      message_extractors={"kotti_site_gallery": [
          ("**.py", "lingua_python", None),
          ("**.pt", "lingua_xml", None), ]},
      entry_points="""\
      [fanstatic.libraries]
      kotti_site_gallery = kotti_site_gallery:lib_kotti_site_gallery
      """,
      )
