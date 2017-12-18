import numpy as np
import pandas as pd
from scipy.ndimage.filters import gaussian_filter1d
from scipy import signal



#Finds the maximum current ("A").  Current is calculated by convolution with a first-deriv. of Gaussian
def current_max(waveform, sigma=1):
  if sigma > 0:
      return np.amax(gaussian_filter1d(waveform, sigma=sigma, order=1))
  else:
      print("Current max requires smooth>0")
      exit(0)

#Finds baseline from start index to end index samples (default linear)
def fit_baseline(waveform, start_index=0, end_index=500, order=1):
    if end_index == -1: end_index = len(waveform)
    p = np.polyfit(np.arange(start_index, end_index), waveform[start_index:end_index], 1)
    return p

def is_saturated(waveform, bit_precision=14):
    return True if np.amax(waveform) >= 0.5*2**bit_precision - 1 else False

#Estimate t0
def t0_estimate(waveform, baseline=0):
    #find max to walk back from:
    maxidx = np.argmax(waveform)

    #find first index below or equal to baseline value walking back from the max
    t0_from_max = np.argmax(waveform[maxidx::-1] <= baseline)
    if t0_from_max == 0:
        # print("warning: t0_from_max is zero")
        return 0
    return maxidx - t0_from_max

#Estimate arbitrary timepoint before max
def calc_timepoint(waveform, percentage=0.5, baseline=0, do_interp=False):
    '''
    percentage: if less than zero, will return timepoint on falling edge
    do_interp: linear linerpolation of the timepoint...
    '''
    if percentage > 0:
        first_over = np.argmax( waveform >= (percentage*(np.amax(waveform) - baseline) + baseline) )
        if do_interp and first_over > 0:
            val = np.interp(percentage, ( waveform[first_over-1],   waveform[first_over] ), (first_over-1, first_over))
        else: val = first_over
    else:
        percentage = np.abs(percentage)
        above_thresh = waveform >= (percentage*(np.amax(waveform) - baseline) + baseline)
        last_over = len(waveform)-1 - np.argmax(above_thresh[::-1])
        if do_interp and last_over < len(waveform)-1:
            val = np.interp(percentage, ( waveform[last_over],   waveform[last_over+1] ), (last_over, last_over+1))
        else: val = last_over
    return val


#Calculate maximum of trapezoid -- no pride here
def trap_max(waveform, method = "max", pickoff_sample = 0):
    if method == "max": return np.amax(waveform)
    elif method == "fixed_time": return waveform[pickoff_sample]
