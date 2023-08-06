from distutils.core import setup
from distutils.command.build_py import build_py
import shutil
import sys

_PY23 = 3 if sys.version_info.major > 2 else 2

class build_py23(build_py):
    """Different build for Py 2 and Py 3"""
    def find_package_modules(self, package, package_dir):
        modules = build_py.find_package_modules(self, package, package_dir)
        if _PY23 == 3:
            modules = [m for m in modules if 'lpcompat2' not in m[1]]
        else:
            modules = [m for m in modules if 'lpcompat3' not in m[1]]
        return modules

cmd_class = dict(
    build_py = build_py23,
) 

shutil.rmtree('build', True)
setup(name="nanolp",
    version="1.0i",
    description="Literate Programming Tool",
    long_description = open('README.txt').read(),
    author="Pavel Y",
    author_email="aquagnu@gmail.com",
    url='http://code.google.com/p/nano-lp/',
    download_url='http://nano-lp.googlecode.com/files/nanolp-1.0i.zip',
    packages = ["nanolp"],
    scripts=['bin/nlp.py', 'bin/lprc'],
    license='GNU GPLv2',
    keywords=['Literate Programming', 'Documentation'],
    classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Documentation',
            'Topic :: Scientific/Engineering',
            'Topic :: Software Development :: Documentation',
            'Topic :: Text Processing :: Markup',
            'Topic :: Utilities',
        ],
    cmdclass=cmd_class,
)
