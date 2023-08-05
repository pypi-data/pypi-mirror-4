from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

version = "0.0"
with open( "README.txt" ) as file:
    long_description = file.read()

setup( name="Pyces",
       version=version,
       author="Julian Rosse",
       author_email="julian@helixbass.net",
       maintainer="Julian Rosse",
       maintainer_email="julian@helixbass.net",
       url="http://bitbucket.org/helixbass/pyces",
       license="MIT",
       description="XML processing library combining Xerces-C++ with the ElementTree API",
       long_description=long_description,
       packages=[ "pyces" ],
       classifiers=[ "Development Status :: 3 - Alpha",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: MIT License",
                     "Programming Language :: Cython",
                     "Programming Language :: Python",
                     "Programming Language :: C",
                     "Operating System :: OS Independent",
                     "Topic :: Text Processing :: Markup :: HTML",
                     "Topic :: Text Processing :: Markup :: XML" ],
       cmdclass=dict( build_ext=build_ext ),
       ext_modules=[ Extension( "pyces.etree",
                                [ "pyces/pyces.etree.pyx" ],
                                language="c++",
                                libraries=[ "stdc++",
                                            # "xerces-c"
                                            ] ) ] )
