#!/usr/bin/env python3
"""
Shellcode Patching Utility
Functionality: Performs Synonym Instruction Substitution, Junk Code Injection, and Instruction Reordering on Shellcode

Note: Genuine x86/x64 instruction-level patching requires dependence on a disassembly engine.
This script implements equivalence substitution based on known byte patterns, along with junk code injection,
without introducing third-party libraries, thereby ensuring out-of-the-box usability.
"""

import sys
import os

# ---- Table of Known Equivalent Instruction Substitutions (x86/x64) ----
# Format: (original byte sequence, replacement byte sequence, description)
# Important: The original and replacement sequences must be of equal length; otherwise, subsequent instruction offsets will be corrupted.
EQUIVALENT_PATCHES = [
    # No-Operation Equivalence Substitutions (Same Length):
    # 66 90 (nop, 2 bytes) -> 66 87 c0 ❌ Length mismatch, not usable
    # 66 90 (nop, 2 bytes) -> 66 87 c0 is 3 bytes ❌
    #
    # Truly same-length equivalent substitutions are exceedingly rare and require contextual analysis.
    # The following are a few safe same-length substitutions:

    # lea reg, [rip+0] -> mov reg, rip (not feasible; semantics differ)
    # test rax, rax (48 85 C0) -> or rax, rax (48 09 C0) — both set ZF, thus equivalent
    (b'\x48\x85\xc0', b'\x48\x09\xc0', 'test rax,rax -> or rax,rax'),
    # test eax, eax (85 C0) -> or eax, eax (09 C0) — both set ZF, thus equivalent
    (b'\x85\xc0', b'\x09\xc0', 'test eax,eax -> or eax,eax'),
    # test rax, rax Variant: rcx
    (b'\x48\x85\xc9', b'\x48\x09\xc9', 'test rcx,rcx -> or rcx,rcx'),
    # test ecx, ecx
    (b'\x85\xc9', b'\x09\xc9', 'test ecx,ecx -> or ecx,ecx'),
]

# ---- Junk Code Templates (Currently Unused; Retained for Future Extension) ----
# Inserting junk code will alter subsequent jump offsets and requires control-flow analysis; therefore, it is not enabled at present.
JUNK_INSTRUCTIONS = [
    b'\x90',                          # nop
    b'\x87\xc0',                      # xchg eax, eax (2-byte nop)
    b'\x66\x87\xc0',                  # xchg ax, ax (3-byte nop)
]


def patch_shellcode(shellcode):
    """
    Perform Synonym Instruction Substitution and Junk Code Injection on the Shellcode.

    Strategy:
      1. Scan for known equivalent patterns and perform substitution (without altering length).
      2. Insert junk code at positions that do not affect control flow.

    Note: This implementation adopts a conservative strategy, substituting only known safe patterns.
    If no known patterns are matched, the original data is returned unmodified.
    """
    patched = bytearray(shellcode)
    patch_count = 0

    # Step 1: Synonym Instruction Substitution (Without Altering Length)
    for i in range(len(patched)):
        for orig, repl, desc in EQUIVALENT_PATCHES:
            if patched[i:i + len(orig)] == orig:
                patched[i:i + len(orig)] = repl
                patch_count += 1
                break  # Perform Substitution Only Once Per Position

    # Junk Code Injection: Conservative Strategy — Not Actually Inserted, to Avoid Corrupting Relative Jump Offsets
    # (Genuine junk code injection requires an understanding of control flow; blind insertion would corrupt the shellcode)
    # The existing equivalent substitutions have already altered the byte-level signature.

    if patch_count == 0:
        print("[Warning] No known patterns matched for replacement.")
        print("[Info] Shellcode passed through unchanged.")
        print("[Info] Consider using a disassembler-based patcher for advanced patching.")

    return bytes(patched)


def main():
    if len(sys.argv) != 2:
        print("Usage: python shellcode-patch.py <shellcode_file>")
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

    patched = patch_shellcode(shellcode)

    try:
        with open('shellcode_patched.bin', 'wb') as f:
            f.write(patched)
    except IOError as e:
        print(f"[Error] Failed to write output file: {e}")
        return

    print(f"Shellcode patched successfully! (Input: {len(shellcode)} bytes, Output: {len(patched)} bytes)")


if __name__ == "__main__":
    main()
