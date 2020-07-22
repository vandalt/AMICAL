from matplotlib import pyplot as plt

import amical

plt.close("all")

datadir = 'TestSPHEREData/'


file_t = datadir + 'HD142527_IRD_SCIENCE_DBI_LEFT_CUBE.fits'
file_c = datadir + 'HD142695_IRD_SCIENCE_DBI_LEFT_CUBE.fits'


# ----------------------------------
# Cleaning step
# ----------------------------------
cube_t = amical.selectCleanData(file_t, clip=True,
                                corr_ghost=False,
                                display=True)

cube_c = amical.selectCleanData(file_c, clip=True,
                                corr_ghost=False,
                                display=True)

#  AMI parameters (refer to the docstrings of `extract_bs` for details)
params_ami = {"peakmethod": 'fft',
              "bs_MultiTri": False,
              "maskname": "g7",
              "fw_splodge": 0.7,
              "filtname": 'K1'
              }


# # Extract raw complex observables for the target and the calibrator:
# # It's the core of the pipeline (amical/mf_pipeline/bispect.py)
bs_t = amical.extract_bs(cube_t, file_t, targetname='HD142527',
                         **params_ami, display=True)
bs_c = amical.extract_bs(cube_c, file_c, targetname='HD142695',
                         **params_ami, display=False)

# (from amical.tools import checkSeeingCond, plotSeeingCond)
# In case of multiple files for a same target, you can
# check the seeing condition and select only the good ones.
# cond_t = checkSeeingCond([bs_t])
# cond_c = checkSeeingCond([bs_c])
# plotSeeingCond([cond_t, cond_c], lim_seeing=1)


# Calibrate the raw data to get get calibrated V2 and CP
# bs_c can be a single calibrator result or a list of calibrator.
# (see amical/core.py for details).
cal = amical.calibrate(bs_t, bs_c)

# Display and save the results as oifits
amical.show(cal, true_flag_t3=False, cmax=180, pa=bs_t.pa)
amical.save(cal, fake_obj=True, verbose=False, pa=bs_t.pa)

plt.show(block=True)
