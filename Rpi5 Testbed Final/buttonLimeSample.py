import gpiod
import time
import subprocess
import numpy as np
import os
import scipy
from matplotlib import pyplot as plt
import SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CS16

# GLOBAL DEFINES
# operating mode
OP_MODE = 1 # 1 = process and send GIF 0 = just send the .bin file

# sampling parameters
filename = 'latestRec.bin'
frequency = 202.928e6
numSamples = 20480000 # 10sec -- 40,096,000 = 20 seconds
sampleRate = 2048000
N = sampleRate * 15  # how long to record for?

# processing file location
RDMfilePath = '/home/flynnmkelly/Desktop/Testbed/RDMgen.py'

# NETWORKIGN STUFF
import socket
# IP of the higher-level computer (UQ)
host = '10.89.118.72'  
port = 5001 # CARMODY CONNECTION PORT
file_path = 'LatestBinRecording.gif'  # Path to the GIF file to send

# buttons
BUTTON_PIN = 4  # GPIO pin connected to the pushbutton - sampling exe
LED_PIN = 17    # GPIO pin connected to the LED

DSP_BUTTON_PIN = 18 # GPIO for DSP
DSP_LED_PIN = 23 

# --------- LimeSDR Config Stuff ------------
rx_chan = 0               # RX1 = 0, RX2 = 1 - Using the RX1 Wideband
use_agc = False         # Use or don't use the AGC
timeout_us = int(5e6)

# Recording Settings
cplx_samples_per_file = N  # Complex samples per file
nfiles = 1              # Number of files to record
rec_dir = '/home/flynnmkelly/Desktop/Testbed'  # Location of drive for recording
file_prefix = filename   # File prefix for each file

# GAIN VALUES
lna_gain = 30  # Adjust this value based on your signal strength
pga_gain = 20
tia_gain = 20


# --------------------------------------------------------------------- #
# ACTUAL CODE

# Get a handle to the GPIO chip
chip = gpiod.Chip('gpiochip0')  # Adjust according to your chip number if needed

# Get line handles for our pins
button_line = chip.get_line(BUTTON_PIN)
led_line = chip.get_line(LED_PIN)

# DSP button and LED lines
dsp_button_line = chip.get_line(DSP_BUTTON_PIN)
dsp_led_line = chip.get_line(DSP_LED_PIN)

# Configure lines
button_line.request(consumer="button", type=gpiod.LINE_REQ_DIR_IN, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
led_line.request(consumer="led", type=gpiod.LINE_REQ_DIR_OUT)

# Configure DSP lines
dsp_button_line.request(consumer="dsp_button", type=gpiod.LINE_REQ_DIR_IN, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
dsp_led_line.request(consumer="dsp_led", type=gpiod.LINE_REQ_DIR_OUT)

# Initialize LED state and command execution state
led_state = False
led_line.set_value(int(led_state))

dsp_led_state = False
dsp_led_line.set_value(int(dsp_led_state))


# Variable to track the last button state and execution state
last_button_state = 1  # Assume button is released at start (1 means not pressed)
command_executed = False  # Flag to track if command has been executed

last_dsp_button_state = 1  # Assume DSP button is released at start
dsp_process = None  # Initialize the DSP process variable
dsp_command_executed = False  # Flag to track if DSP command has been executed


try:
    while True:

        # ---- Sample Button and LED Handling ----
               # Read the main button state
        button_state = button_line.get_value()

        # If the main button is pressed (0 for active low)
        if button_state == 0 and last_button_state == 1:  # Detecting a press
            if not command_executed:
                led_state = True  # Turn on the main LED
                led_line.set_value(int(led_state))  # Set main LED state
                
                # Execute the command
                try:
                    # ACTUALLY SAMPLE THE DATA
                    # File calculations and checks
                    cplx_samples_per_file = N   # Use entire buffer size for one file
                    real_samples_per_file = 2 * cplx_samples_per_file

                    # Initialize the LimeSDR receiver
                    sdr = SoapySDR.Device(dict(driver="lime"))
                    print(sdr.listSensors())  # Print sensor information

                    sdr.setSampleRate(SOAPY_SDR_RX, 0, sampleRate)          # Set sample rate
                    # Set gain mode to manual since AGC is not supported
                    sdr.setGainMode(SOAPY_SDR_RX, 0, use_agc)  # Set to False to use manual gain
                    sdr.setGain(SOAPY_SDR_RX, 0, "LNA", lna_gain)  # Set the gain 
                    sdr.setGain(SOAPY_SDR_RX, 0, "PGA", pga_gain)
                    sdr.setGain(SOAPY_SDR_RX, 0, "TIA", tia_gain)


                    sdr.setFrequency(SOAPY_SDR_RX, 0, frequency)         # Tune to DAB frequency


                    print('Configuration complete')

                    # Create data buffer and start streaming
                    rx_buff = np.empty(2 * N, np.int16)  # Buffer for data
                    rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, [rx_chan]) # Setup data stream
                    sdr.activateStream(rx_stream)  # Start streaming

                    print('Streaming started')

                    # Record the data
                    sr = sdr.readStream(rx_stream, [rx_buff], N, timeoutUs=timeout_us)
                    rc = sr.ret
                    assert rc == N, 'Error Reading Samples from Device (error code = %d)!' % rc

                    # Save data to file
                    file_name = os.path.join(rec_dir, '{}.bin'.format(file_prefix))
                    rx_buff.tofile(file_name)

                    print('Gets to end')

                    # Stop streaming and close connection
                    sdr.deactivateStream(rx_stream)
                    sdr.closeStream(rx_stream)
                    command_executed = True  # Mark command as executed
                    
                except Exception as e:
                    print(f"Error executing command: {e}")

        # If the main button is not pressed
        elif button_state == 1:
            if command_executed:
                led_state = False  # Turn off the main LED
                led_line.set_value(int(led_state))  # Set main LED state

                                    # Stop streaming and close connection
                sdr.deactivateStream(rx_stream)
                sdr.closeStream(rx_stream)

                command_executed = False  # Allow command to be executed again

        # Store the current main button state for the next loop iteration
        last_button_state = button_state

       # ---- DSP Button and LED Handling ----
        dsp_button_state = dsp_button_line.get_value()
        
        # Edge Processing Mode
        if OP_MODE == 1:
            if dsp_button_state == 0 and last_dsp_button_state == 1:
                print("DSP Button Latched")
                if not dsp_command_executed:
                    dsp_led_state = True
                    dsp_led_line.set_value(int(dsp_led_state))
                    dsp_command = ['python3', RDMfilePath]
                    
                    try:
                        dsp_process = subprocess.Popen(dsp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        print("DSP Command executed: ", ' '.join(dsp_command))
                        dsp_command_executed = True
                    except Exception as e:
                        print(f"Error executing DSP command: {e}")

            if dsp_process and dsp_process.poll() is not None:
                dsp_led_state = False
                dsp_led_line.set_value(int(dsp_led_state))
                dsp_process = None
                dsp_command_executed = False

                # After DSP process is complete, send the GIF file over the socket
                try:
                    with socket.socket() as s:
                        s.connect((host, port))
                        print("Connected to", host)

                        with open(file_path, 'rb') as file:
                            print("Sending .gif file...")
                            chunk = file.read(1024)
                            while chunk:
                                s.send(chunk)
                                chunk = file.read(1024)
                            print("File sent successfully.")
                except FileNotFoundError:
                    print(f"File {file_path} not found.")
                except Exception as e:
                    print(f"Error during file transmission: {e}")

            if dsp_button_state == 1 and last_dsp_button_state != 1:
                # print("DSP Button not latched")
                # dsp_led_state = False
                # dsp_led_line.set_value(int(dsp_led_state))
                if dsp_command_executed:
                    dsp_led_state = False  # Turn off the main LED
                    dsp_led_line.set_value(int(dsp_led_state))  # Set main LED state

                    # Terminate the rtl_sdr process if it's running
                    if dsp_process:
                        dsp_process.terminate()  # Gracefully terminate the process
                        dsp_process = None  # Reset the process reference

                    dsp_command_executed = False  # Allow command to be executed again

        # Just send the .bin File (no edge processing)
        if OP_MODE == 0:
            if dsp_button_state == 0 and last_dsp_button_state == 1:
                print("Just send the .bin file")
                dsp_led_state = True
                dsp_led_line.set_value(int(dsp_led_state))
                
                # After DSP process is complete, send the GIF file over the socket
                try:
                    with socket.socket() as s:
                        s.connect((host, port))
                        print("Connected to", host)

                        with open(filename, 'rb') as file:
                            print("Sending .bin file...")
                            chunk = file.read(1024)
                            while chunk:
                                s.send(chunk)
                                chunk = file.read(1024)
                            print("File sent successfully.")

                except FileNotFoundError:
                    print(f"File {file_path} not found.")
                except Exception as e:
                    print(f"Error during file transmission: {e}")

                dsp_led_state = False
                dsp_led_line.set_value(int(dsp_led_state))


            if dsp_button_state == 1 and last_dsp_button_state != 1:
                dsp_led_state = False  # Turn off the main LED
                dsp_led_line.set_value(int(dsp_led_state))  # Set main LED state


        last_dsp_button_state = dsp_button_state
        time.sleep(0.01)


except KeyboardInterrupt:
    # Cleanup GPIO on exit
    print("Exiting program...") # need to modify this
    if process:
        process.terminate()  # Terminate if running
finally:
    # Release GPIO lines
    button_line.release()
    led_line.release()
    dsp_button_line.release()
    dsp_led_line.release()

