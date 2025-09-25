#!/usr/bin/env python3
"""
clash_royale_game.py

Clash Royale — Guess Who? (Pro)
Enhanced with full main menu integration
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
from main_menu import ClashRoyaleMainMenu, LeaderboardManager

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
    Card("Baby Dragon", "epic", "troop", 4, False, True, "air", "support", "card images/clash-baby-dragon.webp"),
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
MAX_LEADERS = 10

# ---------- ENHANCED GAME CLASS ----------
class GuessWhoPro:
    def __init__(self, root: tb.Window, return_to_menu_callback=None):
        self.root = root
        self.return_to_menu_callback = return_to_menu_callback
        self.root.title("Clash Royale — Guess Who? (Pro)")
        self.style = tb.Style(theme="flatly")
        self.secret = random.choice(CARDS)
        self.candidates = CARDS.copy()
        self.photo_cache = {}
        self.card_buttons = {}

        # Timing
        self.start_time = time.time()
        self.end_time = None

        # Enhanced leaderboard integration
        self.leaderboard_manager = LeaderboardManager()

        self.create_ui()

    # ---------- UI ----------
    def create_ui(self):
        # Top bar with enhanced styling
        top = ttk.Frame(self.root, padding=(12,12))
        top.pack(fill="x", padx=8, pady=6)
        
        title_label = ttk.Label(
            top, 
            text="Clash Royale — Guess Who?", 
            font=("Orbitron", 18, "bold"),
            foreground="#e74c3c"
        )
        title_label.pack(side="left")
        
        right = ttk.Frame(top)
        right.pack(side="right")
        
        # Enhanced buttons with better styling
        ttk.Button(
            right, 
            text="Main Menu", 
            command=self.return_to_menu,
            bootstyle="secondary-outline"
        ).pack(side="left", padx=4)
        
        ttk.Button(
            right, 
            text="New Game", 
            command=self.new_game,
            bootstyle="success-outline"
        ).pack(side="left", padx=4)
        
        ttk.Button(
            right, 
            text="Show All", 
            command=self.reset_visuals,
            bootstyle="info-outline"
        ).pack(side="left", padx=4)
        
        ttk.Button(
            right, 
            text="Leaderboard", 
            command=self.show_leaderboard_ui,
            bootstyle="warning-outline"
        ).pack(side="left", padx=4)

        # Enhanced controls with better layout
        control = ttk.Frame(self.root, padding=(12,6))
        control.pack(fill="x", padx=8)
        
        # Question building section
        question_frame = ttk.LabelFrame(control, text="Ask a Question", padding=10)
        question_frame.pack(fill="x", pady=5)
        
        controls_inner = ttk.Frame(question_frame)
        controls_inner.pack(fill="x")
        
        ttk.Label(controls_inner, text="Property:").grid(row=0, column=0, sticky="w", padx=(0,5))
        self.attr_var = tk.StringVar(value="rarity")
        attr_combo = ttk.Combobox(
            controls_inner, 
            textvariable=self.attr_var, 
            values=list(ATTRIBUTES.keys()), 
            state="readonly", 
            width=14
        )
        attr_combo.grid(row=0, column=1, padx=(0,8))
        
        ttk.Label(controls_inner, text="Operator:").grid(row=0, column=2, sticky="w", padx=(0,5))
        self.op_var = tk.StringVar(value="=")
        op_combo = ttk.Combobox(
            controls_inner, 
            textvariable=self.op_var, 
            values=["=", ":", "<", "<=", ">", ">="], 
            width=4, 
            state="readonly"
        )
        op_combo.grid(row=0, column=3, padx=(0,8))
        
        ttk.Label(controls_inner, text="Value:").grid(row=0, column=4, sticky="w", padx=(0,5))
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(controls_inner, textvariable=self.value_var, width=20)
        self.value_entry.grid(row=0, column=5, padx=(0,8))
        self.value_entry.insert(0, "e.g. rare, 4, True")
        
        # Add placeholder text handling
        self.value_entry.bind('<FocusIn>', self.clear_placeholder)
        self.value_entry.bind('<FocusOut>', self.add_placeholder)
        
        button_frame = ttk.Frame(controls_inner)
        button_frame.grid(row=0, column=6, padx=(10,0))
        
        ttk.Button(
            button_frame, 
            text="Ask", 
            command=self.ask,
            bootstyle="primary"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            button_frame, 
            text="Hint", 
            command=self.hint,
            bootstyle="info"
        ).pack(side="left", padx=2)

        # Enhanced status bar with more information
        status_frame = ttk.Frame(self.root, padding=(12,6))
        status_frame.pack(fill="x", padx=8)
        
        self.status_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.update_status()
        
        ttk.Label(status_frame, textvariable=self.status_var, anchor="w").pack(side="left")
        ttk.Label(status_frame, textvariable=self.time_var, anchor="e").pack(side="right")
        
        # Start time updater
        self.update_timer()

        # Scrollable card grid (enhanced)
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(fill="both", expand=True, padx=12, pady=8)
        self.canvas = tk.Canvas(self.canvas_frame, bg='#f8f9fa')
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        self.load_card_grid()

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def clear_placeholder(self, event):
        """Clear placeholder text when entry is focused"""
        if self.value_entry.get() == "e.g. rare, 4, True":
            self.value_entry.delete(0, tk.END)

    def add_placeholder(self, event):
        """Add placeholder text when entry loses focus and is empty"""
        if not self.value_entry.get():
            self.value_entry.insert(0, "e.g. rare, 4, True")

    def update_timer(self):
        """Update the elapsed time display"""
        if not self.end_time:
            elapsed = time.time() - self.start_time
            self.time_var.set(f"Time: {elapsed:.1f}s")
            self.root.after(100, self.update_timer)

    # ---------- ENHANCED LOAD CARDS ----------
    def load_card_grid(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        cols = 5
        card_w, card_h, padding = 150, 190, 8
        
        for idx, card in enumerate(CARDS):
            r, c = divmod(idx, cols)
            
            # Create card frame with better styling
            frame = ttk.Frame(self.scrollable_frame, width=card_w, height=card_h, relief="raised", padding=8)
            frame.grid_propagate(False)
            frame.grid(row=r, column=c, padx=padding, pady=padding)
            
            # Card image
            img = self.load_card_image(card, (120,100))
            lbl_img = ttk.Label(frame, image=img)
            lbl_img.image = img
            lbl_img.pack()
            
            # Card name with better font
            ttk.Label(
                frame, 
                text=card.name, 
                font=("Orbitron", 11, "bold"),
                anchor="center"
            ).pack(pady=(8,2))
            
            # Card details with color coding
            details_text = f"{card.rarity.title()} • {card.elixir}⚡"
            detail_color = {
                'common': '#95a5a6',
                'rare': '#3498db', 
                'epic': '#9b59b6',
                'legendary': '#f39c12'
            }.get(card.rarity, '#95a5a6')
            
            detail_label = ttk.Label(
                frame, 
                text=details_text, 
                font=("Arial", 9),
                foreground=detail_color
            )
            detail_label.pack()
            
            # Guess button with better styling
            btn = ttk.Button(
                frame, 
                text="Guess This!", 
                command=lambda c=card: self.guess(c),
                bootstyle="success-outline",
                width=12
            )
            btn.pack(side="bottom", pady=(10,0))
            
            self.card_buttons[card.name] = (frame, lbl_img, btn)

    # ---------- ENHANCED GAME LOGIC ----------
    def ask(self):
        val = self.value_var.get().strip()
        if not val or val == "e.g. rare, 4, True": 
            messagebox.showwarning("Empty Value", "Please enter a value to compare against")
            return
            
        attr = self.attr_var.get()
        keyfunc = ATTRIBUTES[attr]
        secret_truth = self.evaluate_comparison(keyfunc(self.secret), self.op_var.get(), val)
        
        # Enhanced answer dialog
        answer_text = "✅ YES" if secret_truth else "❌ NO"
        question_text = f"Is the secret card's {attr} {self.op_var.get()} {val}?"
        
        messagebox.showinfo("Answer", f"{question_text}\n\n{answer_text}")
        
        # Filter candidates
        new_candidates = [c for c in self.candidates if self.evaluate_comparison(keyfunc(c), self.op_var.get(), val) == secret_truth]
        removed = [c for c in self.candidates if c not in new_candidates]
        self.candidates = new_candidates
        
        self.update_status()
        self.update_visuals(removed)
        
        # Clear the entry for next question
        self.value_entry.delete(0, tk.END)

    def evaluate_comparison(self, card_val, op, val_raw):
        """Enhanced comparison with better error handling"""
        try:
            if isinstance(card_val, int):
                comp = int(val_raw)
                return ((op == "=" or op=="==") and card_val == comp) or \
                       (op == "<" and card_val < comp) or \
                       (op == "<=" and card_val <= comp) or \
                       (op == ">" and card_val > comp) or \
                       (op == ">=" and card_val >= comp) or \
                       (op == ":" and str(comp) in str(card_val))
            elif isinstance(card_val, bool):
                comp = val_raw.lower() in ["true","1","yes","y","t"]
                return card_val == comp
            else:
                s, v = str(card_val).lower(), val_raw.lower()
                return (op in ["=", "=="] and s==v) or (op==":" and v in s)
        except ValueError as e:
            messagebox.showerror("Invalid Value", f"Cannot compare {attr} with '{val_raw}'. Please check your input.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Comparison error: {str(e)}")
            return False

    def guess(self, card: Card):
        """Enhanced guess handling with better feedback"""
        if card.name == self.secret.name:
            self.end_time = time.time()
            elapsed = round(self.end_time - self.start_time, 2)
            
            # Calculate score based on time
            base_score = 1000
            time_penalty = min(elapsed * 10, 900)  # Max penalty of 900 points
            final_score = max(base_score - time_penalty, 100)
            
            # Victory message
            messagebox.showinfo(
                "🎉 Correct!", 
                f"Congratulations! You found the secret card!\n\n"
                f"Card: {card.name}\n"
                f"Time: {elapsed} seconds\n"
                f"Score: {int(final_score)} points"
            )
            
            self.reveal_secret(card)
            self.check_leaderboard(elapsed, int(final_score))
        else:
            messagebox.showwarning(
                "❌ Incorrect", 
                f"{card.name} is not the secret card.\nKeep trying!"
            )
            self.candidates = [c for c in self.candidates if c.name != card.name]
            self.update_status()
            self.update_visuals([card])

    # ---------- ENHANCED STATUS & VISUALS ----------
    def update_status(self):
        """Enhanced status with more information"""
        remaining = len(self.candidates)
        total = len(CARDS)
        eliminated = total - remaining
        
        status_text = f"Cards remaining: {remaining}/{total} | Eliminated: {eliminated}"
        
        if remaining <= 3:
            status_text += " | 🔥 Getting close!"
        elif remaining <= 1:
            status_text += " | 🎯 Final card!"
            
        self.status_var.set(status_text)

    def update_visuals(self, removed):
        """Enhanced visual updates with better feedback"""
        for c in removed:
            if c.name in self.card_buttons:
                frame, lbl_img, btn = self.card_buttons[c.name]
                btn.state(["disabled"])
                btn.configure(text="Eliminated", bootstyle="secondary")
                
                # Fade the image (create a grayed out version)
                try:
                    faded_img = self.load_card_image(c, (120,100), fade=True)
                    lbl_img.configure(image=faded_img)
                    lbl_img.image = faded_img
                except:
                    pass  # If image processing fails, just disable the button

    def reset_visuals(self):
        """Enhanced reset with better feedback"""
        self.candidates = CARDS.copy()
        self.start_time = time.time()
        self.end_time = None
        
        for c in CARDS:
            frame, lbl_img, btn = self.card_buttons[c.name]
            btn.state(["!disabled"])
            btn.configure(text="Guess This!", bootstyle="success-outline")
            lbl_img.configure(image=self.load_card_image(c, (120,100)))
            
        self.update_status()
        messagebox.showinfo("Reset", "All cards are back in play! Good luck!")

    def new_game(self):
        """Enhanced new game with confirmation"""
        if messagebox.askyesno("New Game", "Start a new game? This will reset your progress."):
            self.secret = random.choice(CARDS)
            self.reset_visuals()
            messagebox.showinfo("New Game", f"New secret card selected! Can you guess it?")

    def reveal_secret(self, card: Card):
        """Enhanced secret reveal with visual highlight"""
        for c in CARDS:
            frame, lbl_img, btn = self.card_buttons[c.name]
            if c.name == card.name:
                frame.configure(relief="solid", borderwidth=3)
                btn.configure(text="🎉 Winner!", bootstyle="success")

    # ---------- ENHANCED LEADERBOARD ----------
    def check_leaderboard(self, elapsed_time, score):
        """Enhanced leaderboard with score-based ranking"""
        leaderboard_data = self.leaderboard_manager.get_sorted_leaderboard()
        
        # Check if score qualifies for leaderboard (top 10)
        if len(leaderboard_data) < MAX_LEADERS or score > leaderboard_data[-1].get('score', 0):
            name = simpledialog.askstring(
                "🏆 New High Score!", 
                f"Congratulations! You scored {score} points!\n"
                f"You made it to the leaderboard!\n\n"
                "Enter your name:"
            )
            if not name or not name.strip():
                name = "Anonymous"
            
            # Add new entry
            new_entry = {
                'name': name.strip(),
                'score': score,
                'games': 1,
                'win_rate': 100,
                'best_time': elapsed_time
            }
            
            # Update existing player or add new one
            existing_player = None
            for entry in leaderboard_data:
                if entry.get('name', '').lower() == name.lower():
                    existing_player = entry
                    break
            
            if existing_player:
                # Update existing player
                existing_player['games'] += 1
                if score > existing_player.get('score', 0):
                    existing_player['score'] = score
                if elapsed_time < existing_player.get('best_time', float('inf')):
                    existing_player['best_time'] = elapsed_time
                # Recalculate win rate (simplified)
                existing_player['win_rate'] = min(100, existing_player['win_rate'] + 1)
            else:
                # Add new player
                leaderboard_data.append(new_entry)
            
            # Save updated leaderboard
            leaderboard_data.sort(key=lambda x: x.get('score', 0), reverse=True)
            leaderboard_data = leaderboard_data[:MAX_LEADERS]
            
            # Save to file
            try:
                with open(LEADERBOARD_FILE, 'w') as f:
                    json.dump(leaderboard_data, f, indent=2)
            except Exception as e:
                print(f"Error saving leaderboard: {e}")
            
            self.show_leaderboard_ui()

    def show_leaderboard_ui(self):
        """Enhanced leaderboard UI"""
        lb_window = tk.Toplevel(self.root)
        lb_window.title("🏆 Leaderboard")
        lb_window.geometry("600x400")
        lb_window.grab_set()
        lb_window.configure(bg='#2c3e50')
        
        # Header
        header_frame = ttk.Frame(lb_window, padding=20)
        header_frame.pack(fill="x")
        
        ttk.Label(
            header_frame, 
            text="🏆 TOP PLAYERS 🏆", 
            font=("Orbitron", 18, "bold"),
            foreground="#f39c12"
        ).pack()
        
        # Leaderboard content
        content_frame = ttk.Frame(lb_window, padding=(20, 0, 20, 20))
        content_frame.pack(fill="both", expand=True)
        
        # Create treeview
        columns = ("Rank", "Name", "Score", "Best Time", "Games")
        tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        
        # Populate with data
        leaderboard_data = self.leaderboard_manager.get_sorted_leaderboard()
        for i, entry in enumerate(leaderboard_data[:MAX_LEADERS], 1):
            tree.insert("", "end", values=(
                f"#{i}",
                entry.get('name', 'Anonymous'),
                entry.get('score', 0),
                f"{entry.get('best_time', 0):.1f}s",
                entry.get('games', 0)
            ))
        
        tree.pack(fill="both", expand=True, pady=10)
        
        # Close button
        ttk.Button(
            content_frame,
            text="Close",
            command=lb_window.destroy,
            bootstyle="secondary"
        ).pack(pady=10)

    # ---------- ENHANCED NAVIGATION ----------
    def return_to_menu(self):
        """Return to main menu with confirmation"""
        if messagebox.askyesno("Return to Menu", "Return to main menu? Current game progress will be lost."):
            if self.return_to_menu_callback:
                self.return_to_menu_callback()
            else:
                # Fallback - recreate main menu
                for widget in self.root.winfo_children(): 
                    widget.destroy()
                ClashRoyaleApp(self.root)

    def hint(self):
        """Enhanced hint system"""
        if len(self.candidates) <= 1:
            messagebox.showinfo("Hint", "You're down to the final card! Make your guess!")
            return
            
        key = random.choice(list(ATTRIBUTES.keys()))
        value = ATTRIBUTES[key](self.secret)
        
        # More descriptive hints
        hint_descriptions = {
            "rarity": f"The secret card's rarity is '{value}'",
            "type": f"The secret card is a {value}",
            "elixir": f"The secret card costs {value} elixir",
            "melee": f"The secret card {'is' if value else 'is not'} a melee unit",
            "flying": f"The secret card {'can' if value else 'cannot'} fly",
            "target": f"The secret card targets {value} units",
            "role": f"The secret card's role is {value}"
        }
        
        hint_text = hint_descriptions.get(key, f"The secret card's {key} is '{value}'")
        messagebox.showinfo("💡 Hint", hint_text)

    def load_card_image(self, card: Card, size=(120,100), fade=False):
        """Enhanced image loading with fade effect"""
        cache_key = (card.name, size, fade)
        if cache_key in self.photo_cache: 
            return self.photo_cache[cache_key]
            
        if card.image_file and os.path.exists(card.image_file):
            try:
                im = Image.open(card.image_file).convert("RGBA")
                im.thumbnail(size, Image.LANCZOS)
                
                if fade:
                    # Create faded version
                    faded = im.copy()
                    faded.putalpha(128)  # 50% transparency
                    
                bg = Image.new("RGBA", size, (255,255,255,0))
                x = (size[0]-im.width)//2
                y = (size[1]-im.height)//2
                
                if fade:
                    bg.paste(faded, (x,y), faded)
                else:
                    bg.paste(im, (x,y), im)
                    
                photo = ImageTk.PhotoImage(bg)
            except Exception as e:
                print(f"Error loading image for {card.name}: {e}")
                # Fallback to placeholder
                img = Image.new("RGBA", size, (200,200,200,255 if not fade else 128))
                photo = ImageTk.PhotoImage(img)
        else:
            # Placeholder image
            alpha = 255 if not fade else 128
            img = Image.new("RGBA", size, (200,200,200,alpha))
            photo = ImageTk.PhotoImage(img)
            
        self.photo_cache[cache_key] = photo
        return photo

# ---------- ENHANCED APP CLASS ----------
class ClashRoyaleApp:
    def __init__(self, root):
        self.root = root
        self.current_screen = None
        self.show_main_menu()
        
    def show_main_menu(self):
        """Show the enhanced main menu"""
        for widget in self.root.winfo_children(): 
            widget.destroy()
            
        self.main_menu = ClashRoyaleMainMenu(
            self.root,
            on_play=self.start_game,
            on_how_to_play=self.show_instructions,
            on_leaderboard=self.show_leaderboard,
            on_settings=self.show_settings
        )
        self.current_screen = "menu"
    
    def start_game(self):
        """Start the game with proper callback"""
        for widget in self.root.winfo_children(): 
            widget.destroy()
            
        self.game = GuessWhoPro(self.root, return_to_menu_callback=self.show_main_menu)
        self.current_screen = "game"
    
    def show_instructions(self):
        """Show instructions - handled by main menu"""
        pass
    
    def show_leaderboard(self):
        """Show leaderboard - handled by main menu"""
        pass
    
    def show_settings(self):
        """Show settings - handled by main menu"""
        pass

# ---------- MAIN ----------
def main():
    root = tb.Window(themename="flatly")
    root.title("Clash Royale Guess Who - Enhanced Edition")
    root.geometry("1000x800")
    root.minsize(800, 600)
    
    app = ClashRoyaleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()