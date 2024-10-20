import gpiod
import time
import subprocess

# GLOBAL DEFINES
# operating mode
OP_MODE = 1 # 1 = process and send GIF | 0 = just send the .bin file

# sampling parameters
filename = '/home/flynnmkelly/Desktop/Testbed/latestRec.bin'
frequency = '202.928e6'
numSamples = '20480000' # 10sec -- 40,096,000 = 20 seconds
sampleRate = '2048000'

# processing file location
RDMfilePath = '/home/flynnmkelly/Desktop/Testbed/RDMgen.py'

# NETWORKIGN STUFF
import socket
# IP of the higher-level computer (UQ)
host = '10.89.118.72'  
# host = '192.168.4.28' # IP of CARMODY
port = 5001 # CARMODY CONNECTION PORT
file_path = '/home/flynnmkelly/Desktop/Testbed/LatestBinRecording.gif'  # Path to the GIF file to send

# buttons
BUTTON_PIN = 4  # GPIO pin connected to the pushbutton - sampling exe
LED_PIN = 17    # GPIO pin connected to the LED

DSP_BUTTON_PIN = 18 # GPIO for DSP
DSP_LED_PIN = 23 


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


# Command to run
command = ['rtl_sdr', '-s', sampleRate, '-f', frequency, '-n', numSamples, filename]

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
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print("Command executed: ", ' '.join(command))
                    command_executed = True  # Mark command as executed
                except Exception as e:
                    print(f"Error executing command: {e}")

        # If the main button is not pressed
        elif button_state == 1:
            if command_executed:
                led_state = False  # Turn off the main LED
                led_line.set_value(int(led_state))  # Set main LED state

                # Terminate the rtl_sdr process if it's running
                if process:
                    process.terminate()  # Gracefully terminate the process
                    process = None  # Reset the process reference

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

