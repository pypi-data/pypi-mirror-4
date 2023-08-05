from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      install_requires=[
        'setuptools', # to make `buildout` happy
        'dm.xmlsec.binding',
        'pyxb >= 1.1.4',
      ] ,
      namespace_packages=['dm',
                          ],
      zip_safe=False,
      entry_points = dict(
        ),
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'saml2')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()


setup(name='dm.saml2',
      version=pread('VERSION.txt').split('\n')[0],
      description="SAML2 support based on PyXB",
      long_description=pread('README.txt'),
      classifiers=[
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.6',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/pypi/dm.xmlsec.pyxb',
      packages=['dm', 'dm.saml2', 'dm.saml2.pyxb'],
      license='BSD',
      keywords='saml2 pyxb',
      **setupArgs
      )
