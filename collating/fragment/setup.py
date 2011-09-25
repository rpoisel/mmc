import os
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
        name="Fragment Classifier",
        cmdclass={'build_ext' : build_ext},
        #ext_package='fragment_classifier',
        ext_modules=[
            Extension(
            name="fragment_context",
            sources=["fragment_context.pyx"],
            libraries=["fragment_classifier"],
            library_dirs=["."],
            include_dirs=["."])]
)
