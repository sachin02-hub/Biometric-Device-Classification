import socket
import hashlib
from PIL import Image
import io
import re
import tempfile
import json
import base64
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from pyfingerprint.pyfingerprint import PyFingerprint
import threading
from cryptography.fernet import Fernet


def generate_hash(message):
    client_id=message["client_id"]
    server_id=message["server_id"]
    timestamp=message["timestamp"]
    image_data=message["image"]
    key=message["Shared_key"]
    concatenated_string = f"{client_id}{server_id}{timestamp}{image_data}{key}"
    hash_object = hashlib.sha256(concatenated_string.encode('utf-8'))
    return hash_object.hexdigest()

def generate_timestamp():
    return datetime.now().isoformat()

def generate_session_key(sec_verify,timestamp,s_timestamp):
    concatenated_string = f"{sec_verify}{timestamp}{s_timestamp}"
    hash_object = hashlib.sha256(concatenated_string.encode('utf-8'))
    return hash_object.hexdigest()

def generate_sec(password,secret):
    concatenated_string = f"{password}{secret}"
    hash_object = hashlib.sha256(concatenated_string.encode('utf-8'))
    return hash_object.hexdigest()

def capture_fingerprint(f, image_event):
        try:
            print('Waiting for finger...')
            while not f.readImage():
                pass
            
            print('Downloading image...')
            image_destination = tempfile.gettempdir() + '/authenticator.bmp'
            f.downloadImage(image_destination)

            # Notify that a new image has been captured
            image_event.set()

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)

# Function to send image to server
def send_message_to_server(UID,SID,image_event,sec_verify):
        # Wait until a new image is captured
        image_event.wait()
        
        image_path = tempfile.gettempdir() + '/authenticator.bmp'
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('192.168.229.118', 8080))  # Update with the server's IP if remote
        session_key=b'1R3I81T6niWuWOdoFW2aMrhhgFsqCL4Kp5PASZS4rhY='
        cipher = Fernet(session_key)
        
        # Read the image using PIL
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        timestamp=generate_timestamp()
        hash_payload = {
        'client_id': UID,
        'server_id': SID,
        'timestamp': timestamp,
        'image': image_data,
        'Shared_key': session_key
        }
        Hsig=generate_hash(hash_payload)
        payload = {
        'client_id': UID,
        'server_id': SID,
        'timestamp': timestamp,
        'image': image_data,
        'Hsig': Hsig
        }
        message=json.dumps(payload)
        message = cipher.encrypt(message.encode('utf-8'))
        message_length = str(len(message)).encode('utf-8').ljust(8)
        client_socket.send(message_length + message)
        print("Message Sent")
        while True:
            try:
                message_length = client_socket.recv(8)
                if not message_length:
                    return
                
                message_length = int(message_length.strip())
                encrypted_message = b''
                while len(encrypted_message) < message_length:
                    chunk = client_socket.recv(message_length - len(encrypted_message))
                    if not chunk:
                        break
                    encrypted_message += chunk
                message = cipher.decrypt(encrypted_message).decode('utf-8')
                payload = json.loads(message)
                
                
                rec_client_id = payload["client_id"]
                rec_server_id = payload["server_id"]
                rec_timestamp = payload["timestamp"]
                new_time = datetime.now().isoformat()
                rec_Hsig = payload["Hsig"]
                
                if UID == rec_client_id and SID == rec_server_id:
                    timestamp_ = datetime.fromisoformat(rec_timestamp)
                    timestamp1 = datetime.fromisoformat(new_time)
                    time_difference = abs((timestamp_ - timestamp1).total_seconds())
                    if time_difference > 20:
                        return
                    if Hsig == rec_Hsig:
                        if 'label' in payload:
                            class_label = payload["label"]
                            if int(class_label) == -1:
                                show_popup("Unauthorized User")
                            else:
                                show_popup("Authentication Failed")
                        else:
                            if 'Hs' in payload:
                                Hs = payload["Hs"]
                                password=input("Enter your Password: ")
                                pass_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                                cal_sec_verify = generate_sec(pass_hash,Hs)
                                if cal_sec_verify == sec_verify:
                                    K_session = generate_session_key(sec_verify,timestamp,rec_timestamp)
                                    print("session key = ",K_session)
                                    show_popup("Authentication Successful")
            
            except Exception as e:
                print(f'Error handling client connection: {e}')
            finally:
                client_socket.close()
                image_event.clear()
                break


# Function to show popup with result
def show_popup(message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showinfo("Authentication Result", message)
    root.destroy()

# Main function
if __name__ == "__main__":
    try:
        f = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)

        if not f.verifyPassword():
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

    print('Currently used templates: ' + str(f.getTemplateCount()) + '/' + str(f.getStorageCapacity()))

    # Create an event to notify when a fingerprint is captured
    image_event = threading.Event()

    # Start the fingerprint capture in a separate thread
    capture_thread = threading.Thread(target=capture_fingerprint, args=(f, image_event))
    capture_thread.daemon = True
    capture_thread.start()
    
    with open('details.txt', 'r') as file:
            content = file.read()

            client_match = re.search(r'client_id:\s*([^\s]+)', content)
            server_match = re.search(r'server_id:\s*([^\s]+)', content)
            secret_match = re.search(r'sec:\s*([^\s]+)', content)

            if client_match:
                UID = client_match.group(1)
            if server_match:
                SID = server_match.group(1)
            if secret_match:
                sec_verify = secret_match.group(1)
    send_message_to_server(UID,SID,image_event,sec_verify)