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
- Cryptographic validation (Authentication using Username and Password)
