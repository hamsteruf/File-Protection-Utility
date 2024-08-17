# File Protection Utility

## Overview

The File Protection Utility is a Python-based tool for encrypting and decrypting files using a custom method. The utility splits a file into two parts and uses a specific encryption technique to secure the file content. This process ensures that the file can only be reconstructed and read when both parts are available.

## How It Works

### Encryption

1. **File Selection**: The user selects a file to encrypt.
2. **Binary Conversion**: The file's content and filename are converted to binary strings.
3. **Combining Data**: The filename (in binary) and file content (in binary) are concatenated, separated by a specific separator.
4. **Splitting into Parts**:
   - The combined binary string is split into two parts. The splitting is performed randomly to ensure that both parts contain different binary data.
   - For each bit, if it's a `1`, both parts will have the same bit. If it's a `0`, each part will get a different bit (`0` or `1`), ensuring the original bit can be reconstructed.
5. **File Saving**:
   - The two parts are saved as `first_file.enc` and `second_file.enc`.

### Decryption

1. **File Selection**: The user selects the two encrypted files (`first_file.enc` and `second_file.enc`).
2. **Binary Extraction**:
   - Each file is read, and the binary data is extracted.
   - The two binary strings are compared to reconstruct the original binary data based on the principle that matching bits are the same and differing bits are `0`.
3. **Reconstruction**:
   - The original filename and file content are extracted from the binary data.
   - The file is reconstructed and saved with the original filename.

## Features

- Encrypts a file into two parts.
- Decrypts files back to their original state using the two encrypted parts.
- User-friendly graphical interface with buttons for encryption and decryption.

## Installation

### Prerequisites

- Python 3.x
- Tkinter (should be included with Python installation)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/File-Protection-Utility.git
   
2. **Navigate to the project directory:**
   ```bash
   cd File-Protection-Utility
   
3. **Install dependencies:**
If you use any additional packages, make sure to install them. The basic script uses Tkinter, which is included with Python.

## Usage
### Running the Program

Encrypt a File:

1. Click the "Encrypt File" button.
2. Select the file you want to encrypt. The tool will generate two files named first_file.enc and second_file.enc.

Decrypt Files:

1. Click the "Decrypt Files" button.
2. Select the two encrypted files (first_file.enc and second_file.enc).
3. The tool will reconstruct and save the original file.

## License
### This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
### For any issues or suggestions, please contact me on Discord: @hamsteruf
