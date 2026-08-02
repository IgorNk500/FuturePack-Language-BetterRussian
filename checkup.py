"""
**Checkup program for checking localization files for omissions.**

Use in root folder.

Usage:
    Please run `python checkup.py -h` for help

-----

Copyright (c) 2026 IgorNk500

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
import json, os

__version__ = "1.0"
__author__ = "IgorNk500"

DEBUG = False
ENCODING = "utf-8"


########## MENU ##########

def menu(orig: str, custom: str):
    """Main function"""

    print("""
    ==========================
    Localization checkup v{}
          by IgorNk500
    ==========================
    """.format(__version__))

    print()
    print(f"Original: {orig}; Custom: {custom}")
    input("Press Enter to continue...")

    print()
    print("SCANNING...")
    _all, found = checkup(orig, custom)

    print()
    print("COMPLETE!")
    print("=" * 50)
    print("STATISTICS:")

    # Generate statistics
    found_percent = found / _all * 100 if found > 0 else 0.0

    not_found = _all - found
    not_found_percent = 100 - found_percent

    # Print statistics
    print("    All: {}".format(_all))
    print("    Found: {} ({}%)".format(found, found_percent))
    print("    Not found: {} ({}%)".format(not_found, not_found_percent))

def robotic(orig: str, custom: str):
    """**Robotic mode. Please read:**
    Returns ALL data in format {"main": dict[str, int], "additional": dict[str, bool]},
    where "main" is the {"lang_key": position} and "additional" is the {"filepath": correct}."""
    res = checkup_all(orig, custom)
    return {"main": res[1], "additional": res[0]}


########## CHECKUPS ##########

def checkup(orig: str, custom: str):
    res, res_main = checkup_all(orig, custom)
    print("Scanning complete")
    print()

    found = 0
    for file, data in res.items():
        if not data:
            print(f"File {file} from {orig} not found in {custom}")
            found += 1

    if res_main != {}:
        print("In main lang file for {}:".format(custom))
        for key, pos in res_main.items():
            print(f"    In [{pos}]: \"{key}\" found in {orig}, but not found in {custom};")
            found += 1

    return len(res) + len(res_main), found


def checkup_all(orig: str, custom: str) -> tuple[dict[str, bool], dict[str, int]]:
    """Checkup all JSON localization files
    :arg orig: Original language path
    :arg custom: Custom language path"""

    # Checkup main file
    if DEBUG: print("Scanning main lang file...")
    results_main = checkup_main(orig + ".json", custom + ".json")

    # Checkup additional files
    results = {}
    for fp in _scan_once(orig):
        if DEBUG: print("Scanning {}...".format(fp))
        results[fp] = os.path.exists(os.path.join(custom, fp))
    return results, results_main
    # {file(str): {key(str): pos(int)}}


def checkup_main(orig: str, lang: str) -> dict[str, int]:
    """Checkup the main localization file"""
    with open(orig, "r", encoding=ENCODING) as f:
        orig_data = json.loads(_preprocess(f.read()))
    with open(lang, "r", encoding=ENCODING) as f:
        lang_data = json.loads(_preprocess(f.read()))

    return {key: pos for pos, key in enumerate(orig_data.keys()) if key not in lang_data.keys()}


########## SPECIALS ##########

def _preprocess(data: str):
    """Preprocess localization data (delete comments)"""
    lines = data.split("\n")
    for i, line in enumerate(lines):
        if "//" in line:
            lines[i] = line[:line.index("//")]
    return "\n".join(lines)


def _scan_once(folder: str):
    """Scan all localization files in folder"""
    from pathlib import Path
    results = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".json") or file.endswith(".jsonl"):
                results.append(os.path.join(str(*Path(root).parts[1:]), file))
    return results


def _selector(variants: list[str], inp_text: str = "Select a variant") -> str:
    """Simple variant selector"""
    for pos, variant in enumerate(variants): print(f"   [{pos + 1}]: {variant}")

    selected = int(input(inp_text + ": ")) - 1
    assert 0 <= selected <= len(variants)
    return variants[selected]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Checks localization files for omissions")
    parser.add_argument("original", type=str, help="Original language name")
    parser.add_argument("custom", type=str, help="Custom Language name")

    parser.add_argument("-e", "--encoding", type=str, required=False,
                        help=f"[PLEASE USE]: Encoding for files (Default: {ENCODING})", )
    parser.add_argument("-d", "--debug", action="store_true", required=False, help="[OPTIONAL]: Debug mode")
    parser.add_argument("-r", "--robotic", required=False, action="store_true",
                        help="[OPTIONAL]: Return in JSON + Silent")
    args = parser.parse_args()

    if args.debug:
        DEBUG = True

    if args.encoding:
        ENCODING = args.encoding

    if args.robotic:
        print(robotic(args.original, args.custom))
    else:
        menu(args.original, args.custom)
