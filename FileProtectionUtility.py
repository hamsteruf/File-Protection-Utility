import os
import random
import sys
import webbrowser
import subprocess
from tkinter import Tk, Button, Label, filedialog, messagebox, Frame, Toplevel

SEPARATOR = '1' * 64  # Separator to distinguish filename from file content

def find_files():
    # Automatically find 'first_file.enc' and 'second_file.enc' in the current directory
    current_dir = os.getcwd()
    part1_path = os.path.join(current_dir, 'first_file.enc')
    part2_path = os.path.join(current_dir, 'second_file.enc')
    
    if os.path.isfile(part1_path) and os.path.isfile(part2_path):
        return part1_path, part2_path
    return None, None

def split_file(input_file=None):
    if input_file is None:
        input_file = filedialog.askopenfilename(title="Select a file to split")
        if not input_file:
            return

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

    with open(part1_path, 'wb') as file:
        file.write(part1_bytes)
    
    with open(part2_path, 'wb') as file:
        file.write(part2_bytes)
    
    show_popup("File Split Successfully!", part1_path)

def merge_files(part1_file=None, part2_file=None):
    if part1_file is None or part2_file is None:
        part1_file, part2_file = find_files()
        if part1_file is None or part2_file is None:
            part1_file = filedialog.askopenfilename(title="Select the first encrypted file", filetypes=[("Encrypted files", "*.enc")])
            if not part1_file:
                return
            part2_file = filedialog.askopenfilename(title="Select the second encrypted file", filetypes=[("Encrypted files", "*.enc")])
            if not part2_file:
                return

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
    
    show_popup("File Merged Successfully!", original_filename, is_merge=True)

def show_popup(message, file_path, is_merge=False):
    popup = Toplevel()
    popup.title("Operation Complete")
    
    # Set size based on operation
    if is_merge:
        popup.geometry("400x200")  # Larger size for merging
    else:
        popup.geometry("300x150")  # Default size for splitting

    Label(popup, text=message, pady=10, font=("Arial", 12, "bold")).pack()

    def close():
        popup.destroy()

    def open_folder():
        open_file_location(file_path)
        popup.destroy()

    def open_file():
        open_file_location(file_path, select_file=True)
        popup.destroy()

    Button(popup, text="Close", command=close, width=15).pack(side="left", padx=10, pady=10)
    Button(popup, text="Open Folder", command=open_folder, width=15).pack(side="left", padx=10, pady=10)

    if is_merge:
        Button(popup, text="Open File", command=open_file, width=15).pack(side="left", padx=10, pady=10)

    popup.mainloop()

def open_github_link(event):
    webbrowser.open('https://github.com/hamsteruf/File-Protection-Utility/')

def open_file_location(file_path, select_file=False):
    # Determine the operating system and open the file location accordingly
    if sys.platform == "win32":
        if select_file:
            subprocess.Popen(['explorer', '/select,', file_path])
        else:
            subprocess.Popen(['explorer', '/root,', os.path.dirname(file_path)])
    elif sys.platform == "darwin":  # macOS
        if select_file:
            subprocess.Popen(["open", "-R", file_path])
        else:
            subprocess.Popen(["open", os.path.dirname(file_path)])
    else:  # Linux and other Unix-like systems
        if select_file:
            subprocess.Popen(["xdg-open", file_path])  # Opens the file directly
        else:
            subprocess.Popen(["xdg-open", os.path.dirname(file_path)])  # Opens the directory containing the file

def display_help():
    help_text = (
        "File Protection Utility\n\n"
        "Usage:\n"
        "  python3 FileProtectionUtility.py [options] [file1] [file2]\n\n"
        "Options:\n"
        "  -s, --split     Split a file into two encrypted parts.\n"
        "  -m, --merge     Merge two encrypted parts into the original file.\n"
        "  -h, --help      Show this help message and exit.\n\n"
        "Arguments:\n"
        "  For splitting: Provide a single file to split after -s/--split.\n"
        "  For merging: Provide two files to merge after -m/--merge. If no files are provided, the script will look for 'first_file.enc' and 'second_file.enc' in the current directory.\n\n"
        "If no options are provided, the graphical user interface (GUI) will be launched."
    )
    print(help_text)

def main():
    try:
        root = Tk()
        root.title("File Protection Utility")
        root.geometry("400x350")

        # Create a frame for the buttons
        button_frame = Frame(root)
        button_frame.pack(pady=10, padx=10)

        def select_and_split():
            split_file()

        def select_and_merge():
            merge_files()

        split_button = Button(button_frame, text="Split File", command=select_and_split, width=20, height=2)
        split_button.pack(side='left', padx=5)

        merge_button = Button(button_frame, text="Merge Files", command=select_and_merge, width=20, height=2)
        merge_button.pack(side='left', padx=5)

        # Instructions and credits
        instructions_text = (
            "Instructions:\n"
            "1. To split a file, click 'Split File' and select a file.\n"
            "2. To merge files, click 'Merge Files', and select the two encrypted parts.\n"
            "3. The program will automatically handle file operations and save results.\n\n"
            "Note: Ensure that 'first_file.enc' and 'second_file.enc' are in the same directory for merging if you don't provide filenames."
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
            display_help()
        elif sys.argv[1] in ['-s', '--split']:
            if len(sys.argv) == 3:
                split_file(sys.argv[2])
            else:
                print("Error: For splitting, provide one filename after -s/--split.")
                display_help()
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
                    display_help()
            else:
                print("Error: For merging, provide two filenames after -m/--merge.")
                display_help()
        else:
            print("Error: Invalid option.")
            display_help()
    else:
        main()
