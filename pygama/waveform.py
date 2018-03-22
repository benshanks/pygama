import numpy as np
from .calculators import calc_timepoint
from .transforms import center

class Waveform():

    def __init__(self, wf_data, sample_period):
        self.data = wf_data
        self.sample_period = sample_period

    #Putting this method here so I can overload it in subclasses w/ more options
    def get_waveform(self):
        return self.data

    def window_waveform(self, time_point=0.5, early_samples=200, num_samples=400):
        '''Windows waveform around a risetime percentage timepoint
            time_point: percentage (0-1)
            early_samples: samples to include before the calculated time_point
            num_samples: total number of samples to include
        '''

        #don't mess with the original data
        wf_copy = np.copy(self.data)

        #bl subtract
        wf_copy -= self.bl_int + np.arange(len(wf_copy))*self.bl_slope

        #Normalize the waveform by the calculated energy (noise-robust amplitude estimation)
        wf_norm = np.copy(wf_copy) / self.amplitude
        tp_idx = np.int( calc_timepoint(wf_norm, time_point, doNorm=False  ))

        self.windowed_wf = center(wf_copy, tp_idx, early_samples, num_samples-early_samples)
        self.window_length = num_samples

        return self.windowed_wf

class MultisampledWaveform(Waveform):
    def __init__(self, time, wf_data, sample_period, full_sample_range, *args, **kwargs):
        self.time = time
        self.full_sample_range = full_sample_range
        super().__init__(wf_data, sample_period, **kwargs)

    def get_waveform(self):
        return self.data[self.full_sample_range[0]:self.full_sample_range[-1]]
