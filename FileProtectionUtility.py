#
# File Protection Utility
#
# Author: @hamsteruf
# GitHub: https://github.com/hamsteruf/File-Protection-Utility/
#
# This script provides functionality to split and merge .enc files. The program
# splits the file into two parts, or merges these parts to retrieve
# the original file.
#

import os
import random
import sys
import webbrowser
import tkinter as tk
from tkinter import Tk, Button, Label, filedialog, messagebox, Frame, Toplevel, StringVar
from tkinter import ttk  # Import ttk for Progressbar
import shutil
import subprocess

SEPARATOR = '1' * 64  # Separator to distinguish filename from file content
PROGRESS_THRESHOLD = 500 * 1024 * 1024  # 500 MB

def secure_delete(file_path):
    """Overwrite file content and delete it securely."""
    with open(file_path, 'r+b') as f:
        length = os.path.getsize(file_path)
        f.seek(0)
        f.write(b'\x00' * length)  # Overwrite with zeros
        f.flush()
        os.fsync(f.fileno())
    os.remove(file_path)  # Remove the file

def find_files():
    """Automatically find 'first_file.enc' and 'second_file.enc' in the current directory."""
    current_dir = os.getcwd()
    part1_path = os.path.join(current_dir, 'first_file.enc')
    part2_path = os.path.join(current_dir, 'second_file.enc')
    
    if os.path.isfile(part1_path) and os.path.isfile(part2_path):
        return part1_path, part2_path
    return None, None

def update_progress(progress_bar, value, max_value):
    """Update progress bar value."""
    progress_bar['value'] = (value / max_value) * 100
    progress_bar.update()

def cancel_operation():
    """Cancel the ongoing operation."""
    global operation_cancelled
    operation_cancelled = True

def split_file(input_file=None):
    global operation_cancelled
    operation_cancelled = False

    if input_file is None:
        input_file = filedialog.askopenfilename(title="Select a file to split")
        if not input_file:
            return

    file_size = os.path.getsize(input_file)
    if file_size > PROGRESS_THRESHOLD:
        # Create a progress window
        progress_window = Toplevel()
        progress_window.title("Progress")
        progress_label = Label(progress_window, text="Splitting file, please wait...")
        progress_label.pack(pady=10)
        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
        progress_bar.pack(pady=10)
        cancel_button = Button(progress_window, text="Cancel", command=cancel_operation)
        cancel_button.pack(pady=10)
        progress_window.update()

    try:
        with open(input_file, 'rb') as file:
            file_content = file.read()

        # Convert file bytes to binary string
        file_bits = ''.join(f'{byte:08b}' for byte in file_content)

        # Convert filename to binary string
        filename = os.path.basename(input_file)
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
        part1_path = os.path.join(os.path.dirname(input_file), 'first_file.enc')
        part2_path = os.path.join(os.path.dirname(input_file), 'second_file.enc')

        if not operation_cancelled:
            with open(part1_path, 'wb') as file:
                file.write(part1_bytes)
            
            with open(part2_path, 'wb') as file:
                file.write(part2_bytes)

            if file_size > PROGRESS_THRESHOLD:
                update_progress(progress_bar, file_size, file_size)
                progress_window.destroy()

            secure_delete(input_file)  # Securely delete the original file
            show_popup("File split successfully!", part1_path,  is_split=True)

    except Exception as e:
        if operation_cancelled:
            messagebox.showinfo("Cancelled", "Operation was cancelled.")
        else:
            show_error_popup(f"An error occurred while splitting the file:\n{e}")

def merge_files(part1_file=None, part2_file=None):
    global operation_cancelled
    operation_cancelled = False

    if part1_file is None or part2_file is None:
        part1_file, part2_file = find_files()
        if part1_file is None or part2_file is None:
            part1_file = filedialog.askopenfilename(title="Select the first file to merge", filetypes=[("Encrypted files", "*.enc")])
            if not part1_file:
                return
            part2_file = filedialog.askopenfilename(title="Select the second file to merge", filetypes=[("Encrypted files", "*.enc")])
            if not part2_file:
                return

    try:
        def read_file(file_path):
            with open(file_path, 'rb') as file:
                return file.read()

        part1_bytes = read_file(part1_file)
        part2_bytes = read_file(part2_file)

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
        
        # Securely delete the .enc files
        secure_delete(part1_file)
        secure_delete(part2_file)

        show_popup("Files merged successfully!", original_filename, is_merge=True)

    except Exception as e:
        if operation_cancelled:
            messagebox.showinfo("Cancelled", "Operation was cancelled.")
        else:
            show_error_popup(f"An error occurred while merging the files:\n{e}")

def open_file_location(file_path, select_file=False):
    """Open the folder containing the file or the file itself."""
    if file_path:
        folder_path = os.path.dirname(file_path)
        if select_file:
            # Open the file using the default application
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
        else:
            # Open the folder containing the file
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", folder_path])
            else:
                subprocess.run(["xdg-open", folder_path])

def show_popup(message, file_path=None, is_merge=False, is_split=False):
    """Show a popup window with a success message and options to open the folder or file."""
    popup = Toplevel()
    popup.title("Operation Complete")
    
    popup.geometry("350x100")

    Label(popup, text=message, pady=10, font=("Arial", 12, "bold")).pack()

    def close():
        popup.destroy()

    def open_folder():
        open_file_location(file_path)
        popup.destroy()

    def open_file():
        open_file_location(file_path, select_file=True)
        popup.destroy()

    # Layout buttons
    button_frame = Frame(popup)
    button_frame.pack(pady=10)

    if is_split:
        Button(button_frame, text="Open Folder", command=open_folder, width=15).pack(side="left", padx=10)
    
    if is_merge:
        Button(button_frame, text="Open File", command=open_file, width=15).pack(side="left", padx=10)

    Button(button_frame, text="Close", command=close, width=15).pack(side="left", padx=10)
    
    popup.mainloop()

def show_error_popup(message):
    """Show an error popup with the provided message and options to copy the message."""
    error_popup = Toplevel()
    error_popup.title("Error")
    error_popup.geometry("400x200")

    label = Label(error_popup, text=message, wraplength=380)
    label.pack(pady=10)

    def copy_message():
        root.clipboard_clear()
        root.clipboard_append(message)
        root.update()  # Keeps clipboard updated
        messagebox.showinfo("Copied", "Error message copied to clipboard.")

    button_frame = Frame(error_popup)
    button_frame.pack(pady=10)

    Button(button_frame, text="Copy", command=copy_message).pack(side='left', padx=5)
    Button(button_frame, text="OK", command=error_popup.destroy).pack(side='left', padx=5)

def toggle_dark_mode():
    """Toggle between dark and light mode."""
    if dark_mode_var.get() == "off":
        dark_mode_var.set("on")
        root.configure(bg='black')
        for widget in root.winfo_children():
            if isinstance(widget, ttk.Progressbar):
                widget.configure(style='dark.Horizontal.TProgressbar')
            elif isinstance(widget, Label):
                widget.configure(bg='black', fg='lightgray')
            elif isinstance(widget, Button) and widget != dark_mode_button:
                widget.configure(bg='lightgray', fg='black')
                widget.bind("<Enter>", lambda e: e.widget.configure(bg='gray'))
                widget.bind("<Leave>", lambda e: e.widget.configure(bg='lightgray'))
            elif isinstance(widget, Button) and widget == dark_mode_button:
                widget.configure(bg='black', fg='lightgray')
                widget.bind("<Enter>", lambda e: e.widget.configure(bg='darkgray'))
                widget.bind("<Leave>", lambda e: e.widget.configure(bg='gray'))
        github_link.configure(fg="blue")
    else:
        dark_mode_var.set("off")
        root.configure(bg='lightgray')
        for widget in root.winfo_children():
            if isinstance(widget, ttk.Progressbar):
                widget.configure(style='light.Horizontal.TProgressbar')
            elif isinstance(widget, Label):
                widget.configure(bg='lightgray', fg='black')
            elif isinstance(widget, Button) and widget != dark_mode_button:
                widget.configure(bg='lightgray', fg='black')
                widget.bind("<Enter>", lambda e: e.widget.configure(bg='gray'))
                widget.bind("<Leave>", lambda e: e.widget.configure(bg='lightgray'))
            elif isinstance(widget, Button) and widget == dark_mode_button:
                widget.configure(bg='lightgray', fg='black')
                widget.bind("<Enter>", lambda e: e.widget.configure(bg='gray'))
                widget.bind("<Leave>", lambda e: e.widget.configure(bg='lightgray'))
        github_link.configure(fg="blue")

def open_github_link(event):
    """Open the GitHub repository in the browser."""
    webbrowser.open("https://github.com/hamsteruf/File-Protection-Utility/")

def create_main_window():
    """Create the main window for the application."""
    global root, dark_mode_var, dark_mode_button, github_link
    try:
        root = Tk()
        root.title("File Protection Utility")
        root.geometry("400x350")

        # Define dark mode styles
        style = ttk.Style()
        style.configure('dark.Horizontal.TProgressbar', background='gray20', troughcolor='black', bordercolor='black', lightcolor='gray40', darkcolor='gray40')
        style.configure('light.Horizontal.TProgressbar', background='lightgray', troughcolor='white', bordercolor='white', lightcolor='gray', darkcolor='gray')

        dark_mode_var = StringVar(value="off")

        dark_mode_button = Button(root, text="Toggle Dark Mode", command=toggle_dark_mode)
        dark_mode_button.pack(pady=10)

        # Create a frame for the buttons
        button_frame = Frame(root)
        button_frame.pack(pady=10, padx=10)

        def select_and_split():
            split_file()

        def select_and_merge():
            merge_files()

        split_button = Button(button_frame, text="Split File", command=lambda: select_and_split(), width=20, height=2)
        split_button.pack(side='left', padx=5)

        merge_button = Button(button_frame, text="Merge Files", command=lambda: select_and_merge(), width=20, height=2)
        merge_button.pack(side='left', padx=5)

        # Instructions and credits
        instructions_text = (
            "Instructions:\n"
            "1. To split a file, click 'Split File' and select a file.\n"
            "2. To merge files, click 'Merge Files', and select the two encrypted parts.\n"
            "3. The program will automatically handle file operations and save results.\n\n"
            "Note: If 'first_file.enc' and 'second_file.enc' are in the same folder as this script, you will have to manually select them."
        )

        instructions_label = Label(root, text=instructions_text, justify='left', wraplength=380)
        instructions_label.pack(pady=10, padx=10, anchor='w')

        github_link = Label(root, text="GitHub Repository", fg="blue", cursor="hand2")
        github_link.pack(pady=10, padx=10, anchor='w')
        github_link.bind("<Button-1>", open_github_link)

        root.mainloop()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: python FileProtectionUtility.py [options]\n")
            print("Options:")
            print("-h, --help        Show this help message and exit")
            print("-s, --split       Split a file. Usage: -s filename")
            print("-m, --merge       Merge files. Usage: -m part1.enc part2.enc")
        elif sys.argv[1] in ['-s', '--split']:
            if len(sys.argv) == 3:
                split_file(sys.argv[2])
            else:
                print("Error: For splitting, provide one filename after -s/--split.")
                print("Usage: python FileProtectionUtility.py -s filename")
        elif sys.argv[1] in ['-m', '--merge']:
            if len(sys.argv) == 4:
                merge_files(sys.argv[2], sys.argv[3])
            elif len(sys.argv) == 2:
                # Attempt to find files for merging if only -m is provided
                part1_file, part2_file = find_files()
                if part1_file and part2_file:
                    merge_files(part1_file, part2_file)
                else:
                    print("Error: For merging, provide two filenames after -m/--merge or ensure 'first_file.enc' and 'second_file.enc' are in the current directory.")
                    print("Usage: python FileProtectionUtility.py -m part1.enc part2.enc")
            else:
                print("Error: For merging, provide two filenames after -m/--merge.")
                print("Usage: python FileProtectionUtility.py -m part1.enc part2.enc")
        else:
            print("Error: Invalid option.")
            print("Usage: python FileProtectionUtility.py [options]")
    else:
        create_main_window()
