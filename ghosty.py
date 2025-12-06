#!/usr/bin/env python3
"""
Ghosty Todo - A minimalist todo list manager
By AK
"""
import os
import sys
import json
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path

# -------------------------
# Theme System
# -------------------------
THEMES = {
    "Ghosty Classic": {
        "name": "Ghosty Classic",
        "colors": {
            "light_grey": (180, 180, 190),
            "dark_grey": (120, 120, 130),
            "white": (245, 245, 245),
            "ghost_purple": (140, 120, 170),
            "haunted_green": (140, 200, 170),
            "shadow_blue": (120, 160, 200),
            "yellow": (230, 200, 120),
            "red": (220, 80, 80),
            "cyan_faint": (150, 220, 220),
            "banner_start": (110, 110, 115),
            "banner_end": (240, 240, 245)
        }
    },
    "Dracula": {
        "name": "Dracula",
        "colors": {
            "light_grey": (189, 147, 249),  # Purple
            "dark_grey": (139, 233, 253),   # Cyan
            "white": (248, 248, 242),       # Foreground
            "ghost_purple": (189, 147, 249), # Purple
            "haunted_green": (80, 250, 123), # Green
            "shadow_blue": (139, 233, 253),  # Cyan
            "yellow": (241, 250, 140),      # Yellow
            "red": (255, 85, 85),           # Red
            "cyan_faint": (139, 233, 253),  # Cyan
            "banner_start": (68, 71, 90),   # Dracula Background
            "banner_end": (189, 147, 249)   # Dracula Purple
        }
    },
    "Tokyo Dark": {
        "name": "Tokyo Dark",
        "colors": {
            "light_grey": (148, 162, 199),  # Purple
            "dark_grey": (105, 118, 155),   # Cyan
            "white": (141, 152, 182),       # Foreground
            "ghost_purple": (255, 204, 100), # Purple
            "haunted_green": (126, 193, 95), # Green
            "shadow_blue": (113, 90, 255),  # Cyan
            "yellow": (107, 72, 153),      # Yellow
            "red": (255, 72, 65),           # Red
            "cyan_faint": (86, 93, 139),  # Cyan
            "banner_start": (169, 175, 214),   # Dracula Background
            "banner_end": (107, 116, 182)   # Dracula Purple
        }        
    }
}

class G:
    END = '\033[0m'
    BOLD = '\033[1m'
    
    # These will be set by the theme
    LIGHT_GREY = ''
    DARK_GREY = ''
    WHITE = ''
    GHOST_PURPLE = ''
    HAUNTED_GREEN = ''
    SHADOW_BLUE = ''
    YELLOW = ''
    RED = ''
    CYAN_FAINT = ''

def load_theme(theme_name="Ghosty Classic"):
    """Load a theme by name"""
    theme = THEMES.get(theme_name, THEMES["Ghosty Classic"])
    colors = theme["colors"]
    
    G.LIGHT_GREY = f'\033[38;2;{colors["light_grey"][0]};{colors["light_grey"][1]};{colors["light_grey"][2]}m'
    G.DARK_GREY = f'\033[38;2;{colors["dark_grey"][0]};{colors["dark_grey"][1]};{colors["dark_grey"][2]}m'
    G.WHITE = f'\033[38;2;{colors["white"][0]};{colors["white"][1]};{colors["white"][2]}m'
    G.GHOST_PURPLE = f'\033[38;2;{colors["ghost_purple"][0]};{colors["ghost_purple"][1]};{colors["ghost_purple"][2]}m'
    G.HAUNTED_GREEN = f'\033[38;2;{colors["haunted_green"][0]};{colors["haunted_green"][1]};{colors["haunted_green"][2]}m'
    G.SHADOW_BLUE = f'\033[38;2;{colors["shadow_blue"][0]};{colors["shadow_blue"][1]};{colors["shadow_blue"][2]}m'
    G.YELLOW = f'\033[38;2;{colors["yellow"][0]};{colors["yellow"][1]};{colors["yellow"][2]}m'
    G.RED = f'\033[38;2;{colors["red"][0]};{colors["red"][1]};{colors["red"][2]}m'
    G.CYAN_FAINT = f'\033[38;2;{colors["cyan_faint"][0]};{colors["cyan_faint"][1]};{colors["cyan_faint"][2]}m'
    
    return colors

# -------------------------
# UI / Color helpers
# -------------------------
def set_terminal_title(title: str):
    try:
        if os.name == 'nt':
            os.system(f'title {title}')
        else:
            sys.stdout.write(f"\33]0;{title}\a")
            sys.stdout.flush()
    except Exception:
        pass

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def gradient_text(text, start_rgb, end_rgb):
    lines = text.splitlines()
    out_lines = []
    for line in lines:
        length = max(1, len(line))
        parts = []
        for i, ch in enumerate(line):
            t = i / (length - 1) if length > 1 else 0
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t)
            parts.append(f"\033[38;2;{r};{g};{b}m{ch}")
        out_lines.append(''.join(parts) + G.END)
    return '\n'.join(out_lines)

def clear_line():
    """Clear the current line"""
    print("\033[K", end="")

def move_cursor_up(lines=1):
    """Move cursor up specified number of lines"""
    print(f"\033[{lines}F", end="")

def show_error(message, duration=1.0):
    """Display error message for specified duration"""
    print(f"{G.RED}{message}{G.END}")
    sys.stdout.flush()
    time.sleep(duration)
    move_cursor_up()
    clear_line()

def show_success(message, duration=0.5, force_show=False):
    """Display success message if enabled in config"""
    config = load_config()
    show_responses = config.get("show_responses", True)
    
    if show_responses or force_show:
        print(f"{G.HAUNTED_GREEN}{message}{G.END}")
        sys.stdout.flush()
        time.sleep(duration)
        move_cursor_up()
        clear_line()

def show_info(message, duration=0.5):
    """Display info message"""
    print(f"{G.CYAN_FAINT}{message}{G.END}")
    sys.stdout.flush()
    time.sleep(duration)
    move_cursor_up()
    clear_line()

# Alternate banner - ASCII empty
ALTERNATE_BANNER = r"""
       ________.__                    __          
      /  _____/|  |__   ____  _______/  |_ ___.__.
     /   \  ___|  |  \ /  _ \/  ___/\   __<   |  |
     \    \_\  \   Y  (  <_> )___ \  |  |  \___  |
      \______  /___|  /\____/____  > |__|  / ____|
             \/     \/           \/        \/     
"""

BANNER = r"""
   ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗██╗   ██╗
  ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝╚██╗ ██╔╝
  ██║  ███╗███████║██║   ██║███████╗   ██║    ╚████╔╝ 
  ██║   ██║██╔══██║██║   ██║╚════██║   ██║     ╚██╔╝  
  ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║      ██║   
   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝      ╚═╝   
"""

def center_text(text, width=56):
    return text.center(width)

def print_banner():
    config = load_config()
    hide_banner = config.get("hide_banner", False)
    if hide_banner:
        return
    
    use_alternate = config.get("alternate_banner", False)
    banner_text = ALTERNATE_BANNER if use_alternate else BANNER
    
    colors = load_theme(config.get("theme", "Ghosty Classic"))
    start_rgb = colors["banner_start"]
    end_rgb = colors["banner_end"]
    
    grad = gradient_text(banner_text, start_rgb, end_rgb)
    print(grad)
    print(f"{G.GHOST_PURPLE}{G.BOLD}{center_text('[ Ghosty - The ghost in your machine ]', 56)}{G.END}")
    print(f"{G.SHADOW_BLUE}{center_text('[ Made with love - By AK ]', 56)}{G.END}")

# -------------------------
# Data Management
# -------------------------
def get_data_dir():
    """Get data directory - portable if portable.txt exists in script dir"""
    script_dir = Path(__file__).parent.absolute()
    portable_marker = script_dir / "portable.txt"
    
    if portable_marker.exists():
        # Portable mode: store data in script directory
        return script_dir / ".ghosty_data"
    else:
        # Normal mode: store in user home directory
        return Path.home() / ".ghosty_todo"

DATA_DIR = get_data_dir()
TODO_FILE = DATA_DIR / "todos.json"
CONFIG_FILE = DATA_DIR / "config.json"

def ensure_data_dir():
    """Ensure data directory exists and portable marker if needed"""
    # Re-check in case DATA_DIR wasn't set yet
    DATA_DIR = get_data_dir()
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    return DATA_DIR

def load_todos():
    """Load todos from JSON file"""
    if not TODO_FILE.exists():
        return []
    try:
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_todos(todos):
    """Save todos to JSON file"""
    ensure_data_dir()
    try:
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{G.RED}Error saving todos: {e}{G.END}")

def load_config():
    """Load configuration"""
    if not CONFIG_FILE.exists():
        return {
            "current_focus": "default", 
            "focuses": ["default"],
            "theme": "Ghosty Classic",
            "alternate_banner": False,
            "hide_banner": False,
            "reprint_list": True,
            "show_responses": True
        }
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Ensure required keys exist
            if "focuses" not in config:
                config["focuses"] = ["default"]
            if "current_focus" not in config:
                config["current_focus"] = "default"
            if "theme" not in config:
                config["theme"] = "Ghosty Classic"
            if "alternate_banner" not in config:
                config["alternate_banner"] = False
            if "hide_banner" not in config:
                config["hide_banner"] = False
            if "reprint_list" not in config:
                config["reprint_list"] = True
            if "show_responses" not in config:
                config["show_responses"] = True
            
            # Ensure current focus is in focuses list
            if config["current_focus"] not in config["focuses"]:
                config["focuses"].append(config["current_focus"])
            
            # Load theme colors
            load_theme(config["theme"])
            
            return config
    except Exception:
        return {
            "current_focus": "default", 
            "focuses": ["default"],
            "theme": "Ghosty Classic",
            "alternate_banner": False,
            "hide_banner": False,
            "reprint_list": True,
            "show_responses": True
        }

def save_config(config):
    """Save configuration"""
    ensure_data_dir()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{G.RED}Error saving config: {e}{G.END}")

def time_ago(date_str):
    """Calculate time ago from ISO date string"""
    try:
        created = datetime.fromisoformat(date_str)
        delta = datetime.now() - created
        
        total_seconds = delta.total_seconds()
        
        if total_seconds < 60:
            return "now"
        elif total_seconds < 3600:  # Less than 1 hour
            mins = int(total_seconds / 60)
            return f"{mins}m"
        elif total_seconds < 86400:  # Less than 1 day
            hours = int(total_seconds / 3600)
            return f"{hours}h"
        elif delta.days == 1:
            return "1d"
        else:
            return f"{delta.days}d"
    except Exception:
        return ""

# -------------------------
# Settings Menus
# -------------------------
def themes_menu():
    """Themes selection menu"""
    while True:
        config = load_config()
        current_theme = config.get("theme", "Ghosty Classic")
        
        clear()
        print_banner()
        print(f"\n{G.BOLD}{G.GHOST_PURPLE}[ THEMES ]{G.END}")
        
        # List available themes
        themes = list(THEMES.keys())
        for idx, theme in enumerate(themes, 1):
            star = f" {G.YELLOW}★{G.END}" if theme == current_theme else ""
            print(f"{G.CYAN_FAINT}{idx}.{G.END} {G.WHITE}{theme}{star}{G.END}")
        
        print()
        print(f"{G.CYAN_FAINT}[s]{G.END} select {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[b]{G.END} back")
        
        choice = input(f"{G.CYAN_FAINT}choose:{G.END} ").strip().lower()
        
        if choice == 's':
            try:
                idx = int(input(f"{G.CYAN_FAINT}Select theme number:{G.END} ").strip()) - 1
                if 0 <= idx < len(themes):
                    selected = themes[idx]
                    config["theme"] = selected
                    save_config(config)
                    show_success(f"✔ Theme set to: {selected}", 1.0)
                else:
                    show_error("✖ Invalid theme number")
            except (ValueError, IndexError):
                show_error("✖ Invalid input")
        
        elif choice == 'b':
            break
        elif choice != '':
            show_error("✖ Invalid choice")

def appearance_menu():
    """Appearance settings menu"""
    while True:
        config = load_config()
        
        clear()
        print_banner()
        print(f"\n{G.BOLD}{G.GHOST_PURPLE}[ APPEARANCE ]{G.END}")
        
        alternate_banner = config.get("alternate_banner", False)
        hide_banner = config.get("hide_banner", False)
        
        print(f"{G.CYAN_FAINT}1.{G.END} Alternate Banner: {G.HAUNTED_GREEN if alternate_banner else G.RED}{'ON' if alternate_banner else 'OFF'}{G.END}")
        print(f"{G.CYAN_FAINT}2.{G.END} Hide Banner in Menus: {G.HAUNTED_GREEN if hide_banner else G.RED}{'ON' if hide_banner else 'OFF'}{G.END}")
        
        print()
        print(f"{G.CYAN_FAINT}[s]{G.END} select {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[b]{G.END} back")
        
        choice = input(f"{G.CYAN_FAINT}choose:{G.END} ").strip().lower()
        
        if choice == 's':
            try:
                option = int(input(f"{G.CYAN_FAINT}Select option number:{G.END} ").strip())
                if option == 1:
                    config["alternate_banner"] = not config.get("alternate_banner", False)
                    status = "ON" if config["alternate_banner"] else "OFF"
                    show_success(f"✔ Alternate Banner: {status}", 1.0)
                elif option == 2:
                    config["hide_banner"] = not config.get("hide_banner", False)
                    status = "ON" if config["hide_banner"] else "OFF"
                    show_success(f"✔ Hide Banner: {status}", 1.0)
                else:
                    show_error("✖ Invalid option")
                save_config(config)
            except ValueError:
                show_error("✖ Invalid input")
        
        elif choice == 'b':
            break
        elif choice != '':
            show_error("✖ Invalid choice")

def preferences_menu():
    """Preferences settings menu"""
    while True:
        config = load_config()
        
        clear()
        print_banner()
        print(f"\n{G.BOLD}{G.GHOST_PURPLE}[ PREFERENCES ]{G.END}")
        
        reprint_list = config.get("reprint_list", True)
        show_responses = config.get("show_responses", True)
        
        print(f"{G.CYAN_FAINT}1.{G.END} Reprint list after CLI commands: {G.HAUNTED_GREEN if reprint_list else G.RED}{'ON' if reprint_list else 'OFF'}{G.END}")
        print(f"{G.CYAN_FAINT}2.{G.END} Show success responses: {G.HAUNTED_GREEN if show_responses else G.RED}{'ON' if show_responses else 'OFF'}{G.END}")
        
        print()
        print(f"{G.CYAN_FAINT}[s]{G.END} select {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[b]{G.END} back")
        
        choice = input(f"{G.CYAN_FAINT}choose:{G.END} ").strip().lower()
        
        if choice == 's':
            try:
                option = int(input(f"{G.CYAN_FAINT}Select option number:{G.END} ").strip())
                if option == 1:
                    config["reprint_list"] = not config.get("reprint_list", True)
                    status = "ON" if config["reprint_list"] else "OFF"
                    show_success(f"✔ Reprint list: {status}", 1.0)
                    save_config(config)
                elif option == 2:
                    config["show_responses"] = not config.get("show_responses", True)
                    status = "ON" if config["show_responses"] else "OFF"
                    show_success(f"✔ Show responses: {status}", 1.0, force_show=True)
                    save_config(config)
                else:
                    show_error("✖ Invalid option")
            except ValueError:
                show_error("✖ Invalid input")
        
        elif choice == 'b':
            break
        elif choice != '':
            show_error("✖ Invalid choice")

def help_menu():
    """Display help information"""
    while True:
        clear()
        print_banner()
        print(f"\n{G.BOLD}{G.GHOST_PURPLE}[ HELP ]{G.END}")
        
        print(f"{G.WHITE}{G.BOLD}Interactive Mode:{G.END}")
        print(f"  {G.CYAN_FAINT}[1]{G.END} To-Do List")
        print(f"  {G.CYAN_FAINT}[2]{G.END} Edit Focuses")
        print(f"  {G.CYAN_FAINT}[3]{G.END} Settings")
        print(f"  {G.CYAN_FAINT}[0]{G.END} Exit")
        
        print(f"\n{G.WHITE}{G.BOLD}To-Do List Commands:{G.END}")
        print(f"  {G.CYAN_FAINT}[a]{G.END} Add new todo")
        print(f"  {G.CYAN_FAINT}[c]{G.END} Check/uncheck todo(s)")
        print(f"  {G.CYAN_FAINT}[h]{G.END} Hold/unhold todo(s)")
        print(f"  {G.CYAN_FAINT}[r]{G.END} Remove todo(s)")
        print(f"  {G.CYAN_FAINT}[b]{G.END} Back to main menu")
        
        print(f"\n{G.WHITE}{G.BOLD}CLI Commands:{G.END}")
        print(f"  {G.CYAN_FAINT}ghosty list{ G.END} (or ls)")
        print(f"  {G.CYAN_FAINT}ghosty add <text>{G.END} (or a)")
        print(f"  {G.CYAN_FAINT}ghosty check <numbers>{G.END} (or c)")
        print(f"  {G.CYAN_FAINT}ghosty hold <numbers>{G.END} (or h)")
        print(f"  {G.CYAN_FAINT}ghosty remove <numbers>{G.END} (or r/rm)")
        
        print(f"\n{G.WHITE}{G.BOLD}Number Formats:{G.END}")
        print(f"  Single: {G.CYAN_FAINT}1{G.END}")
        print(f"  Multiple: {G.CYAN_FAINT}1 3 5{G.END}")
        print(f"  Ranges: {G.CYAN_FAINT}1-5{G.END} or {G.CYAN_FAINT}3-5 7 9-11{G.END}")
        
        print(f"\n{G.WHITE}{G.BOLD}Examples:{G.END}")
        print(f"  {G.CYAN_FAINT}ghosty check 1 3-5{G.END}")
        print(f"  {G.CYAN_FAINT}ghosty remove 2 4-6{G.END}")
        print(f"  {G.CYAN_FAINT}ghosty add \"Buy groceries\"{G.END}")
        
        print()
        print(f"{G.CYAN_FAINT}[b]{G.END} back")
        
        choice = input(f"{G.CYAN_FAINT}choose:{G.END} ").strip().lower()
        
        if choice == 'b':
            break
        elif choice != '':
            show_error("✖ Invalid choice")

def settings_menu():
    """Main settings menu"""
    while True:
        clear()
        print_banner()
        print(f"\n{G.BOLD}{G.GHOST_PURPLE}[ SETTINGS ]{G.END}")
        
        print(f"{G.HAUNTED_GREEN}[1]{G.END}  Themes")
        print(f"{G.HAUNTED_GREEN}[2]{G.END}  Appearance")
        print(f"{G.HAUNTED_GREEN}[3]{G.END}  Preferences")
        print(f"{G.HAUNTED_GREEN}[4]{G.END}  Help")
        print(f"{G.RED}[b]{G.END}  Back to Main Menu")
        
        print()
        choice = input(f"{G.BOLD}{G.CYAN_FAINT}settings>{G.END} ").strip().lower()
        
        if choice == '1':
            themes_menu()
        elif choice == '2':
            appearance_menu()
        elif choice == '3':
            preferences_menu()
        elif choice == '4':
            help_menu()
        elif choice == 'b':
            break
        else:
            show_error("✖ Invalid choice")

# -------------------------
# Focuses Menu
# -------------------------
def edit_focuses_menu():
    """Interactive focuses management menu"""
    while True:
        config = load_config()
        current_focus = config.get("current_focus", "default")
        focuses = config.get("focuses", ["default"])
        
        clear()
        print_banner()
        print(f"\n{G.BOLD}{G.GHOST_PURPLE}[ FOCUSES ]{G.END}")
        
        # Display focuses
        for idx, focus in enumerate(focuses, 1):
            star = f" {G.YELLOW}★{G.END}" if focus == current_focus else ""
            print(f"{G.CYAN_FAINT}{idx}.{G.END} {G.WHITE}{focus}{star}{G.END}")
        
        # Menu
        print()
        print(f"{G.CYAN_FAINT}[a]{G.END} add {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[r]{G.END} remove {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[s]{G.END} select {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[b]{G.END} back")
        
        choice = input(f"{G.CYAN_FAINT}choose:{G.END} ").strip().lower()
        
        if choice == 'a':
            name = input(f"{G.CYAN_FAINT}Focus name:{G.END} ").strip()
            if name:
                if name in focuses:
                    show_error(f"✖ Focus '{name}' already exists")
                else:
                    focuses.append(name)
                    config["focuses"] = focuses
                    save_config(config)
                    show_success(f"✔ Added focus: {name}", 1.0)
            else:
                show_error("✖ Focus name cannot be empty")
        
        elif choice == 'r':
            try:
                idx = int(input(f"{G.CYAN_FAINT}Focus number:{G.END} ").strip()) - 1
                if 0 <= idx < len(focuses):
                    focus_to_remove = focuses[idx]
                    if focus_to_remove == "default":
                        show_error("✖ Cannot remove default focus")
                    else:
                        # Check if it's the current focus
                        if focus_to_remove == current_focus:
                            config["current_focus"] = "default"
                        
                        # Remove the focus and all its todos
                        focuses.remove(focus_to_remove)
                        config["focuses"] = focuses
                        save_config(config)
                        
                        all_todos = load_todos()
                        all_todos = [t for t in all_todos if t.get('focus') != focus_to_remove]
                        save_todos(all_todos)
                        
                        show_success(f"✔ Removed focus: {focus_to_remove}", 1.0)
                else:
                    show_error("✖ Invalid focus number")
            except (ValueError, IndexError):
                show_error("✖ Invalid input")
        
        elif choice == 's':
            try:
                idx = int(input(f"{G.CYAN_FAINT}Select focus number:{G.END} ").strip()) - 1
                if 0 <= idx < len(focuses):
                    selected = focuses[idx]
                    config["current_focus"] = selected
                    save_config(config)
                    show_success(f"✔ Selected focus: @{selected}", 1.0)
                else:
                    show_error("✖ Invalid focus number")
            except (ValueError, IndexError):
                show_error("✖ Invalid input")
        
        elif choice == 'b':
            break
        elif choice != '':
            show_error("✖ Invalid choice")

# -------------------------
# Todo List UI
# -------------------------
def parse_numbers(input_str):
    """Parse comma-separated or space-separated numbers, including ranges"""
    numbers = []
    parts = input_str.replace(',', ' ').split()
    
    for part in parts:
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                numbers.extend(range(start, end + 1))
            except ValueError:
                pass
        else:
            try:
                numbers.append(int(part))
            except ValueError:
                pass
    
    # Remove duplicates and sort
    return sorted(set(numbers))

def display_todo_list(show_banner=True):
    """Display the todo list with all formatting"""
    config = load_config()
    current_focus = config.get("current_focus", "default")
    todos = [t for t in load_todos() if t.get('focus') == current_focus]
    
    if show_banner:
        clear()
        print_banner()
        print(f"\n{G.BOLD}{G.GHOST_PURPLE}[ TO-DO LIST ]{G.END}")
    
    # Calculate stats
    total = len(todos)
    done = sum(1 for t in todos if t.get('status') == 'done')
    on_hold = sum(1 for t in todos if t.get('status') == 'on-hold')
    pending = total - done - on_hold
    
    # Header with focus and stats (no indent)
    stats = f"[{done}/{total}]" if total > 0 else "[0/0]"
    print(f"{G.WHITE}@{current_focus}{G.END} {G.DARK_GREY}{stats}{G.END}")
    
    # Display todos (3 space indent)
    if not todos:
        print(f"   {G.LIGHT_GREY}(no todos yet){G.END}")
    else:
        for idx, item in enumerate(todos, 1):
            status = item.get('status', 'pending')
            if status == 'done':
                symbol = '✔'
                color = G.HAUNTED_GREEN
            elif status == 'on-hold':
                symbol = '●'
                color = G.YELLOW
            else:
                symbol = '☐'
                color = G.WHITE
            
            text = item.get('text', '')
            created = item.get('created', '')
            age = time_ago(created)
            age_display = f" {G.DARK_GREY}{age}{G.END}" if age else ""
            
            print(f"   {G.CYAN_FAINT}{idx}.{G.END} {color}{symbol} {text}{age_display}{G.END}")
    
    # Stats summary (lined up with todos - 3 space indent)
    print()
    if total > 0:
        percentage = int((done / total) * 100) if total > 0 else 0
        print(f"   {G.LIGHT_GREY}{percentage}% of all tasks complete.{G.END}")
        print(f"   {G.HAUNTED_GREEN}{done} done{G.END} {G.LIGHT_GREY}•{G.END} {G.YELLOW}{on_hold} on-hold{G.END} {G.LIGHT_GREY}•{G.END} {G.WHITE}{pending} pending{G.END}")
    
    # Menu (only show in interactive mode, no indent)
    if show_banner:
        print()
        print(f"{G.CYAN_FAINT}[a]{G.END} add {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[c]{G.END} check/uncheck {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[h]{G.END} hold {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[r]{G.END} remove {G.LIGHT_GREY}•{G.END} {G.CYAN_FAINT}[b]{G.END} back")
    
    return todos

def todo_list_menu():
    """Interactive todo list menu with multi-command support"""
    config = load_config()
    current_focus = config.get("current_focus", "default")
    
    while True:
        todos = display_todo_list()
        all_todos = load_todos()
        
        choice = input(f"{G.CYAN_FAINT}choose:{G.END} ").strip().lower()
        
        if choice == 'a':
            text = input(f"{G.CYAN_FAINT}New todo:{G.END} ").strip()
            if text:
                new_todo = {
                    'text': text,
                    'status': 'pending',
                    'focus': current_focus,
                    'created': datetime.now().isoformat()
                }
                all_todos.append(new_todo)
                save_todos(all_todos)
                show_success(f"✔ Added: \"{text}\"", 1.0)
            else:
                show_error("✖ Todo text cannot be empty")
        
        elif choice == 'c':
            numbers_input = input(f"{G.CYAN_FAINT}Todo number(s):{G.END} ").strip()
            numbers = parse_numbers(numbers_input)
            
            if not numbers:
                show_error("✖ No valid numbers provided")
                continue
            
            # Process numbers in reverse to avoid index shifting issues
            numbers = sorted(numbers, reverse=True)
            checked_count = 0
            unchecked_count = 0
            for num in numbers:
                idx = num - 1
                if 0 <= idx < len(todos):
                    # Find the actual todo in all_todos
                    todo_to_update = todos[idx]
                    for t in all_todos:
                        if (t.get('text') == todo_to_update.get('text') and 
                            t.get('created') == todo_to_update.get('created')):
                            if t.get('status') == 'done':
                                t['status'] = 'pending'
                                print(f"{G.YELLOW}✖ Unchecked:{G.END} {t['text']}")
                                unchecked_count += 1
                            else:
                                t['status'] = 'done'
                                print(f"{G.HAUNTED_GREEN}✔ Checked:{G.END} {t['text']}")
                                checked_count += 1
                            break
                else:
                    show_error(f"✖ Invalid todo number: {num}")
                    continue
                time.sleep(0.2)  # Brief pause between updates
            
            save_todos(all_todos)
            if checked_count > 0 or unchecked_count > 0:
                summary = []
                if checked_count > 0:
                    summary.append(f"{checked_count} checked")
                if unchecked_count > 0:
                    summary.append(f"{unchecked_count} unchecked")
                show_success(f"✔ {', '.join(summary)}", 1.0)
        
        elif choice == 'h':
            numbers_input = input(f"{G.CYAN_FAINT}Todo number(s):{G.END} ").strip()
            numbers = parse_numbers(numbers_input)
            
            if not numbers:
                show_error("✖ No valid numbers provided")
                continue
            
            # Process numbers in reverse to avoid index shifting issues
            numbers = sorted(numbers, reverse=True)
            held_count = 0
            unheld_count = 0
            for num in numbers:
                idx = num - 1
                if 0 <= idx < len(todos):
                    todo_to_update = todos[idx]
                    for t in all_todos:
                        if (t.get('text') == todo_to_update.get('text') and 
                            t.get('created') == todo_to_update.get('created')):
                            if t.get('status') == 'on-hold':
                                t['status'] = 'pending'
                                print(f"{G.YELLOW}✔ Unhold:{G.END} {t['text']}")
                                unheld_count += 1
                            else:
                                t['status'] = 'on-hold'
                                print(f"{G.YELLOW}✔ On hold:{G.END} {t['text']}")
                                held_count += 1
                            break
                else:
                    show_error(f"✖ Invalid todo number: {num}")
                    continue
                time.sleep(0.2)  # Brief pause between updates
            
            save_todos(all_todos)
            if held_count > 0 or unheld_count > 0:
                summary = []
                if held_count > 0:
                    summary.append(f"{held_count} on hold")
                if unheld_count > 0:
                    summary.append(f"{unheld_count} unheld")
                show_success(f"✔ {', '.join(summary)}", 1.0)
        
        elif choice == 'r':
            numbers_input = input(f"{G.CYAN_FAINT}Todo number(s):{G.END} ").strip()
            numbers = parse_numbers(numbers_input)
            
            if not numbers:
                show_error("✖ No valid numbers provided")
                continue
            
            # Sort in reverse to avoid index shifting issues
            numbers = sorted(numbers, reverse=True)
            removed_count = 0
            for num in numbers:
                idx = num - 1
                if 0 <= idx < len(todos):
                    todo_to_remove = todos[idx]
                    all_todos = [t for t in all_todos if not (
                        t.get('text') == todo_to_remove.get('text') and
                        t.get('created') == todo_to_remove.get('created')
                    )]
                    print(f"{G.RED}✖ Removed:{G.END} {todo_to_remove['text']}")
                    removed_count += 1
                    # Update todos list for next iteration
                    todos = [t for t in all_todos if t.get('focus') == current_focus]
                else:
                    show_error(f"✖ Invalid todo number: {num}")
                    continue
                time.sleep(0.2)  # Brief pause between updates
            
            save_todos(all_todos)
            if removed_count > 0:
                show_success(f"✔ Removed {removed_count} todo(s)", 1.0)
        
        elif choice == 'b':
            break
        elif choice != '':
            show_error("✖ Invalid choice")

# -------------------------
# Main Menu
# -------------------------
def main_menu():
    """Display and handle main menu"""
    while True:
        clear()
        print_banner()
        print()
        print(f"{G.BOLD}{G.CYAN_FAINT}═══════════════════════════════════════════════════════{G.END}")
        print(f"{G.HAUNTED_GREEN}[1]{G.END}  To-Do List")
        print(f"{G.HAUNTED_GREEN}[2]{G.END}  Edit Focuses")
        print(f"{G.HAUNTED_GREEN}[3]{G.END}  Settings")
        print(f"{G.RED}[0]{G.END}  Exit")
        print(f"{G.BOLD}{G.CYAN_FAINT}═══════════════════════════════════════════════════════{G.END}")
        print()
        
        choice = input(f"{G.BOLD}{G.CYAN_FAINT}ghosty>{G.END} ").strip()
        
        if choice == '1':
            todo_list_menu()
        elif choice == '2':
            edit_focuses_menu()
        elif choice == '3':
            settings_menu()
        elif choice == '0':
            goodbye_and_exit()
        else:
            show_error("✖ Invalid choice")

def goodbye_and_exit():
    """Exit with goodbye message"""
    print(f"\n{G.GHOST_PURPLE}Thanks for using Ghosty - By AK! Stay spooky! 👻{G.END}\n")
    time.sleep(1.5)
    clear()
    set_terminal_title("Ghosty - By AK - Goodbye")
    sys.exit(0)

# -------------------------
# CLI Interface
# -------------------------
def setup_cli():
    """Setup argparse CLI interface with range support"""
    parser = argparse.ArgumentParser(
        prog='ghosty',
        description='Ghosty Todo - A minimalist todo list manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ghosty list                            Show todos
  ghosty add "Buy groceries"             Add a todo
  ghosty check 1 3-5                     Check todos 1, 3, 4, 5
  ghosty hold 2-4                        Hold todos 2, 3, 4
  ghosty remove 1 3-5 7                  Remove todos 1, 3, 4, 5, 7

Number Formats:
  Single: 1
  Multiple: 1 3 5
  Ranges: 1-5 or 3-5 7 9-11
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', aliases=['ls'], help='List all todos')
    
    # Add command
    add_parser = subparsers.add_parser('add', aliases=['a'], help='Add a new todo')
    add_parser.add_argument('text', nargs='+', help='Todo text (supports multiple todos)')
    
    # Check/uncheck command - accept strings for ranges
    check_parser = subparsers.add_parser('check', aliases=['c'], help='Check/uncheck a todo')
    check_parser.add_argument('numbers', nargs='+', help='Todo number(s) or ranges (e.g., 1 3-5 7)')
    
    # Hold command - accept strings for ranges
    hold_parser = subparsers.add_parser('hold', aliases=['h'], help='Toggle hold status')
    hold_parser.add_argument('numbers', nargs='+', help='Todo number(s) or ranges (e.g., 1 3-5 7)')
    
    # Remove command - accept strings for ranges
    remove_parser = subparsers.add_parser('remove', aliases=['r', 'rm'], help='Remove a todo')
    remove_parser.add_argument('numbers', nargs='+', help='Todo number(s) or ranges (e.g., 1 3-5 7)')
    
    # Help command
    help_parser = subparsers.add_parser('help', aliases=['?'], help='Show help information')
    
    return parser

def handle_cli(args):
    """Handle CLI commands with range support"""
    config = load_config()
    current_focus = config.get("current_focus", "default")
    all_todos = load_todos()
    todos = [t for t in all_todos if t.get('focus') == current_focus]
    
    if args.command in ['list', 'ls']:
        display_todo_list(show_banner=False)
        return
    
    elif args.command in ['help', '?']:
        # Show CLI help
        parser = setup_cli()
        parser.print_help()
        return
    
    elif args.command in ['add', 'a']:
        # Join text arguments that might be split
        if hasattr(args, 'text'):
            text = ' '.join(args.text)
        else:
            text = ''
            
        if text:
            new_todo = {
                'text': text,
                'status': 'pending',
                'focus': current_focus,
                'created': datetime.now().isoformat()
            }
            all_todos.append(new_todo)
            save_todos(all_todos)
            print(f"{G.HAUNTED_GREEN}✔ Added:{G.END} \"{text}\"")
        else:
            print(f"{G.RED}✖ No todo text provided{G.END}")
            return
        
        # Reprint list if enabled
        if config.get("reprint_list", True):
            print()
            display_todo_list(show_banner=False)
    
    elif args.command in ['check', 'c']:
        if not hasattr(args, 'numbers') or not args.numbers:
            print(f"{G.RED}✖ No numbers provided{G.END}")
            return
        
        # Parse numbers including ranges
        numbers_input = ' '.join(map(str, args.numbers))
        numbers = parse_numbers(numbers_input)
        
        if not numbers:
            print(f"{G.RED}✖ No valid numbers provided{G.END}")
            return
            
        # Process in reverse to avoid index shifting
        numbers = sorted(numbers, reverse=True)
        checked_count = 0
        unchecked_count = 0
        for num in numbers:
            idx = num - 1
            if 0 <= idx < len(todos):
                todo_to_update = todos[idx]
                for t in all_todos:
                    if (t.get('text') == todo_to_update.get('text') and 
                        t.get('created') == todo_to_update.get('created')):
                        if t.get('status') == 'done':
                            t['status'] = 'pending'
                            print(f"{G.YELLOW}✖ Unchecked:{G.END} {t['text']}")
                            unchecked_count += 1
                        else:
                            t['status'] = 'done'
                            print(f"{G.HAUNTED_GREEN}✔ Checked:{G.END} {t['text']}")
                            checked_count += 1
                        break
            else:
                print(f"{G.RED}Invalid todo number: {num}{G.END}")
        save_todos(all_todos)
        
        if checked_count > 0 or unchecked_count > 0:
            summary = []
            if checked_count > 0:
                summary.append(f"{checked_count} checked")
            if unchecked_count > 0:
                summary.append(f"{unchecked_count} unchecked")
            print(f"{G.HAUNTED_GREEN}✔ {', '.join(summary)}{G.END}")
        
        # Reprint list if enabled
        if config.get("reprint_list", True):
            print()
            display_todo_list(show_banner=False)
    
    elif args.command in ['hold', 'h']:
        if not hasattr(args, 'numbers') or not args.numbers:
            print(f"{G.RED}✖ No numbers provided{G.END}")
            return
        
        # Parse numbers including ranges
        numbers_input = ' '.join(map(str, args.numbers))
        numbers = parse_numbers(numbers_input)
        
        if not numbers:
            print(f"{G.RED}✖ No valid numbers provided{G.END}")
            return
            
        # Process in reverse to avoid index shifting
        numbers = sorted(numbers, reverse=True)
        held_count = 0
        unheld_count = 0
        for num in numbers:
            idx = num - 1
            if 0 <= idx < len(todos):
                todo_to_update = todos[idx]
                for t in all_todos:
                    if (t.get('text') == todo_to_update.get('text') and 
                        t.get('created') == todo_to_update.get('created')):
                        if t.get('status') == 'on-hold':
                            t['status'] = 'pending'
                            print(f"{G.YELLOW}✔ Unhold:{G.END} {t['text']}")
                            unheld_count += 1
                        else:
                            t['status'] = 'on-hold'
                            print(f"{G.YELLOW}✔ On hold:{G.END} {t['text']}")
                            held_count += 1
                        break
            else:
                print(f"{G.RED}Invalid todo number: {num}{G.END}")
        save_todos(all_todos)
        
        if held_count > 0 or unheld_count > 0:
            summary = []
            if held_count > 0:
                summary.append(f"{held_count} on hold")
            if unheld_count > 0:
                summary.append(f"{unheld_count} unheld")
            print(f"{G.HAUNTED_GREEN}✔ {', '.join(summary)}{G.END}")
        
        # Reprint list if enabled
        if config.get("reprint_list", True):
            print()
            display_todo_list(show_banner=False)
    
    elif args.command in ['remove', 'r', 'rm']:
        if not hasattr(args, 'numbers') or not args.numbers:
            print(f"{G.RED}✖ No numbers provided{G.END}")
            return
        
        # Parse numbers including ranges
        numbers_input = ' '.join(map(str, args.numbers))
        numbers = parse_numbers(numbers_input)
        
        if not numbers:
            print(f"{G.RED}✖ No valid numbers provided{G.END}")
            return
            
        # Sort in reverse to avoid index shifting issues
        numbers = sorted(numbers, reverse=True)
        removed_count = 0
        for num in numbers:
            idx = num - 1
            if 0 <= idx < len(todos):
                todo_to_remove = todos[idx]
                all_todos = [t for t in all_todos if not (
                    t.get('text') == todo_to_remove.get('text') and
                    t.get('created') == todo_to_remove.get('created')
                )]
                print(f"{G.RED}✖ Removed:{G.END} {todo_to_remove['text']}")
                removed_count += 1
                # Update todos list for next iteration
                todos = [t for t in all_todos if t.get('focus') == current_focus]
            else:
                print(f"{G.RED}Invalid todo number: {num}{G.END}")
        save_todos(all_todos)
        
        if removed_count > 0:
            print(f"{G.HAUNTED_GREEN}✔ Removed {removed_count} todo(s){G.END}")
        
        # Reprint list if enabled
        if config.get("reprint_list", True):
            print()
            display_todo_list(show_banner=False)

# -------------------------
# Main Entry Point
# -------------------------
def main():
    """Main entry point"""
    set_terminal_title("Ghosty Todo - By AK")
    
    # Ensure data directory exists (this will set DATA_DIR correctly)
    global DATA_DIR, TODO_FILE, CONFIG_FILE
    DATA_DIR = ensure_data_dir()
    TODO_FILE = DATA_DIR / "todos.json"
    CONFIG_FILE = DATA_DIR / "config.json"
    
    # Load config to set theme
    config = load_config()
    load_theme(config.get("theme", "Ghosty Classic"))
    
    parser = setup_cli()
    args = parser.parse_args()
    
    # If no command provided, launch interactive UI
    if not args.command:
        try:
            main_menu()
        except KeyboardInterrupt:
            print()
            goodbye_and_exit()
    else:
        # Handle CLI command
        handle_cli(args)

if __name__ == "__main__":
    main()