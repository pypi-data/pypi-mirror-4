from setuptools import setup, find_packages

version = '0.4.7'

setup(name='thornbed',
      version=version,
      description="Simple oEmbed wrapper for different services",
      long_description="""\
""",
      classifiers=[
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='oembed youtube vimeo imgur flickr quickmeme',
      author='Esteban Feldman',
      author_email='esteban.feldman@gmail.com',
      url='https://bitbucket.org/eka/thornbed',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'oEmbed',
          'simplejson',
          'requests',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
