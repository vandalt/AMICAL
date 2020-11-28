import numpy as np
from termcolor import cprint
from uncertainties import ufloat, umath

from amical.analysis import candid


def candid_grid(input_data, step=10, rmin=20, rmax=400, diam=0, obs=['cp', 'v2'],
                extra_error_cp=0, err_scale=1, extra_error_v2=0, instruments=None,
                doNotFit=['diam*', ], ncore=1, verbose=False):
    """ This function is an user friendly interface between the users of amical
    pipeline and the CANDID analysis package (https://github.com/amerand/CANDID).

    Parameters:
    -----------
    `input_data` {str or list}:
        oifits file names or list of oifits files,\n
    `step` {int}:
        step used to compute the binary grid positions,\n
    `rmin`, `rmax` {float}:
        Bounds of the grid [mas],\n
    `diam` {float}:
        Stellar diameter of the primary star [mas] (default=0),\n
    `obs` {list}:
        List of observables to be fitted (default: ['cp', 'v2']),\n
    `doNotFit` {list}:
        Parameters not fitted (default: ['diam*']),\n
    `verbose` {boolean}:
        print some informations {default: False}.

    Outputs:
    --------
    `res` {dict}:
        Dictionnary of the results ('best'), uncertainties ('uncer'),
        reduced chi2 ('chi2') and sigma detection ('nsigma').
    """

    cprint(' | --- Start CANDID fitting --- :', 'green')
    o = candid.Open(input_data, extra_error=extra_error_cp,
                    err_scale=err_scale, extra_error_v2=extra_error_v2,
                    instruments=instruments)

    o.observables = obs

    o.fitMap(rmax=rmax, rmin=rmin, ncore=ncore, fig=0,
             step=step, addParam={"diam*": diam}, doNotFit=doNotFit, verbose=verbose)

    fit = o.bestFit["best"]
    e_fit = o.bestFit["uncer"]
    chi2 = o.bestFit['chi2']
    nsigma = o.bestFit['nsigma']

    f = fit["f"] / 100.0
    e_f = e_fit["f"] / 100.0
    if (e_f < 0) or (e_fit["x"] < 0) or (e_fit["y"] < 0):
        print('Warning: error dm is negative.')
        e_f = abs(e_f)
        e_fit["x"] = 0
        e_fit["y"] = 0

    f_u = ufloat(f, e_f)
    x, y = fit["x"], fit["y"]
    x_u = ufloat(x, e_fit["x"])
    y_u = ufloat(y, e_fit["y"])

    dm = 2.5*umath.log(1 / (f_u)) / umath.log(10)
    s = (x_u ** 2 + y_u ** 2) ** 0.5
    posang = ((umath.atan2(x_u, y_u)*180/np.pi))
    if posang.nominal_value < 0:
        posang = 360 + posang

    cr = 1/f_u
    cprint("\nResults binary fit (χ2 = %2.1f, nσ = %2.1f):" %
           (chi2, nsigma), "cyan")
    cprint("-------------------", "cyan")

    print("Sep = %2.1f +/- %2.1f mas" % (s.nominal_value, s.std_dev))
    print("Theta = %2.1f +/- %2.1f deg" %
          (posang.nominal_value, posang.std_dev))
    print("CR = %2.1f +/- %2.1f" % (cr.nominal_value, cr.std_dev))
    print("dm = %2.2f +/- %2.2f" % (dm.nominal_value, dm.std_dev))
    res = {'best': {'model': 'binary_res',
                    'dm': dm.nominal_value,
                    'theta': posang.nominal_value,
                    'sep': s.nominal_value,
                    'diam': fit["diam*"],
                    'x0': 0,
                    'y0': 0},
           'uncer': {'dm': dm.std_dev,
                     'theta': posang.std_dev,
                     'sep': s.std_dev},
           'chi2': chi2,
           'nsigma': nsigma,
           'comp': o.bestFit["best"]
           }

    return res


def candid_cr_limit(input_data, step=10, rmin=20, rmax=400,
                    extra_error_cp=0, err_scale=1, extra_error_v2=0,
                    obs=['cp', 'v2'], fitComp=None, ncore=1,
                    diam=None, methods=['injection'], instruments=None,
                    drawMaps=False):
    cprint(' | --- Start CANDID contrast limit --- :', 'green')
    o = candid.Open(input_data, extra_error=extra_error_cp,
                    err_scale=err_scale, extra_error_v2=extra_error_v2,
                    instruments=instruments)
    o.observables = obs

    res = o.detectionLimit(rmin=rmin, rmax=rmax, step=step, drawMaps=drawMaps,
                           fratio=1, methods=methods, removeCompanion=fitComp,
                           ncore=ncore, diam=diam)
    return res
