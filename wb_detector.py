# Author: Jianfeng Liu (andyandhope@gmail.com)
# This script contains functions for detecting white balance bands in images and calculating the area under the curve for each band.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.integrate import simps
import cv2
import os
from PIL import Image

def find_pks(data_valid, n_bands, idx_corr=0, threshold=np.arange(0.8, 1, 0.01)):
    # This function finds peaks in the data_valid array based on specified parameters.
    # It adjusts the threshold until it finds the desired number of peaks.

    # Find initial peaks using a peak finding function (not provided)
    pks_pre, _ = find_peaks(data_valid)

    # Iterate through different threshold values
    for thr in threshold:
        # Calculate distance between peaks based on threshold
        distance = ((pks_pre[-1] - pks_pre[0]) // n_bands) * thr

        # Find peaks using adjusted threshold and other parameters
        peaks, _ = find_peaks(
            (np.max(data_valid) - data_valid),
            distance=distance,
            height=(np.max(data_valid) - np.min(data_valid)) * 0.1,
        )

        # Check if the number of found peaks matches the expected number of bands
        if peaks.shape[0] == (n_bands - 1):
            break

        # If the threshold reaches its last value and the desired number of peaks is not found, print a message
        if thr == threshold[-1]:
            print("did not find the perfect threshold")

    # Adjust the peaks indices to reflect their position in the original data
    peaks += idx_valid[0][0]

    # Print information about found peaks, threshold, and distance
    print(f"peaks={peaks}\npeaks_shape={len(peaks)}\nthr={thr}\ndistance={distance}")

    # Return the peaks indices
    return peaks


def cal_area(data, peaks, idx_valid_bands, x_range):
    # This function calculates the area under the curve between adjacent peaks for each band.
    area_values = []
    for iband in idx_valid_bands:
        if iband + 1 >= len(peaks):
            break
        # Define the x and y values within the band
        x_band = x_range[peaks[iband] : peaks[iband + 1]]
        y_band = data[peaks[iband] : peaks[iband + 1]]
        # Integrate the y-values within the band to find the area
        area = simps(y_band, x_band)
        area_values.append(area)
    return area_values

def check_load_img(dir_data): 
    if isinstance(dir_data,str):
        rgb_image = cv2.imread(dir_data)
        data = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
    elif isinstance(dir_data, Image.Image):
        # convert it
        rgb_image = np.array(dir_data) 
        data = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    else:
        raise TypeError(f"{dir_data} is neither a directory nor a PIL.Image.Image instance.")
    return data

def detect_wb_bands(dir_data, n_bands=24, weight=0.25, outlier=None):
    # This function detects the white balance bands in an image.
    """ param:
        dir_data, [path]
        n_bands [int], default 24 lanes. how many bands
        weight=0.25, [float], 0.01 means keep more light bands, 0.5 remove 
            light band. the greater, the less sensitivity
        outlier=None, [list], e.g., [0,3] means the 1st and 4th bands will 
            be removed, will not taken into account
    """
    # Load the image and convert it to grayscale 
    data = check_load_img(dir_data)

    # Determine the bit depth of the image
    if data.dtype == np.uint16:
        bit_depth = 16
    elif data.dtype == np.uint8:
        bit_depth = 8
    print(f"bit_depth:{bit_depth}")

    # Invert the grayscale image
    data_ivrt = 2**bit_depth - data
    data_cum = np.sum(data_ivrt, axis=0)
    x_range = np.arange(data.shape[1])  # Generate x-axis values

    # Identify baseline and normalize cumulative intensity values
    bsln = np.min(data_cum)
    data_cum_bsln = data_cum - bsln
    data_valid = np.zeros((data_cum_bsln.shape))  # Initialize valid data array
    idx_valid = np.where(data_cum_bsln > np.max(data_cum_bsln) * weight)[
        0
    ]  # Determine valid indices
    data_valid[idx_valid] = data_cum_bsln[idx_valid]  # Assign valid data values

    threshold = np.arange(0.5, 1, 0.01)  # Define threshold range
    for thr in threshold:
        # Calculate distance between peaks based on threshold
        distance = ((idx_valid[-1] - idx_valid[0]) // n_bands) * thr

        # Find peaks using adjusted threshold
        peaks, _ = find_peaks(
            (np.max(data_valid) - data_valid),
            distance=distance,
        )

        # Check if the number of found peaks matches the expected number of bands
        if peaks.shape[0] == (n_bands - 1):
            break

        # If the threshold reaches its last value and the desired number of peaks is not found, print a message
        if thr == threshold[-1]:
            print("did not find the perfect threshold")

    # Adjust the peaks indices to include the start and end of the data
    peaks_tail = [idx_valid[0]]
    for i in peaks:
        peaks_tail.append(i)
    peaks_tail.append(idx_valid[-1])

    # Handle outlier bands if specified
    if outlier is None:
        idx_valid_bands = np.arange(n_bands)
    else:
        idx_valid_bands = np.delete(np.arange(n_bands), outlier)

    # Calculate area under the curve for each band
    area_values = cal_area(data_valid, peaks_tail, idx_valid_bands, x_range)

    # Plot the detected bands on the image
    fig, axs = plt.subplots(1, 1)
    axs.imshow(data_ivrt)
    axs.set_ylim([0, data.shape[0]])
    axr = axs.twinx()
    ylim_ = axr.get_ylim()
    for iband in idx_valid_bands:
        axr.fill_between(
            x_range[peaks_tail[iband] : peaks_tail[iband + 1]],
            0,
            data_cum_bsln[peaks_tail[iband] : peaks_tail[iband + 1]],
            alpha=0.5,
        )
        axr.text(
            peaks_tail[iband],
            np.min(ylim_) - (np.max(ylim_) - np.min(ylim_)) * 0.05,
            str(iband + 1),
        )

    axs.set_title("WB raw image")
    axs.set_ylabel("Height pixels")
    axs.set_xlabel("Width pixels")
    axr.set_ylabel("Integrated intensity")

    # Return area values and the plotted figure
    return area_values, fig