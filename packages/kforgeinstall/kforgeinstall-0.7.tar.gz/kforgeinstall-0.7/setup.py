from setuptools import setup, find_packages
import sys, os

scripts = [
    os.path.join('bin', 'kforge-install'),
    os.path.join('bin', 'kforgeinstall-test'),
]

setup(name='kforgeinstall',
      version='0.7',
      description='Installer for KForge software.',
      long_description=open('README').read() + open('INSTALL').read(),
      classifiers=[],
      keywords='',
      author='Appropriate Software Foundation',
      author_email='john.bywater@appropriatesoftware.net',
      url='',
      license='AGPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      scripts=scripts,
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pexpect',
          'virtualenv',
      ],
)
