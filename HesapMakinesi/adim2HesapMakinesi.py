import tkinter as tk
from tkinter import messagebox

class HesapMakinesiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hesap Makinesi")

        tk.Label(root, text="Sayı 1:").grid(row=0, column=0)
        tk.Label(root, text="Sayı 2:").grid(row=1, column=0)

        self.entry_a = tk.Entry(root)
        self.entry_b = tk.Entry(root)
        self.entry_a.grid(row=0, column=1)
        self.entry_b.grid(row=1, column=1)

        tk.Button(root, text="Topla", command=self.topla).grid(row=2, column=0)
        tk.Button(root, text="Çıkar", command=self.cikar).grid(row=2, column=1)
        tk.Button(root, text="Çarp", command=self.carp).grid(row=3, column=0)
        tk.Button(root, text="Böl", command=self.bol).grid(row=3, column=1)

        self.sonuc_label = tk.Label(root, text="Sonuç: ")
        self.sonuc_label.grid(row=4, column=0, columnspan=2)

    def get_values(self):
        try:
            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            return a, b
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayılar girin!")
            return None, None

    def topla(self):
        a, b = self.get_values()
        if a is not None:
            self.sonuc_label.config(text=f"Sonuç: {a + b}")

    def cikar(self):
        a, b = self.get_values()
        if a is not None:
            self.sonuc_label.config(text=f"Sonuç: {a - b}")

    def carp(self):
        a, b = self.get_values()
        if a is not None:
            self.sonuc_label.config(text=f"Sonuç: {a * b}")

    def bol(self):
        a, b = self.get_values()
        if a is not None:
            if b == 0:
                messagebox.showerror("Hata", "Bir sayı sıfıra bölünemez!")
            else:
                self.sonuc_label.config(text=f"Sonuç: {a / b}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HesapMakinesiGUI(root)
    root.mainloop()