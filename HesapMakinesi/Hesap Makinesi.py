import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import tkinter as tk
from moviepy import VideoFileClip
import threading
import time

#  Splash Video
class SplashVideo(tk.Toplevel):
    def __init__(self, master, video_path, duration=3):
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry("400x400+500+200")
        self.label = tk.Label(self)
        self.label.pack()
        self.video = VideoFileClip(video_path)
        self.duration = duration
        self.after(100, self.play_video)
        threading.Thread(target=self.auto_close, daemon=True).start()

    def play_video(self):
        for frame in self.video.iter_frames(fps=24, dtype="uint8"):
            img = Image.fromarray(frame).resize((400, 400))
            imgtk = ImageTk.PhotoImage(img)
            self.label.imgtk = imgtk
            self.label.config(image=imgtk)
            self.update()
            time.sleep(1 / 24)
        self.destroy()

    def auto_close(self):
        time.sleep(self.duration)
        self.destroy()

def show_splash_and_main():
    root = tk.Tk()
    root.withdraw()
    splash = SplashVideo(root, "pythonProject/cAlgo.mp4", duration=3)
    splash.wait_window()
    root.destroy()
    app = HesapMakinesiGUI()
    app.mainloop()

# --- Hesap Makinesi GUI ---
class HesapMakinesiGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hesap Makinesi")
        self.geometry("400x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Başlık simgesi için .ico dosyası
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cAlgo2.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Başlık simgesi yüklenemedi: {e}")
        else:
            print(f"Icon dosyası bulunamadı: {icon_path}")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.display_var = ctk.StringVar(value="0")
        self.display = ctk.CTkEntry(
            self, font=("Consolas", 32, "bold"),
            justify="right", textvariable=self.display_var, corner_radius=10
        )
        self.display.grid(row=1, column=0, columnspan=2, padx=15, pady=(10, 15), sticky="nsew")
        self.display.configure(state="readonly")

        self.binary_mode = False

        self.binary_button = ctk.CTkButton(self, text="Binary Mod", fg_color="#607d8b", hover_color="#455a64", command=self.toggle_binary_mode)
        self.binary_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew", columnspan=1)

        self.base_var = ctk.StringVar(value="2")
        self.base_optionmenu = ctk.CTkOptionMenu(self, values=["2", "8", "10", "16"], variable=self.base_var, width=80)
        self.base_optionmenu.grid(row=5, column=1, padx=10, pady=(0,10), sticky="ew")

        self.convert_button = ctk.CTkButton(self, text="Convert", fg_color="#ffa000", hover_color="#ff6f00", command=self.convert_result)
        self.convert_button.grid(row=4, column=1, padx=10, pady=10, sticky="ew", columnspan=1)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=5, padx=10, sticky="nsew")
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1, uniform="op")
        button_frame.grid_rowconfigure(0, weight=1)

        self.button_topla = ctk.CTkButton(button_frame, text="+", width=80, height=40, fg_color="#1e88e5", hover_color="#1565c0", font=("Arial", 18, "bold"), command=lambda: self.set_operation("+"))
        self.button_topla.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.button_cikar = ctk.CTkButton(button_frame, text="-", width=80, height=40, fg_color="#1e88e5", hover_color="#1565c0", font=("Arial", 18, "bold"), command=lambda: self.set_operation("-"))
        self.button_cikar.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.button_carp = ctk.CTkButton(button_frame, text="×", width=80, height=40, fg_color="#1e88e5", hover_color="#1565c0", font=("Arial", 18, "bold"), command=lambda: self.set_operation("*"))
        self.button_carp.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        self.button_bol = ctk.CTkButton(button_frame, text="÷", width=80, height=40, fg_color="#1e88e5", hover_color="#1565c0", font=("Arial", 18, "bold"), command=lambda: self.set_operation("/"))
        self.button_bol.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")

        numpad_frame = ctk.CTkFrame(self, fg_color="transparent")
        numpad_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        for i in range(5):
            numpad_frame.grid_rowconfigure(i, weight=1, uniform="np")
        for j in range(3):
            numpad_frame.grid_columnconfigure(j, weight=1, uniform="np")

        numpad_buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2),
            ('0', 4, 1), ('.', 4, 2), ('C', 4, 0),
            ('=', 0, 2)
        ]
        self.numpad_buttons_dict = {}
        for (text, r, c) in numpad_buttons:
            btn = ctk.CTkButton(
                numpad_frame, text=text, font=("Arial", 18, "bold"),
                width=80, height=60,
                fg_color="#263238" if text not in ("=", "C") else ("#43a047" if text == "=" else "#e53935"),
                hover_color="#37474f" if text not in ("=", "C") else ("#388e3c" if text == "=" else "#b71c1c"),
                command=lambda t=text: self.numpad_press(t)
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            self.numpad_buttons_dict[text] = btn

        self.first_value = None
        self.operation = None
        self.reset_next = False
        self.bind("<Key>", self.key_input)

    def toggle_binary_mode(self):
        self.binary_mode = not self.binary_mode
        if self.binary_mode:
            self.binary_button.configure(text="Binary Mod: ON", fg_color="#388e3c")
            for key, btn in self.numpad_buttons_dict.items():
                if key not in ("1", "0", "C", "=",):
                    btn.configure(state="disabled")
        else:
            self.binary_button.configure(text="Binary Mod", fg_color="#607d8b")
            for btn in self.numpad_buttons_dict.values():
                btn.configure(state="normal")

    def numpad_press(self, value):
        if self.binary_mode and value not in ("1", "0", "C", "=",):
            return
        if value == 'C':
            self.display_var.set("0")
            self.first_value = None
            self.operation = None
            self.reset_next = False
        elif value == '=':
            self.calculate_result()
        else:
            current = self.display_var.get()
            if self.reset_next or current == "0":
                current = ""
                self.reset_next = False
            if value == '.' and '.' in current:
                return
            self.display_var.set(current + value)

    def set_operation(self, op):
        try:
            self.first_value = int(self.display_var.get(), 2) if self.binary_mode else float(self.display_var.get())
            self.operation = op
            self.reset_next = True
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı girin!")

    def calculate_result(self):
        if self.first_value is None or self.operation is None:
            return
        try:
            second_value = int(self.display_var.get(), 2) if self.binary_mode else float(self.display_var.get())
            if self.operation == "+":
                result = self.first_value + second_value
            elif self.operation == "-":
                result = self.first_value - second_value
            elif self.operation == "*":
                result = self.first_value * second_value
            elif self.operation == "/":
                if second_value == 0:
                    messagebox.showerror("Hata", "Bir sayı sıfıra bölünemez!")
                    return
                result = self.first_value // second_value if self.binary_mode else self.first_value / second_value
            else:
                return
            if self.binary_mode:
                self.display_var.set(bin(result)[2:])
            else:
                self.display_var.set(str(result))
            self.first_value = None
            self.operation = None
            self.reset_next = True
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı girin!")

    def convert_result(self):
        try:
            base = int(self.base_var.get())
            value = self.display_var.get()
            dec_value = int(value, 2) if self.binary_mode else int(float(value))
            if base == 2:
                converted = bin(dec_value)[2:]
            elif base == 8:
                converted = oct(dec_value)[2:]
            elif base == 10:
                converted = str(dec_value)
            elif base == 16:
                converted = hex(dec_value)[2:].upper()
            else:
                digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                if base < 2 or base > 36:
                    raise ValueError
                result = ""
                n = dec_value
                while n > 0:
                    result = digits[n % base] + result
                    n //= base
                converted = result or "0"
            self.display_var.set(converted)
        except Exception:
            messagebox.showerror("Hata", "Dönüşüm yapılamadı! Tabana ve girişe dikkat edin.")

    def key_input(self, event):
        if event.char.isdigit() or event.char == '.':
            self.numpad_press(event.char)
        elif event.char in "+-*/":
            self.set_operation(event.char)
        elif event.keysym == "Return":
            self.numpad_press("=")
        elif event.keysym in ("BackSpace", "Delete"):
            current = self.display_var.get()
            self.display_var.set(current[:-1] if len(current) > 1 else "0")

if __name__ == "__main__":
    show_splash_and_main()
