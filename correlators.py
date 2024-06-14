# correlations
import numpy as np
import pandas as pd

from scipy.interpolate import interp1d
import statsmodels.api as sm
from scipy.stats import pearsonr, spearmanr
# (1) pd.Series(data1).rolling(window=winsize).corr(pd.Series(data2))
def corr_pd_roll(x,y,window=3):
    """
    winsize = 10
    series_1 = pd.Series(res_spin.spin["freq"])
    series_2 = pd.Series(res_spin.spin["pk2pk"])
    # Compute the rolling correlation coefficient
    rolling_correlation = corr_pd_roll(series_1, series_2,window=winsize)
    Returns:
        rolling_correlation
    """
    # pd.Series() data1 and data2 
    series_1 = pd.Series(x)
    series_2 = pd.Series(y)
    # Compute the rolling correlation coefficient
    rolling_correlation = series_1.rolling(window=window).corr(series_2)
    print(f" corr_pd_roll correlation to check similarity, \nwindow is {window}, cannot be 1")
    return rolling_correlation
# Sliding window: a sliding window with incremental updates. This method is computationally 
# efficient compared to recalculating the correlation coefficient for each window.
def corr_sliding_window(x, y, window=1):
    """
    corr_sliding_window a sliding window with incremental updates. 
    This method is computationally efficient compared to recalculating 
    the correlation coefficient for each window.

    series_1 = pd.Series(res_spin.spin["freq"])
    series_2 = pd.Series(res_spin.spin["pk2pk"])
    sliding_corr=corr_sliding_window(series_1, series_2, window=3)
    Returns:
        sliding_corr: r values
    """
    # Initialize variables
    n = len(x)
    sum_x = np.sum(x[:window])
    sum_y = np.sum(y[:window])
    sum_xy = np.sum(x[:window] * y[:window])
    sum_x_sq = np.sum(x[:window] ** 2)
    sum_y_sq = np.sum(y[:window] ** 2)

    # Compute the initial correlation coefficient
    corr = [
        (n * sum_xy - sum_x * sum_y)
        / np.sqrt((n * sum_x_sq - sum_x**2) * (n * sum_y_sq - sum_y**2))
    ]

    # Update correlation coefficient for each subsequent window
    for i in range(1, n - window + 1):
        sum_x += x[i + window - 1] - x[i - 1]
        sum_y += y[i + window - 1] - y[i - 1]
        sum_xy += np.dot(x[i : i + window], y[i : i + window]) - np.dot(
            x[i - 1 : i + window - 1], y[i - 1 : i + window - 1]
        )
        sum_x_sq += np.sum(x[i : i + window] ** 2) - np.sum(
            x[i - 1 : i + window - 1] ** 2
        )
        sum_y_sq += np.sum(y[i : i + window] ** 2) - np.sum(
            y[i - 1 : i + window - 1] ** 2
        )

        # Compute the correlation coefficient for the current window
        corr.append(
            (window * sum_xy - sum_x * sum_y)
            / np.sqrt(
                (window * sum_x_sq - sum_x**2)
                * (window * sum_y_sq - sum_y**2)
            )
        )

    return np.array(corr)


# Fourier Transform for correlation analysis
# Compute the cross-power spectral density (CPSD) between the two time series.
# Compute the power spectral density (PSD) of each time series separately.
# Divide the CPSD by the square root of the product of the individual PSDs to obtain the cross-correlation function.
# Apply the inverse Fourier Transform to obtain the correlation coefficient as a function of time.
def corr_fft(x, y):
    """
    corr_fft _summary_

    Args:
        x (_type_): _description_
        y (_type_): _description_
    series_1 = pd.Series(res_spin.spin["freq"])
    series_2 = pd.Series(res_spin.spin["pk2pk"])
    r=corr_fft(series_1, series_2)
    Returns:
        r: r values
    """
    # Compute FFT of each time series
    fft_x = np.fft.fft(x)
    fft_y = np.fft.fft(y)

    # Compute cross-power spectral density
    cpsd = fft_x * np.conj(fft_y)

    # Compute power spectral density of each time series
    psd_x = np.abs(fft_x) ** 2
    psd_y = np.abs(fft_y) ** 2

    # Compute cross-correlation function
    cross_corr = np.fft.ifft(cpsd / np.sqrt(psd_x * psd_y))
    return cross_corr.real

# Exponentially Weighted Moving Average (EWMA)
# You can use exponentially weighted moving average to compute the correlation coefficient continuously over time. This method assigns exponentially decreasing weights
# to the past observations, giving more weight to recent observations. Here's an example of how you can implement it:
def corr_ewma(x, y, smth=0.1):  # alpha is the smth factor
    """
    smth = 0.1  # default
    # Compute the EWMA correlation coefficient
    series_1 = pd.Series(res_spin.spin["freq"])
    series_2 = pd.Series(res_spin.spin["pk2pk"])
    ewma_correlation = corr_ewma(series_1, series_2, smth=smth)

    Args:
        x (_type_): data1
        y (_type_): data2
        smth (float, optional): alpha is the smth factor. Defaults to 0.1.

    Returns:
        ewma_correlation: r values
    """
    corr = []
    corr.append(np.corrcoef(x, y)[0, 1])
    for i in range(1, len(x)):
        corr.append(
            smth * np.corrcoef(x[: i + 1], y[: i + 1])[0, 1] + (1 - smth) * corr[i - 1]
        )
    return np.array(corr)

# Recursive Formulas
# where each new value is computed based on the previous one. This method is similar to 
# rolling window functions but calculates each new value efficiently without re-computing 
# the entire window.
def corr_recursive(x, y):
    corr = []
    corr.append(np.corrcoef(x[:2], y[:2])[0, 1])
    for i in range(2, len(x)):
        corr.append(
            (i - 1) / i * corr[-1] + 1 / i * np.corrcoef(x[: i + 1], y[: i + 1])[0, 1]
        )
    return np.array(corr)

# adaptive or online algorithm
# One such algorithm is the Online Pearson Correlation Coefficient algorithm, which updates the correlation coefficient as new data points become available without the need for storing or reprocessing past data.
class ContinuousOnlinePearsonCorrelation:
    """ 
    x = pd.Series(res_spin.spin["freq"])
    y = pd.Series(res_spin.spin["pk2pk"])

    # Initialize ContinuousOnlinePearsonCorrelation
    continuous_online_corr = ContinuousOnlinePearsonCorrelation()
    for i, j in zip(x, y):
        continuous_online_corr.update(i, j)

    print("Continuous correlation coefficients:")
    print(continuous_online_corr.correlation_values[:10])
    """
    def __init__(self):
        self.n = 0
        self.mean_x = 0
        self.mean_y = 0
        self.m2_x = 0
        self.m2_y = 0
        self.cov_xy = 0
        self.correlation_values = []

    def update(self, x, y):
        self.n += 1
        delta_x = x - self.mean_x
        delta_y = y - self.mean_y
        self.mean_x += delta_x / self.n
        self.mean_y += delta_y / self.n
        delta2_x = x - self.mean_x
        delta2_y = y - self.mean_y
        self.m2_x += delta_x * delta2_x
        self.m2_y += delta_y * delta2_y
        self.cov_xy += delta_x * delta_y * (self.n - 1) / self.n
        if self.m2_x > 0 and self.m2_y > 0:
            correlation = self.cov_xy / (self.m2_x**0.5 * self.m2_y**0.5)
            self.correlation_values.append(correlation)


"""
# what if the two data series with different sample rate. how to do the correlation?

If the two data series have different sample rates, you can still compute the correlation between them. However, you need to ensure that they are synchronized or resampled to a common time grid before calculating the correlation.

general approach to handle data series with different sample rates:

(1) Resample both data series to a common time grid using interpolation or other resampling techniques.

(2) Compute the correlation between the resampled data series.

example:
    series_1 = pd.Series(res_spin.spin["freq"])
    series_2 = pd.Series(res_spin.spin["pk2pk"])
    series_3 = resample_data(res_spin.spin["freq"], 1000, 12)
    series_3 = pd.Series(series_3)
    series_4 = resample_data(res_spin.spin["pk2pk"], 1000, 12)
    series_4 = pd.Series(series_4)
    window_size = 10
    resample_sliding_corr = sliding_window_corr(series_3, series_4, window_size)
"""

def corr_interp_sliding(
    x, y, x_timestamps, y_timestamps, window_size
):
    """
    Using interpolation to align timestamps followed by sliding window computation of the correlation coefficient

    Args:
        x (np.array): _description_
        y (_type_): _description_
        x_timestamps (int): _description_
        y_timestamps (int): _description_
        window_size (int): sliding window
    # Example data
        x = np.random.randn(10000)  # sampled at 1000 Hz
        y = np.random.randn(120)  # sampled at 12 Hz

        x_timestamps = np.linspace(0, 10, 10000)  # EEG timestamps
        y_timestamps = np.linspace(0, 10, 120)  # Glucose timestamps

        # Set the window size for sliding window correlation computation
        window_size = 100  # Adjust according to your needs

        # Compute continuous correlation coefficients using interpolation and sliding window
        continuous_correlation = corr_interp_sliding(
            x, y, x_timestamps, y_timestamps, window_size
        )

        print("Continuous correlation coefficients:")
        print(continuous_correlation)
    Returns:
        continuous_correlation: r value
    """
    # Interpolate y data onto x timestamps
    interp_func = interp1d(y_timestamps, y, kind="linear", fill_value="extrapolate")
    y_interp = interp_func(x_timestamps)

    # Compute correlation coefficient using sliding window
    n = len(x)
    corr_values = []

    for i in range(n - window_size + 1):
        x_window = x[i : i + window_size]
        y_window = y_interp[i : i + window_size]

        # Calculate correlation coefficient for the current window
        correlation = np.corrcoef(x_window, y_window)[0, 1]
        corr_values.append(correlation)

    return np.array(corr_values)


"""
Autocorrelation is used in various fields and applications, including:

Time Series Analysis: Autocorrelation is fundamental in time series analysis 
for understanding the structure and patterns in sequential data. It helps identify 
seasonality, trends, and other repeating patterns within the data.

Modeling and Forecasting: Autocorrelation informs the selection of appropriate models 
for forecasting future values of a time series. Models such as autoregressive 
integrated moving average (ARIMA) and seasonal autoregressive integrated moving 
average (SARIMA) rely on autocorrelation patterns to capture dependencies between 
observations.

Quality Control: In manufacturing and process control, autocorrelation analysis 
is used to detect correlations between successive measurements. Deviations from 
expected autocorrelation patterns can indicate process instability or abnormalities.

Signal Processing: Autocorrelation is used in signal processing for tasks such as 
speech recognition, audio processing, and seismic analysis to analyze time-domain 
signals and extract useful information about signal characteristics.

Overall, autocorrelation provides valuable insights into the temporal dependencies
and behavior of time series data, enabling better understanding, modeling, and prediction 
of sequential phenomena.
"""
def autocorr_np(x, lag=1):
    """
    autocorr_np : use np.correlate(x)

    Args:
        x (_type_): _description_
        lag (_type_): _description_
    # Example data
        data = np.random.randn(100)

        # Compute autocorrelation at lag 1
        lag_1_autocorr = autocorr_np(data, 1)
        print("Autocorrelation at lag 1:", lag_1_autocorr)
    Returns:
        lag_corr: r value
    """
    n = len(x)
    mean = np.mean(x)
    var = np.var(x)
    x = x - mean
    lag_corr = np.correlate(x, x, mode="full") / (var * n)
    return lag_corr[n - 1 : n + lag]

def autocorr_pd(data,max_lag=10):
    """
    Compute autocorrelation of a 1D numpy array.

    Parameters:
    data (numpy.ndarray): 1D array containing the data.

    # Example data
        data_series = np.random.randn(100)
        autocorr_series = autocorr_pd(data_series)
        print("Autocorrelation:", autocorr_series)
    Returns:
    float: Autocorrelation value.
    """
    # Compute mean and centered data
    mean = np.mean(data)
    centered_data = data - mean
    
    # Compute autocovariance at lag 0
    auto_covariance_0 = np.mean(centered_data ** 2)
    
    # Compute autocorrelation values for a range of lags
    autocorr_values = np.zeros(max_lag + 1)
    for lag in range(max_lag + 1):
        if lag == 0:
            autocorr_values[lag] = 1.0
        else:
            auto_covariance_lag = np.mean(centered_data[:-lag] * centered_data[lag:])
            autocorr_values[lag] = auto_covariance_lag / auto_covariance_0
    
    return autocorr_values


def autocorr_statsmodels(data, nlags=1):
    """
    Compute autocorrelation of a 1D numpy array using StatsModels.

    Parameters:
        data (numpy.ndarray): 1D array containing the data.
        nlags (int): Number of lags for which to compute autocorrelation (default: 1).
    # Example data
        data_array = np.random.randn(100)
        autocorr_array = compute_autocorrelation(data_array, nlags=1)
        print("Autocorrelation at lag 1:", autocorr_array)
    Returns:
        autocorr_array(float): Autocorrelation value at the specified lag.
    """
    # Compute autocorrelation using StatsModels
    autocorr_result = sm.tsa.acf(data, nlags=nlags)

    return autocorr_result


"""
cross-correlation

Cross-correlation is a statistical method used to measure the similarity between two 
time series by comparing them at different time lags. Unlike autocorrelation, which 
measures the similarity of a time series with itself at different lags, cross-correlation 
measures the similarity between two different time series.

Cross-correlation has several applications, including:
Signal Processing: In signal processing, cross-correlation is used to detect similarities 
between different signals or to find the time delay between them. It is widely used in 
fields such as audio processing, radar signal processing, and image processing.

Time Series Analysis: Cross-correlation helps identify relationships and dependencies between
different time series data. It is used in fields such as economics, finance, and environmental 
science to analyze the interactions between various variables over time.

Pattern Recognition: Cross-correlation is used in pattern recognition tasks to match and 
compare patterns in different datasets. It is employed in fields such as speech recognition, 
pattern matching, and machine vision.
"""

def cross_corr_np(x, y,mode='same'):
    """
    cross_corr_np _summary_

    Args:
        x (_type_): _description_
        y (_type_): _description_
        mode: default 'same', returns the same lengh  "full",  in NumPy, setting the mode parameter to "full" returns the 
        cross-correlation of x and y at each position of their overlap, with the result 
        being twice the length of the original sequences minus 1.
    # Example data
    x = np.random.randn(100)
    y = np.random.randn(100) 
    cross_corr_values = cross_corr_np(x, y)
    print("Cross-correlation values:", cross_corr_values[:4])
    Returns:
        _type_: _description_
    """
    n = len(x)
    mean_x = np.mean(x)
    mean_y = np.mean(y)
    x = x - mean_x
    y = y - mean_y
    cross_corr_values = np.correlate(x, y, mode=mode) / (np.std(x) * np.std(y) * n)
    return cross_corr_values

def cross_corr_pd(x, y):
    """
    Compute cross-correlation coefficient between two pandas Series.
    Example:
    x=np.random.randn(100)
    y=np.random.randn(100)
    cross_corr_values = cross_corr_pd(x,y)
    print("Cross-correlation:", cross_corr_values)
    Returns:
    cross_corr_values(float): Cross-correlation coefficient between the two Series.
    """
    Series1=pd.Series(x)
    Series2=pd.Series(y)
    # Compute cross-correlation using pandas
    cross_corr_value = Series1.corr(Series2)
    
    return cross_corr_value

def cross_corr_scipy(x, y):
    from scipy.signal import correlate
    cross_corr_values = correlate(x, y)
    print("Cross-correlation values:", cross_corr_values[:4])
    return cross_corr_values

"""Autocorrelation is used in various fields and applications, including:

Time Series Analysis: Autocorrelation is fundamental in time series analysis for understanding the structure and patterns in sequential data. It helps identify seasonality, trends, and other repeating patterns within the data.

Modeling and Forecasting: Autocorrelation informs the selection of appropriate models for forecasting future values of a time series. Models such as autoregressive integrated moving average (ARIMA) and seasonal autoregressive integrated moving average (SARIMA) rely on autocorrelation patterns to capture dependencies between observations.

Quality Control: In manufacturing and process control, autocorrelation analysis is used to detect correlations between successive measurements. Deviations from expected autocorrelation patterns can indicate process instability or abnormalities.

Signal Processing: Autocorrelation is used in signal processing for tasks such as speech recognition, audio processing, and seismic analysis to analyze time-domain signals and extract useful information about signal characteristics.

Overall, autocorrelation provides valuable insights into the temporal dependencies and behavior of time series data, enabling better understanding, modeling, and prediction of sequential phenomena."""
def autocorr(x, lag):
    n = len(x)
    mean = np.mean(x)
    var = np.var(x)
    x = x - mean
    corr = np.correlate(x, x, mode="full") / (var * n)
    return corr[n - 1 : n + lag]

"""
General correlation
e.g., Pearson correlation or Spearman correlation
"""
def corr(x, y, method='pearson'):
    if method.lower() in ['pe','pear','pearson','peson','pearon']:
        r, p = pearsonr(x, y)
        print("Pearson correlation coefficient:", r)
        print("Pearson p-value:", p)
        return r,p
    elif method.lower() in ['spear','sp','spea','spearman','speaman']:
        r, p = spearmanr(x, y)
        print("Spearman correlation coefficient:", r)
        print("Spearman p-value:", p)
        return r,p
    else:
        print(f"{method} is not supported, do you mean 'pearson' or 'spearman'")
        return None, None