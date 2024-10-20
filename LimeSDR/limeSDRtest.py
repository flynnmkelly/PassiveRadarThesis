import numpy as np
import os
import scipy
from matplotlib import pyplot as plt
import SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CS16

# ########################################################################################
# # Settings
# ########################################################################################
# # Data transfer settings
# rx_chan = 0               # RX1 = 0, RX2 = 1 - Using the RX1 Wideband
#                # Number of complex samples per transfer
# fs = 2000000             # Radio sample Rate
# N = fs * 15  
# freq = 202.928e6              # LO tuning frequency in Hz freq = 177.5e6- DAB 9A --> DVB-T = 177.5e6
# #req = 177.5e6
# use_agc = False         # Use or don't use the AGC
# timeout_us = int(5e6)

# # Recording Settings
# cplx_samples_per_file = N  # Complex samples per file
# nfiles = 1              # Number of files to record
# rec_dir = '/Users/flynnmkelly/Desktop/Thesis/PassiveRadarThesis/LimeSDR'  # Location of drive for recording
# file_prefix = 'Lime_2Ms_Flight3'   # File prefix for each file


# ########################################################################################
# # Receive Signal
# ########################################################################################
# # File calculations and checks
# cplx_samples_per_file = N   # Use entire buffer size for one file
# real_samples_per_file = 2 * cplx_samples_per_file

# # Initialize the LimeSDR receiver
# sdr = SoapySDR.Device(dict(driver="lime"))
# print(sdr.listSensors())  # Print sensor information

# sdr.setSampleRate(SOAPY_SDR_RX, 0, fs)          # Set sample rate
# # Set gain mode to manual since AGC is not supported
# sdr.setGainMode(SOAPY_SDR_RX, 0, use_agc)  # Set to False to use manual gain
# # SET THE GAIN HERE
# lna_gain = 30  # Adjust this value based on your signal strength
# sdr.setGain(SOAPY_SDR_RX, 0, "LNA", lna_gain)  # Set the gain for the selected channel
# # SET THE GAIN HERE
# lna_gain = 30  # Adjust this value based on your signal strength
# sdr.setGain(SOAPY_SDR_RX, 0, "LNA", lna_gain)  # Set the gain for the selected channel
# pga_gain = 20
# sdr.setGain(SOAPY_SDR_RX, 0, "PGA", pga_gain)
# tia_gain = 20
# sdr.setGain(SOAPY_SDR_RX, 0, "TIA", tia_gain)


# sdr.setFrequency(SOAPY_SDR_RX, 0, freq)         # Tune to DAB frequency


# print('Configuration complete')

# # Create data buffer and start streaming
# rx_buff = np.empty(2 * N, np.int16)  # Buffer for data
# rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, [rx_chan]) # Setup data stream
# sdr.activateStream(rx_stream)  # Start streaming

# print('Streaming started')

# # Record the data
# sr = sdr.readStream(rx_stream, [rx_buff], N, timeoutUs=timeout_us)
# rc = sr.ret
# assert rc == N, 'Error Reading Samples from Device (error code = %d)!' % rc

# # Save data to file
# file_name = os.path.join(rec_dir, '{}.bin'.format(file_prefix))
# rx_buff.tofile(file_name)

# print('Gets to end')

# # Stop streaming and close connection
# sdr.deactivateStream(rx_stream)
# sdr.closeStream(rx_stream)

# ########################################################################################
# # Plot Power Spectral Density (PSD)
# ########################################################################################
# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.signal import welch

# # Helper Function (reads in complex 16-bit IQ data)
# def read_complex_int16(filename, MAX_SAMPLES=-1):
#     # Load SDR data from a 16-bit I/Q file
#     # Normalise the data to [-1, 1] and return as a complex array
#     data = np.fromfile(filename, dtype=np.dtype('<h'), count=MAX_SAMPLES*2)
    
#     # Normalize the data to [-1, 1]
#     normdata = data.astype(float) / 32768.0
    
#     # Convert to complex
#     complex_data = normdata[::2] + 1j * normdata[1::2]
    
#     return complex_data

##################################

# Main Code to Read Data and Plot PSD
file_name = 'LimeSampleFile.bin'  # Specify your file name here
fs = 2.048e6  # Sampling frequency
center_freq = 202.928e6  # Center frequency of the signal

# IQ to Normalized Complex Data
def read_complex_int16(filename, MAX_SAMPLES=-1):
    # Load SDR data from a 16-bit I/Q file
    # Normalise the data to [-1, 1] and return as a complex array
    data = np.fromfile(filename, dtype=np.dtype('<h'), count=MAX_SAMPLES*2)
    # Normalize the data to [-1, 1]
    normdata = data.astype(float) / 32768.0
    # Convert to complex
    complex_data = normdata[::2] + 1j * normdata[1::2]
    return complex_data


# Read complex data from the file
complex_data = read_complex_int16(file_name)
print(complex_data)

def plot_psd(filename, sampling_rate, nperseg):
    # Read the binary file
    samples = read_complex_int16(filename)

    # Compute the Power Spectral Density using Welch's method
    frequencies, psd = welch(samples, fs=sampling_rate, nperseg=nperseg, return_onesided=False)


    frequencies_total = np.fft.fftshift(frequencies) + center_freq
    # frequencies_shifted = np.fft.fftshift(frequencies)
    psd_shifted = np.fft.fftshift(20*np.log10(psd))

    plt.plot(frequencies_total, psd_shifted)  # Frequencies in MHz
    
    plt.title('Power Spectral Density of Sampled Signal (DAB 9A)')
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Power[dB]')
    plt.grid(True)
    plt.show()

# Plot the PSD 
plot_psd(file_name, fs, 2048)

# # Compute the power spectral density
# f, Pxx = welch(complex_data, fs, nperseg=2048)

# # Shift the frequency axis
# f_shifted = f + center_freq

# # Plot PSD
# plt.figure(figsize=(12, 6))
# plt.semilogy(f_shifted, (20*np.log10(Pxx)))
# plt.title('Power Spectral Density of the DAB Signal')
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Power dB')
# plt.grid(True)

# # Set x-axis limits to show the full spectrum around the center frequency
# plt.xlim(center_freq - 2e6, center_freq + 2e6)

# # Format x-axis ticks to show MHz instead of Hz
# plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x/1e6:.3f}"))
# plt.xlabel('Frequency (MHz)')

# plt.show()



    
# Plot the RAW IQ data from the file
# plt.figure()
# plt.plot(complex_data[0:100].real)
# plt.title("Raw IQ Data")
# plt.show()


    



