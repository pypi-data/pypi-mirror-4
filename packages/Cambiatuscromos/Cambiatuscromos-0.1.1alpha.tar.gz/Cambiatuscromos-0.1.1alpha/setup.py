from setuptools import setup, find_packages
import sys, os

version = '0.1.1'
REQUIRES = ['mechanize', 'BeautifulSoup', 'colorama'],




setup(name='Cambiatuscromos',
      version=version,
      description="Chequeo automatico de intercambios para Cambiatuscromos.org",
      long_description="""\
Chequeo automatico de intercambios para Cambiatuscromos.org""",
      classifiers=[
                        "Development Status :: 3 - Alpha",
                        "Programming Language :: Python",
                        "Environment :: Console",
                        "Topic :: Utilities",
                        "Topic :: Internet :: WWW/HTTP",
                        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                  ],
      keywords='checker chequeo automatico cambiatuscromos cromos cambiar intercambios panini',
      author='Miguel Sempere',
      author_email='odoncopon@gmail.com',
      url='',
      license="GPLv3",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIRES,
      entry_points={
            'console_scripts': [
                  'exchange-checker = cambiatuscromos.cromos:run'
            ]
      }


      
      )
