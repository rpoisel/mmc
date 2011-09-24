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
            name="libfragment_classifier",
            sources=["src" + os.sep + "fragment_classifier.c",
                "src" + os.sep + "ncd.c"],
            libraries=["z"],
            library_dirs=["."],
            include_dirs=["include"]),
            Extension(
            name="fragment_context",
            sources=["fragment_context.pyx"],
            libraries=["fragment_classifier"],
            library_dirs=["."],
            include_dirs=["."])]
)
