# setup.py

from setuptools import setup, Extension, find_packages

from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import numpy as np
import sys, os, platform
from pathlib import Path

IS_DARWIN = sys.platform == "darwin"
IS_LINUX  = sys.platform.startswith("linux")
IS_WIN    = sys.platform.startswith("win")

# Where conda-forge puts headers/libs if you're in a conda env
CONDA_PREFIX = os.environ.get("CONDA_PREFIX", "")
CONDA_INC = [str(Path(CONDA_PREFIX) / "include")] if CONDA_PREFIX else []
CONDA_LIB = [str(Path(CONDA_PREFIX) / "lib")] if CONDA_PREFIX else []

def omp_compile_args():
    if IS_WIN:
        # MSVC
        return ["/openmp"]
    elif IS_DARWIN:
        # Apple Clang: needs the preprocessor flag
        return ["-Xpreprocessor", "-fopenmp"]
    else:  # Linux / other clang/gcc
        return ["-fopenmp"]

def omp_link_args():
    if IS_WIN:
        # MSVC links OpenMP automatically with /openmp
        return []
    elif IS_DARWIN:
        # Link against libomp (from conda-forge llvm-openmp)
        return ["-lomp"]
    else:
        return ["-fopenmp"]

# Common includes/libs
include_dirs_common = [np.get_include()] + CONDA_INC
library_dirs_common = CONDA_LIB

# If users set FFTW_DIR/VORO_DIR explicitly, respect them too
def env_paths(var):
    p = os.environ.get(var)
    if not p: return [], []
    inc = [str(Path(p) / "include")]
    lib = [str(Path(p) / "lib")]
    return inc, lib

fftw_inc_env, fftw_lib_env = env_paths("FFTW_DIR")
voro_inc_env, voro_lib_env = env_paths("VORO_DIR")

include_dirs_fftw = include_dirs_common + fftw_inc_env
library_dirs_fftw = library_dirs_common + fftw_lib_env

include_dirs_voro = include_dirs_common + voro_inc_env
library_dirs_voro = library_dirs_common + voro_lib_env

extra_compile = omp_compile_args()
extra_link    = omp_link_args()

# ---- Extensions -------------------------------------------------------------
extensions = [
    Extension(
        name="newanalysis.correl",
        sources=[
            "newanalysis/helpers/correl.pyx",
            "newanalysis/helpers/mod_Correl.cpp",
            "newanalysis/helpers/BertholdHorn.cpp",
        ],
        language="c++",
        include_dirs=include_dirs_fftw,
        library_dirs=library_dirs_fftw,
        libraries=["fftw3"],              # from conda-forge fftw
        extra_compile_args=extra_compile,
        extra_link_args=extra_link,
    ),
    Extension(
        name="newanalysis.helpers",
        sources=[
            "newanalysis/helpers/helpers.pyx",
            "newanalysis/helpers/BertholdHorn.cpp",
        ],
        language="c++",
        include_dirs=include_dirs_common,
        library_dirs=library_dirs_common,
        extra_compile_args=extra_compile,
        extra_link_args=extra_link,
    ),
    Extension(
        name="newanalysis.miscellaneous",
        sources=[
            "newanalysis/helpers/miscellaneous.pyx",
            "newanalysis/helpers/miscellaneous_implementation.cpp",
        ],
        language="c++",
        include_dirs=include_dirs_common,
        library_dirs=library_dirs_common,
        extra_compile_args=extra_compile,
        extra_link_args=extra_link,
    ),
    Extension(
        name="newanalysis.diffusion",
        sources=["newanalysis/helpers/diffusion.pyx"],
        language="c++",
        include_dirs=include_dirs_common,
        library_dirs=library_dirs_common,
        extra_compile_args=extra_compile,
        extra_link_args=extra_link,
    ),
    Extension(
        name="newanalysis.unfold",
        sources=[
            "newanalysis/helpers/unfold.pyx",
            "newanalysis/helpers/BertholdHorn.cpp",
        ],
        language="c++",
        include_dirs=include_dirs_common,
        library_dirs=library_dirs_common,
        extra_compile_args=extra_compile,
        extra_link_args=extra_link,
    ),
    Extension(
        name="newanalysis.voro",
        sources=[
            "newanalysis/voro/voro.pyx",
            "newanalysis/voro/mod_voro.cpp",
        ],
        language="c++",
        include_dirs=include_dirs_voro,
        library_dirs=library_dirs_voro,
        libraries=["voro++"],            # from conda-forge voro++
        extra_compile_args=extra_compile,
        extra_link_args=extra_link,
    ),
    Extension(
        name="newanalysis.gfunction",
        sources=["newanalysis/gfunction/gfunction.pyx"],
        language="c++",
        include_dirs=include_dirs_common,
        library_dirs=library_dirs_common,
        extra_compile_args=extra_compile,
        extra_link_args=extra_link,
    ),
    # NOTE: no compiled extension for newanalysis.functions anymore.
]

ext_modules = cythonize(
    extensions,
    language_level=3,
    compiler_directives={"boundscheck": False, "wraparound": False},
)
setup(
    name="newanalysis",
    version="0.1dev",
    license="None",
    packages=find_packages(include=["newanalysis", "newanalysis.*"]),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)

