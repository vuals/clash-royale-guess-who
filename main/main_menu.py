import tkinter as tk
from tkinter import ttk, font, messagebox
from PIL import Image, ImageTk, ImageFilter
import os
import ttkbootstrap as tb

class ClashRoyaleMainMenu:
    def __init__(self, root, on_play=None, on_how_to_play=None, on_leaderboard=None, on_settings=None):
        self.root = root
        self.on_play = on_play or self.default_play
        self.on_how_to_play = on_how_to_play or self.default_how_to_play
        self.on_leaderboard = on_leaderboard or self.default_leaderboard
        self.on_settings = on_settings or self.default_settings
        
        # Configure root window
        self.root.title("Clash Royale Guess Who")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e293b')
        self.root.resizable(True, True)
        
        # Initialize ttkbootstrap style
        self.style = tb.Style(theme="flatly")
        
        # Color scheme matching the React version
        self.colors = {
            'bg_primary': '#1e293b',
            'bg_card': '#1e293b',
            'border_blue': '#60a5fa',
            'text_gold': "#dda823",
            'text_white': '#ffffff',
            'text_light_blue': '#dbeafe',
            'button_orange': "#fd5e08",
            'button_orange_hover': "#b84112",
            'button_cyan': "#0aa1c7",
            'button_yellow': "#ddab14",
            'button_gray': "#6d727c"
        }
        
        # Load and setup background
        self.setup_background()
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg=self.colors['bg_primary'])
        self.main_frame.pack(fill='both', expand=True)
        
        # Setup fonts
        self.setup_fonts()
        
        # Create UI elements
        self.create_ui()
        
        # Center the window
        self.center_window()
    
    def setup_fonts(self):
        """Setup custom fonts for the UI"""
        self.title_font = font.Font(family="Arial", size=32, weight="bold")
        self.subtitle_font = font.Font(family="Arial", size=18, weight="bold")
        self.button_font = font.Font(family="Arial", size=14, weight="bold")
        self.desc_font = font.Font(family="Arial", size=12)
    
    def setup_background(self):
        """Setup background image if available"""
        try:
            # Try to load background image (you'll need to provide this)
            bg_path = "assets/clash_royale_background.png"
            if os.path.exists(bg_path):
                self.bg_image = Image.open(bg_path)
                self.bg_image = self.bg_image.resize((800, 600), Image.Resampling.LANCZOS)
                # Add overlay effect
                overlay = Image.new('RGBA', self.bg_image.size, (30, 41, 59, 180))
                self.bg_image = Image.alpha_composite(self.bg_image.convert('RGBA'), overlay)
                self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            else:
                self.bg_photo = None
        except Exception as e:
            print(f"Could not load background image: {e}")
            self.bg_photo = None
    
    def create_ui(self):
        """Create the main UI elements"""
        # Background label if image is available
        if self.bg_photo:
            bg_label = tk.Label(self.main_frame, image=self.bg_photo, bg=self.colors['bg_primary'])
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Main container frame
        container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        container.pack(expand=True, fill='both')
        
        # Title section
        title_frame = tk.Frame(container, bg=self.colors['bg_primary'])
        title_frame.pack(pady=(50, 30))
        
        # Crown symbols (using text symbols)
        crown_left = tk.Label(title_frame, text="♛", fg=self.colors['text_gold'], 
                             bg=self.colors['bg_primary'], font=("Arial", 24))
        crown_left.pack(side='left', padx=10)
        
        # Title text frame
        title_text_frame = tk.Frame(title_frame, bg=self.colors['bg_primary'])
        title_text_frame.pack(side='left')
        
        # Main title
        title_label = tk.Label(title_text_frame, text="ROYALE", 
                              fg=self.colors['text_gold'], bg=self.colors['bg_primary'],
                              font=self.title_font)
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(title_text_frame, text="GUESS WHO", 
                                 fg=self.colors['text_white'], bg=self.colors['bg_primary'],
                                 font=self.subtitle_font)
        subtitle_label.pack()
        
        # Crown right
        crown_right = tk.Label(title_frame, text="♛", fg=self.colors['text_gold'], 
                              bg=self.colors['bg_primary'], font=("Arial", 24))
        crown_right.pack(side='left', padx=10)
        
        # Description
        desc_label = tk.Label(container, text="Can you guess the Clash Royale card?",
                             fg=self.colors['text_light_blue'], bg=self.colors['bg_primary'],
                             font=self.desc_font)
        desc_label.pack(pady=10)
        
        # Menu card frame
        menu_frame = tk.Frame(container, bg=self.colors['bg_card'], relief='raised', bd=2)
        menu_frame.pack(pady=20, padx=50, ipadx=20, ipady=20)
        
        # Configure menu frame border
        menu_frame.configure(highlightbackground=self.colors['border_blue'], 
                           highlightthickness=2)
        
        # Play button (main action)
        play_btn = tk.Button(menu_frame, text="▶ PLAY", 
                           bg=self.colors['button_orange'],
                           fg=self.colors['text_white'],
                           font=self.button_font,
                           relief='raised', bd=2,
                           pady=15, padx=40,
                           command=self.on_play,
                           cursor='hand2')
        play_btn.pack(fill='x', pady=5)
        
        # How to Play button
        help_btn = tk.Button(menu_frame, text="? How to Play",
                           bg=self.colors['button_cyan'],
                           fg=self.colors['text_white'],
                           font=self.button_font,
                           relief='raised', bd=2,
                           pady=12, padx=40,
                           command=self.on_how_to_play,
                           cursor='hand2')
        help_btn.pack(fill='x', pady=5)
        
        # Leaderboard button
        leaderboard_btn = tk.Button(menu_frame, text="🏆 Leaderboard",
                                  bg=self.colors['button_yellow'],
                                  fg=self.colors['text_white'],
                                  font=self.button_font,
                                  relief='raised', bd=2,
                                  pady=12, padx=40,
                                  command=self.on_leaderboard,
                                  cursor='hand2')
        leaderboard_btn.pack(fill='x', pady=5)
        
        # Settings button
        settings_btn = tk.Button(menu_frame, text="⚙ Settings",
                               bg=self.colors['button_gray'],
                               fg=self.colors['text_white'],
                               font=self.button_font,
                               relief='raised', bd=2,
                               pady=12, padx=40,
                               command=self.on_settings,
                               cursor='hand2')
        settings_btn.pack(fill='x', pady=5)
        
        # Footer
        footer_frame = tk.Frame(container, bg=self.colors['bg_primary'])
        footer_frame.pack(side='bottom', pady=20)
        
        footer_text = tk.Label(footer_frame, text="Test your knowledge of Clash Royale cards!",
                              fg=self.colors['text_light_blue'], bg=self.colors['bg_primary'],
                              font=self.desc_font)
        footer_text.pack()
        
        footer_subtext = tk.Label(footer_frame, text="Inspired by the classic Guess Who? game",
                                 fg=self.colors['text_light_blue'], bg=self.colors['bg_primary'],
                                 font=("Arial", 10))
        footer_subtext.pack()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Default callback methods (to be overridden)
    def default_play(self):
        print("Play button clicked - implement your game start logic here")
        # You can replace this with your game's start function
    
    def default_how_to_play(self):
        print("How to Play button clicked - implement help dialog here")
        # You can replace this with your help/instructions function
    
    def default_leaderboard(self):
        print("Leaderboard button clicked - implement leaderboard display here")
        # You can replace this with your leaderboard function
    
    def default_settings(self):
        print("Settings button clicked - implement settings dialog here")
        # You can replace this with your settings function


def main():
    """Example usage of the main menu"""
    root = tk.Tk()
    
    # Example callback functions for your game
    def start_game():
        print("Starting Clash Royale Guess Who game...")
        # Add your game start logic here
        # root.destroy()  # Close menu and start game
    
    def show_instructions():
        # Create a simple instruction dialog
        instruction_window = tk.Toplevel(root)
        instruction_window.title("How to Play")
        instruction_window.geometry("400x300")
        instruction_window.configure(bg='#1e293b')
        
        text = """
        HOW TO PLAY CLASH ROYALE GUESS WHO
        
        1. Choose a Clash Royale card to guess
        2. Ask yes/no questions about the card
        3. Try to guess the card in as few questions as possible
        4. Compare your score with others on the leaderboard
        
        Features of cards you can ask about:
        • Elixir cost
        • Card type (troop, spell, building)
        • Rarity (common, rare, epic, legendary)
        • Arena unlocked
        • Special abilities
        """
        
        label = tk.Label(instruction_window, text=text, 
                        fg='white', bg='#1e293b',
                        font=("Arial", 11), justify='left')
        label.pack(padx=20, pady=20)
        
        close_btn = tk.Button(instruction_window, text="Got it!", 
                             command=instruction_window.destroy,
                             bg='#ea580c', fg='white', font=("Arial", 12, "bold"))
        close_btn.pack(pady=10)
    
    def show_leaderboard():
        print("Showing leaderboard...")
        # Implement your leaderboard logic here
    
    def show_settings():
        print("Showing settings...")
        # Implement your settings logic here
    
    # Create the main menu with custom callbacks
    menu = ClashRoyaleMainMenu(
        root, 
        on_play=start_game,
        on_how_to_play=show_instructions,
        on_leaderboard=show_leaderboard,
        on_settings=show_settings
    )
    
    root.mainloop()


if __name__ == "__main__":
    main()