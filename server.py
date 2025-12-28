import socket
import numpy as np
import json
import base64
import hashlib
from datetime import datetime
from PIL import Image
from keras.models import load_model
import io
import tensorflow as tf
from cryptography.fernet import Fernet
import subprocess
import re


model = load_model('OnevAll-95%.h5')

def generate_hash(message):
    client_id=message["client_id"]
    server_id=message["server_id"]
    timestamp=message["timestamp"]
    image_data=message["image"]
    key=message["Shared_key"]
    concatenated_string = f"{client_id}{server_id}{timestamp}{image_data}{key}"
    hash_object = hashlib.sha256(concatenated_string.encode('utf-8'))
    return hash_object.hexdigest()

def generate_sec(password,secret):
    concatenated_string = f"{password}{secret}"
    hash_object = hashlib.sha256(concatenated_string.encode('utf-8'))
    return hash_object.hexdigest()

def generate_shared_key(sec_verify,timestamp,s_timestamp):
    concatenated_string = f"{sec_verify}{timestamp}{s_timestamp}"
    hash_object = hashlib.sha256(concatenated_string.encode('utf-8'))
    return hash_object.hexdigest()

def predict_image(image):
    image = image.convert('RGB')
    
    image = image.resize((256, 288))
    
    image_array = np.array(image)

    image_array = np.expand_dims(image_array, axis=0)
    
    prediction = model.predict(image_array)

    print(prediction)
    return (prediction[0][0] >= 0.5).astype(int)

def handle_client_connection(client_socket):
    session_key = b'1R3I81T6niWuWOdoFW2aMrhhgFsqCL4Kp5PASZS4rhY='
    cipher=Fernet(session_key)
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
        with open('User.txt', 'r') as file:
            content = file.read()

            client_match = re.search(r'client_id:\s*([^\s]+)', content)
            server_match = re.search(r'server_id:\s*([^\s]+)', content)
            password_match = re.search(r'password_hash:\s*([^\s]+)', content)
            secret_match = re.search(r'secret_hash:\s*([^\s]+)', content)

            if client_match:
                s_client_id = client_match.group(1)
            if server_match:
                s_server_id = server_match.group(1) 
            if password_match:
                password = password_match.group(1)
            if secret_match:
                secret = secret_match.group(1)

        s_timestamp = datetime.now().isoformat()
        client_id=payload["client_id"]
        server_id=payload["server_id"]
        timestamp=payload["timestamp"]
        image_data = payload['image']
        rec_Hsig=payload["Hsig"]
        hash_payload = {
        'client_id': client_id,
        'server_id': server_id,
        'timestamp': timestamp,
        'image': image_data,
        'Shared_key': session_key
        }
        Hsig=generate_hash(hash_payload)

        if client_id==s_client_id and server_id==s_server_id and rec_Hsig==Hsig:
            timestamp_ = datetime.fromisoformat(timestamp)
            timestamp1 = datetime.fromisoformat(s_timestamp)
            time_difference = abs((timestamp_ - timestamp1).total_seconds())
            if time_difference > 20:
                return

            
            image = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image))
            image.save('image.bmp')
            command = ['python', 'fingerprint_check.py', 'original.bmp', 'image.bmp']
            result = subprocess.run(command, capture_output=True, text=True)
            print("Output:", result.stdout)

            sec_verify = generate_sec(password,secret)
            print("sec verify = ", sec_verify)
            
            new_time = datetime.now().isoformat()
            K_session = generate_shared_key(sec_verify,timestamp,new_time)
            print("session key = ",K_session)
            
            if (result.stdout.strip())=="Fingerprint matches":
                class_label = predict_image(image)
                if class_label == 1:
                    payload = {
                    'client_id': s_client_id,
                    'server_id': s_server_id,
                    'timestamp': new_time,
                    'Hs':secret,
                    'Hsig': Hsig
                    }
                    message = json.dumps(payload)
                    message = cipher.encrypt(message.encode('utf-8'))
                    message_length = str(len(message)).encode('utf-8').ljust(8)
                    client_socket.send(message_length+message)
                    print("Message Sent")
                else:
                    payload = {
                    'client_id': s_client_id,
                    'server_id': s_server_id,
                    'timestamp': new_time,
                    'label':str(class_label),
                    'Hsig': Hsig
                    }
                    message = json.dumps(payload)
                    message = cipher.encrypt(message.encode('utf-8'))
                    message_length = str(len(message)).encode('utf-8').ljust(8)
                    client_socket.send(message_length+message)
                    print("Auth Success - Message Sent")
            else:
                payload = {
                    'client_id': s_client_id,
                    'server_id': s_server_id,
                    'timestamp': new_time,
                    'label':str(-1),
                    'Hsig': Hsig
                }
                message = json.dumps(payload)
                message = cipher.encrypt(message.encode('utf-8'))
                message_length = str(len(message)).encode('utf-8').ljust(8)
                client_socket.send(message_length+message)
                print("Auth Failed - Message Sent")
    except Exception as e:
        print(f'Error handling client connection: {e}')
    finally:
        client_socket.close()

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8080))
    server.listen(5)
    print("Server is listening on port 8080...")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        handle_client_connection(client_socket)
