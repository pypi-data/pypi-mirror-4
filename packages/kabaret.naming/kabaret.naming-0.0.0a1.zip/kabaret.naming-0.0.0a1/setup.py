
import sys
from setuptools import setup

# (
#    (Major, Minor, [Micros]),
#    [(Alpha/Beta/rc marker, version)],
# )
__version_info__ = ((0, 0, 0), ('a', 1))

def get_version():
    global __version_info__
    return (
        '.'.join(str(x) for x in __version_info__[0]) 
        +''.join(str(x) for x in __version_info__[1])
    )

if not hasattr(sys, 'version_info') or sys.version_info < (2, 6, 0, 'final'):
    raise SystemExit("Kabaret requires Python 2.6 or later.")

install_requires = []

setup(
    name='kabaret.naming',
    namespace_packages=['kabaret'],
    packages=[
        'kabaret',
        'kabaret.naming', 
        'kabaret.naming.fields',
        'kabaret.naming.examples',
    ],
    version=get_version(),
    install_requires=install_requires,
    description='File and Folder naming convention modeling and exploitation.',
    url='http://packages.python.org/kabaret/naming',
    author='Damien Coureau',
    author_email='dee@dee909.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        
        'Topic :: Office/Business',
        
        'Intended Audience :: Developers',
        
        'Operating System :: OS Independent',
        
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    ],
)