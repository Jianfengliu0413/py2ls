import numpy as np
import pandas as pd
from scipy.signal import butter, hilbert, filtfilt, find_peaks,resample, resample_poly
from scipy.interpolate import interp1d
from scipy.ndimage import convolve1d
import os
import mne
import scipy.io
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import seaborn as sns
# from multitaper_spectrogram_python import *

def load_mat(dir_mat):
    return scipy.io.loadmat(dir_mat)

# def loadmat(dir_mat):
#     return scipy.io.loadmat(dir_mat)

# Define data path
# data_file = "./UCLA_data/CSC4.Ncs"def 
def load_ncs(dir_file, header_size=16 * 1024):
    # Header has 16 kilobytes length
    # header_size = 16 * 1024

    # Open file
    fid = open(dir_file, "rb")

    # Skip header by shifting position by header size
    fid.seek(header_size)

    # Read data according to Neuralynx information
    data_format = np.dtype(
        [
            ("TimeStamp", np.uint64),
            ("ChannelNumber", np.uint32),
            ("SampleFreq", np.uint32),
            ("NumValidSamples", np.uint32),
            ("Samples", np.int16, 512),
        ]
    )

    raw = np.fromfile(fid, dtype=data_format)
    # Close file
    fid.close()

    # filling output
    res = {}
    res["data"] = raw["Samples"].ravel()  # Create data vector
    res["fs"] = raw["SampleFreq"][0]  # Get sampling frequency
    res["dur_sec"] = (
        res["data"].shape[0] / raw["SampleFreq"][0]
    )  # Determine duration of recording in seconds
    res["time"] = np.linspace(
        0, res["dur_sec"], res["data"].shape[0]
    )  # Create time vector
    return pd.DataFrame(res)

def ncs2_single_raw(fpath, ch_names=None, ch_types=None):
    ncs_data = load_ncs(fpath)
    data = ncs_data["data"]
    sfreq = ncs_data["fs"][0]
    if ch_names is None:
        ch_names = [os.path.splitext(os.path.basename(fpath))[0]]
    if ch_types is None:
        ch_types = "eeg" if "eeg" in ch_names[0].lower() else "eog"  # should be 'lfp'
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    data_nchan_nsamples = np.array(data)[np.newaxis, :]
    raw = mne.io.RawArray(data_nchan_nsamples, info)
    return raw

def trial_extract(trial):
    # the mat should be stored older version, otherwise, cannot be read
    # recommend: mat_data = scipy.io.loadmat(dir_data) #import scipy.io
    while (type(trial[0]) == "numpy.float64") or (len(trial[0]) == 1):
        trial = trial[0].copy()
    print(trial[0].shape)
    return trial[0]

# # dir_data = "/Users/macjianfeng/Desktop/test_v7_dat.mat"
# dir_data = "/Users/macjianfeng/Desktop/mat_r06rec1.mat"
# mat_data = scipy.io.loadmat(dir_data)

# trials = trial_extract(mat_data["trial"])
# fs = mat_data["fsample"][0][0]
# label = repr(mat_data["label"][0][0][0])  # convert to 'str'

# print("first 12 trials: ", trials[:12])
# print("fs=", fs)
# print("label=", label, "type(label):", type(label))
def cal_slope(data, segment=1, correct=True):
    length = len(data)
    slope = []
    for i in range(0, length - segment, segment):
        change_in_y = data[i + segment] - data[i]
        change_in_x = segment
        slope.append(change_in_y / change_in_x)
    if correct:
        # Interpolate the slopes to fill in the gaps
        interpolated_slopes = np.repeat(slope, segment)
        # Adjust the length of interpolated_slopes to match the length of continuous_line
        missing_values = len(data) - len(interpolated_slopes)
        if missing_values > 0:
            interpolated_slopes = np.append(
                interpolated_slopes, [slope[-1]] * missing_values
            )
        return interpolated_slopes
    else:
        return slope
# Apply bandpass filter to EEG signal
def butter_band_filter(data, lowcut, highcut, fs, ord=3):
    from scipy.signal import butter

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(ord, [low, high], btype="band")
    dat_spin_filt = filtfilt(b, a, data)
    return dat_spin_filt


def butter_bandpass_filter(data=None, ord=4, freq_range=[11, 16], fs=1000):
    from scipy.signal import butter
    print("usage:\n butter_bandpass_filter(data=None, ord=4, freq_range=[11, 16], fs=1000)")
    # alternative:
    b, a = butter(ord, freq_range, btype="bandpass", fs=fs)
    data_filt = filtfilt(b,a,data)
    return data_filt

def filter_bandpass(data=None, ord=4, freq_range=[11, 16], fs=1000):
    from scipy.signal import butter
    # print("usage:\n butter_bandpass_filter(data=None, ord=4, freq_range=[11, 16], fs=1000)")
    # alternative:
    b, a = butter(ord, freq_range, btype="bandpass", fs=fs)
    data_filt = filtfilt(b,a,data)
    return data_filt

# Apply smoothing (moving average)
def moving_average(data, window_size):
    return convolve1d(data, np.ones(window_size) / window_size)

def detect_cross(data, thr=0):
    if isinstance(data, list):
        data = np.array(data)
    if data.ndim == 1:
        pass
    elif data.ndim == 2 and data.shape[0] > data.shape[1]:
        data = data.T
    else:
        raise ValueError("Input data must have two dimensions.")

    thr_cross = np.sign(data[:, np.newaxis] - thr)
    falling_before = np.where((thr_cross[:-1] == 1) & (thr_cross[1:] == -1))[0] #+ 1
    rising_before = np.where((thr_cross[:-1] == -1) & (thr_cross[1:] == 1))[0]
    falling_before = falling_before.tolist()
    rising_before = rising_before.tolist()
    if rising_before and falling_before:
        if rising_before[0] < falling_before[0]:
            if len(rising_before) > len(falling_before):
                rising_before.pop(0)
        else:
            falling_before.pop(0)
            if len(rising_before) > len(falling_before):
                rising_before.pop(0)
    ## debug
    # a = np.sin(np.arange(0, 10 * np.pi, np.pi / 100))

    # thres = 0.75
    # rise, fall = detect_cross(a, thres)
    # RisingFalling = np.column_stack((rise, fall))
    # plt.figure(figsize=[5, 2])
    # t = np.arange(len(a))
    # plt.plot(t, a)
    # for i in range(4):
    #     plt.plot(
    #         t[RisingFalling[i][0] : RisingFalling[i][1]],
    #         a[RisingFalling[i][0] : RisingFalling[i][1]],
    #         lw=10 - i,
    #     )
    #     plt.plot(
    #         t[RisingFalling[i][0] : RisingFalling[i + 1][0]],
    #         a[RisingFalling[i][0] : RisingFalling[i + 1][0]],
    #         lw=7 - i,
    #     )
    #     plt.plot(
    #         t[RisingFalling[i][0] : RisingFalling[i + 1][1]],
    #         a[RisingFalling[i][0] : RisingFalling[i + 1][1]],
    #         lw=5 - i,
    #     )
    # plt.gca().axhline(thres)
    return rising_before, falling_before

def find_repeats(data, N, nGap=None):
    """
    Find the beginning and end points of repeated occurrences in a dataset.

    Parameters:
        data (list or numpy.ndarray): The dataset in which repeated occurrences are to be found.
        N (int or list of int): The element(s) to search for.
        nGap (int, optional): The number of elements that can appear between repeated occurrences.
                              Defaults to 1 if not provided.

    Returns:
        numpy.ndarray: An array containing the beginning and end points of repeated occurrences
                       of the specified element(s).

    Description:
        This function identifies the beginning and end points of repeated occurrences
        of specified elements in a dataset. It searches for the element(s) specified
        by `N` in the input `data` and returns the indices where consecutive occurrences
        are separated by at most `nGap` elements.

    Example:
        data = [1, 2, 3, 4, 1, 2, 5, 1, 2, 2, 3]
        idx = find_repeats(data, [1, 2])
        print(idx)  # Output: [[0, 2], [3, 5], [6, 8], [7, 9]]

        idx = find_repeats(data, 2, 2)
        print(idx)  # Output: [[4, 8]]

    """
    # Convert data to numpy array if it's a list
    if isinstance(data, list):
        data = np.array(data)

    if nGap is None:
        nGap = 1

    if isinstance(N, int):
        N = [N]

    idx = []
    for num in N:
        if num in data:
            idx_beg = [
                i
                for i, x in enumerate(data)
                if x == num and (i == 0 or data[i - 1] != num)
            ]
            idx_end = [
                i - 1
                for i, x in enumerate(data)
                if x == num and (i == len(data) - 1 or data[i + 1] != num)
            ]

            # Adjust indices for Python's zero-based indexing
            # idx_beg = [i + 1 for i in idx_beg]
            idx_end = [i + 1 for i in idx_end]

            idx_array = list(zip(idx_beg, idx_end))
            # Correct the first column of idx_array
            idx_single = [
                i
                for i in range(len(idx_array))
                if idx_array[i][1] - idx_array[i][0] == 0
            ]
            for single in idx_single:
                idx_array[single] = (idx_array[single][0], idx_array[single][1] + 1)

            if nGap == 1:
                idx.append([(beg, end) for beg, end in idx_array])
            elif nGap > 1:
                idx.append([(beg * nGap + 1, end * nGap) for beg, end in idx_array])
        else:
            idx.append([])

    return np.concatenate(idx)

def find_continue(data, step=1):
    """
    Find indices for the beginning and end of continuous segments in data.

    Parameters:
        data (numpy.ndarray): Input array.
        step (int): Comparison difference. Default is 1.

    Returns:
        tuple: Tuple containing arrays of indices for the beginning and end of continuous segments.
    """
    if isinstance(data, (list, np.ndarray)):
        data = np.array(data)  # Ensure data is a numpy array
    if not isinstance(step, int):
        raise TypeError("step must be an integer")

    idx_beg = np.where(np.diff([-99999] + data.tolist()) != step)[0]
    idx_end = np.where(np.diff(data.tolist() + [-99999]) != step)[0]

    return idx_beg, idx_end

def resample_data(data, input_fs, output_fs, t=None, axis=0, window=None, domain='time',method='fourier', **kwargs):
    """
    Downsample a signal to a target sampling frequency.
    
    Parameters:
        data (array-like): 
            The signal to be downsampled.
        input_fs (float): 
            The original sampling frequency of the signal.
        output_fs (float): 
            The target sampling frequency for downsampling.
        # num int:
        #     The number of samples in the resampled signal.
        t : array_like, optional
            If t is given, it is assumed to be the equally spaced sample positions associated with the 
            signal data in x.
        axis : int, optional
            The axis of x that is resampled. Default is 0.
        window: array_like, callable, string, float, or tuple, optional
            Specifies the window applied to the signal in the Fourier domain. See below for details.
        domain: string, optional
            A string indicating the domain of the input x: time Consider the input x as time-domain (Default), 
            freq Consider the input x as frequency-domain.
    Returns:
        array-like: The downsampled signal.
    """
    if input_fs < output_fs:
        # raise ValueError(f"Target freq = {output_fs} must be <= {input_fs} Hz(input_fs) .")
        # The resample function in scipy uses Fourier method by default for resampling. This method involves 
        # upsampling the signal in the frequency domain, then low-pass filtering to remove aliasing, and 
        # finally downsampling to the desired rate.
        if method == 'fourier':
            # Upsampling using Fourier method
            factor = output_fs / input_fs
            num_samples_new = int(len(data) * factor)
            data_resampled = resample(data, num_samples_new)
            print(f"Original data {input_fs} Hz\nUpsampled data {output_fs} Hz using Fourier method")

        elif method == 'linear':
            # Upsampling using linear interpolation
            t_original = np.arange(len(data)) / input_fs
            t_resampled = np.arange(len(data) * output_fs / input_fs) / output_fs
            f = interp1d(t_original, data, kind='linear', fill_value='extrapolate')
            data_resampled = f(t_resampled)
            print(f"Original data {input_fs} Hz\nUpsampled data {output_fs} Hz using linear interpolation")

        elif method == 'spline':
            # Upsampling using spline interpolation
            t_original = np.arange(len(data)) / input_fs
            t_resampled = np.arange(len(data) * output_fs / input_fs) / output_fs
            f = interp1d(t_original, data, kind='cubic', fill_value='extrapolate')
            data_resampled = f(t_resampled)
            print(f"Original data {input_fs} Hz\nUpsampled data {output_fs} Hz using spline interpolation")

        elif method == 'sinc':
            # Upsampling using windowed sinc interpolation
            upsample_factor = output_fs / input_fs
            data_resampled = resample_poly(data, int(len(data) * upsample_factor), 1)
            print(f"Original data {input_fs} Hz\nUpsampled data {output_fs} Hz using sinc interpolation")

        elif method == 'zero':
            # Upsampling by zero-padding
            upsample_factor = output_fs / input_fs
            data_resampled = np.repeat(data, int(upsample_factor))
            print(f"Original data {input_fs} Hz\nUpsampled data {output_fs} Hz using zero-padding")

    elif input_fs == output_fs:
        print(f"Input = output = {output_fs} Hz. \nNo resampling is performed.")
        return data
    else:
        if method == 'fourier':
            # Calculate the resampling factor
            resampling_factor = input_fs / output_fs

            # Calculate the new number of samples
            num_samples_new = int(len(data) / resampling_factor)

            # Perform resampling
            data_resampled = resample(data, num_samples_new)
            
            print(f"Original data {input_fs} Hz\nResampled data {output_fs} Hz using Fourier method")
        elif method == 'decimate':
            # Downsampling using decimate function (which internally uses FIR filter)
            decimation_factor = int(input_fs / output_fs)
            data_resampled = decimate(data, decimation_factor, zero_phase=True)
            print(f"Original data {input_fs} Hz\nDownsampled data {output_fs} Hz using decimation")

    return data_resampled


def extract_score(dir_score, kron_go=True,scalar=10*1000):
    df_score = pd.read_csv(dir_score, sep="\t")
    score_val = df_score[df_score.columns[1]].values
    if kron_go:
        score_val = np.kron(
            score_val, np.ones((1,round(scalar)))
        ).reshape(1, -1)
    return score_val[0]

def plot_sleeparc(
    ax,
    score,
    code_org=[1, 2, 3],
    code_new=[1, 0, -1],
    kind="patch",
    c=["#474747", "#0C5DA5", "#0C5DA5"],
):
    score[np.where(score == code_org[0])] = code_new[0]
    score[np.where(score == code_org[1])] = code_new[1]
    score[np.where(score == code_org[2])] = code_new[2]
    dist = code_new[0] - code_new[1]
    colorlist = c
    # patch method
    if "pa" in kind.lower():
        for i in range(score.shape[0]):
            x = [i - 1, i, i, i - 1]
            if score[i] == code_new[0]:
                y = [code_new[0], code_new[0], code_new[0] + dist, code_new[0] + dist]
                c = colorlist[0]
            elif score[i] == code_new[1]:
                y = [code_new[1], code_new[1], code_new[0], code_new[0]]
                c = colorlist[1]
            elif score[i] == code_new[2]:
                y = [code_new[2], code_new[2], code_new[1], code_new[1]]
                c = colorlist[2]
            ax.fill(x, y, c=c, edgecolor="none")
    # line method
    if "l" in kind.lower():
        ax.plot(score, c=colorlist[0])
    return ax

def filter_linenoise(
    data, fs, method="notch", bandwidth=2, n_components=None, random_state=None
):
    from scipy import signal

    nyquist = fs / 2
    freq = np.arange(1, 100) * 50
    freq = list(freq[np.where(freq <= nyquist)])
    print(f"nyquist={nyquist}hz, clearned freq:{freq}")
    if method == "notch":
        for f0 in freq:

            w0 = f0 / nyquist  # Normalized Frequency
            # Design notch filter
            b_, a_ = signal.iirnotch(w0, Q=bandwidth)
            if f0 == freq[0]:
                clean_data = signal.lfilter(b_, a_, data)
            else:
                clean_data = signal.lfilter(b_, a_, clean_data)
    elif method == "bandstop":
        b_, a_ = signal.iirnotch(w0=freq / nyquist, Q=bandwidth, fs=fs)
        clean_data = signal.filtfilt(b_, a_, data, axis=-1)
    elif method == "ica":  # Independent Component Analysis (ICA)
        from sklearn.decomposition import FastICA

        ica = FastICA(n_components=n_components, random_state=random_state)
        ica_components = ica.fit_transform(data.T).T
        clean_data = ica.inverse_transform(ica_components)

    return clean_data

def MAD(signal, mSTD=1.4826):
    """
        to calculate the MedianAbsoluteDeviation (MAD) of a 1D array (signal)
        Parameters:
            signal: 1D array of data.
            mSTD: Multiplier used to scale the MAD. Default value is 1.4826, which is a scaling 
                factor to make MAD asymptotically consistent for the estimation of standard deviation
                under the assumption of a normal distribution.
            Output:
            MAD: The Median Absolute Deviation of the input signal.
            Explanation:
                The function calculates the median of the input signal using np.median(signal).
                It then calculates the absolute deviations of each element in the signal from the median
            The median of these absolute deviations is then calculated using np.median().
            Finally, the MAD is obtained by multiplying this median absolute deviation by the scaling factor mSTD.
    """
    # signal is a 1-d array
    medians = np.median(signal)
    MAD = mSTD * np.median(np.abs(signal - medians))
    return MAD


def detect_spikes(data, Fs, mSTD=1.4826, direction="both"):
    """
    Purpose: This function detects spikes in the input data.
    Parameters:
    data: The input signal data.
    Fs: The sampling rate of the signal in Hz.
    mSTD: The multiplier used to compute the threshold. Default is set to 1.4826, 
        which is equivalent to the standard deviation of a Gaussian distribution. This 
        value is typically used with the Median Absolute Deviation (MAD) to estimate 
        the threshold.
    direction: Specifies the direction of spikes to detect. Default is set to "both", 
        meaning it detects both positive and negative spikes.
    Return:
        spike_idx: Indices of the detected spikes in the input data.
    time: Time stamps of the detected spikes in milliseconds.
    Explanation:
        The function computes the threshold (thr_) based on the Median Absolute Deviation 
        (MAD) of the input data.
        It then detects spikes based on the specified direction using the computed threshold.
        The detected spike indices and their corresponding time stamps are returned.
    """
    # Detect spikes
    # s, t = detectSpikes(x,Fs) detects spikes in x, where Fs the sampling
    #   rate (in Hz). The outputs s and t are column vectors of spike times in
    #   samples and ms, respectively. By convention the time of the zeroth
    #   sample is 0 ms.

    # if is_dataframe(x):
    #     pass
    # mad_ = (x - x.mean()).abs().mean()
    spike_idx = {}
    t = {}
    thr_ = MAD(data, mSTD=mSTD)
    # thr_ = np.percentile(signal, 66.6)

    # # alternative: thr_ is set to 8.0, and the threshold is calculated as 8 times
    # # the square root of the variance of the first 10 seconds of data
    # thr_ = mSTD * np.sqrt(x[col][: 10 * Fs].astype("float64"))

    directions = ["both", "pos", "neg"]  # 'both': detect both posi and neg.
    if direction in "both":
        time = [x / Fs for x in np.where(np.abs(data) >= thr_)]
        spike_idx, _ = find_peaks(np.abs(data), height=thr_)

    elif direction in "positive":
        time = [x / Fs for x in np.where(data >= thr_)]
        spike_idx, _ = find_peaks(data, height=thr_)
    elif direction in "negative":
        time = [x / Fs for x in np.where((-1) * data <= thr_)]
        spike_idx, _ = find_peaks((-1) * data, height=thr_)

    return spike_idx, time

def extract_spikes_waveforms(data, Fs, mSTD=1.4826, win=[-10, 20], direction="both"):
    """
    Purpose: This function extracts waveforms of detected spikes from the input data.
    Parameters:
        data: The input signal data.
        Fs: The sampling rate of the signal in Hz.
        mSTD: The multiplier used to compute the threshold. Default is set to 1.4826, which is 
            equivalent to the standard deviation of a Gaussian distribution. This value is typically 
            used with the Median Absolute Deviation (MAD) to estimate the threshold.
        win: The window size around each detected spike to extract the waveform. It is specified as a 
            list [start_offset, end_offset], where start_offset is the number of samples before the 
            spike index and end_offset is the number of samples after the spike index.
        direction: Specifies the direction of spikes to detect. Default is set to "both", meaning it 
            extracts waveforms for both positive and negative spikes.
    Output:
    waveforms: Extracted waveforms of the detected spikes.
        It first detects spikes using the detect_spikes() function.
        For each detected spike, it extracts the waveform within the specified window 
        around the spike index.
        The extracted waveforms are stored in a NumPy array and returned.
    """
    spike_idx, _ = detect_spikes(data, Fs, mSTD=mSTD, direction=direction)
    num_spikes = len(spike_idx)
    win_start = win[0] + 1
    win_end = win[1] + 1
    waveform_length = win_end - win_start

    waveforms = np.empty((num_spikes, waveform_length)) * np.nan

    for i, idx in enumerate(spike_idx):
        start_idx = int(idx + win_start)
        end_idx = int(idx + win_end)

        # Ensure the start and end indices are within bounds
        if start_idx >= 0 and end_idx <= data.shape[0]:
            waveforms[i, :] = data[start_idx:end_idx]

    # Remove rows with NaN values (corresponding to spikes outside bounds)
    waveforms = waveforms[~np.isnan(waveforms).all(axis=1)]

    print(f"Extracted waveforms number: {waveforms.shape}")

    return waveforms

def extract_peaks_waveforms(data, pks, win_size):
    """
    Extracts waveforms from data centered around peak indices.

    Parameters:
    - data (1d-array): The data array from which waveforms are to be extracted.
    - pks (list): A list of peak indices.
    - win_size: A tuple specifying the window size around each peak.
                   It should be of the form (start_offset, end_offset).

    Returns:
    - waveform_array: A 2D NumPy array containing the extracted waveforms.
                      Each row corresponds to a waveform.
    """
    waveforms = []
    for i in pks:
        start_index = int(i + win_size[0])
        end_index = int(i + win_size[1])
        waveforms.append(data[start_index:end_index])
    waveform_array = np.array(waveforms)
    return waveform_array
# usage: win_size = [-500, 500]
# waveform = extract_peaks_waveforms(
#     data=data_ds, pks=res_sos.sos.pks_neg_idx, win_size=win_size
# )
# Function to find the closest timestamp
def find_closest_timestamp(time_rel, time_fly):
    closest_idx = np.argmin(np.abs(time_fly - time_rel))
    return time_fly[closest_idx]


def coupling_finder(rel_pks, fly_pks, win, verbose=False):
    pks_cp_rel = []
    pks_cp_fly = []
    for rel_pk in rel_pks:
        closest_pt = find_closest_timestamp(rel_pk, fly_pks)
        delta_t = closest_pt - rel_pk
        if abs(delta_t) <= win:
            pks_cp_rel.append(rel_pk)
            pks_cp_fly.append(closest_pt)

    # Calculate coupling rate
    if not pks_cp_rel:
        cp_rate = 0
    else:
        cp_rate = (len(pks_cp_rel) / len(rel_pks)) * 100

    if verbose:
        print(f"Coupling Rate: {cp_rate}%")

    return pks_cp_rel, pks_cp_fly, cp_rate

def perm_circ(data_1d):
    # to perform circular permutation
    permuted_1d = np.roll(data_1d, np.random.randint(len(data_1d)))
    return permuted_1d


def coupling_permutate(rel_pks, fly_pks, win, n_perm=1000):
    # Function to simulate SWR-shuffled condition   
    pks_cp_rel_shuf, pks_cp_fly_shuf, cp_rate_shuf = [], [], []
    for _ in range(n_perm):
        pks_rel_shuf = perm_circ(rel_pks)
        pks_cp_rel_tmp, pks_cp_fly_tmp, cp_rate_tmp = coupling_finder(
            rel_pks=pks_rel_shuf, fly_pks=fly_pks, win=win, verbose=False
        )
        pks_cp_rel_shuf.append(pks_cp_rel_tmp)
        pks_cp_fly_shuf.append(pks_cp_fly_tmp)
        cp_rate_shuf.append(cp_rate_tmp)
    return pks_cp_rel_shuf, pks_cp_fly_shuf, cp_rate_shuf

def detect_spindles(data, opt):
    # usage: prepare the opt cfg
    # opt = pd.DataFrame(
    # {
    #     "spin": {
    #         "thr": [1.5, 2, 2.5],
    #         "dur_sec": [0.5, 2.5],
    #         "freq_range": [11, 16],
    #         "stage": 2,
    #         "smth": False,
    #     },
    #     "info": {
    #         "fs": 1000,
    #         "epoch_dur": 10,
    #         "dir_score": "/Users/macjianfeng/DataCenter/Meflo-SSD/Data_Scored_Txt/R6Rec1_scoring.txt",
    #     },
    # }
    # )

    fs = opt["info"]["fs"]
    epoch_dur = opt["info"]["epoch_dur"]

    # Filter
    # amp_filt = butter_band_filter(
    #     data=data,
    #     lowcut=opt["spin"]["freq_range"][0],
    #     highcut=opt["spin"]["freq_range"][1],
    #     fs=fs,
    # )
    amp_filt = filter_bandpass(
        ord=opt['spin']['filt_ord'],
        data=data,
        freq_range=opt["spin"]["freq_range"],
        fs=fs,
    )

    # Calculate amp_filt_env using Hilbert transform
    amp_filt_env = np.abs(hilbert(amp_filt))

    # Apply additional smoothing (moving average with 200-ms window size)
    if opt["spin"]["smth"]:
        # Calculate mean and standard deviation of amp_filt_env
        amp_filt_env_mean = np.mean(moving_average(amp_filt_env, int(0.2 * fs)))
        amp_filt_env_std = np.std(moving_average(amp_filt_env, int(0.2 * fs)))
    else:
        # Calculate mean and standard deviation of amp_filt_env
        amp_filt_env_mean = np.mean(amp_filt_env)
        amp_filt_env_std = np.std(amp_filt_env)

    # 2.3 filling in one matrix
    Thr = []
    for m_std in opt["spin"]["thr"]:
        Thr.append(amp_filt_env_std * m_std)
    # 2.4 use the defined Thresholds
    if len(Thr) >= 1:
        a, b = detect_cross(amp_filt_env, Thr[0])
    else:
        raise ValueError("Didn not find the 1st spi.Thr")

    RisingFalling = np.column_stack((a, b))
    dur_sec = opt["spin"]["dur_sec"]
    Dura_tmp = np.diff(RisingFalling, axis=1)
    Thr1Spin1 = RisingFalling[
        np.where((dur_sec[0] * fs < Dura_tmp) & (Dura_tmp < dur_sec[1] * fs)),
        :,
    ][0]
    Thr1Spin1 = Thr1Spin1.reshape(-1, 2)

    # 2.4.1.2 calcultion the EventsSpin1 in NREM (specific sleep stages) or not
    score_code = extract_score(opt["info"]["dir_score"],scalar=fs * epoch_dur)
    stage_spin_idx = find_repeats(
        score_code, opt["spin"]["stage"], nGap=1
    )
    stage_spin_idx = stage_spin_idx[
        np.where(
            (stage_spin_idx[:, 0] >= fs * epoch_dur)
            & (stage_spin_idx[:, 1] <= len(amp_filt) - fs * epoch_dur)
        )
    ]
    EventsSpin1 = Thr1Spin1[
        np.where(
            (stage_spin_idx[:, 0] < Thr1Spin1[:, 0].reshape(-1, 1))
            & (Thr1Spin1[:, 1].reshape(-1, 1) < stage_spin_idx[:, 1])
        )[0],
        :,
    ]
    # print("step1", EventsSpin1.shape)
    # 2.4.2 Thr2 crossing
    if len(Thr) >= 2:
        a, b = detect_cross(amp_filt_env, Thr[1])
        RisingFalling = np.column_stack((a, b))
        SpinDura_min2 = dur_sec[0] / 2  # half of the minium duration
        SpinDura_max2 = dur_sec[1]
        Dura_tmp = np.diff(RisingFalling, axis=1)
        EventsSpin2 = RisingFalling[
            np.where(
                (SpinDura_min2 * fs <= Dura_tmp) & (Dura_tmp <= SpinDura_max2 * fs)
            ),
            :,
        ]
    else:
        EventsSpin2 = np.copy(EventsSpin1)
    EventsSpin2 = EventsSpin2.reshape(-1, 2)
    # print("step2", EventsSpin2.shape)
    # 2.4.2.3 check EventsSpin2 in EventsSpin1
    EventsSpin3 = []
    if (
        ("EventsSpin1" in locals())
        and ("EventsSpin2" in locals())
        and (EventsSpin1.shape[0] != 0)
        and (EventsSpin2.shape[0] != 0)
    ):
        EventsSpin3 = EventsSpin1[
            np.where(
                (EventsSpin1[:, 0] < EventsSpin2[:, 0].reshape(-1, 1))
                & (EventsSpin2[:, 1].reshape(-1, 1) < EventsSpin1[:, 1])
            )[1],
            :,
        ]
    # print("step3", EventsSpin3.shape)
    # 2.4.2.4 unique EventsSpin3
    if EventsSpin3.shape[0] != 0:
        EventsSpin3_orgs = np.copy(EventsSpin3)
        EventsSpin3 = np.unique(EventsSpin3_orgs[:, 0:2], axis=0)

    if len(Thr) >= 3:
        # 2.4.3 Crossing positions - Thr 3
        EventsSpin4 = []
        iSpi4 = 0
        if EventsSpin3.shape[0] != 0:
            for iSpi3 in range(EventsSpin3.shape[0]):
                if (
                    np.max(amp_filt_env[EventsSpin3[iSpi3, 0] : EventsSpin3[iSpi3, 1]])
                    >= Thr[2]
                ):
                    EventsSpin4.append([EventsSpin3[iSpi3, 0], EventsSpin3[iSpi3, 1]])
                    iSpi4 += 1
            if isinstance(EventsSpin4, list):
                EventsSpin4 = np.array(EventsSpin4)
            EventsSpin4 = EventsSpin4.reshape(-1, 2)
        else:
            EventsSpin4 = EventsSpin3.copy()
    else:
        EventsSpin4 = EventsSpin3.copy()
        print("\ncannot find the 3rd Thr_spin, only 2 Thr were used for spin dtk \n")
    # print("step4", EventsSpin4.shape)
    # 2.5 checking if two spindles are too close? gap should be more than 50 ms;
    if "EventsSpin4" in locals() and EventsSpin4.shape[0] != 0:
        iSpin4 = 0
        EventsSpin5 = []
        for iSpin in range(1, EventsSpin4.shape[0]):
            tmp_gap = (
                EventsSpin4[iSpin, 0] - EventsSpin4[iSpin - 1, 1]
            ) / fs  # in second
            if (
                tmp_gap <= 0.05
            ):  # gap less than SpinDura_min and the total duration should not more than SpinDura_max1
                EventsSpin5.append([EventsSpin4[iSpin - 1, 0], EventsSpin4[iSpin, 1]])
            else:
                EventsSpin5.append(list(EventsSpin4[iSpin]))
            iSpin4 += 1
    else:
        EventsSpin5 = EventsSpin4.copy()
    if isinstance(EventsSpin5, list):
        EventsSpin5 = np.array(EventsSpin5)
    EventsSpin5 = EventsSpin5.reshape(-1, 2)
    # print("step5", EventsSpin5.shape)
    if "EventsSpin5" in locals():
        # 2.5.2 merge into one spindles
        if EventsSpin5.shape[0] != 0:
            EventsSpin5_diff_merge = np.where(
                np.diff(np.hstack((0, EventsSpin5[:, 0]))) == 0
            )[0]
            EventsSpin5_diff_rm = EventsSpin5_diff_merge - 1
            EventsSpin5 = np.delete(
                EventsSpin5, EventsSpin5_diff_rm, axis=0
            )  # remove the merged parts
            del EventsSpin5_diff_rm, EventsSpin5_diff_merge

            # 2.5.3 remove the last 5s recording;
            RecTail = len(amp_filt)  # in sample resolution
            Last5s = RecTail - epoch_dur / 2 * fs  # half epoch
            if EventsSpin5.shape[0] != 0:
                for iSpin in range(EventsSpin5.shape[0], 0, -1):
                    if EventsSpin5[iSpin - 1, 1] <= Last5s:
                        EventsSpin6 = EventsSpin5[0:iSpin, :]
                        break
                    else:
                        EventsSpin6 = EventsSpin5.copy()
        else:
            EventsSpin6 = EventsSpin5.copy()
    else:
        EventsSpin6 = EventsSpin5.copy()
    EventsSpin6 = EventsSpin6.reshape(-1, 2)
    # print("step6", EventsSpin6.shape)
    # 2.5.3 spin2spin duration should not beyond the 'SpinDura_max2'
    if len(Thr) >= 2:
        EventsSpin = EventsSpin6[
            np.where(np.diff(EventsSpin6, axis=1) <= SpinDura_max2 * fs)[0], :
        ]
    else:
        EventsSpin = EventsSpin6.copy()
    EventsSpin = EventsSpin.reshape(-1, 2)
    # print("final detected spindle number: ", EventsSpin.shape)
    # 2.6 Spindle density (counts during NREM) Spin density (events/min)
    # calculated as the number of spindle detected in each recording site
    # divided by the time in SWS.
    SpinDensity = EventsSpin.shape[0] / (
        np.sum(np.diff(stage_spin_idx, axis=1)) / fs / 60
    )  # in minute
    # print("spindle density: ", SpinDensity)

    # Freq of each Spindles
    num_spin_pks = []
    for i in range(EventsSpin.shape[0]):
        peaks, _ = find_peaks(
            amp_filt[EventsSpin[i, 0] : EventsSpin[i, 1]], height=Thr[0]
        )  # Assuming Thr is a scalar
        num_spin_pks.append(len(peaks))

    dur_spin_sec = np.diff(EventsSpin, axis=1) / fs
    spin_freq = [
        (x / y).tolist()[0] for (x, y) in zip(np.array(num_spin_pks), dur_spin_sec)
    ]
    spin_avg_freq = np.nanmean(spin_freq, axis=0)
    # print(f"Average spindle frequency: {spin_avg_freq:.4f} Hz")

    # Spindle Power
    spin_pow_single = []
    for iPow in range(EventsSpin.shape[0]):
        spin_pow_single.append(np.trapz(amp_filt_env[EventsSpin[i, 0] : EventsSpin[i, 1]]))

    # find the max pks loc
    if EventsSpin.shape[0] > 1:
        spin_pk2pk = []
        spin_pks_loc = []
        loc_max_spin=[]
        ipk = 0
        for ispin in range(EventsSpin.shape[0]):
            tmp = amp_filt[
                EventsSpin[ispin, 0] : EventsSpin[ispin, 1] + 1
            ]  # +1 to include the end index
            # (1) find pks_max
            locs_max, _ = find_peaks(list(tmp))
            pks_max = tmp[locs_max]
            pks_max_spin = np.max(pks_max)
            loc_max_spin_ = (
                locs_max[np.where(pks_max == pks_max_spin)[0][0]] + EventsSpin[ispin, 0]
            )
            loc_max_spin.append(loc_max_spin_)
            # (2) find pks_min
            pks_min = tmp[locs_max]
            pks_min = pks_min * (-1)  # don't forget to multiply by -1
            pks_min_spin = np.min(pks_min)
            loc_min_spin_ = (
                locs_max[np.where(pks_min == pks_min_spin)[0][0]] + EventsSpin[ispin, 0]
            )
            # (3) spin_pk2pk
            spin_pk2pk.append(pks_max_spin - pks_min_spin)
            spin_pks_loc.append(
                [loc_min_spin_, pks_min_spin, loc_max_spin_, pks_max_spin]
            )
            ipk += 1
        spin_pk2pk = np.array(spin_pk2pk)
        spin_pks_loc = np.array(spin_pks_loc)
    else:
        spin_pks_loc = np.array([])
        spin_pk2pk = np.array([])
    if opt.spin['extract']:
        waveform = extract_peaks_waveforms(data=data, pks=loc_max_spin, win_size=opt.spin["win_size"])
    print(f"detected {EventsSpin.shape[0]} spindles, density={SpinDensity}")
    # fillint output
    res = pd.DataFrame(
        {
            "spin": {
                "idx_start_stop": EventsSpin,
                "num":EventsSpin.shape[0],
                "density": SpinDensity,
                "thr": Thr,
                "freq": spin_freq,
                "pow": spin_pow_single,
                "pk2pk": spin_pk2pk,
                "pk2pk_loc": spin_pks_loc,
                "max_pks_loc":loc_max_spin,
                "avg_freq":spin_avg_freq,
                "win_size":opt.spin["win_size"],
                "waveform":waveform
            }
        }
    )
    del amp_filt_env 
    del amp_filt 
    del data
    return res

def detect_sos(data, opt):
    fs = opt["info"]["fs"]
    epoch_dur = opt["info"]["epoch_dur"]

    amp_filt = filter_bandpass(
        ord=opt["sos"]["filt_ord"],
        data=data,
        freq_range=opt["sos"]["freq_range"],
        fs=fs,
    )
    # zero_cross
    rise_b4, fall_b4 = detect_cross(amp_filt, 0)
    loc_cross = np.zeros((len(fall_b4) - 1, 2))
    # [falling1, falling2; falling2, faling3;....]
    loc_cross[:, 0] = [x for x in fall_b4[:-1]]
    loc_cross[:, 1] = [x for x in fall_b4[1:]]
    # #+++++++++ check the loc_cross+++++++++
    # t = np.arange(len(amp_filt))
    # plt.figure(figsize=[6, 2])
    # plt.plot(
    #     t[int(loc_cross[0][0] - 50) : int(loc_cross[0][1] + 50)],
    #     amp_filt[int(loc_cross[0][0] - 50) : int(loc_cross[0][1] + 50)],
    #     lw=0.75,
    # )
    # plt.plot(
    #     t[int(loc_cross[0][0]) : int(loc_cross[0][1])],
    #     amp_filt[int(loc_cross[0][0]) : int(loc_cross[0][1])],
    #     lw=1.5,
    #     c="r",
    # )
    # plt.axhline(0, lw=0.75)
    # plt.show()
    # # sos candidates within NREM_idx time-frame
    score_code = extract_score(
        opt["info"]["dir_score"], kron_go=True, scalar=fs * epoch_dur
    )
    so_stage_idx = find_repeats(score_code, opt["sos"]["stage"], nGap=1)
    so_stage_idx = so_stage_idx[np.where(so_stage_idx[:, 0] >= fs * epoch_dur)]
    so_stage_idx = so_stage_idx[
        np.where(so_stage_idx[:, 1] <= (len(data) - fs * epoch_dur))
    ]
    sos_kndt_Loc = loc_cross[
        np.where(
            (so_stage_idx[:, 0] < loc_cross[:, 0].reshape(-1, 1))
            & (loc_cross[:, 1].reshape(-1, 1) < so_stage_idx[:, 1])
        )[0],
        :,
    ]

    dur_sec = opt["sos"]["dur_sec"]
    dura_tmp = np.diff(sos_kndt_Loc, axis=1)
    event_sos_loc = sos_kndt_Loc[
        np.where((dur_sec[0] * fs < dura_tmp) & (dura_tmp < dur_sec[1] * fs))[0].tolist(), :
    ]
    event_sos_loc = np.array(
        [(int(x), int(y)) for (x, y) in np.array(event_sos_loc).reshape(-1, 2)]
    ).reshape(
        -1, 2
    )  # int
    sos_pks_pos_idx = []
    sos_pks_neg_idx = []
    sos_pks_neg_value = []
    sos_pk2pk = []

    for iso in range(event_sos_loc.shape[0]):
        # max
        sos_max_tmp = np.max(amp_filt[event_sos_loc[iso, 0] : event_sos_loc[iso, 1]])
        sos_pks_idx_max_tmp = list(
            amp_filt[event_sos_loc[iso, 0] : event_sos_loc[iso, 1]]
        ).index(sos_max_tmp)
        sos_pks_pos_idx.append(int(event_sos_loc[iso, 0] + sos_pks_idx_max_tmp))
        # min
        sos_min_tmp = np.min(amp_filt[event_sos_loc[iso, 0] : event_sos_loc[iso, 1]])
        sos_pks_idx_min_tmp = list(
            amp_filt[event_sos_loc[iso, 0] : event_sos_loc[iso, 1]]
        ).index(sos_min_tmp)
        sos_pks_neg_idx.append(int(event_sos_loc[iso, 0] + sos_pks_idx_min_tmp))
        sos_pks_neg_value.append(sos_min_tmp)
        # pk2pk
        sos_pk2pk.append(sos_max_tmp + np.abs(sos_min_tmp))
    if isinstance(sos_pks_neg_value, list):
        sos_pks_neg_value = np.array(sos_pks_neg_value)
        sos_pk2pk = np.array(sos_pk2pk)
    if opt["sos"]["thr"] == []:
        n_prctile_amplitude = opt["sos"]["n_prctile_amplitude"]
        thr_negpks_amp = np.percentile(
            np.abs(sos_pks_neg_value), n_prctile_amplitude, axis=0
        )
        thr_pks2pks = np.percentile(sos_pk2pk, n_prctile_amplitude, axis=0)
        sos_thr = np.array([-thr_negpks_amp, thr_pks2pks])
    else:
        if len(opt["sos"]["thr"]) == 1:
            thr_negpks_amp = abs(opt["sos"]["thr"][0])
            sos_thr = np.array([-thr_negpks_amp])
        elif len(opt["sos"]["thr"]) == 2:
            thr_negpks_amp = abs(opt["sos"]["thr"][0])
            thr_pks2pks = opt["sos"]["thr"][1]
            sos_thr = np.array([-thr_negpks_amp, thr_pks2pks])
    ithr = 1
    sos_loc = []
    (
        abs(sos_pks_neg_value[iso]) > sos_thr[0] and abs(sos_pk2pk[iso]) > sos_thr[1]
        if len(sos_thr) == 2
        else abs(sos_pks_neg_value[iso]) > sos_thr[0]
    )
    if "event_sos_loc" in locals() and event_sos_loc.shape[0] != 0:
        for iso in range(sos_pk2pk.shape[0]):
            thr_criterion = (
                abs(sos_pks_neg_value[iso]) > sos_thr[0]
                and abs(sos_pk2pk[iso]) > sos_thr[1]
                if len(sos_thr) == 2
                else abs(sos_pks_neg_value[iso]) > sos_thr[0]
            )

            if thr_criterion:
                sos_loc.append(
                    [
                        event_sos_loc[iso, 0],
                        event_sos_loc[iso, 1],
                        sos_pks_neg_idx[iso],
                        amp_filt[sos_pks_neg_idx[iso]],
                        sos_pks_pos_idx[iso],
                        amp_filt[sos_pks_pos_idx[iso]],
                    ]
                )
                ithr += 1

    if len(sos_loc) != 0:
        sos_loc = np.array(sos_loc)
        sos_idx = sos_loc[:, :2].astype(int)
        sos_pks_neg_idx = sos_loc[:, 2].astype(int)
        sos_pks_pos_idx = sos_loc[:, 4].astype(int)
        sos_pks_loc = sos_loc[:, 2:6]
        sos_pk2pk = sos_loc[:, 5] - sos_loc[:, 3]
    # 3.7 sos density
    if "sos_idx" in locals():
        sos_density = len(sos_idx) / (
            np.sum(np.diff(so_stage_idx, axis=1)) / fs / 60
        )  # in minutes
    # 3.8 Freq of each sos
    if "sos_idx" in locals():
        # sos Power and sos Freq
        # amp_filt = np.abs(hilbert(amp_filt))
        sos_power = np.zeros((len(sos_idx), 1))
        sos_dura_sec = np.diff(sos_idx, axis=1) / fs
        for i in range(len(sos_idx)):
            sos_power[i] = np.trapz(amp_filt[sos_idx[i, 0] : sos_idx[i, 1]])
        sos_freq = 1 / sos_dura_sec.flatten()  # Frequency
    # 3.10 slope_sos
    # calculating the slope of slow wave events by taking the difference between
    # the positive and negative peaks and dividing it by the respective time
    # interval.
    #
    # Calculate slope for each slow wave event
    sos_slope = np.zeros(len(sos_pks_pos_idx))
    for i in range(len(sos_pks_pos_idx)):
        # Calculate the slope as (positive peak - negative peak) / time interval
        sos_slope[i] = (amp_filt[sos_pks_pos_idx[i]] - amp_filt[sos_pks_neg_idx[i]]) / (
            sos_pks_pos_idx[i] - sos_pks_neg_idx[i]
        )
    if opt.sos["extract"]:
        waveform = extract_peaks_waveforms(
            data=data, pks=sos_pks_neg_idx, win_size=opt.sos["win_size"]
        )
    else:
        waveform = []
    print(f"detected {sos_idx.shape[0]} SOs, density={sos_density}")
    # fillint output
    res = pd.DataFrame(
        {
            "sos": {
                "idx_start_stop": sos_idx,
                "num":sos_idx.shape[0],
                "density": sos_density,
                "thr": sos_thr,
                "slope": sos_slope,
                "freq": sos_freq,
                "pks_neg_idx": sos_pks_neg_idx,
                "pks_pos_idx": sos_pks_pos_idx,
                "pk2pk": sos_pk2pk,
                "pks_loc": sos_pks_loc,
                "pow": sos_power,
                "win_size":opt.spin["win_size"],
                "waveform":waveform
            },
        }
    )
    
    # # debug++++++++plot the grandaverage sos+++++++++++
    # win_size = 1.5
    # waveform = []
    # for pks_ne_idx in res.sos.pks_neg_idx:
    #     waveform.append(
    #         amp_filt[int(pks_ne_idx - win_size * fs) : int(pks_ne_idx + win_size * fs)]
    #     )
    # waveform = np.array(waveform).reshape(-1, int(win_size * 2 * fs))
    # # plot
    # fig, axs = plt.subplots(1, 1, figsize=[8, 3])

    # stdshade(
    #     axs,
    #     range(waveform.shape[1]),
    #     waveform,
    #     0.39,
    #     [x / 255 for x in [48, 109, 99]],
    #     30,
    # )
    # plt.axvline(waveform.shape[1] / 2, c="k", label="t0='sos negtive peak'")
    # plt.axhline(0, c=".6")
    # plt.legend()
    # plt.show()
    del amp_filt 
    del data
    return res

def detect_ripples(data, opt):
    fs = opt["info"]["fs"]
    epoch_dur = opt["info"]["epoch_dur"]

    amp_filt = filter_bandpass(
        ord=opt["rip"]["filt_ord"],
        data=data,
        freq_range=opt["rip"]["freq_range"],
        fs=fs,
    )

    # Calculate amp_filt_env using Hilbert transform
    amp_filt_env = np.abs(hilbert(amp_filt))
    # Apply additional smoothing (moving average with 200-ms window size)
    if opt["rip"]["smth"]:
        # Calculate mean and standard deviation of amp_filt_env
        amp_filt_env_mean = np.mean(moving_average(amp_filt_env, int(0.2 * fs)))
        amp_filt_env_std = np.std(moving_average(amp_filt_env, int(0.2 * fs)))
    else:
        # Calculate mean and standard deviation of amp_filt_env
        amp_filt_env_mean = np.mean(amp_filt_env)
        amp_filt_env_std = np.std(amp_filt_env)
    # 2.3 filling in one matrix
    Thr = np.array(opt["rip"]["thr"]) * amp_filt_env_std
    # 2.4 use the defined Thresholds
    if len(Thr) >= 1:
        a, b = detect_cross(amp_filt_env, Thr[0])
    else:
        raise ValueError("Didn not find the 1st spi.Thr")
    RisingFalling = np.column_stack((a, b))
    rip_dura_sec = opt["rip"]["dur_sec"]
    Dura_tmp = np.diff(RisingFalling, axis=1)
    Thr1rip1 = RisingFalling[
        np.where((rip_dura_sec[0] * fs < Dura_tmp) & (Dura_tmp < rip_dura_sec[1] * fs)),
        :,
    ][0]
    # 2.4.1.2 calcultion the EventsRip1 in NREM (specific sleep stages) or not
    score_code = extract_score(opt["info"]["dir_score"], scalar=fs * epoch_dur)
    stage_rip_idx = find_repeats(score_code, opt["rip"]["stage"], nGap=1)
    stage_rip_idx = stage_rip_idx[
        np.where(
            (stage_rip_idx[:, 0] >= fs * epoch_dur)
            & (stage_rip_idx[:, 1] <= len(amp_filt) - fs * epoch_dur)
        )
    ]
    EventsRip1 = Thr1rip1[
        np.where(
            (stage_rip_idx[:, 0] < Thr1rip1[:, 0].reshape(-1, 1))
            & (Thr1rip1[:, 1].reshape(-1, 1) < stage_rip_idx[:, 1])
        )[0],
        :,
    ]
    # print("step1", EventsRip1.shape)
    # 2.4.2 Thr2 crossing
    if len(Thr) >= 2:
        a, b = detect_cross(amp_filt_env, Thr[1])
        RisingFalling = np.column_stack((a, b))
        ripDura_min2 = rip_dura_sec[0] / 2  # half of the minium duration
        ripDura_max2 = rip_dura_sec[1]
        Dura_tmp = np.diff(RisingFalling, axis=1)
        EventsRip2 = RisingFalling[
            np.where((ripDura_min2 * fs <= Dura_tmp) & (Dura_tmp <= ripDura_max2 * fs)),
            :,
        ][0]
    else:
        EventsRip2 = np.copy(EventsRip1)
    # print("step2", EventsRip2.shape)
    # 2.4.2.3 check EventsRip2 in EventsRip1
    if (
        ("EventsRip1" in locals())
        and ("EventsRip2" in locals())
        and (EventsRip1.shape[0] != 0)
        and (EventsRip2.shape[0] != 0)
    ):
        EventsRip3 = EventsRip1[
            np.where(
                (EventsRip1[:, 0] < EventsRip2[:, 0].reshape(-1, 1))
                & (EventsRip2[:, 1].reshape(-1, 1) < EventsRip1[:, 1])
            )[1],
            :,
        ]
    # print("step3", EventsRip3.shape)
    # 2.4.2.4 unique EventsRip3
    if EventsRip3.shape[0] != 0:
        EventsRip3_orgs = np.copy(EventsRip3)
        EventsRip3 = np.unique(EventsRip3_orgs[:, 0:2], axis=0)
    if len(Thr) >= 3:
        # 2.4.3 Crossing positions - Thr 3
        EventsRip = []
        irip4 = 0
        if EventsRip3.shape[0] != 0:
            for irip3 in range(EventsRip3.shape[0]):
                if (
                    np.max(amp_filt_env[EventsRip3[irip3, 0] : EventsRip3[irip3, 1]])
                    >= Thr[2]
                ):
                    EventsRip.append([EventsRip3[irip3, 0], EventsRip3[irip3, 1]])
                    irip4 += 1
            if isinstance(EventsRip, list):
                EventsRip = np.array(EventsRip)
            EventsRip = EventsRip.reshape(-1, 2)
        else:
            EventsRip = EventsRip3.copy()
    else:
        EventsRip = EventsRip3.copy()
        print("\ncannot find the 3rd Thr_rip, only 2 Thr were used for rip dtk \n")
    EventsRip = EventsRip.reshape(-1, 2)
    # print("final detected ripple number: ", EventsRip.shape)
    # 2.6 ripple density (counts during NREM) rip density (events/min)
    # calculated as the number of ripple detected in each recording site
    # divided by the time in SWS.
    rip_density = EventsRip.shape[0] / (
        np.sum(np.diff(stage_rip_idx, axis=1)) / fs / 60
    )  # in minute
    print(f"detected {EventsRip.shape[0]} ripples, density={rip_density}")
    # Freq of each ripples
    num_rip_pks = []
    for i in range(EventsRip.shape[0]):
        peaks, _ = find_peaks(
            amp_filt[EventsRip[i, 0] : EventsRip[i, 1]], height=Thr[0]
        )  # Assuming Thr is a scalar
        num_rip_pks.append(len(peaks))

    dur_rip_sec = np.diff(EventsRip, axis=1) / fs
    rip_freq = [(x / y).tolist()[0] for (x, y) in zip(np.array(num_rip_pks), dur_rip_sec)]
    rig_avg_freq = np.nanmean(rip_freq, axis=0)
    print(f"Average ripple frequency: {rig_avg_freq:.4f} Hz")
    # ripple Power # Use numpy's np.trapz() to compute the area under the curve
    rip_pow_single = [np.trapz(amp_filt_env[start:end]) for start, end in EventsRip]

    if EventsRip.shape[0] > 1:
        loc_max_rip = [np.argmax(amp_filt[start:end]) + start for start, end in EventsRip]
        rip_pk2pk = [
            (np.max(amp_filt[start:end]) - np.min(amp_filt[start:end]))
            for start, end in EventsRip
        ]
        # rip_pk2pk = []
        # rip_pks_loc = []
        # loc_max_rip = []
        # ipk = 0
        # for irip in range(EventsRip.shape[0]):
        #     tmp = amp_filt[
        #         EventsRip[irip, 0] : EventsRip[irip, 1] + 1
        #     ]  # +1 to include the end index
        #     # (1) find pks_max
        #     locs_max, _ = find_peaks(list(tmp))
        #     pks_max = tmp[locs_max]
        #     pks_max_rip = np.max(pks_max)
        #     loc_max_rip_ = (
        #         locs_max[np.where(pks_max == pks_max_rip)[0][0]] + EventsRip[irip, 0]
        #     )
        #     loc_max_rip.append(loc_max_rip_)

        #     # (2) find pks_min
        #     pks_min = tmp[locs_max]
        #     pks_min = pks_min * (-1)  # don't forget to multiply by -1
        #     pks_min_rip = np.min(pks_min)
        #     loc_min_rip_ = (
        #         locs_max[np.where(pks_min == pks_min_rip)[0][0]] + EventsRip[irip, 0]
        #     )
        #     # (3) rip_pk2pk
        #     rip_pk2pk.append(pks_max_rip - pks_min_rip)
        #     rip_pks_loc.append([loc_min_rip_, pks_min_rip, loc_max_rip_, pks_max_rip])
        #     ipk += 1
        # rip_pk2pk = np.array(rip_pk2pk)
        # rip_pks_loc = np.array(rip_pks_loc)
    else:
        # rip_pks_loc = np.array([])
        rip_pk2pk = np.array([])
    if opt.rip["extract"] and EventsRip.shape[0] > 1:
        waveform = extract_peaks_waveforms(
            data=data, pks=loc_max_rip, win_size=opt.rip["win_size"]
        )
    else:
        waveform = []
    # fillint output
    res = pd.DataFrame(
        {
            "rip": {
                "idx_start_stop": EventsRip,
                "num": EventsRip.shape[0],
                "density": rip_density,
                "thr": Thr,
                "freq": rip_freq,
                "pow": rip_pow_single,
                "pk2pk": rip_pk2pk,
                # "pk2pk_loc": rip_pks_loc,
                "avg_freq": rig_avg_freq,
                "max_pks_loc": loc_max_rip,
                "win_size": opt.spin["win_size"],
                "waveform": waveform,
            }
        }
    )
    del amp_filt
    del data
    del amp_filt_env

    return res