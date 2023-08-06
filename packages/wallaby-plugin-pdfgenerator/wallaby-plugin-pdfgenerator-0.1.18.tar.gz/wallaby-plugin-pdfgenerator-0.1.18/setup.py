from setuptools import setup, find_packages

setup(name='wallaby-plugin-pdfgenerator',
      version='0.1.18',
      url='http://freshx.de/wallaby/plugins/pdfgenerator',
      author='FreshX GbR',
      author_email='wallaby@freshx.de',
      license='BSD',
      description='This package provides a PDF generator for wallaby.',
      long_description=open('README.md').read(),
      package_data={'': ['LICENSE', 'AUTHORS', 'README.md']},
      classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
      ],
      packages=find_packages('.'),
      install_requires=['wallaby-base', 'Cheetah']
  )
