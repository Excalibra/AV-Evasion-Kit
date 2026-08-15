#!/usr/bin/env python3
"""
Shellcode Encryption Utility
Functionality: Encrypts Shellcode Using a Custom Encryption Algorithm
"""

import sys
import os


def custom_encrypt(shellcode, key):
    """
    Encrypt the Shellcode Using XOR.

    Parameters:
      shellcode: bytes, the raw shellcode to be encrypted
      key: bytes, the encryption key

    Returns:
      bytearray, the encrypted data

    Raises:
      ValueError: Raised when the provided key is empty
    """
    if not key:
        raise ValueError("Encryption key cannot be empty")

    encrypted = bytearray()
    key_len = len(key)
    for i, byte in enumerate(shellcode):
        encrypted_byte = (byte ^ key[i % key_len])
        encrypted.append(encrypted_byte)
    return encrypted


def main():
    if len(sys.argv) != 3:
        print("Usage: python shellcode-encrypt.py <shellcode_file> <key>")
        return

    filepath = sys.argv[1]
    key_str = sys.argv[2]

    if not os.path.exists(filepath):
        print(f"[Error] File not found: {filepath}")
        return

    try:
        with open(filepath, 'rb') as f:
            shellcode = f.read()
    except IOError as e:
        print(f"[Error] Failed to read file: {e}")
        return

    if not shellcode:
        print("[Error] Shellcode file is empty.")
        return

    key = key_str.encode()

    try:
        encrypted = custom_encrypt(shellcode, key)
    except ValueError as e:
        print(f"[Error] {e}")
        return

    try:
        with open('shellcode_encrypted.bin', 'wb') as f:
            f.write(encrypted)
    except IOError as e:
        print(f"[Error] Failed to write output file: {e}")
        return

    # Generate C-Style Array Format
    c_array = "unsigned char shellcode[] = {" + ",".join([f"0x{byte:02x}" for byte in encrypted]) + "};"

    try:
        with open('shellcode_encrypted.c', 'w') as f:
            f.write(c_array)
    except IOError as e:
        print(f"[Error] Failed to write C array file: {e}")
        return

    print(f"Shellcode encrypted successfully! (Input: {len(shellcode)} bytes, Output: {len(encrypted)} bytes)")


if __name__ == "__main__":
    main()
