# Biometric Source Scanner Identification for Secure Authentication

This repository implements an end-to-end secure fingerprint-based authentication system using an R307 fingerprint scanner, Raspberry Pi, deep learning, and a custom cryptographic client-server protocol.

The project combines biometric verification, machine-learning-based fingerprint classification, and secure socket communication to demonstrate a robust multi-factor authentication workflow.

## System Overview

The system operates in four major stages:

### Fingerprint Acquisition

- Fingerprint images are captured from an R307 sensor connected to a Raspberry Pi via UART.

### Model Training & Selection

- Extracted fingerprint images are used to train multiple classification models.
- The best-performing model is saved and used during authentication.

### Secure Client-Server Communication

A socket-based protocol securely transmits fingerprint data from client to server using:

- Hash-based integrity checks
- Timestamp validation (replay attack prevention)
- Symmetric encryption

### Biometric Authentication
The server verifies:

- Fingerprint similarity (feature-based matching)
- Biometric Scanner
- Cryptographic validation (Authentication using Hashed Username and Password)

## Repository Structure

```bash
.
├── Image_Download.py
├── Binary_Biometric_model.ipynb
├── client.py
├── server.py
├── fingerprint_check.py
├── OnevAll-95%.h5
├── User.txt
├── details.txt
└── README.md
```

## File Descriptions

### Image_Download.py

Purpose:
- Captures and stores raw fingerprint images from the R307 fingerprint sensor connected to a Raspberry Pi 3 via UART.

Key Features:

- Uses pyfingerprint library

- Continuously listens for fingerprint input

- Saves images as .bmp files for dataset creation

- Supports organizing images by sensor or user

### Binary_Biometric_model.ipynb

Purpose:
- End-to-end notebook for data preprocessing, model training, evaluation, and export.

Workflow:

- Loads fingerprint images

- Performs preprocessing and resizing

- Trains multiple binary classification models

- Evaluates performance metrics

- Saves the best model as a .h5 file


### client.py

Purpose:
- Acts as the biometric client running on the Raspberry Pi.

Responsibilities:

- Captures fingerprint image from R307 sensor

- Encodes image using Base64

Generates:

- SHA-256 integrity hash

- Timestamps

- Encrypts payload using Fernet symmetric encryption

- Sends fingerprint securely to the server

- Displays authentication result via GUI popup

Security Highlights:

- Prevents replay attacks (timestamp checks)

- Encrypted socket communication

- Multi-step verification logic


### server.py

Purpose:
- Acts as the authentication server responsible for biometric verification.

Responsibilities:

- Receives encrypted fingerprint payload

- Verifies hash integrity & timestamps

- Decodes fingerprint image

- Compares Fingerprint image with database for authentication

- Runs Fingerprint image through the trained model for Biometric Source Scanner Identification

Performs:

- Feature-based fingerprint matching

- Deep learning-based scanner classification

- Generates session keys

- Sends authentication decision back to client

Machine Learning:

- Loads trained .h5 model

- Predicts scanner validity

- Uses threshold-based binary classification

### fingerprint_check.py

Purpose:
- Performs traditional fingerprint feature matching between two images.

Techniques Used:

- CLAHE contrast enhancement

- Skeletonization & thinning

- Harris corner detection

- ORB feature extraction

- Brute-Force Hamming matching

Outcome:

- Determines whether two fingerprints match based on a distance threshold

## Authentication Flow

```bash
Fingerprint Capture (Client)
        ↓
Image Encryption + Hashing
        ↓
Secure Socket Transmission
        ↓
Server Verification
  ├─ Hash Validation
  ├─ Timestamp Check
  ├─ Feature Matching
  └─ DL Classification
        ↓
Authentication Decision
        ↓
Encrypted Response to Client
```

## Tech Stack

- Hardware: Raspberry Pi 3, R307 Fingerprint Sensor

- Languages: Python

- Libraries:

    - OpenCV

    - TensorFlow / Keras

    - NumPy, PIL

    - PyFingerprint

    - Cryptography (Fernet)

    - Socket Programming

- Model: Binary CNN classifier (.h5)

- Security: SHA-256 hashing, symmetric encryption, timestamps


## How to Run
### Hardware Setup

- Connect R307 sensor to Raspberry Pi UART pins

- Enable UART on Raspberry Pi

### Install Dependencies
```python
pip install pyfingerprint opencv-python tensorflow cryptography pillow numpy
```

### Capture Fingerprint Dataset
```python
python Image_Download.py
```

### Train the Model

Open and run:

Binary_Biometric_model.ipynb

### Start the Server
```python
python server.py
```

### Run the Client
```python
python client.py
```

## Key Highlights

- Combines biometrics + cryptography + DL

- Protects against replay & tampering attacks

- Modular design (easy to extend)

- Suitable for academic research, patents, and real-world demos
