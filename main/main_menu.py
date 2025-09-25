#!/usr/bin/env python3
"""
main_menu.py

Enhanced Clash Royale Main Menu with Leaderboard, Instructions, and Settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import json
import os
from PIL import Image, ImageTk

class KeybindRecorder:
    """Handles keybind recording and validation"""
    
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.recording = False
        self.current_action = None
        self.current_button = None
        self.bound_widget = None
        
    def start_recording(self, action, button, modal_window=None):
        """Start recording a keybind for the specified action"""
        print(f"Starting recording for action: {action}")  # Debug
        self.recording = True
        self.current_action = action
        self.current_button = button
        
        # Update button appearance
        button.configure(text="Press key...", bootstyle="warning")
        
        # Bind to the modal window if provided, otherwise use parent
        self.bound_widget = modal_window if modal_window else self.parent
        
        print(f"Binding to widget: {self.bound_widget}")  # Debug
        self.bound_widget.bind('<Key>', self.on_key_press)
        self.bound_widget.focus_force()
    
    def on_key_press(self, event):
        """Handle key press during recording"""
        print(f"Key pressed: {event.keysym}, Recording: {self.recording}")  # Debug
        
        if not self.recording:
            return
            
        # Prevent certain keys from being bound
        forbidden_keys = ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 
                         'Alt_L', 'Alt_R', 'Super_L', 'Super_R', 'Caps_Lock']
        
        if event.keysym in forbidden_keys:
            messagebox.showwarning("Invalid Key", f"Cannot bind modifier key: {event.keysym}")
            self.cancel_recording()
            return
        
        # Get the key representation
        key = self.format_key(event)
        print(f"Formatted key: {key}")  # Debug
        
        if key:
            # Stop recording
            self.recording = False
            
            # Unbind the key event
            if self.bound_widget:
                self.bound_widget.unbind('<Key>')
            
            # Update the keybind through callback
            print(f"Calling callback with action={self.current_action}, key={key}")  # Debug
            self.callback(self.current_action, key)
            
            # Reset
            self.current_button = None
            self.current_action = None
            self.bound_widget = None
    
    def cancel_recording(self):
        """Cancel the current recording"""
        self.recording = False
        if self.current_button:
            # Get the callback's parent object to access settings_manager
            try:
                settings_manager = self.callback.__self__.settings_manager
                original_key = settings_manager.get_keybind(self.current_action)
                self.current_button.configure(text=original_key, bootstyle="primary")
            except:
                self.current_button.configure(text="Error", bootstyle="danger")
        
        # Unbind the key event
        if self.bound_widget:
            self.bound_widget.unbind('<Key>')
        
        # Rebind global keybinds
        try:
            self.callback.__self__.setup_keybinds()
        except:
            pass
        
        self.bound_widget = None
    
    def format_key(self, event):
        """Format key event into readable string"""
        # Handle special keys
        special_keys = {
            'Return': 'Enter',
            'Escape': 'Esc',
            'space': 'Space',
            'Tab': 'Tab',
            'BackSpace': 'Backspace',
            'Delete': 'Del',
            'Up': 'Up',
            'Down': 'Down',
            'Left': 'Left',
            'Right': 'Right'
        }
        
        if event.keysym in special_keys:
            return special_keys[event.keysym]
        elif len(event.keysym) == 1 and event.keysym.isalnum():
            return event.keysym.upper()
        elif event.keysym.startswith('F') and event.keysym[1:].isdigit():
            return event.keysym
        else:
            # For any other key, use the keysym as-is
            return event.keysym

class SettingsManager:
    """Manages game settings and keybinds"""
    
    def __init__(self):
        self.settings_file = "data/settings.json"
        self.ensure_data_dir()
        self.load_settings()
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def get_default_settings(self):
        """Get default settings"""
        return {
            "keybinds": {
                "new_game": "N",
                "instructions": "H",
                "leaderboard": "L",
                "settings": "S",
                "submit": "Enter",
                "close": "Esc"
            },
            "sound_enabled": True,
            "animations_enabled": True,
            "difficulty": "medium"
        }
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.get_default_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.get_default_settings()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_keybind(self, action):
        """Get keybind for action"""
        return self.settings.get("keybinds", {}).get(action, "")
    
    def set_keybind(self, action, key):
        """Set keybind for action"""
        if "keybinds" not in self.settings:
            self.settings["keybinds"] = {}
        
        # Check if key is already used
        for existing_action, existing_key in self.settings["keybinds"].items():
            if existing_key == key and existing_action != action:
                return False, f"Key '{key}' is already assigned to {existing_action}"
        
        self.settings["keybinds"][action] = key
        self.save_settings()
        return True, "Keybind updated successfully"
    
    def reset_keybinds(self):
        """Reset keybinds to defaults"""
        self.settings["keybinds"] = self.get_default_settings()["keybinds"]
        self.save_settings()

class LeaderboardManager:
    """Manages leaderboard data"""
    
    def __init__(self):
        self.leaderboard_file = "leaderboard.json"
        self.load_leaderboard()
    
    def load_leaderboard(self):
        """Load leaderboard from file"""
        try:
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r') as f:
                    data = json.load(f)
                    # Convert old format if needed
                    if isinstance(data, list) and data and isinstance(data[0], dict) and 'time' in data[0]:
                        # Old format - convert to new format
                        self.leaderboard = []
                        for entry in data:
                            self.leaderboard.append({
                                'name': entry.get('name', 'Anonymous'),
                                'score': max(1000 - int(entry.get('time', 60) * 10), 100),
                                'games': 1,
                                'win_rate': 100,
                                'best_time': entry.get('time', 60)
                            })
                    else:
                        self.leaderboard = data
            else:
                self.leaderboard = self.get_default_leaderboard()
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            self.leaderboard = self.get_default_leaderboard()
    
    def get_default_leaderboard(self):
        """Get default leaderboard"""
        return [
            {"name": "ClashMaster", "score": 2450, "games": 87, "win_rate": 94, "best_time": 15.2},
            {"name": "RoyalePro", "score": 2380, "games": 76, "win_rate": 91, "best_time": 18.7},
            {"name": "CardWizard", "score": 2250, "games": 102, "win_rate": 88, "best_time": 22.1},
            {"name": "ElixirKing", "score": 2190, "games": 65, "win_rate": 87, "best_time": 25.3},
            {"name": "TowerTaker", "score": 2050, "games": 93, "win_rate": 85, "best_time": 28.9}
        ]
    
    def get_sorted_leaderboard(self):
        """Get leaderboard sorted by score"""
        return sorted(self.leaderboard, key=lambda x: x.get('score', 0), reverse=True)

class ClashRoyaleMainMenu:
    """Enhanced Main Menu with all functionality"""
    
    def __init__(self, root, on_play=None, on_how_to_play=None, on_leaderboard=None, on_settings=None):
        self.root = root
        self.on_play = on_play
        self.on_how_to_play = on_how_to_play
        self.on_leaderboard = on_leaderboard
        self.on_settings = on_settings
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.leaderboard_manager = LeaderboardManager()
        self.keybind_recorder = KeybindRecorder(root, self.update_keybind)
        
        # Variables
        self.current_modal = None
        
        self.create_ui()
        self.setup_keybinds()
    
    def create_ui(self):
        """Create the main menu UI"""
        # Debug information
        import os
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        print(f"Files in parent directory: {os.listdir('..')}")
        print(f"Looking for: ../clash_royale_background.png")
        print(f"File exists: {os.path.exists('../clash_royale_background.png')}")
        
        # Try to load background image
        try:
            # Load the background image (look in parent directory)
            bg_image = Image.open("../clash_royale_background.png")
            print("Successfully loaded background image!")
            # Resize to fit window
            bg_image = bg_image.resize((1000, 800), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
            # Create canvas for background
            canvas = tk.Canvas(self.root, width=1000, height=800, highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            
            # Create frame on top of canvas with transparency effect
            main_frame = ttk.Frame(canvas, style='Transparent.TFrame')
            canvas.create_window(500, 400, window=main_frame, anchor="center")
            
        except Exception as e:
            print(f"Could not load background image: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to gradient background
            self.root.configure(bg='#2c3e50')
            main_frame = ttk.Frame(self.root, padding=40)
            main_frame.pack(fill="both", expand=True)
        
        # Create semi-transparent container for menu items
        container = ttk.Frame(main_frame, padding=40, relief="raised", borderwidth=2)
        container.pack()
        
        # Configure style for better visibility on background
        style = ttk.Style()
        style.configure('Title.TLabel', font=("Orbitron", 36, "bold"), foreground="#FFD700", background="#1a1a1a")
        style.configure('Subtitle.TLabel', font=("Orbitron", 16), foreground="#00BFFF", background="#1a1a1a")
        
        # Title with dark background for visibility
        title_frame = ttk.Frame(container, style='TFrame')
        title_frame.configure(relief="solid", borderwidth=0)
        title_frame.pack(pady=(0, 30))
        
        # Add dark semi-transparent background to title area
        title_bg = tk.Frame(title_frame, bg='#1a1a1a', padx=30, pady=20)
        title_bg.pack()
        
        title_label = tk.Label(
            title_bg, 
            text="CLASH ROYALE", 
            font=("Orbitron", 36, "bold"),
            foreground="#FFD700",
            bg='#1a1a1a'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_bg, 
            text="Guess Who Edition", 
            font=("Orbitron", 16),
            foreground="#00BFFF",
            bg='#1a1a1a'
        )
        subtitle_label.pack()
        
        # Menu buttons with better styling
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=20)
        
        # Play button (larger)
        self.play_btn = ttk.Button(
            button_frame,
            text="⚔️ PLAY GAME",
            command=self.start_game,
            bootstyle="success",
            width=30
        )
        self.play_btn.pack(pady=10)
        
        # Other buttons
        buttons_data = [
            ("🏆 LEADERBOARD", self.show_leaderboard, "warning"),
            ("📖 HOW TO PLAY", self.show_instructions, "info"),
            ("⚙️ SETTINGS", self.show_settings, "primary")
        ]
        
        for text, command, style in buttons_data:
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                bootstyle=style,
                width=30
            )
            btn.pack(pady=5)
        
        # Version info with dark background
        version_frame = tk.Frame(container, bg='#1a1a1a', padx=10, pady=5)
        version_frame.pack(side="bottom", pady=(20, 0))
        
        version_label = tk.Label(
            version_frame,
            text="v2.1.0 - Enhanced Edition",
            font=("Arial", 8),
            foreground="#7f8c8d",
            bg='#1a1a1a'
        )
        version_label.pack()
    
    def setup_keybinds(self):
        """Setup global keybinds"""
        # Clear any existing keybinds
        self.root.unbind('<KeyPress>')
        
        # Create mapping of keys to actions
        self.keybind_map = {}
        for action in ["new_game", "instructions", "leaderboard", "settings", "close"]:
            key = self.settings_manager.get_keybind(action).lower()
            self.keybind_map[key] = action
        
        def on_key_press(event):
            # Don't handle if we're recording a keybind
            if self.keybind_recorder.recording:
                return
            
            # Don't handle if focus is on an Entry widget (typing)
            focused_widget = self.root.focus_get()
            if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
                return
                
            key = event.keysym.lower()
            
            # Check for direct key match
            if key in self.keybind_map:
                action = self.keybind_map[key]
                if action == "new_game":
                    self.start_game()
                elif action == "instructions":
                    self.show_instructions()
                elif action == "leaderboard":
                    self.show_leaderboard()
                elif action == "settings":
                    self.show_settings()
                elif action == "close":
                    self.close_current_modal()
            
            # Also check uppercase version for letter keys
            elif key.upper() in self.keybind_map:
                action = self.keybind_map[key.upper()]
                if action == "new_game":
                    self.start_game()
                elif action == "instructions":
                    self.show_instructions()
                elif action == "leaderboard":
                    self.show_leaderboard()
                elif action == "settings":
                    self.show_settings()
                elif action == "close":
                    self.close_current_modal()
            
            # Handle special keys like 'Return' -> 'Enter'
            special_map = {
                'return': 'Enter',
                'escape': 'Esc',
                'space': 'Space'
            }
            if key in special_map:
                mapped_key = special_map[key].lower()
                if mapped_key in self.keybind_map:
                    action = self.keybind_map[mapped_key]
                    if action == "new_game":
                        self.start_game()
                    elif action == "instructions":
                        self.show_instructions()
                    elif action == "leaderboard":
                        self.show_leaderboard()
                    elif action == "settings":
                        self.show_settings()
                    elif action == "close":
                        self.close_current_modal()
        
        self.root.bind('<KeyPress>', on_key_press)
        self.root.focus_set()
    
    def start_game(self):
        """Start the game"""
        if self.on_play:
            self.on_play()
        else:
            messagebox.showinfo("Game", "Starting game...")
    
    def show_leaderboard(self):
        """Show the leaderboard modal"""
        self.close_current_modal()
        
        # Create modal window
        modal = tk.Toplevel(self.root)
        modal.title("🏆 Leaderboard")
        modal.geometry("500x400")
        modal.transient(self.root)
        modal.grab_set()
        modal.configure(bg='#2c3e50')
        
        self.current_modal = modal
        
        # Header
        header_frame = ttk.Frame(modal, padding=20)
        header_frame.pack(fill="x")
        
        ttk.Label(
            header_frame,
            text="🏆 LEADERBOARD 🏆",
            font=("Orbitron", 18, "bold"),
            foreground="#f39c12"
        ).pack()
        
        # Leaderboard content
        content_frame = ttk.Frame(modal, padding=(20, 0, 20, 20))
        content_frame.pack(fill="both", expand=True)
        
        # Create treeview for leaderboard
        columns = ("Rank", "Name", "Score", "Games", "Win Rate", "Best Time")
        tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        tree.heading("Rank", text="Rank")
        tree.heading("Name", text="Player")
        tree.heading("Score", text="Score")
        tree.heading("Games", text="Games")
        tree.heading("Win Rate", text="Win %")
        tree.heading("Best Time", text="Best Time")
        
        tree.column("Rank", width=60, anchor="center")
        tree.column("Name", width=120, anchor="w")
        tree.column("Score", width=80, anchor="center")
        tree.column("Games", width=70, anchor="center")
        tree.column("Win Rate", width=70, anchor="center")
        tree.column("Best Time", width=90, anchor="center")
        
        # Populate leaderboard
        leaderboard_data = self.leaderboard_manager.get_sorted_leaderboard()
        for i, entry in enumerate(leaderboard_data[:10], 1):
            tree.insert("", "end", values=(
                f"#{i}",
                entry.get('name', 'Anonymous'),
                entry.get('score', 0),
                entry.get('games', 0),
                f"{entry.get('win_rate', 0)}%",
                f"{entry.get('best_time', 0):.1f}s"
            ))
        
        tree.pack(fill="both", expand=True)
        
        # Close button
        ttk.Button(
            content_frame,
            text="Close",
            command=modal.destroy,
            bootstyle="secondary"
        ).pack(pady=10)
    
    def show_instructions(self):
        """Show the instructions modal"""
        self.close_current_modal()
        
        # Create modal window
        modal = tk.Toplevel(self.root)
        modal.title("📖 How to Play")
        modal.geometry("600x500")
        modal.transient(self.root)
        modal.grab_set()
        modal.configure(bg='#2c3e50')
        
        self.current_modal = modal
        
        # Header
        header_frame = ttk.Frame(modal, padding=20)
        header_frame.pack(fill="x")
        
        ttk.Label(
            header_frame,
            text="📖 HOW TO PLAY",
            font=("Orbitron", 18, "bold"),
            foreground="#f39c12"
        ).pack()
        
        # Instructions content with scrollbar
        content_frame = ttk.Frame(modal, padding=(20, 0, 20, 20))
        content_frame.pack(fill="both", expand=True)
        
        # Create scrollable text widget
        text_widget = tk.Text(
            content_frame,
            wrap="word",
            font=("Arial", 11),
            bg='#34495e',
            fg='white',
            relief="flat",
            padx=15,
            pady=15
        )
        
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Instructions text
        instructions = """🎯 OBJECTIVE
Guess the hidden Clash Royale card by asking yes/no questions about its properties!

🎮 GAMEPLAY
• A random Clash Royale card is selected secretly
• Use the dropdown menus to ask questions about the card's properties:
  - Rarity (common, rare, epic, legendary)
  - Type (troop, spell, building)
  - Elixir cost (1-10)
  - Melee (True/False for close combat)
  - Flying (True/False for air units)
  - Target (ground, air, both)
  - Role (defense, support, win_condition, swarm)
• Choose comparison operators: = (equals), : (contains), <, <=, >, >=
• Enter the value you want to compare against
• Click "Ask" to get a YES/NO answer
• Use "Hint" for a direct clue about the secret card
• When you think you know the card, click "Guess" on that card

💡 STRATEGY TIPS
• Start with broad questions about card type or elixir cost
• Use the "=" operator for exact matches (e.g., rarity = rare)
• Use ":" operator for partial matches (e.g., target : ground)
• Pay attention to the number of remaining candidates
• Think logically about which questions will eliminate the most cards

🏆 SCORING
• Your score is based on how quickly you guess the card
• Faster guesses = higher scores
• Make it to the top 5 to appear on the leaderboard!

⌨️ KEYBOARD SHORTCUTS
• N - Start New Game
• H - Show/Hide Instructions
• L - Show Leaderboard
• S - Open Settings
• Esc - Close Modal Windows

🎨 FEATURES
• Visual card elimination as you ask questions
• Real-time candidate counter
• Hint system for stuck moments
• Persistent leaderboard tracking
• Customizable keyboard shortcuts

Good luck, and may the cards be with you! 🃏"""
        
        text_widget.insert("1.0", instructions)
        text_widget.config(state="disabled")  # Make read-only
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        ttk.Button(
            content_frame,
            text="Close",
            command=modal.destroy,
            bootstyle="secondary"
        ).pack(pady=10)
    
    def show_settings(self):
        """Show the settings modal with keybind configuration"""
        self.close_current_modal()
        
        # Create modal window
        modal = tk.Toplevel(self.root)
        modal.title("⚙️ Settings")
        modal.geometry("500x600")
        modal.transient(self.root)
        modal.grab_set()
        modal.configure(bg='#2c3e50')
        
        self.current_modal = modal
        
        # Header
        header_frame = ttk.Frame(modal, padding=20)
        header_frame.pack(fill="x")
        
        ttk.Label(
            header_frame,
            text="⚙️ SETTINGS",
            font=("Orbitron", 18, "bold"),
            foreground="#f39c12"
        ).pack()
        
        # Settings content
        content_frame = ttk.Frame(modal, padding=(20, 0, 20, 20))
        content_frame.pack(fill="both", expand=True)
        
        # Keybinds section
        keybind_frame = ttk.LabelFrame(content_frame, text="🎹 Keyboard Shortcuts", padding=15)
        keybind_frame.pack(fill="x", pady=(0, 20))
        
        keybind_actions = [
            ("new_game", "Start New Game"),
            ("instructions", "Show/Hide Instructions"),
            ("leaderboard", "Show Leaderboard"),
            ("settings", "Open Settings"),
            ("submit", "Submit Guess"),
            ("close", "Close Modal")
        ]
        
        self.keybind_buttons = {}
        
        for i, (action, description) in enumerate(keybind_actions):
            row_frame = ttk.Frame(keybind_frame)
            row_frame.pack(fill="x", pady=5)
            
            # Description
            ttk.Label(row_frame, text=description, width=25, anchor="w").pack(side="left")
            
            # Current keybind button
            current_key = self.settings_manager.get_keybind(action)
            keybind_btn = ttk.Button(
                row_frame,
                text=current_key,
                width=10,
                bootstyle="primary",
                command=lambda a=action, b=None: self.start_keybind_recording(a, b)
            )
            keybind_btn.pack(side="right", padx=(10, 0))
            
            # Store reference for updating
            self.keybind_buttons[action] = keybind_btn
            
            # Update the command to pass the button reference
            keybind_btn.configure(command=lambda a=action, b=keybind_btn: self.start_keybind_recording(a, b))
        
        # Reset button
        ttk.Button(
            keybind_frame,
            text="Reset to Defaults",
            command=self.reset_keybinds,
            bootstyle="warning"
        ).pack(pady=10)
        
        # Game settings section
        game_frame = ttk.LabelFrame(content_frame, text="🎮 Game Settings", padding=15)
        game_frame.pack(fill="x", pady=(0, 20))
        
        # Sound setting
        sound_frame = ttk.Frame(game_frame)
        sound_frame.pack(fill="x", pady=5)
        ttk.Label(sound_frame, text="Sound Effects:", width=25, anchor="w").pack(side="left")
        
        self.sound_var = tk.BooleanVar(value=self.settings_manager.settings.get("sound_enabled", True))
        ttk.Checkbutton(
            sound_frame,
            variable=self.sound_var,
            bootstyle="success-round-toggle",
            command=self.update_sound_setting
        ).pack(side="right")
        
        # Animations setting
        anim_frame = ttk.Frame(game_frame)
        anim_frame.pack(fill="x", pady=5)
        ttk.Label(anim_frame, text="Animations:", width=25, anchor="w").pack(side="left")
        
        self.anim_var = tk.BooleanVar(value=self.settings_manager.settings.get("animations_enabled", True))
        ttk.Checkbutton(
            anim_frame,
            variable=self.anim_var,
            bootstyle="success-round-toggle",
            command=self.update_animation_setting
        ).pack(side="right")
        
        # Close button
        ttk.Button(
            content_frame,
            text="Close",
            command=modal.destroy,
            bootstyle="secondary"
        ).pack(pady=10)
    
    def start_keybind_recording(self, action, button):
        """Start recording a new keybind"""
        print(f"start_keybind_recording called: action={action}")  # Debug
        # Pass the current modal window to the recorder
        self.keybind_recorder.start_recording(action, button, self.current_modal)
    
    def update_keybind(self, action, key):
        """Update keybind after recording"""
        print(f"update_keybind called: action={action}, key={key}")  # Debug
        
        success, message = self.settings_manager.set_keybind(action, key)
        print(f"set_keybind result: success={success}, message={message}")  # Debug
        
        if success:
            # Update the button text
            if action in self.keybind_buttons:
                self.keybind_buttons[action].configure(text=key, bootstyle="primary")
                print(f"Updated button text to: {key}")  # Debug
            
            # Re-setup global keybinds
            self.setup_keybinds()
            print("Re-setup keybinds")  # Debug
        else:
            messagebox.showwarning("Keybind Error", message)
            # Reset button text to original
            if action in self.keybind_buttons:
                current_key = self.settings_manager.get_keybind(action)
                self.keybind_buttons[action].configure(text=current_key, bootstyle="primary")
            # Re-setup global keybinds even on failure
            self.setup_keybinds()
    
    def reset_keybinds(self):
        """Reset all keybinds to defaults"""
        if messagebox.askyesno("Reset Keybinds", "Reset all keybinds to default values?"):
            self.settings_manager.reset_keybinds()
            
            # Update button texts
            for action, button in self.keybind_buttons.items():
                current_key = self.settings_manager.get_keybind(action)
                button.configure(text=current_key, bootstyle="primary")
            
            # Refresh keybind handlers
            self.setup_keybinds()
            messagebox.showinfo("Reset Complete", "Keybinds have been reset to defaults!")
    
    def update_sound_setting(self):
        """Update sound setting"""
        self.settings_manager.settings["sound_enabled"] = self.sound_var.get()
        self.settings_manager.save_settings()
    
    def update_animation_setting(self):
        """Update animation setting"""
        self.settings_manager.settings["animations_enabled"] = self.anim_var.get()
        self.settings_manager.save_settings()
    
    def close_current_modal(self):
        """Close the current modal if any"""
        if self.current_modal and self.current_modal.winfo_exists():
            self.current_modal.destroy()
            self.current_modal = None

# Test function (for standalone testing)
def test_main_menu():
    root = tb.Window(themename="darkly")
    root.title("Clash Royale Guess Who - Main Menu")
    root.geometry("800x600")
    
    def dummy_start_game():
        messagebox.showinfo("Game", "Starting game... (This would launch your game)")
    
    menu = ClashRoyaleMainMenu(root, on_play=dummy_start_game)
    root.mainloop()

if __name__ == "__main__":
    test_main_menu()