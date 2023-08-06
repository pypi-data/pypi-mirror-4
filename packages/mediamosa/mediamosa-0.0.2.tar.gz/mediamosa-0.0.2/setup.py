from setuptools import setup

with open('README.rst', 'r') as file:
    long_desc = file.read()

version = __import__('mediamosa').get_version()

setup(
    name='mediamosa',
    version=version,
    author='UGent Portaal Team',
    author_email='portaal-tech@ugent.be',
    packages=['mediamosa', 'tests'],
    scripts=[],
    url='https://github.com/UGentPortaal/python-mediamosa',
    license='BSD',
    description='A high-level API interface for MediaMosa.',
    long_description=long_desc,
    install_requires=(
        'requests>=1.0.3'
    ),
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Multimedia :: Video',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities'
          ],
)
