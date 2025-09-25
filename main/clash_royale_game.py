#!/usr/bin/env python3
"""
clash_royale_game.py

Clash Royale — Guess Who? (Pro)
Leaderboard now based on how fast the card is guessed.
"""

import os
import random
import re
import json
import time
from dataclasses import dataclass
from typing import List, Dict, Callable, Any
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import ttkbootstrap as tb
from main_menu import ClashRoyaleMainMenu

# ---------- CARD DATA ----------
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

CARDS: List[Card] = [
    Card("Knight", "common", "troop", 3, True, False, "ground", "defense", "card images/clash-knight.webp"),
    Card("Archers", "common", "troop", 3, False, False, "both", "support", "card images/clash-archers.webp"),
    Card("Giant", "rare", "troop", 5, False, False, "ground", "win_condition", "card images/clash-giant.webp"),
    Card("Baby Dragon", "rare", "troop", 4, False, True, "air", "support", "card images/clash-baby-dragon.webp"),
    Card("Hog Rider", "rare", "troop", 4, True, False, "ground", "win_condition", "card images/clash-hog-rider.webp"),
    Card("Wizard", "rare", "troop", 5, False, False, "both", "support", "card images/clash-wizard.webp"),
    Card("Inferno Tower", "rare", "building", 5, False, False, "ground", "defense", "card images/clash-inferno-tower.webp"),
    Card("Balloon", "epic", "troop", 5, False, True, "air", "win_condition", "card images/clash-balloon.webp"),
    Card("Electro Wizard", "legendary", "troop", 4, False, False, "both", "support", "card images/clash-electro-wizard.webp"),
    Card("Skeletons", "common", "troop", 1, False, False, "ground", "swarm", "card images/clash-skeletons.webp"),
    Card("Prince", "epic", "troop", 5, True, False, "ground", "win_condition","card images/clash-prince.webp"),
    Card("Miner", "legendary", "troop", 3, False, False, "ground", "support","card images/clash-royale-miner.webp"),
    Card("Princess", "legendary", "troop", 3, False, True, "both", "support","card images/clash-princess.webp"),
    Card("Goblin Barrel", "epic", "spell", 3, False, False, "ground", "win_condition","card images/clash-goblin-barrel.webp"),
    Card("Fireball", "rare", "spell", 4, False, False, "ground", "support","card images/clash-fireball.webp"),
    Card("Mortar", "common", "building", 4, False, False, "ground", "defense","card images/clash-mortar.webp"),
    Card("Musketeer", "rare", "troop", 4, False, False, "both", "support","card images/clash-musketeer.webp"),
    Card("Goblin Gang", "common", "troop", 3, False, False, "ground", "swarm","card images/clash-goblin-gang.webp"),
    Card("Minion Horde", "common", "troop", 5, False, True, "air", "swarm","card images/clash-minion-horde.webp"),
    Card("Lava Hound", "legendary", "troop", 7, False, True, "air", "win_condition","card images/clash-lava-hound.webp"),
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

LEADERBOARD_FILE = "leaderboard.json"
MAX_LEADERS = 5

# ---------- GAME CLASS ----------
class GuessWhoPro:
    def __init__(self, root: tb.Window):
        self.root = root
        self.root.title("Clash Royale — Guess Who? (Pro)")
        self.style = tb.Style(theme="flatly")
        self.secret = random.choice(CARDS)
        self.candidates = CARDS.copy()
        self.photo_cache = {}
        self.card_buttons = {}

        # Timing
        self.start_time = time.time()
        self.end_time = None

        # Leaderboard
        self.leaderboard = self.load_leaderboard()

        self.create_ui()

    # ---------- UI ----------
    def create_ui(self):
        # Top bar
        top = ttk.Frame(self.root, padding=(12,12))
        top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="Clash Royale — Guess Who?", font=("Segoe UI", 18, "bold")).pack(side="left")
        right = ttk.Frame(top)
        right.pack(side="right")
        ttk.Button(right, text="Main Menu", command=self.return_to_menu).pack(side="left", padx=4)
        ttk.Button(right, text="New Game", command=self.new_game).pack(side="left", padx=4)
        ttk.Button(right, text="Show All", command=self.reset_visuals).pack(side="left", padx=4)
        ttk.Button(right, text="Leaderboard", command=self.show_leaderboard_ui).pack(side="left", padx=4)

        # Controls
        control = ttk.Frame(self.root, padding=(12,6))
        control.pack(fill="x", padx=8)
        self.attr_var = tk.StringVar(value="rarity")
        ttk.Combobox(control, textvariable=self.attr_var, values=list(ATTRIBUTES.keys()), state="readonly", width=14).grid(row=0, column=0, padx=(0,8))
        self.op_var = tk.StringVar(value="=")
        ttk.Combobox(control, textvariable=self.op_var, values=["=", ":", "<", "<=", ">", ">="], width=4, state="readonly").grid(row=0, column=1, padx=(0,8))
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(control, textvariable=self.value_var, width=20)
        self.value_entry.grid(row=0, column=2, padx=(0,8))
        self.value_entry.insert(0, "enter value (e.g. rare / 4 / True)")
        ttk.Button(control, text="Ask", command=self.ask).grid(row=0, column=3, padx=(4,0))
        ttk.Button(control, text="Hint", command=self.hint).grid(row=0, column=4, padx=(6,0))

        # Status bar
        self.status_var = tk.StringVar()
        self.update_status()
        ttk.Label(self.root, textvariable=self.status_var, anchor="w").pack(fill="x", padx=12, pady=(4,0))

        # Scrollable card grid
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(fill="both", expand=True, padx=12, pady=8)
        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.load_card_grid()

    # ---------- LOAD CARDS ----------
    def load_card_grid(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        cols = 5
        card_w, card_h, padding = 140, 170, 8
        for idx, card in enumerate(CARDS):
            r, c = divmod(idx, cols)
            frame = ttk.Frame(self.scrollable_frame, width=card_w, height=card_h, relief="raised", padding=6)
            frame.grid_propagate(False)
            frame.grid(row=r, column=c, padx=padding, pady=padding)
            img = self.load_card_image(card, (120,100))
            lbl_img = ttk.Label(frame, image=img)
            lbl_img.image = img
            lbl_img.pack()
            ttk.Label(frame, text=card.name, font=("Segoe UI", 10, "bold")).pack(pady=(6,0))
            ttk.Label(frame, text=f"{card.rarity.title()} • {card.elixir}ⓔ", font=("Segoe UI", 9)).pack()
            btn = ttk.Button(frame, text="Guess", command=lambda c=card: self.guess(c))
            btn.pack(side="bottom", pady=(8,0))
            self.card_buttons[card.name] = (frame, lbl_img, btn)

    # ---------- GAME LOGIC ----------
    def ask(self):
        val = self.value_var.get().strip()
        if not val: 
            messagebox.showwarning("Empty value", "Enter a value")
            return
        attr = self.attr_var.get()
        keyfunc = ATTRIBUTES[attr]
        secret_truth = self.evaluate_comparison(keyfunc(self.secret), self.op_var.get(), val)
        messagebox.showinfo("Answer", "YES" if secret_truth else "NO")
        new_candidates = [c for c in self.candidates if self.evaluate_comparison(keyfunc(c), self.op_var.get(), val) == secret_truth]
        removed = [c for c in self.candidates if c not in new_candidates]
        self.candidates = new_candidates
        self.update_status()
        self.update_visuals(removed)

    def evaluate_comparison(self, card_val, op, val_raw):
        try:
            if isinstance(card_val, int):
                comp = int(val_raw)
                return ((op == "=" or op=="==") and card_val == comp) or \
                       (op == "<" and card_val < comp) or \
                       (op == "<=" and card_val <= comp) or \
                       (op == ">" and card_val > comp) or \
                       (op == ">=" and card_val >= comp) or \
                       (op == ":" and str(comp) in str(card_val))
            if isinstance(card_val, bool):
                comp = val_raw.lower() in ["true","1","yes","y"]
                return card_val == comp
            s, v = str(card_val).lower(), val_raw.lower()
            return (op in ["=", "=="] and s==v) or (op==":" and v in s)
        except: 
            return False

    def guess(self, card: Card):
        if card.name == self.secret.name:
            self.end_time = time.time()
            elapsed = round(self.end_time - self.start_time, 2)
            messagebox.showinfo("Correct!", f"🎉 Correct — {card.name}!\nTime: {elapsed} seconds")
            self.reveal_secret(card)
            self.check_leaderboard(elapsed)
        else:
            messagebox.showwarning("Incorrect", f"{card.name} is not the secret card.")
            self.candidates = [c for c in self.candidates if c.name != card.name]
            self.update_status()
            self.update_visuals([card])

    # ---------- STATUS & VISUALS ----------
    def update_status(self):
        self.status_var.set(f"Candidates: {len(self.candidates)}")

    def update_visuals(self, removed):
        for c in removed:
            if c.name in self.card_buttons:
                frame, lbl_img, btn = self.card_buttons[c.name]
                btn.state(["disabled"])

    def reset_visuals(self):
        self.candidates = CARDS.copy()
        self.start_time = time.time()
        for c in CARDS:
            frame, lbl_img, btn = self.card_buttons[c.name]
            btn.state(["!disabled"])
            lbl_img.configure(image=self.load_card_image(c, (120,100)))
        self.update_status()

    def new_game(self):
        self.secret = random.choice(CARDS)
        self.reset_visuals()
        messagebox.showinfo("New Game", "A new secret card has been chosen!")

    def reveal_secret(self, card: Card):
        for c in CARDS:
            frame, lbl_img, btn = self.card_buttons[c.name]
            if c.name == card.name:
                frame.configure(relief="solid")

    # ---------- LEADERBOARD ----------
    def load_leaderboard(self):
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        return []

    def save_leaderboard(self):
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(self.leaderboard, f, indent=2)

    def check_leaderboard(self, elapsed_time):
        if len(self.leaderboard)<MAX_LEADERS or elapsed_time < self.leaderboard[-1]["time"]:
            name = simpledialog.askstring("New High Score!", "You made it to the leaderboard! Enter your name:")
            if not name: name = "Anonymous"
            self.leaderboard.append({"name": name, "time": elapsed_time})
            self.leaderboard.sort(key=lambda x: x["time"])
            self.leaderboard = self.leaderboard[:MAX_LEADERS]
            self.save_leaderboard()
            self.show_leaderboard_ui()

    def show_leaderboard_ui(self):
        lb_window = tk.Toplevel(self.root)
        lb_window.title("Leaderboard — Fastest Times")
        lb_window.geometry("300x250")
        lb_window.grab_set()
        ttk.Label(lb_window, text="🏆 Top 5 Fastest Players 🏆", font=("Segoe UI", 14, "bold")).pack(pady=8)
        for entry in self.leaderboard:
            ttk.Label(lb_window, text=f"{entry['name']}: {entry['time']}s").pack(anchor="w", padx=12)
        ttk.Button(lb_window, text="Close", command=lb_window.destroy).pack(pady=12)

    # ---------- NAVIGATION ----------
    def return_to_menu(self):
        if messagebox.askyesno("Return to Menu", "Return to main menu? Current game will be lost."):
            for widget in self.root.winfo_children(): widget.destroy()
            ClashRoyaleApp(self.root)

    def hint(self):
        key = random.choice(list(ATTRIBUTES.keys()))
        value = ATTRIBUTES[key](self.secret)
        messagebox.showinfo("Hint", f"The secret card's {key} is '{value}'.")

    def load_card_image(self, card: Card, size=(120,100)):
        key = (card.name, size)
        if key in self.photo_cache: return self.photo_cache[key]
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

# ---------- APP ----------
class ClashRoyaleApp:
    def __init__(self, root):
        self.root = root
        self.current_screen = None
        self.show_main_menu()
    def show_main_menu(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.main_menu = ClashRoyaleMainMenu(
            self.root,
            on_play=self.start_game,
            on_how_to_play=lambda: None,
            on_leaderboard=lambda: None,
            on_settings=lambda: None
        )
        self.current_screen = "menu"
    def start_game(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.game = GuessWhoPro(self.root)
        self.current_screen = "game"

# ---------- MAIN ----------
def main():
    root = tb.Window(themename="flatly")
    root.title("Clash Royale Guess Who")
    root.geometry("900x700")
    app = ClashRoyaleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
