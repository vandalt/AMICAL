# -*- coding: utf-8 -*-
"""
@author: Anthony Soulain (University of Sydney)

-------------------------------------------------------------------------
AMICAL: Aperture Masking Interferometry Calibration and Analysis Library
-------------------------------------------------------------------------

The idea is to provide the users with all the tools to analyze and interpret
their AMI data in the best possible way. We included with AMICAL two additional
(and independant) packages to perform this purposes.

CANDID developed by A. Merand & A. Gallenne (https://github.com/amerand/CANDID) and
Pymask developed by B. Pope, A. Cheetham (https://github.com/AnthonyCheetham/pymask).

With AMICAL, we provide some easy interface between these codes and the outputs 
of our extraction pipeline. We give below some example to analyze and 
extract the quantitative values of our simulated binary.

-------------------------------------------------------------------- 
"""

from matplotlib import pyplot as plt

import amical

# Your inputdata is an oifits file or a list of oifits.
inputdata = 'Saveoifits/fakebinary_NIRISS_g7_F430M_58886_1.oifits'

use_candid = False
use_pymask = False

# Analysis with CANDID package
# ----------------------------
if use_candid:
    param_candid = {'rmin': 20,  # inner radius of the grid
                    'rmax': 250,  # outer radius of the grid
                    'step': 20,  # grid sampling
                    'ncore': 12  # core for multiprocessing (see warning below)
                    }

    fit1 = amical.candidGrid(inputdata, **param_candid)

    cr_candid = amical.candidCRlimit(
        inputdata, **param_candid, fitComp=fit1['comp'])

# WARNING: the use of multiprocessing appeared
# to be unstable in the last version of OSX catalina+
# So we imposed ncore=1 by default (no multiproc), you can
# try to increase ncore option but it could crash
# depending on your system (tested on OSX-mojave).

# Analysis with PYMASK package
# ----------------------------
if use_pymask:
    param_pymask = {'sep_prior': [100, 180],  # Prior on the separation
                    'pa_prior': [20, 80],  # Prior on the position angle
                    'cr_prior': [230, 270],  # Prior on the contrast ratio
                    'ncore': 12,  # core for multiprocessing
                    'extra_error': 0,
                    'err_scale': 1,
                    }

    # Pymask proposes to add some extra_error on the CP. This allows to take
    # into account a possibly understimated uncertainties on the data. Indeed,
    # some bias due to mismatch between the calibrator and the science spectral type,
    # or some systematic temporal effect could produce additional errors not properly
    # retrieved by the covariance matrix.

    # In addition, we can also add some scaling parameter (`err_scale`) on the CP
    # uncertainties to deal with the number of independant closure phases (N(N-1)(N-2)/6)
    # compare to the dependant one ((N-1)(N-2)/2). If you considere the full CP set (35 for
    # a 7 holes mask), you possibly over-use your data, so you have to scale
    # your uncertainties by the factor of additional CP, which is sqrt(N/3).

    # ** Note that if you used only a subset of CP (by selecting one common hole to
    # save the oifits, see amical.save for details), this additional `err_scale` is unusable.

    fit2 = amical.pymaskGrid(inputdata, **param_pymask)

    param_mcmc = {'niters': 800,
                  'walkers': 100,
                  'initial_guess': [146, 47, 244],
                  'burn_in': 100}

    fit3 = amical.pymaskMcmc(inputdata, **param_pymask, **param_mcmc)

    cr_pymask = amical.pymaskCRlimit(inputdata, nsim=500, ncore=12, smax=250,
                                     nsep=100, cmax=5000, nth=30, ncrat=60)

if use_candid & use_pymask:
    plt.figure()
    plt.plot(cr_candid['r'], cr_candid['cr_limit'],
             label='CANDID', alpha=.5, lw=3)
    plt.plot(cr_pymask['r'], cr_pymask['cr_limit'],
             label='Pymask', alpha=.5, lw=3)
    plt.ylim(plt.ylim()[1], plt.ylim()[0])  # -- rreverse plot
    plt.xlabel('Separation [mas]')
    plt.ylabel('$\Delta \mathrm{Mag}_{3\sigma}$')
    plt.legend(loc='best')
    plt.grid()
    plt.tight_layout()

plt.show(block=True)
