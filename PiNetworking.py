## RECEIVING A FILE
import socket
import os

host = ""  # Listen on all available interfaces
# port = 6000  # Same port as the client UQ
port = 5001  # Same port as the client CARMODY
OP_MODE = 0  # 1 for GIF, 0 for BIN

s = socket.socket()
s.bind((host, port))
s.listen()

print("Server started. Waiting for connection...")
c, addr = s.accept()  # Accept the incoming connection
print("Connection from:", addr)

print("Current working directory:", os.getcwd())

# Path to save the received file
gif_output_file_path = '/Users/flynnmkelly/Desktop/Thesis/PassiveRadarThesis/received_sample_file.gif'
bin_output_file_path = '/Users/flynnmkelly/Desktop/Thesis/PassiveRadarThesis/received_sample_file.bin'

# Choose the correct output file path based on the operation mode
if OP_MODE == 1:
    output_file_path = gif_output_file_path
    print("Operating in GIF mode. Saving as:", output_file_path)
elif OP_MODE == 0:
    output_file_path = bin_output_file_path
    print("Operating in BIN mode. Saving as:", output_file_path)
else:
    print("Invalid OP_MODE. Please set OP_MODE to 1 for GIF or 2 for BIN.")
    c.close()
    s.close()
    exit(1)

try:
    with open(output_file_path, 'wb') as file:
        print("Receiving file from Rpi5 Client...")
        while True:
            data = c.recv(1024)  # Receive in chunks
            if not data:
                break  # No more data, transfer complete
            file.write(data)  # Write the chunk to the file
        print("File received successfully and saved as", output_file_path)
finally:
    c.close()  # Close the client connection
    s.close()  # Close the server socket
