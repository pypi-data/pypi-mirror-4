#!/usr/bin/env python
from __future__ import print_function

import os
from numpy.distutils.system_info import get_info
from scikits.odes._build import cython
#from Cython.Distutils import build_ext

base_path = os.path.abspath(os.path.dirname(__file__))

# Edit following paths if programs are installed differently!
# paths for LAPACK
INCL_DIRS_LAPACK = []
LIB_DIRS_LAPACK  = []
LIBS_LAPACK      = []

# paths for SUNDIALS
INCL_DIRS_SUNDIALS = [base_path]
LIB_DIRS_SUNDIALS  = [base_path, '/usr/lib', '/usr/local/lib/']

LIBS_SUNDIALS = ['sundials_nvecserial']
LIBS_IDA      = ['sundials_ida']
LIBS_CVODE    = ['sundials_cvode']

# paths for FORTRAN
LIB_DIRS_FORTRAN = []
LIBS_FORTRAN     = []

use_lapack = False
try:
    if INCL_DIRS_LAPACK and LIB_DIRS_LAPACK and LIBS_LAPACK:
        print('Using user provided LAPACK paths...')
        use_lapack = True
    else:
        lapack_opt = get_info('lapack_opt', notfound_action=2)

        if lapack_opt:
            INCL_DIRS_LAPACK = lapack_opt.get('include_dirs',[])
            LIB_DIRS_LAPACK  = lapack_opt.get('library_dirs',[])
            LIBS_LAPACK      = lapack_opt.get('libraries',[])
            use_lapack = True
        else:
            raise ValueError
except:
    print('LAPACK was not detected, disabling sundials solvers')


def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    print("=============================================")
    print("parent package is %s" % parent_package)
    print("top path is %s" % top_path)
    print("=============================================")
    config = Configuration('sundials', parent_package, top_path)

    if use_lapack:
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
                             library_dirs=LIB_DIRS_SUNDIALS+LIB_DIRS_LAPACK+LIB_DIRS_FORTRAN,
                             libraries=LIBS_IDA+LIBS_SUNDIALS+LIBS_LAPACK+LIBS_FORTRAN)

        cython(['cvode.pyx'], working_path=base_path)
        config.add_extension("cvode",
                             sources=['cvode.c'],
                             depends=['common_defs.c'],
                             include_dirs=INCL_DIRS_SUNDIALS+INCL_DIRS_LAPACK,
                             library_dirs=LIB_DIRS_SUNDIALS+LIB_DIRS_LAPACK+LIB_DIRS_FORTRAN,
                             libraries=LIBS_CVODE+LIBS_SUNDIALS+LIBS_LAPACK+LIBS_FORTRAN)
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
