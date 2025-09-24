import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import os


class ClashRoyaleMainMenu:
    def __init__(self, root, bg_image_path="extra images/clash royale scene.png",
                 on_play=None, on_how_to_play=None, on_leaderboard=None, on_settings=None):
        self.root = root
        self.bg_image_path = bg_image_path

        self.on_play = on_play or self.default_play
        self.on_how_to_play = on_how_to_play or self.default_how_to_play
        self.on_leaderboard = on_leaderboard or self.default_leaderboard
        self.on_settings = on_settings or self.default_settings

        # Configure window
        self.root.title("Clash Royale Guess Who")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0a0e27")
        self.root.resizable(True, True)

        # Center on screen
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - 1400) // 2, (sh - 900) // 2
        self.root.geometry(f"1400x900+{x}+{y}")

        # Fonts
        self.setup_fonts()

        # Canvas
        self.canvas = tk.Canvas(root, highlightthickness=0, bg="#0a0e27")
        self.canvas.pack(fill="both", expand=True)

        self.bg_photo = None
        self.overlay_color = (0, 0, 0, 140)  # dark overlay for readability

        # Draw
        self.setup_background()
        self.create_ui()

        # Resize binding
        self.canvas.bind("<Configure>", self.on_resize)

    def setup_fonts(self):
        try:
            self.title_font = font.Font(family="Arial Black", size=72, weight="bold")
        except:
            self.title_font = font.Font(family="Arial", size=72, weight="bold")

        try:
            self.subtitle_font = font.Font(family="Arial Black", size=36, weight="bold")
        except:
            self.subtitle_font = font.Font(family="Arial", size=36, weight="bold")

        self.desc_font = font.Font(family="Arial", size=18, weight="bold")
        self.button_font = font.Font(family="Arial", size=18, weight="bold")
        self.small_font = font.Font(family="Arial", size=12)

    def setup_background(self):
        cw = self.canvas.winfo_width() or 1400
        ch = self.canvas.winfo_height() or 900

        if os.path.exists(self.bg_image_path):
            from PIL import ImageDraw
            img = Image.open(self.bg_image_path).convert("RGBA")
            img = img.resize((cw, ch), Image.LANCZOS)

            overlay = Image.new("RGBA", img.size, self.overlay_color)
            img = Image.alpha_composite(img, overlay)

            self.bg_photo = ImageTk.PhotoImage(img)
            self.canvas.delete("background")
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo, tags="background")
        else:
            self.canvas.create_rectangle(0, 0, cw, ch, fill="#0a0e27", outline="", tags="background")

    def create_ui(self):
        self.canvas.delete("ui")
        cw = self.canvas.winfo_width() or 1400
        ch = self.canvas.winfo_height() or 900
        cx = cw // 2

        # Title section (top quarter)
        self.create_title(cx, ch // 5)

        # Buttons (middle lower section)
        self.create_buttons(cx, ch // 2 + 100)

        # Footer
        self.create_footer(cx, ch - 60)

    def create_title(self, cx, y):
        shadow = 6

        # Main title
        self.canvas.create_text(cx + shadow, y + shadow,
                                text="ROYALE", font=self.title_font,
                                fill="#000000", tags="ui")
        self.canvas.create_text(cx, y, text="ROYALE",
                                font=self.title_font, fill="#FFD700", tags="ui")

        # Subtitle
        self.canvas.create_text(cx + shadow // 2, y + 70 + shadow // 2,
                                text="GUESS WHO", font=self.subtitle_font,
                                fill="#000000", tags="ui")
        self.canvas.create_text(cx, y + 70, text="GUESS WHO",
                                font=self.subtitle_font, fill="#FFFFFF", tags="ui")

        # Tagline
        self.canvas.create_text(cx, y + 120,
                                text="Can you guess the Clash Royale card?",
                                font=self.desc_font, fill="#E0E7FF", tags="ui")

    def create_buttons(self, cx, y_start):
        spacing = 80
        button_width, button_height = 400, 60

        self.create_custom_button(cx, y_start, button_width, button_height,
                                  "▶  PLAY", "#ff4757", "#ffffff",
                                  self.button_font, self.on_play, "#ff6b7a")

        self.create_custom_button(cx, y_start + spacing, button_width, button_height,
                                  "❓  HOW TO PLAY", "#2f3542", "#70a1ff",
                                  self.button_font, self.on_how_to_play, "#5352ed")

        self.create_custom_button(cx, y_start + spacing * 2, button_width, button_height,
                                  "🏆  LEADERBOARD", "#2f3542", "#ffa502",
                                  self.button_font, self.on_leaderboard, "#ff9f43")

        self.create_custom_button(cx, y_start + spacing * 3, button_width, button_height,
                                  "⚙️  SETTINGS", "#2f3542", "#ffffff",
                                  self.button_font, self.on_settings, "#747d8c")

    def create_custom_button(self, x, y, width, height, text, bg_color, text_color,
                             font_obj, command, border_color=None):
        shadow_offset = 5
        self.canvas.create_rectangle(
            x - width // 2 + shadow_offset, y - height // 2 + shadow_offset,
            x + width // 2 + shadow_offset, y + height // 2 + shadow_offset,
            fill="#000000", outline="", tags="ui"
        )

        btn_id = self.canvas.create_rectangle(
            x - width // 2, y - height // 2, x + width // 2, y + height // 2,
            fill=bg_color, outline=border_color or bg_color, width=3, tags="ui"
        )

        text_id = self.canvas.create_text(
            x, y, text=text, font=font_obj, fill=text_color, tags="ui"
        )

        info = {
            "bg_id": btn_id,
            "text_id": text_id,
            "command": command,
            "original_bg": bg_color,
            "hover_bg": self.get_hover_color(bg_color),
            "border_color": border_color
        }

        for element in [btn_id, text_id]:
            self.canvas.tag_bind(element, "<Enter>",
                                 lambda e, i=info: self.on_button_hover(i))
            self.canvas.tag_bind(element, "<Leave>",
                                 lambda e, i=info: self.on_button_leave(i))
            self.canvas.tag_bind(element, "<Button-1>",
                                 lambda e, i=info: self.on_button_click(i))

    def get_hover_color(self, color):
        return {
            "#ff4757": "#ff6b7a",
            "#2f3542": "#40495a"
        }.get(color, color)

    def on_button_hover(self, info):
        self.canvas.itemconfig(info["bg_id"], fill=info["hover_bg"])
        if info["border_color"]:
            self.canvas.itemconfig(info["bg_id"], outline=info["border_color"], width=4)
        self.root.config(cursor="hand2")

    def on_button_leave(self, info):
        self.canvas.itemconfig(info["bg_id"], fill=info["original_bg"])
        if info["border_color"]:
            self.canvas.itemconfig(info["bg_id"], outline=info["border_color"], width=3)
        self.root.config(cursor="")

    def on_button_click(self, info):
        self.canvas.itemconfig(info["bg_id"], fill="#ffffff")
        self.root.after(100, lambda: self.canvas.itemconfig(info["bg_id"],
                                                            fill=info["original_bg"]))
        if info["command"]:
            self.root.after(150, info["command"])

    def create_footer(self, cx, y):
        self.canvas.create_text(cx, y,
                                text="Inspired by the classic Guess Who? game • Test your Clash Royale knowledge!",
                                font=("Arial", 12, "bold"), fill="#DBEAFE", tags="ui")

    def on_resize(self, event):
        self.setup_background()
        self.create_ui()

    # Default callbacks
    def default_play(self): print("Play clicked")
    def default_how_to_play(self): print("How to play clicked")
    def default_leaderboard(self): print("Leaderboard clicked")
    def default_settings(self): print("Settings clicked")


def main():
    root = tk.Tk()

    menu = ClashRoyaleMainMenu(
        root,
        bg_image_path="extra images/clash royale scene.png",
        on_play=lambda: messagebox.showinfo("Play", "Start Game!"),
        on_how_to_play=lambda: messagebox.showinfo("How to Play", "Instructions..."),
        on_leaderboard=lambda: messagebox.showinfo("Leaderboard", "Coming soon!"),
        on_settings=lambda: messagebox.showinfo("Settings", "Coming soon!")
    )

    root.mainloop()


if __name__ == "__main__":
    main()
