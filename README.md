# P2P Secure Share

A peer-to-peer (P2P) secure file-sharing web application designed to bring authentication, control, and clarity to traditional P2P systems.

## Overview

P2P Secure Share eliminates the limitations of traditional P2P apps by providing authenticated file sharing, request-based transfer, and peer communication—ensuring security and user control.

## Key Features

- **User Registration & Authentication**: Only authenticated users can join the network.
- **Peer File Requests**: Users can request files; transfers occur only after approval.
- **Chat Functionality**: Communicate with peers to clarify requests, download status, or request alternate files.
- **Controlled Sharing**: File sharing is manual and based on request/approval flow.
- **File Transfer**: Securely share and download files post-authentication and approval.

## Tech Stack

- **Backend**: Django (Python)  
  Follows Model-View-Template (MVT) architecture
- **Socket Programming**: Real-time peer communication and file transfer
- **Version Control**: Git

## Why P2P Secure Share?

Traditional P2P apps like uTorrent suffer from:

- Limited authentication
- No control over who accesses what
- Risk of bundled or malicious downloads

P2P Secure Share addresses these by:

- Introducing login authentication
- Allowing peer-based file request approvals
- Adding in-built chat for clarity and communication

## Functionalities

- Register and authenticate peers
- Update and manage file paths
- Send/receive file requests
- Approve/reject file access
- Download files securely
- In-app chat for file discussion and status

## Demo

Run the application locally using the GitHub repo below

## Future Scope

We’re excited to continue development! This project is open source, and we welcome external contributions. Let’s build a better, safer P2P system—together.

## Setup Instructions

1. Clone the repository  
   ```bash
   git clone https://github.com/pawar-ashwin/p2p_SecureShare.git
   cd p2p_SecureShare

2. Create and Activate virtual environments
   ```bash
    # Create virtual environment
    python -m venv venv

    # Activate (Windows)
    venv\Scripts\activate

    # Activate (macOS/Linux)
    source venv/bin/activate

3. Install Dependencies
   ```bash
   pip install -r requirements.txt

4. Run the application
   ```bash
   python manage.py runserver
