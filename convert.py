#!/usr/bin/env python3
import sys
import time
import json
from pathlib import Path
from PIL import Image  # type: ignore
from tqdm import tqdm  # type: ignore
from colorama import init, Fore, Style, Back  # type: ignore
import humanize  # type: ignore

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

init(autoreset=True)

def print_header():
    print(f"{Back.BLUE}{Fore.WHITE} Convert icns to png {Style.RESET_ALL}")
    print(f"{Back.BLUE}{Fore.WHITE} By RepoSileo {Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

def ask_output_format():
    print(f"{Fore.GREEN}1. PNG (Preserve transparency): {Style.RESET_ALL}", end="")
    user_input = input().strip().lower()
    if user_input in ('q', 'quit'):
        print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
        sys.exit(0)
    return "png"

def convert_files():
    script_dir = Path(__file__).resolve().parent
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    files = [f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() == '.icns']

    if not files:
        print(f"{Fore.RED}No .icns files in 'input' folder.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Enter to return, or Q to quit.{Style.RESET_ALL}")
        choice = input().strip().lower()
        if choice in ('q', 'quit'):
            print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            sys.exit(0)
        return None

    print(f"\n{Fore.GREEN}Found {len(files)} .icns file(s). Converting to PNG (with transparency)...{Style.RESET_ALL}")

    stats = []
    pbar = tqdm(files, desc="Converting", unit="file",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                ncols=80, dynamic_ncols=True)

    for fp in pbar:
        try:
            orig_size = fp.stat().st_size
            with Image.open(fp) as img:
                img.load()
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
                out_path = output_dir / (fp.stem + ".png")
                img.save(out_path, "PNG", optimize=False)

            stats.append({
                'filename': fp.name,
                'original_size': orig_size,
                'converted_size': out_path.stat().st_size,
            })
            pbar.set_description(f" {fp.stem[:25]}.png")
        except Exception as e:
            tqdm.write(f"\n{Fore.RED}Error {fp.name}: {e}{Style.RESET_ALL}")

    return stats

def print_summary(stats):
    print(f"\n{Back.GREEN}{Fore.BLACK} Conversion Complete {Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    total_orig = sum(s['original_size'] for s in stats)
    total_conv = sum(s['converted_size'] for s in stats)

    print(f"\n{Fore.GREEN}Files converted: {len(stats)}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Format: PNG (with transparency)")
    print(f"{Fore.YELLOW}Size summary:{Style.RESET_ALL}")
    print(f"   Original: {Fore.CYAN}{humanize.naturalsize(total_orig)}{Style.RESET_ALL}")
    print(f"   Converted: {Fore.CYAN}{humanize.naturalsize(total_conv)}{Style.RESET_ALL}")

    delta = total_conv - total_orig
    sign = "↑" if delta > 0 else "↓"
    color = Fore.RED if delta > 0 else Fore.GREEN
    print(f"   Change: {sign} {color}{humanize.naturalsize(abs(delta))}{Style.RESET_ALL}")

    if stats:
        top3 = sorted(stats, key=lambda x: x['converted_size'], reverse=True)[:3]
        print(f"\n{Fore.YELLOW}Top 3 largest outputs:{Style.RESET_ALL}")
        for s in top3:
            ratio = s['converted_size'] / s['original_size'] if s['original_size'] else 1
            print(f"   • {s['filename']}: {humanize.naturalsize(s['original_size'])} → "
                  f"{humanize.naturalsize(s['converted_size'])} ({ratio:.2f}x)")

def main():
    while True:
        print_header()
        ask_output_format()
        stats = convert_files()

        if stats is None:
            continue

        if stats:
            print_summary(stats)

        print(f"\n{Fore.CYAN}Ready for next conversion.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Enter to restart, or Q to quit.{Style.RESET_ALL}")
        choice = input().strip().lower()
        if choice in ('q', 'quit'):
            print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")