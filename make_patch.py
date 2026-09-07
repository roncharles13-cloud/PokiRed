"""Diff the clean Red ROM against the modded ROM and emit an IPS patch
(mod.ips) containing ONLY the differences (the mods). Verifies the patch
reconstructs the modded ROM exactly when applied to a clean ROM.
"""
import sys

def make_ips(orig, mod):
    assert len(orig) == len(mod), "size mismatch"
    out = bytearray(b"PATCH")
    i, n = 0, len(orig)
    recs = 0
    while i < n:
        if orig[i] != mod[i]:
            j = i
            while j < n and orig[j] != mod[j] and (j - i) < 0xFFFF:
                j += 1
            data = mod[i:j]
            out += bytes([(i >> 16) & 0xFF, (i >> 8) & 0xFF, i & 0xFF,
                          (len(data) >> 8) & 0xFF, len(data) & 0xFF]) + data
            recs += 1
            i = j
        else:
            i += 1
    out += b"EOF"
    return bytes(out), recs

def apply_ips(rom, patch):
    assert patch[:5] == b"PATCH"
    rom = bytearray(rom); p = 5
    while patch[p:p+3] != b"EOF":
        off = (patch[p] << 16) | (patch[p+1] << 8) | patch[p+2]
        size = (patch[p+3] << 8) | patch[p+4]; p += 5
        rom[off:off+size] = patch[p:p+size]; p += size
    return bytes(rom)

if __name__ == "__main__":
    orig = open(sys.argv[1], "rb").read()
    mod = open("red_mod.gb", "rb").read()
    patch, recs = make_ips(orig, mod)
    open("mod.ips", "wb").write(patch)
    ok = apply_ips(orig, patch) == mod
    print(f"mod.ips: {len(patch)} bytes, {recs} change records")
    print(f"verify (clean ROM + patch == modded ROM): {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)
