import numpy as np


# Load SDR data from an RTLSDR (8-bit I/Q) file. Normalise the data to
# [-1, 1] and return as a complex array.
# To limit the amount of data loaded, specify MAX_SAMPLES
def read_complex_byte(filename, MAX_SAMPLES=-1):
    data = np.fromfile(filename, dtype=np.dtype('B'), count=MAX_SAMPLES)
    normdata = (np.array(data, dtype=float)-127)/128
    normdata.dtype = complex
    return normdata

def read_complex_int16(filename, MAX_SAMPLES=-1):
    # Load SDR data from a 16-bit I/Q file
    # Normalise the data to [-1, 1] and return as a complex array
    data = np.fromfile(filename, dtype=np.dtype('<h'), count=MAX_SAMPLES*2)
    
    # Normalize the data to [-1, 1]
    normdata = data.astype(float) / 32768.0
    
    # Convert to complex
    complex_data = normdata[::2] + 1j * normdata[1::2]
    
    return complex_data