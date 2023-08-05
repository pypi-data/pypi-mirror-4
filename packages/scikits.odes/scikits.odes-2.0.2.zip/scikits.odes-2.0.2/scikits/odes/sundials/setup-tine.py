#!/usr/bin/env python
from __future__ import print_function

import os
import platform
from numpy.distutils.system_info import get_info
from scikits.odes._build import cython
#from Cython.Distutils import build_ext

base_path = os.path.abspath(os.path.dirname(__file__))

lapack_opt = None

def win():
    """
    Return True if a windows system
    """
    if platform.system() in ["Windows", "win32"]:
        return True
    return False
if not win():    
    try:
        lapack_opt = get_info('lapack_opt',notfound_action=2)
    except:
        print('LAPACK not found, no sundials solvers')

if win():
    print ('In win')
    INCL_DIRS_LAPACK = ['C:/MinGW/lib/Lapack/lapack-3.4.1/SRC']
    LIB_DIRS_LAPACK = ['C:/MinGW/lib/Lapack/lib']
    LIBS_LAPACK = ['lapack', 'blas']    
    INCL_DIRS_SUNDIALS = ['C:/Program Files/sundials/include']
    LIB_DIRS_SUNDIALS  = ['C:/Program Files/sundials', 'C:/Program Files/sundials/lib']
    LIBS_SUNDIALS = ['sundials_nvecserial']
    LIBS_IDA   = ['sundials_ida']
    LIBS_CVODE = ['sundials_cvode']
    LIB_DIRS_GFORTRAN = ['C:/MinGW/lib/gcc/mingw32/4.6.2']
    LIBS_FORTRAN = ['gfortran']

else:    
    INCL_DIRS_LAPACK = []
    LIB_DIRS_LAPACK = []
    LIBS_LAPACK = []
    if lapack_opt:
        INCL_DIRS_LAPACK = lapack_opt.get('include_dirs',[])
        LIB_DIRS_LAPACK = lapack_opt.get('library_dirs',[])
        LIBS_LAPACK = lapack_opt.get('libraries',[])

    # Edit following lines if sundials is installed differently!
    INCL_DIRS_SUNDIALS = [os.path.abspath(os.path.dirname(__file__))]
    LIB_DIRS_SUNDIALS  = [os.path.abspath(os.path.dirname(__file__)),
                      '/usr/lib', '/usr/local/lib/',
                        ]
    LIBS_SUNDIALS = ['sundials_nvecserial']
    LIBS_IDA   = ['sundials_ida']
    LIBS_CVODE = ['sundials_cvode']

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    print("=============================================")
    print("parent package is %s" % parent_package)
    print("top path is %s" % top_path)
    print("=============================================")
    config = Configuration('sundials', parent_package, top_path)

    if lapack_opt or win():
        # sundials library
        ## assume installed globally at the moment
        ##config.add_library('sundials_ida',
        
        # sundials cython wrappers
        cython(['common_defs.pyx'], working_path=base_path, 
                        include_dirs=[])
        
        config.add_extension("common_defs", 
                             sources=['common_defs.c'], 
                             include_dirs=INCL_DIRS_SUNDIALS)

        cython(['ida.pyx'], working_path=base_path)
        config.add_extension("ida",
                             sources=['ida.c'],
                             depends=['common_defs.c'], 
                             include_dirs=INCL_DIRS_SUNDIALS+INCL_DIRS_LAPACK,
                             library_dirs=LIB_DIRS_SUNDIALS+LIB_DIRS_LAPACK+LIB_DIRS_GFORTRAN,
                             libraries=LIBS_IDA+LIBS_SUNDIALS+LIBS_LAPACK+LIBS_FORTRAN)

        cython(['cvode.pyx'], working_path=base_path)
        config.add_extension("cvode",
                             sources=['cvode.c'],
                             depends=['common_defs.c'],
                             include_dirs=INCL_DIRS_SUNDIALS+INCL_DIRS_LAPACK,
                             library_dirs=LIB_DIRS_SUNDIALS+LIB_DIRS_LAPACK+LIB_DIRS_GFORTRAN,
                             libraries=LIBS_CVODE+LIBS_SUNDIALS+LIBS_LAPACK+LIBS_FORTRAN)
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
