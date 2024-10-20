import socket

# IP of the higher-level computer (UQ)
host = '10.89.118.72'  
#host = '192.168.4.28' #at CARMODY Connection
# port number to connect to
# port = 6000 # UQ CONNECtiON PORT
port = 5001 # CARMODY CONNECTION PORT

# Path to the GIF file you want to send
file_path = 'LatestBinRecording.gif'

# Create a socket object
s = socket.socket()
s.connect((host, port))  # Connect to the server
print("Connected to", host)

try:
    # Open the GIF file in binary mode
    with open(file_path, 'rb') as file:
        print("Sending .gif file...")
        chunk = file.read(1024)  # Read in chunks of 1024 bytes
        while chunk:
            s.send(chunk)  # Send each chunk
            chunk = file.read(1024)  # Read the next chunk
        print("File sent successfully.")
except FileNotFoundError:
    print(f"File {file_path} not found.")
except Exception as e:
    print(f"Error: {e}")
finally:
    s.close()  # Close the socket connection
