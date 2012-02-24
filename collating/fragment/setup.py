import os
import platform
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
            libraries=["libfragment_classifier_ncd" if platform.system().lower() == "windows" else "fragment_classifier_ncd"],
            library_dirs=["."],
            include_dirs=["."])]
)
