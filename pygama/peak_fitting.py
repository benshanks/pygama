import numpy as np
from scipy.optimize import minimize, curve_fit
from scipy.special import erfc

#unbinned max likelihood fit to data with given likelihood func
def fit_unbinned(likelihood_func, data, start_guess, min_method="L-BFGS-B", bounds=None):
    result = minimize(neg_log_like,     # function to minimize
                  x0=start_guess,          # start value
                  args=(likelihood_func,data),      # additional arguments for function
                  method=min_method, # minimization method, see docs
                  bounds=bounds
                  )
    return result.x

#regular old binned fit (nonlinear least squares)
def fit_binned(likelihood_func, hist_data, bin_centers, start_guess):
    #data should already be histogrammed.
    coeff, var_matrix = curve_fit(likelihood_func, bin_centers, hist_data, p0=start_guess)
    return coeff

#Wrapper to give me neg log likelihoods
def neg_log_like(params,likelihood_func, data,  **kwargs):
    lnl = - np.sum(np.log(likelihood_func(data, *params, **kwargs)))
    return lnl

#Define a gaussian distribution and corresponding neg log likelihood
def gauss(x, *p):
    # print(p)
    if len(p) == 2:
        mu, sigma = p
        A= 1
    elif len(p) == 3:
        mu,sigma,A = p
    else:
        print("Incorrect usage of gaussian function!  params: mu, sigma, area (optional).  You input: {}".format(p))
        exit(0)
    return A*(1./sigma/np.sqrt(2*np.pi))*np.exp(-(x-mu)**2/(2.*sigma**2))

def radford_peak(x,*p):
    if len(p) == 6:
        mu, sigma, hstep, htail, tau, bg0,  = p
        a=1
    elif len(p) == 7:
        mu, sigma, hstep, htail, tau, bg0, a = p
    else:
        print("Incorrect usage of radford peak function!  You input: {}".format(p))
        exit(0)

    #make sure the fractional amplitude parameters stay reasonable...
    if htail < 0 or htail > 1: return np.zeros_like(x)
    if hstep < 0 or hstep > 1: return np.zeros_like(x)

    bg_term = bg0 #+ x*bg1
    if np.any(bg_term < 0): return np.zeros_like(x)
    step    = a * hstep * erfc( (x-mu)/(sigma*np.sqrt(2))  )
    le_tail = a * htail * erfc( (x-mu)/(sigma*np.sqrt(2)) +
              sigma/(tau*np.sqrt(2))) *np.exp( (x-mu)/tau) / ( 2*tau*np.exp( -(sigma/(np.sqrt(2)*tau))**2 ) )
    return (1-htail)*gauss(x, mu, sigma, a) + bg_term + step + le_tail