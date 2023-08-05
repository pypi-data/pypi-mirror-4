from distutils.core import setup
import codecs

def readme(filename):
    in_file = codecs.open(filename, 'r')
    return unicode(in_file.read())

files = ["wemplate/*"]

setup(name = "wempy",
    version = "0.1.4",
    description = "Embedded python interpreter (very similar to Ruby's erb).",
    author = "G. Clifford Williams",
    author_email = "gcw@notadiscussion.com",
    license = "LGPLv3",
    url = "http://www.wempy.org/",
    packages = ['wemplate'],
    package_data = {'wemplate' : [
                                    'LICENSE',
                                    'README.rst',
                                    'README.wiki',
                                    'wemplate/*.py',
                                    'wempy',
                                    ]
                    },
    scripts = ["wempy"],
    long_description = readme('README'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing :: Filters',
    ]     
) 
