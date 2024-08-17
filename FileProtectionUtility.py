"""
#
# File Protection Utility
#
# Author: @hamsteruf
# GitHub: https://github.com/hamsteruf/File-Protection-Utility/
#
# This script provides functionality to encrypt and decrypt files. The encryption
# splits the file into two parts, and the decryption combines these parts to retrieve
# the original file.
#
"""


import os
import random
from tkinter import Tk, Button, Label, filedialog, messagebox, Frame

SEPARATOR = '1' * 64  # Separator to distinguish filename from file content

def encrypt_file():
    root = Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(title="Select a file to encrypt")
    if not file_path:
        return

    with open(file_path, 'rb') as file:
        file_content = file.read()

    # Convert file bytes to binary string
    file_bits = ''.join(f'{byte:08b}' for byte in file_content)

    # Convert filename to binary string
    filename = os.path.basename(file_path)
    filename_bits = ''.join(f'{ord(c):08b}' for c in filename)

    # Combine filename bits with file content bits
    combined_bits = filename_bits + SEPARATOR + file_bits
    part1_bits = []
    part2_bits = []

    # Randomly split combined bits into two parts
    for bit in combined_bits:
        if bit == '1':
            bit_value = '0' if random.random() < 0.5 else '1'
            part1_bits.append(bit_value)
            part2_bits.append(bit_value)
        else:
            bit1 = '0' if random.random() < 0.5 else '1'
            bit2 = '1' if bit1 == '0' else '0'
            part1_bits.append(bit1)
            part2_bits.append(bit2)

    def bits_to_bytes(bits):
        return bytearray(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))

    part1_bytes = bits_to_bytes(''.join(part1_bits))
    part2_bytes = bits_to_bytes(''.join(part2_bits))

    # Save files with fixed names
    with open('first_file.enc', 'wb') as file:
        file.write(part1_bytes)
    
    with open('second_file.enc', 'wb') as file:
        file.write(part2_bytes)
    
    messagebox.showinfo("Success", "Encryption complete. Files saved as 'first_file.enc' and 'second_file.enc'.")

def decrypt_files():
    root = Tk()
    root.withdraw()  # Hide the main window

    part1_path = filedialog.askopenfilename(title="Select the first encrypted file", filetypes=[("Encrypted files", "*.enc")])
    part2_path = filedialog.askopenfilename(title="Select the second encrypted file", filetypes=[("Encrypted files", "*.enc")])
    
    if not part1_path or not part2_path:
        return

    def read_file(file_path):
        with open(file_path, 'rb') as file:
            return file.read()

    part1_bytes = read_file(part1_path)
    part2_bytes = read_file(part2_path)

    def bytes_to_bits(bytes_data):
        return ''.join(f'{byte:08b}' for byte in bytes_data)

    bit_string1 = bytes_to_bits(part1_bytes)
    bit_string2 = bytes_to_bits(part2_bytes)

    original_bits = ''.join('1' if b1 == b2 else '0' for b1, b2 in zip(bit_string1, bit_string2))

    separator_index = original_bits.find(SEPARATOR)
    if separator_index == -1:
        messagebox.showerror("Error", "Separator not found in combined bit string.")
        return

    filename_bits = original_bits[:separator_index]
    file_bits = original_bits[separator_index + len(SEPARATOR):]

    def bits_to_string(bits):
        return ''.join(chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8))

    original_filename = bits_to_string(filename_bits)
    original_bytes = bytearray(int(file_bits[i:i + 8], 2) for i in range(0, len(file_bits), 8))

    with open(original_filename, 'wb') as file:
        file.write(original_bytes)
    
    messagebox.showinfo("Success", f"Decryption complete. File saved as '{original_filename}'.")

def open_github_link(event):
    import webbrowser
    webbrowser.open('https://github.com/hamsteruf/File-Protection-Utility/')

def main():
    root = Tk()
    root.title("File Protection Utility")
    root.geometry("400x350")

    # Create a frame for the buttons
    button_frame = Frame(root)
    button_frame.pack(pady=10, padx=10)

    encrypt_button = Button(button_frame, text="Encrypt File", command=encrypt_file, width=20, height=2)
    encrypt_button.pack(side='left', padx=5)

    decrypt_button = Button(button_frame, text="Decrypt Files", command=decrypt_files, width=20, height=2)
    decrypt_button.pack(side='left', padx=5)


    # Instructions and credits
    instructions_text = (
        "Instructions:\n"
        "1. To encrypt a file, click 'Encrypt File' and select a file.\n"
        "2. To decrypt files, click 'Decrypt Files', and select the two encrypted parts.\n"
        "3. The program will automatically handle file operations and save results."
    )

    instructions_label = Label(root, text=instructions_text, justify='left', wraplength=380)
    instructions_label.pack(pady=10, padx=10, anchor='w')


    github_link = Label(root, text="GitHub Repository", fg="blue", cursor="hand2")
    github_link.pack(pady=10, padx=10, anchor='w')
    github_link.bind("<Button-1>", open_github_link)

    root.mainloop()

if __name__ == "__main__":
    main()


# PS: You can also DM me on Discord: @hamsteruf :)