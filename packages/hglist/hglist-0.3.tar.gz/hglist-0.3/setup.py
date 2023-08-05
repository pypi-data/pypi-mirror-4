from distutils.core import setup

__version__ = '0.3'

setup(name='hglist',
      version=__version__,
      description='An ls command for Mercurial',
      license='GNU GPLv2',
      long_description="""
hglist adds an `ls' command to Mercurial, similar to but more comprehensive
than the `manifest' built-in command, and with templatized output support.
""",
      author='Alastair Houghton',
      author_email='alastair@alastairs-place.net',
      url='http://alastairs-place.net/projects/hglist/',
      packages=['hglist'],
      classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Topic :: Software Development :: Version Control',
    ])
