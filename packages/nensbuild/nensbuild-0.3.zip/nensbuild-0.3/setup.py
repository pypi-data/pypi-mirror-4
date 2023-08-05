from setuptools import setup

version = '0.3'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'setuptools',
    ],

tests_require = [
    'mock',
    ]

setup(name='nensbuild',
      version=version,
      description="One step buildout build.",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: Unix',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Build Tools',
      ],
      keywords=[],
      author='Roland van Laar',
      author_email='roland.vanlaar@nelen-schuurmans.nl',
      url='http://github.com/nens/nensbuild',
      license='BSD',
      packages=['nensbuild'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
              'nensbuild = nensbuild.build:main',
          ]},
      )
