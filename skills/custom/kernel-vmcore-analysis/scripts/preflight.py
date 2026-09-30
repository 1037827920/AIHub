#!/usr/bin/env python3
"""Read-only, bounded metadata inspection. Does not validate symbol matching."""

import argparse
import collections
import json
import os
from pathlib import Path
import selectors
import shutil
import stat
import struct
import subprocess
import time

TIMEOUT = 3.0
MAX_HEADERS = 4096
METADATA_LIMIT = 2 * 1024 * 1024
OUTPUT_LIMIT = 64 * 1024
TOOLS = (
    "crash", "drgn", "drgn-crash", "gdb", "readelf", "eu-readelf",
    "objdump", "addr2line", "eu-addr2line", "nm", "eu-nm", "pahole",
    "eu-unstrip", "makedumpfile", "vmcore-dmesg", "kexec", "virsh",
    "qemu-system-x86_64", "qemu-system-aarch64", "vmss2core", "pycrash",
)
MACHINES = {3: "i386", 21: "ppc64", 22: "s390", 40: "ARM", 62: "x86_64",
            183: "AArch64", 243: "RISC-V", 258: "LoongArch"}


def command_header(executable, path):
    """Read a small header report with a deadline and bounded pipe output."""
    env = dict(os.environ, LC_ALL="C", DEBUGINFOD_URLS="")
    process = subprocess.Popen(
        [executable, "-h", "--", str(path)], stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, env=env,
    )
    data = bytearray()
    deadline = time.monotonic() + TIMEOUT
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("readelf header inspection timed out")
                for key, _ in selector.select(remaining):
                    chunk = os.read(key.fd, 4096)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    data.extend(chunk)
                    if len(data) > OUTPUT_LIMIT:
                        raise ValueError("readelf output exceeded 64 KiB")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("readelf header inspection timed out")
            code = process.wait(timeout=remaining)
        output = data.decode("utf-8", errors="replace")
        if code:
            raise ValueError("readelf failed: " + output[:2000])
        return output
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("readelf header inspection timed out") from exc
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()
        process.stdout.close()


def elf_metadata(stream, header):
    if len(header) < 16:
        raise ValueError("truncated ELF identification")
    if header[4] not in (1, 2) or header[5] not in (1, 2):
        raise ValueError("invalid or unsupported ELF identification")
    bits = 64 if header[4] == 2 else 32
    endian = "<" if header[5] == 1 else ">"
    header_format = endian + ("HHIQQQIHHHHHH" if bits == 64 else "HHIIIIIHHHHHH")
    required = 16 + struct.calcsize(header_format)
    if len(header) < required:
        raise ValueError("truncated ELF header")
    fields = struct.unpack(header_format, header[16:required])
    elf_type, machine = fields[:2]
    phoff, shoff = fields[4:6]
    phsize, phnum, shsize, shnum, shstr = fields[8:13]
    result = {"bits": bits, "byte_order": "little" if endian == "<" else "big",
              "type": {1: "REL", 2: "EXEC", 3: "DYN", 4: "CORE"}.get(elf_type, elf_type),
              "machine": MACHINES.get(machine, machine), "warnings": []}
    warnings = result["warnings"]
    budget = METADATA_LIMIT

    def read_at(offset, size):
        nonlocal budget
        if size > budget:
            raise ValueError("ELF metadata exceeded 2 MiB inspection budget")
        budget -= size
        stream.seek(offset)
        data = stream.read(size)
        if len(data) != size:
            raise ValueError("truncated ELF metadata at offset " + hex(offset))
        return data

    notes = set()
    if phnum == 0xFFFF:
        warnings.append("extended program header count: skipped; use format-aware tools")
    elif phnum:
        fmt = endian + ("IIQQQQQQ" if bits == 64 else "IIIIIIII")
        size = struct.calcsize(fmt)
        if not phoff or phsize < size or phsize > 4096 or phnum > MAX_HEADERS:
            raise ValueError("invalid or excessive program header table")
        table = read_at(phoff, phsize * phnum)
        for index in range(phnum):
            item = struct.unpack_from(fmt, table, index * phsize)
            if item[0] == 4:  # PT_NOTE; never read PT_LOAD memory contents.
                notes.add((item[2], item[5]) if bits == 64 else (item[1], item[4]))

    section_names = []
    if shoff and (shnum == 0 or shstr == 0xFFFF):
        warnings.append("extended section numbering: skipped")
    elif shnum:
        fmt = endian + ("IIQQQQIIQQ" if bits == 64 else "IIIIIIIIII")
        size = struct.calcsize(fmt)
        if not shoff or shsize < size or shsize > 4096 or shnum > MAX_HEADERS:
            raise ValueError("invalid or excessive section header table")
        table = read_at(shoff, shsize * shnum)
        sections = [struct.unpack_from(fmt, table, i * shsize) for i in range(shnum)]
        if 0 < shstr < shnum:
            names_section = sections[shstr]
            names = read_at(names_section[4], names_section[5])
            for item in sections:
                offset = item[0]
                if offset >= len(names):
                    warnings.append("section name offset outside string table")
                    continue
                name = names[offset:].split(b"\0", 1)[0].decode("utf-8", "replace")
                section_names.append(name)
        elif shstr:
            raise ValueError("invalid section name table index")
        for item in sections:
            if item[1] == 7:  # SHT_NOTE
                notes.add((item[4], item[5]))
    result["debug_sections"] = [name for name in section_names
                                if name.startswith((".debug_", ".zdebug_"))
                                or name in (".BTF", ".gnu_debuglink", ".gnu_debugaltlink")]
    result["debug_info_note"] = "Section presence does not prove usable or matching debuginfo."
    counts = collections.Counter()
    build_ids = set()
    vmcoreinfo = {}
    seen_notes = set()
    for offset, size in sorted(notes):
        if size > budget:
            warnings.append("note region skipped: metadata budget exhausted")
            continue
        data = read_at(offset, size)
        cursor = 0
        while cursor + 12 <= len(data):
            note_offset = offset + cursor
            namesz, descsz, note_type = struct.unpack_from(endian + "III", data, cursor)
            cursor += 12
            desc_start = cursor + ((namesz + 3) & ~3)
            end = desc_start + descsz
            next_note = desc_start + ((descsz + 3) & ~3)
            if end > len(data) or next_note > len(data):
                warnings.append("incomplete or unsupported note alignment")
                break
            # A PT_NOTE segment and SHT_NOTE section can cover the same note.
            if note_offset in seen_notes:
                cursor = next_note
                continue
            seen_notes.add(note_offset)
            owner = data[cursor:cursor + namesz].rstrip(b"\0").decode("utf-8", "replace")
            desc = data[desc_start:end]
            counts[f"{owner}:type={note_type}"] += 1
            if owner == "GNU" and note_type == 3:
                build_ids.add(desc.hex())
            if owner == "VMCOREINFO":
                for line in desc.rstrip(b"\0").decode("utf-8", "replace").splitlines():
                    key, sep, value = line.partition("=")
                    if sep and key in ("OSRELEASE", "PAGESIZE", "KERNELOFFSET"):
                        vmcoreinfo[key] = value
            cursor = next_note
    result["note_counts"] = dict(counts)
    result["build_ids"] = sorted(build_ids)
    result["vmcoreinfo_summary"] = vmcoreinfo
    if not counts:
        warnings.append("no notes observed in inspected regions; absence is not a completeness verdict")
    return result


def inspect_file(raw_path, readelf):
    path = Path(raw_path).expanduser().absolute()
    result = {"path": str(path)}
    try:
        info = path.stat()
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("input must be a regular or procfs file, not a device/FIFO/directory")
        result["size_bytes"] = info.st_size
        with path.open("rb") as stream:
            header = stream.read(64)
            result["readable"] = True
            result["header_hex"] = header[:16].hex()
            if header.startswith(b"\x7fELF"):
                result["format"] = "ELF"
                result["elf"] = elf_metadata(stream, header)
            else:
                if header.startswith((b"KDUMP", b"DISKDUMP")):
                    kind = "possible kdump/diskdump"
                elif header.startswith(b"makedumpfile"):
                    kind = "possible makedumpfile flattened stream"
                else:
                    kind = "non-ELF / unrecognized"
                result["format"] = kind
                result["guidance"] = "Use format-specific tools; non-ELF alone does not mean corruption."
        if result["format"] == "ELF" and readelf:
            result["readelf_header"] = command_header(readelf, path)
        elif result["format"] == "ELF":
            result["guidance"] = "readelf missing; standard-library metadata inspection completed."
    except (OSError, ValueError, TimeoutError, struct.error) as exc:
        result["error"] = str(exc)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vmcore", required=True)
    parser.add_argument("--vmlinux")
    args = parser.parse_args(argv)
    tools = {name: shutil.which(name) for name in TOOLS}
    report = {
        "limitations": ["Cannot prove symbol matching or dump completeness.",
                        "Only bounded metadata is inspected; no memory contents are scanned.",
                        "Build IDs belong to the containing ELF, not necessarily the crashed kernel.",
                        "Missing tools are optional capability hints, not installation requests."],
        "tools": tools,
        "vmcore": inspect_file(args.vmcore, tools["readelf"]),
    }
    if args.vmlinux:
        report["vmlinux"] = inspect_file(args.vmlinux, tools["readelf"])
    core_elf = report["vmcore"].get("elf")
    if core_elf and core_elf["type"] != "CORE":
        core_elf["warnings"].append("ELF is not ET_CORE; confirm that this input is a kernel dump.")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(any("error" in report[name] for name in ("vmcore", "vmlinux") if name in report))


if __name__ == "__main__":
    raise SystemExit(main())
