
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import imageio


def create_windows(data, window_size, overlap_size):
    step_size = window_size - overlap_size
    num_windows = (len(data) - overlap_size) // step_size
    windows = np.array([
        data[i * step_size: i * step_size + window_size]
        for i in range(num_windows)
    ])
    return windows

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

# Load data
filename = 'Lime_2Ms_Flight1.bin' # target?
GIFsaveName = 'Flight1_2_MSs.gif'
window_size = 500000  # 500k samples
overlap_fraction = 0.16  # 20% overlap-
overlap_size = int(window_size * overlap_fraction)

# Read the normalized complex data
data = read_complex_int16(filename)

# Create the overlapping windows - based on overlap size
windows = create_windows(data, window_size, overlap_size)

nn = windows[0] #default set to first window
 
bs = 256  # batch size
## OVERLAP NEEDS TO BE DIFFERENT FOR DIFFERENT SAMPLE DATE
overlap = 200  # corresponds to maximum timeshift - TRUNCATION VALUE 
# 128 samples delay at 2.048 MHz is 62.5us -> distance of 18.75km
nbatches = int(np.floor((len(nn)-overlap)/bs))
# Now can process 'windows' which is an array of data windows
print("Number of windows:", len(windows))

# Other variables defined in the data import section ^^
N = window_size #500k samples
fs = 2e6 # Sampling rate - LIMESDR
t = np.arange(N) / fs # Time vector

fig, ax = plt.subplots()  # Set up the plotting figure and axis
images = []  # List to store each image plot

# Process each window and create plot data
for i, nn in enumerate(windows[0:10]):

    fig = Figure(figsize=(8, 6))  # Adjust size as needed
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)

    fmap = np.arange(-(bs * 0.3), bs * 0.3, 1)
    rdmapX = np.zeros((len(fmap), len(nn)), dtype=complex)
    nn2F = np.conj(np.fft.fft(nn))

    for fi, f in enumerate(fmap):
        nnf = nn * np.exp(1j * 2 * np.pi * -f * t)
        rdmapX[fi, :] = np.fft.ifft(np.fft.fft(nnf) * nn2F)

    rdmapXTRUNC = np.abs(rdmapX[:, 1:overlap])
    print(f"Truncated Range Doppler Data: {rdmapXTRUNC[:, 1:5]}")
    
    ## DATA STUFFFF
    #Skip the zero range column - SHOW LOG10 of data np.log10
    image = ax.imshow(np.log10(rdmapXTRUNC), extent=[0, overlap, np.min(fmap), np.max(fmap)], aspect='auto')
    ax.set_xlabel('Range (samples)')
    ax.set_ylabel('Doppler (Hz)')
    ax.set_title(f"Window {i+1}")

    # Convert plot to image
    canvas.draw()
    image = np.frombuffer(canvas.buffer_rgba(), dtype='uint8')
    image = image.reshape(canvas.get_width_height()[::-1] + (4,))
    
    # Convert RGBA to RGB
    image_rgb = image[:, :, :3]
    
    images.append(image_rgb)
    
    print(f"Processed window {i+1} of {len(windows)}")

    plt.close(fig)  # Close the figure to free up memory

# Set up animation
# Save as a Gif
imageio.mimsave(GIFsaveName, images, fps=5) 



