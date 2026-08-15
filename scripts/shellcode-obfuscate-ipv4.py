#!/usr/bin/env python3
"""
Shellcode IPv4 Obfuscation Utility
Functionality: Disguises Shellcode as an Array of IPv4 Addresses
"""

import sys
import os


def obfuscate_as_ipv4(shellcode):
    """
    Convert Every 4-Byte Block of the Shellcode into an IPv4 Address.

    Parameters:
      shellcode: bytes, the raw shellcode to be transformed

    Returns:
      list[str], a list of IPv4 address strings
    """
    ipv4_list = []
    for i in range(0, len(shellcode), 4):
        chunk = shellcode[i:i + 4]
        if len(chunk) < 4:
            chunk = chunk.ljust(4, b'\x00')
        # Convert in Direct Byte Order: chunk[0].chunk[1].chunk[2].chunk[3]
        ipv4 = f"{chunk[0]}.{chunk[1]}.{chunk[2]}.{chunk[3]}"
        ipv4_list.append(ipv4)
    return ipv4_list


def format_c_array(ipv4_list, ips_per_line=5):
    """
    Generate a Formatted C-Style IPv4 Array, with a Fixed Number of IPs per Line.

    Parameters:
      ipv4_list: list[str], a list of IPv4 address strings
      ips_per_line: int, the number of IP addresses to display per line

    Returns:
      str, a C-style array declaration as a string
    """
    lines = []
    lines.append("char* ipv4_array[] = {")

    for i in range(0, len(ipv4_list), ips_per_line):
        chunk = ipv4_list[i:i + ips_per_line]
        # Enclose Each IP within Double Quotes, Separate with Commas, and Omit the Trailing Comma for the Final Entry
        is_last_chunk = (i + ips_per_line) >= len(ipv4_list)
        line_ips = ", ".join([f'"{ip}"' for ip in chunk])
        # Append a Comma Unless It Is the Final Group
        if not is_last_chunk:
            line_ips += ","
        lines.append(f"    {line_ips}")

    lines.append("};")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: python shellcode-obfuscate-ipv4.py <shellcode_file>")
        return

    filepath = sys.argv[1]

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

    ipv4_list = obfuscate_as_ipv4(shellcode)

    # Generate a Formatted C-Style Array
    c_array = format_c_array(ipv4_list)

    try:
        with open('shellcode_obfuscated_ipv4.c', 'w') as f:
            f.write(c_array)
    except IOError as e:
        print(f"[Error] Failed to write output file: {e}")
        return

    print(f"Shellcode obfuscated as IPv4 successfully! Total: {len(ipv4_list)} IPs")


if __name__ == "__main__":
    main()
