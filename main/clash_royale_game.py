#!/usr/bin/env python3
"""
clash_royale_game.py

Main entry point that combines the main menu with the game.
Handles transitions between menu and game states.
"""

import tkinter as tk
import ttkbootstrap as tb
from main_menu import ClashRoyaleMainMenu
from tkinter import messagebox
import os
import random
import math
from tkinter import ttk
from dataclasses import dataclass
from typing import List, Dict, Callable, Any
from PIL import Image, ImageTk
import re

# Import your existing game classes and data
@dataclass
class Card:
    name: str
    rarity: str
    card_type: str
    elixir: int
    melee: bool
    flying: bool
    target: str
    role: str
    image_file: str = None

# Your existing card data
CARDS: List[Card] = [
    Card("Knight", "common", "troop", 3, True, False, "ground", "defense", "images/knight.png"),
    Card("Archers", "common", "troop", 3, False, False, "both", "support", "images/archers.png"),
    Card("Giant", "rare", "troop", 5, False, False, "ground", "win_condition", "images/giant.png"),
    Card("Baby Dragon", "rare", "troop", 4, False, True, "air", "support", "images/baby-dragon.png"),
    Card("Hog Rider", "rare", "troop", 4, True, False, "ground", "win_condition", "images/hog-rider.png"),
    Card("Wizard", "rare", "troop", 5, False, False, "both", "support", "images/wizard.png"),
    Card("Inferno Tower", "rare", "building", 5, False, False, "ground", "defense", "images/inferno-tower.png"),
    Card("Balloon", "epic", "troop", 5, False, True, "air", "win_condition", "images/balloon.png"),
    Card("Electro Wizard", "legendary", "troop", 4, False, False, "both", "support", "images/electro-wizard.png"),
    Card("Skeletons", "common", "troop", 1, False, False, "ground", "swarm", "images/skeletons.png"),
]

ATTRIBUTES: Dict[str, Callable[[Card], Any]] = {
    "rarity": lambda c: c.rarity,
    "type": lambda c: c.card_type,
    "elixir": lambda c: c.elixir,
    "melee": lambda c: c.melee,
    "flying": lambda c: c.flying,
    "target": lambda c: c.target,
    "role": lambda c: c.role,
}

def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s

class GuessWhoPro:
    def __init__(self, root: tb.Window):
        self.root = root
        self.root.title("Clash Royale — Guess Who? (Pro)")
        self.style = tb.Style(theme="flatly")
        self.secret = random.choice(CARDS)
        self.candidates = CARDS.copy()
        self.photo_cache = {}
        self.card_buttons = {}
        self.create_ui()

    def create_ui(self):
        top = ttk.Frame(self.root, padding=(12,12))
        top.pack(fill="x", padx=8, pady=6)

        title = ttk.Label(top, text="Clash Royale — Guess Who?", font=("Segoe UI", 18, "bold"))
        title.pack(side="left")

        right = ttk.Frame(top)
        right.pack(side="right")
        ttk.Button(right, text="Main Menu", command=self.return_to_menu).pack(side="left", padx=4)
        ttk.Button(right, text="New Game", command=self.new_game).pack(side="left", padx=4)
        ttk.Button(right, text="Show All", command=self.reset_visuals).pack(side="left", padx=4)

        # Controls area
        control = ttk.Frame(self.root, padding=(12,6))
        control.pack(fill="x", padx=8)

        # Attribute combobox
        self.attr_var = tk.StringVar(value="rarity")
        attr_combo = ttk.Combobox(control, textvariable=self.attr_var, values=list(ATTRIBUTES.keys()), state="readonly", width=14)
        attr_combo.grid(row=0, column=0, padx=(0,8))
        attr_combo.bind("<<ComboboxSelected>>", lambda e: self.value_entry.focus_set())

        # Operator combobox
        self.op_var = tk.StringVar(value="=")
        op_combo = ttk.Combobox(control, textvariable=self.op_var, values=["=", ":", "<", "<=", ">", ">="], width=4, state="readonly")
        op_combo.grid(row=0, column=1, padx=(0,8))

        # Value entry
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(control, textvariable=self.value_var, width=20)
        self.value_entry.grid(row=0, column=2, padx=(0,8))
        self.value_entry.insert(0, "enter value (e.g. rare / 4 / True)")

        ttk.Button(control, text="Ask", command=self.ask).grid(row=0, column=3, padx=(4,0))
        ttk.Button(control, text="Hint", command=self.hint).grid(row=0, column=4, padx=(6,0))

        # Candidate count
        self.status_var = tk.StringVar()
        self.update_status()
        status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        status_label.pack(fill="x", padx=12, pady=(4,0))

        # Card grid
        self.grid_frame = ttk.Frame(self.root, padding=12)
        self.grid_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.load_card_grid()

    def return_to_menu(self):
        """Return to the main menu"""
        if messagebox.askyesno("Return to Menu", "Return to main menu? Current game will be lost."):
            # Clear the current window
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Create new main menu
            app = ClashRoyaleApp(self.root)

    def update_status(self):
        self.status_var.set(f"Candidates remaining: {len(self.candidates)}    (Secret card: ???)")

    def load_card_grid(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        cols = 5
        card_w = 140
        card_h = 170
        padding = 8

        for idx, card in enumerate(CARDS):
            r = idx // cols
            c = idx % cols
            frame = ttk.Frame(self.grid_frame, width=card_w, height=card_h, relief="raised", padding=6)
            frame.grid_propagate(False)
            frame.grid(row=r, column=c, padx=padding, pady=padding)

            img = self.load_card_image(card, (120, 100))
            lbl_img = ttk.Label(frame, image=img)
            lbl_img.image = img
            lbl_img.pack()

            lbl_name = ttk.Label(frame, text=card.name, font=("Segoe UI", 10, "bold"))
            lbl_name.pack(pady=(6,0))

            info = f"{card.rarity.title()} • {card.elixir}ⓔ"
            ttk.Label(frame, text=info, font=("Segoe UI", 9)).pack()

            btn = ttk.Button(frame, text="Guess", command=lambda c=card: self.guess(c))
            btn.pack(side="bottom", pady=(8,0))
            self.card_buttons[card.name] = (frame, lbl_img, lbl_name, btn)

            frame.configure(cursor="hand2")

    def load_card_image(self, card: Card, size=(120,100)):
        key = (card.name, size)
        if key in self.photo_cache:
            return self.photo_cache[key]
        
        if card.image_file and os.path.exists(card.image_file):
            im = Image.open(card.image_file).convert("RGBA")
            im.thumbnail(size, Image.LANCZOS)
            bg = Image.new("RGBA", size, (255,255,255,0))
            x = (size[0]-im.width)//2
            y = (size[1]-im.height)//2
            bg.paste(im, (x,y), im)
            photo = ImageTk.PhotoImage(bg)
        else:
            img = Image.new("RGBA", size, (200,200,200,255))
            photo = ImageTk.PhotoImage(img)
        
        self.photo_cache[key] = photo
        return photo

    def ask(self):
        attr = self.attr_var.get()
        op = self.op_var.get()
        val = self.value_var.get().strip()
        if not val:
            messagebox.showwarning("Empty value", "Enter a value to ask about (e.g. 'rare', '4', 'True')")
            return

        keyfunc = ATTRIBUTES[attr]
        sec_val = keyfunc(self.secret)
        secret_truth = self.evaluate_comparison(sec_val, op, val)

        messagebox.showinfo("Answer", "YES" if secret_truth else "NO")

        if secret_truth:
            new_candidates = [c for c in self.candidates if self.evaluate_comparison(keyfunc(c), op, val)]
        else:
            new_candidates = [c for c in self.candidates if not self.evaluate_comparison(keyfunc(c), op, val)]

        removed = [c for c in self.candidates if c not in new_candidates]
        self.candidates = new_candidates
        self.update_status()
        self.update_visuals(removed)

    def evaluate_comparison(self, card_val, op: str, val_raw: str) -> bool:
        try:
            if isinstance(card_val, int):
                comp = int(val_raw)
                if op == "<": return card_val < comp
                if op == "<=": return card_val <= comp
                if op in ("=", "=="): return card_val == comp
                if op == ">=": return card_val >= comp
                if op == ">": return card_val > comp
                if op == ":": return str(comp) in str(card_val)
            if isinstance(card_val, bool):
                v = val_raw.lower()
                if v in ("true","1","yes","y"): comp = True
                elif v in ("false","0","no","n"): comp = False
                else: return False
                return card_val == comp
            s = str(card_val).lower()
            v = val_raw.lower()
            if op in ("=", "=="): return s == v
            if op == ":": return v in s
        except Exception:
            return False
        return False

    def update_visuals(self, removed_cards: List[Card]):
        for c in removed_cards:
            if c.name in self.card_buttons:
                frame, lbl_img, lbl_name, btn = self.card_buttons[c.name]
                btn.state(["disabled"])
                overlay = Image.new("RGBA", (120,100), (180,180,180,180))
                if c.image_file and os.path.exists(c.image_file):
                    im = Image.open(c.image_file).convert("RGBA")
                    im.thumbnail((120,100), Image.LANCZOS)
                    bg = Image.new("RGBA", (120,100), (255,255,255,255))
                    x = (120-im.width)//2
                    y = (100-im.height)//2
                    bg.paste(im, (x,y), im)
                    bg = Image.alpha_composite(bg, overlay)
                    photo = ImageTk.PhotoImage(bg)
                    lbl_img.configure(image=photo)
                    lbl_img.image = photo
                lbl_name.configure(foreground="#888888")

    def reset_visuals(self):
        self.candidates = CARDS.copy()
        for c in CARDS:
            if c.name in self.card_buttons:
                frame, lbl_img, lbl_name, btn = self.card_buttons[c.name]
                btn.state(["!disabled"])
                img = self.load_card_image(c, (120,100))
                lbl_img.configure(image=img)
                lbl_img.image = img
                lbl_name.configure(foreground="black")
        self.update_status()

    def hint(self):
        hint = self.make_hint()
        messagebox.showinfo("Hint", hint)

    def make_hint(self) -> str:
        attrs = list(ATTRIBUTES.keys())
        random.shuffle(attrs)
        for a in attrs:
            key = ATTRIBUTES[a]
            sec_val = key(self.secret)
            matches = [c for c in self.candidates if key(c) == sec_val]
            if 0 < len(matches) < len(self.candidates):
                return f"The secret card's {a} is '{sec_val}'."
        return f"The secret card's name starts with '{self.secret.name[0]}'"

    def guess(self, card: Card):
        if card.name == self.secret.name:
            messagebox.showinfo("Correct!", f"🎉 Correct — the secret card was {card.name}!")
            self.reveal_secret(card)
        else:
            messagebox.showwarning("Incorrect", f"❌ {card.name} is not the secret card.")
            self.candidates = [c for c in self.candidates if c.name != card.name]
            self.update_status()
            self.update_visuals([card])

    def reveal_secret(self, card: Card):
        for c in CARDS:
            frame, lbl_img, lbl_name, btn = self.card_buttons[c.name]
            if c.name == card.name:
                frame.configure(relief="solid")
                lbl_name.configure(foreground="#0a84ff")
            else:
                btn.state(["disabled"])
        self.update_status()

    def new_game(self):
        self.secret = random.choice(CARDS)
        self.candidates = CARDS.copy()
        self.reset_visuals()
        messagebox.showinfo("New Game", "A new secret card has been chosen!")

class ClashRoyaleApp:
    def __init__(self, root):
        self.root = root
        self.current_screen = None
        self.show_main_menu()
    
    def show_main_menu(self):
        """Display the main menu"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main menu
        self.main_menu = ClashRoyaleMainMenu(
            self.root,
            on_play=self.start_game,
            on_how_to_play=self.show_instructions,
            on_leaderboard=self.show_leaderboard,
            on_settings=self.show_settings
        )
        self.current_screen = "menu"
    
    def start_game(self):
        """Transition from menu to game"""
        print("Starting Clash Royale Guess Who game...")
        
        # Clear menu widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Start the game
        self.game = GuessWhoPro(self.root)
        self.current_screen = "game"
    
    def show_instructions(self):
        """Show game instructions"""
        instruction_window = tk.Toplevel(self.root)
        instruction_window.title("How to Play")
        instruction_window.geometry("500x400")
        instruction_window.configure(bg='#1e293b')
        instruction_window.grab_set()  # Make it modal
        
        # Center the window
        instruction_window.transient(self.root)
        instruction_window.update_idletasks()
        x = (instruction_window.winfo_screenwidth() // 2) - (instruction_window.winfo_width() // 2)
        y = (instruction_window.winfo_screenheight() // 2) - (instruction_window.winfo_height() // 2)
        instruction_window.geometry(f"+{x}+{y}")
        
        text = """
HOW TO PLAY CLASH ROYALE GUESS WHO

🎯 OBJECTIVE:
Guess the secret Clash Royale card in as few questions as possible!

🎮 HOW TO PLAY:
1. A secret card is randomly chosen from the deck
2. Ask yes/no questions about the card's properties
3. Use the dropdown menus to select attributes and values
4. Cards that don't match your questions will be eliminated
5. When you're confident, click "Guess" on a card
6. Try to guess correctly with the fewest questions!

🔍 CARD PROPERTIES YOU CAN ASK ABOUT:
• Rarity: common, rare, epic, legendary
• Type: troop, spell, building
• Elixir Cost: 1-10 elixir
• Melee: True/False (close combat vs ranged)
• Flying: True/False (air vs ground units)
• Target: ground, air, both
• Role: defense, support, win_condition, swarm

💡 TIPS:
• Start with broad questions (like rarity or type)
• Use the "Hint" button if you're stuck
• Pay attention to elixir costs - they're key identifiers
• Remember: flying units can only target air troops!

🏆 STRATEGY:
The best players can guess cards in 3-5 questions by asking
strategic questions that eliminate the most possibilities.

Good luck, and may the elixir be with you! ⚡
        """
        
        # Create scrollable text widget
        text_frame = tk.Frame(instruction_window, bg='#1e293b')
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, wrap='word', bg='#2d3748', fg='white',
                             font=("Arial", 11), relief='flat', bd=0,
                             padx=15, pady=15)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')  # Make read-only
        
        # Close button
        close_btn = ttk.Button(instruction_window, text="Got it!", 
                             command=instruction_window.destroy,
                             style="success.TButton")
        close_btn.pack(pady=(0, 20))
    
    def show_leaderboard(self):
        """Show leaderboard (placeholder)"""
        messagebox.showinfo("Leaderboard", 
                           "🏆 LEADERBOARD 🏆\n\n" +
                           "Feature coming soon!\n\n" +
                           "Track your best guessing records:\n" +
                           "• Fewest questions to win\n" +
                           "• Win streaks\n" +
                           "• Cards guessed correctly\n\n" +
                           "Keep playing to improve your skills!")
    
    def show_settings(self):
        """Show settings (placeholder)"""
        messagebox.showinfo("Settings", 
                           "⚙️ SETTINGS ⚙️\n\n" +
                           "Settings coming soon!\n\n" +
                           "Future options:\n" +
                           "• Sound effects\n" +
                           "• Difficulty levels\n" +
                           "• Card set selection\n" +
                           "• Visual themes")

def main():
    """Main entry point"""
    # Create the main window with ttkbootstrap
    root = tb.Window(themename="flatly")
    root.title("Clash Royale Guess Who")
    root.geometry("900x700")
    
    # Create the app
    app = ClashRoyaleApp(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()