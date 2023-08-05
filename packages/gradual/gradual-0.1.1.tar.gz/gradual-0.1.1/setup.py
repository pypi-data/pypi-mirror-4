import distutils.core
import os

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

distutils.core.setup(
    name='gradual',
    version='0.1.1',
    packages=['gradual'],
    author='Shashank Bharadwaj',
    author_email='shanka.mns@gmail.com',
    url='http://bitbucket.org/gradual/',
    description='A package providing runtime semantics of Gradual Typing',
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries',
        ],
    )

