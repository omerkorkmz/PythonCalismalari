import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
# Veritabanı oluşturma ve tabloları kontrol etme
def create_database():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # Inventory tablosunu oluştur
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            location TEXT
        )
    ''')
    
    # Loans tablosunu oluştur veya güncelle
    cursor.execute("PRAGMA table_info(loans)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if not columns:  # Eğer loans tablosu yoksa
        cursor.execute('''
            CREATE TABLE loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                loan_quantity INTEGER NOT NULL,
                borrower_name TEXT NOT NULL,
                borrower_surname TEXT NOT NULL,
                phone TEXT NOT NULL,
                return_date TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES inventory(id)
            )
        ''')
    else:  # Eğer tablo varsa eksik sütunları ekle
        if 'product_name' not in columns:
            cursor.execute("ALTER TABLE loans ADD COLUMN product_name TEXT NOT NULL DEFAULT ''")
        if 'product_id' not in columns:
            cursor.execute("ALTER TABLE loans ADD COLUMN product_id INTEGER")
        if 'loan_quantity' not in columns:
            cursor.execute("ALTER TABLE loans ADD COLUMN loan_quantity INTEGER NOT NULL DEFAULT 0")
        if 'borrower_name' not in columns:
            cursor.execute("ALTER TABLE loans ADD COLUMN borrower_name TEXT NOT NULL DEFAULT ''")
        if 'borrower_surname' not in columns:
            cursor.execute("ALTER TABLE loans ADD COLUMN borrower_surname TEXT NOT NULL DEFAULT ''")
        if 'phone' not in columns:
            cursor.execute("ALTER TABLE loans ADD COLUMN phone TEXT NOT NULL DEFAULT ''")
        if 'return_date' not in columns:
            cursor.execute("ALTER TABLE loans ADD COLUMN return_date TEXT NOT NULL DEFAULT ''")
    
    conn.commit()
    conn.close()
# Eksik location sütununu kontrol etme
def ensure_location_column():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(inventory)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'location' not in columns:
        cursor.execute("ALTER TABLE inventory ADD COLUMN location TEXT DEFAULT 'Bilinmiyor'")
        conn.commit()
    conn.close()

# Ürün ekleme
def add_product():
    name = entry_name.get()
    quantity = entry_quantity.get()
    location = dropdown_location.get()

    if name and quantity.isdigit():
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (product_name, quantity, location) VALUES (?, ?, ?)",
                       (name, int(quantity), location))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", f"{name} başarıyla eklendi.")
        clear_entries()
        list_products()
    else:
        messagebox.showerror("Hata", "Geçerli ürün adı ve miktar girin.")

# Stok güncelleme
def update_stock(increase=None):
    id_val = entry_id.get()
    quantity = entry_quantity.get()

    if id_val.isdigit() and quantity.isdigit():
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        if increase is None:
            cursor.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (int(quantity), int(id_val)))
        elif increase:
            cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (int(quantity), int(id_val)))
        else:
            cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (int(quantity), int(id_val)))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", f"ID {id_val} güncellendi.")
        clear_entries()
        list_products()
    else:
        messagebox.showerror("Hata", "Geçerli ID ve miktar girin.")
def delete_product():
    id_val = entry_id.get().strip()

    # Eğer hiç ID girilmediyse, tüm ürünleri silmeyi teklif et
    if id_val == "":
        if messagebox.askyesno("Tüm Ürünleri Sil", 
                               "Hiçbir ID girmediniz.\nTüm ürünleri silmek istiyor musunuz?"):
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory")
            conn.commit()
            conn.close()
            messagebox.showinfo("Silindi", "Tüm ürünler silindi.")
            clear_entries()
            list_products()
        return

    # Eğer ID girilmişse, tek ürünü silmeye devam et
    if id_val.isdigit():
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        
        # Ürünün varlığını kontrol et
        cursor.execute("SELECT product_name FROM inventory WHERE id = ?", (int(id_val),))
        product = cursor.fetchone()
        
        if product:
            product_name = product[0]
            cursor.execute("SELECT COUNT(*) FROM loans WHERE product_name = ?", (product_name,))
            loan_count = cursor.fetchone()[0]
            
            if loan_count > 0:
                if not messagebox.askyesno("Uyarı", 
                                           f"Bu ürünün {loan_count} adet ödünç kaydı var.\n"
                                           "Silerseniz iade işlemlerinde sorun yaşayabilirsiniz.\n"
                                           "Yine de silmek istiyor musunuz?"):
                    conn.close()
                    return
            
            # Ürünü sil
            cursor.execute("DELETE FROM inventory WHERE id = ?", (int(id_val),))
            conn.commit()
            conn.close()
            messagebox.showinfo("Silindi", f"ID {id_val} silindi.")
            clear_entries()
            list_products()
        else:
            conn.close()
            messagebox.showerror("Hata", "Bu ID ile eşleşen ürün bulunamadı.")
    else:
        messagebox.showerror("Hata", "Geçerli bir ID girin ya da boş bırakarak tüm ürünleri silin.")
   
# Ürün listeleme
def list_products():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)
    conn.close()

def list_clear():
    for row in tree.get_children():
        tree.delete(row)

# Arama
def search_product():
    id_val = entry_id.get()
    name_val = entry_name.get().strip()

    # Eğer ID girilmişse, ID'ye göre arama yap
    if id_val.isdigit():
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE id = ?", (int(id_val),))
        row = cursor.fetchone()
        tree.delete(*tree.get_children())
        if row:
            tree.insert("", "end", values=row)
        else:
            messagebox.showinfo("Sonuç", "Ürün bulunamadı.")
        conn.close()
    
    # Eğer ürün adı girilmişse, ürün adına göre arama yap
    elif name_val:
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE product_name LIKE ?", ('%' + name_val + '%',))
        rows = cursor.fetchall()
        tree.delete(*tree.get_children())
        if rows:
            for row in rows:
                tree.insert("", "end", values=row)
        else:
            messagebox.showinfo("Sonuç", "Ürün bulunamadı.")
        conn.close()
    
    # Eğer hiçbir şey girilmemişse
    else:
        messagebox.showinfo("Hata", "Lütfen bir ID veya ürün adı girin.")

# Giriş alanlarını temizle
def clear_entries():
    entry_id.delete(0, "end")
    entry_name.delete(0, "end")
    entry_quantity.delete(0, "end")
    dropdown_location.set("Secim Yapiniz")

# Ödünç verilecek ürün ve bilgileri al
def loan_product():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Hata", "Ödünç verilecek ürünü seçin.")
        return
    
    product = tree.item(selected_item)["values"]
    
    # Ürün bilgilerini al
    product_id = product[0]
    product_name = product[1]
    product_quantity = product[2]

    loan_window = ctk.CTkToplevel(app)
    loan_window.geometry("600x400")
    loan_window.title(f"{product_name} - Ödünç Ver")

    # Kullanıcıdan bilgileri al
    ctk.CTkLabel(loan_window, text="İsim:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_name_loan = ctk.CTkEntry(loan_window)
    entry_name_loan.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(loan_window, text="Soyisim:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_surname_loan = ctk.CTkEntry(loan_window)
    entry_surname_loan.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(loan_window, text="Telefon No:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_phone_loan = ctk.CTkEntry(loan_window)
    entry_phone_loan.grid(row=2, column=1, padx=5, pady=5)

    ctk.CTkLabel(loan_window, text="İade Tarihi (dd/mm/yyyy):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_return_date = ctk.CTkEntry(loan_window)
    entry_return_date.grid(row=3, column=1, padx=5, pady=5)

    ctk.CTkLabel(loan_window, text="Verilen Miktar:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    entry_quantity_loan = ctk.CTkEntry(loan_window)
    entry_quantity_loan.grid(row=4, column=1, padx=5, pady=5)

    # Onay butonu
    def confirm_loan():
        name = entry_name_loan.get()
        surname = entry_surname_loan.get()
        phone = entry_phone_loan.get()
        return_date = entry_return_date.get()
        loan_quantity = entry_quantity_loan.get()

            # Veri doğrulama
        try:
            return_date_obj = datetime.strptime(return_date, "%d/%m/%Y")
            return_date_str = return_date_obj.strftime("%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir tarih formatı girin (dd/mm/yyyy).")
            return

        if not loan_quantity.isdigit() or int(loan_quantity) > int(product_quantity):
            messagebox.showerror("Hata", "Geçerli bir miktar girin.")
            return

        # Ödünç bilgilerini veritabanına kaydet
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO loans (product_id, product_name, loan_quantity, borrower_name, borrower_surname, phone, return_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, product_name, int(loan_quantity), name, surname, phone, return_date_str))
            
        # Stoktan düşür
        cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (int(loan_quantity), product_id))
            
        conn.commit()
        conn.close()

        # Ödünç bilgilerini yazdır
        loan_info = f"Ürün: {product_name}\nMiktar: {loan_quantity}\nİsim: {name} {surname}\nTelefon: {phone}\nİade Tarihi: {return_date_str}"
        messagebox.showinfo("Ödünç Verildi", loan_info)

        # Listeyi güncelle
        load_loans()
        list_products()
        loan_window.destroy()
        
    ctk.CTkButton(loan_window, text="Ödünç Ver", command=confirm_loan).grid(row=5, column=0, columnspan=2, pady=10)   

# Ödünç listesini yükle
def load_loans():
    for row in loan_list.get_children():
        loan_list.delete(row)
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, loan_quantity, borrower_name, borrower_surname, phone, return_date FROM loans")
    rows = cursor.fetchall()
    for row in rows:
        loan_list.insert("", "end", values=row)
    conn.close()


def toggle_loan_buttons():
    if loan_buttons_frame.winfo_ismapped():
        loan_buttons_frame.pack_forget()
        toggle_btn.configure(text="Ödünç Araçları ▼")
    else:
        loan_buttons_frame.pack(pady=10, fill="x")
        toggle_btn.configure(text="Ödünç Araçları ▲")

def return_product():
    selected = loan_list.selection()
    if not selected:
        messagebox.showerror("Hata", "Lütfen iade edilecek ürünü seçin")
        return
    
    item = loan_list.item(selected[0])
    product_name = item['values'][0]
    borrower = f"{item['values'][2]} {item['values'][3]}"
    loan_quantity = item['values'][1]
    
    if messagebox.askyesno("Onay", f"{borrower} adlı kişiden {product_name} ürünü iade alındı mı?"):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        
        # Önce ürünün envanterde olup olmadığını kontrol et
        cursor.execute("SELECT id, quantity FROM inventory WHERE product_name = ?", (product_name,))
        product = cursor.fetchone()
        
        if product:
            # Ürün envanterde varsa miktarı güncelle
            cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", 
                          (loan_quantity, product[0]))
        else:
            # Ürün envanterde yoksa yeniden ekle
            cursor.execute("INSERT INTO inventory (product_name, quantity, location) VALUES (?, ?, ?)",
                          (product_name, loan_quantity, "Bilinmiyor"))
        
        # Ödünç kaydını sil
        cursor.execute("DELETE FROM loans WHERE product_name = ? AND borrower_name = ? AND borrower_surname = ?",
                      (product_name, item['values'][2], item['values'][3]))
        
        conn.commit()
        conn.close()
        
        load_loans()
        list_products()
        messagebox.showinfo("Başarılı", "Ürün iade alındı ve stok güncellendi")

def filter_overdue():
    today = datetime.now().strftime("%d/%m/%Y")
    for item in loan_list.get_children():
        return_date = loan_list.item(item)['values'][5]
        try:
            return_date_obj = datetime.strptime(return_date, "%d/%m/%Y")
            today_obj = datetime.strptime(today, "%d/%m/%Y")
            if return_date_obj < today_obj:
                loan_list.item(item, tags=("overdue",))
            else:
                loan_list.item(item, tags=())
        except ValueError:
            pass
    
    loan_list.tag_configure("overdue", background="#ffcccc")

def filter_today():
    today = datetime.now().strftime("%d/%m/%Y")
    for item in loan_list.get_children():
        return_date = loan_list.item(item)['values'][5]
        if return_date == today:
            loan_list.item(item, tags=("today",))
        else:
            loan_list.item(item, tags=())
    
    loan_list.tag_configure("today", background="#ffffcc")

def show_all_loans():
    for item in loan_list.get_children():
        loan_list.item(item, tags=())
    load_loans()

def edit_loan():
    selected = loan_list.selection()
    if not selected:
        messagebox.showerror("Hata", "Lütfen düzenlenecek kaydı seçin")
        return
    
    item = loan_list.item(selected[0])
    
    edit_window = ctk.CTkToplevel(app)
    edit_window.title("Ödünç Kaydını Düzenle")
    edit_window.geometry("400x300")
    
    # Mevcut bilgileri göster
    ctk.CTkLabel(edit_window, text="Ürün Adı:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ctk.CTkLabel(edit_window, text=item['values'][0]).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    ctk.CTkLabel(edit_window, text="Miktar:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    quantity_entry = ctk.CTkEntry(edit_window)
    quantity_entry.insert(0, item['values'][1])
    quantity_entry.grid(row=1, column=1, padx=5, pady=5)
    
    ctk.CTkLabel(edit_window, text="İade Tarihi:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    date_entry = ctk.CTkEntry(edit_window)
    date_entry.insert(0, item['values'][5])
    date_entry.grid(row=2, column=1, padx=5, pady=5)
    
    def save_changes():
        new_quantity = quantity_entry.get()
        new_date = date_entry.get()
        
        if not new_quantity.isdigit():
            messagebox.showerror("Hata", "Geçerli bir miktar girin")
            return
        
        try:
            datetime.strptime(new_date, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Hata", "Tarih formatı dd/mm/yyyy olmalıdır")
            return
        
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE loans 
            SET loan_quantity = ?, return_date = ? 
            WHERE product_name = ? AND borrower_name = ? AND borrower_surname = ?
        """, (new_quantity, new_date, item['values'][0], item['values'][2], item['values'][3]))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Başarılı", "Kayıt güncellendi")
        edit_window.destroy()
        load_loans()
    
    ctk.CTkButton(edit_window, text="Kaydet", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

# Ana uygulama
app = ctk.CTk()
app.geometry("1200x800")  # Boyut ayarlandı
app.title("Envanter Yönetimi")

create_database()
ensure_location_column()

# Frame ile sol tarafı düzenle
left_frame = ctk.CTkFrame(app, width=300)
left_frame.pack(side="left", padx=10, pady=10, fill="y")



loan_buttons_frame = ctk.CTkFrame(left_frame)
# Başlangıçta gizli
loan_buttons_frame.pack_forget()

# Ödünç yönetim butonları
ctk.CTkButton(loan_buttons_frame, text="İade Al", command=return_product).pack(fill="x", pady=2)
ctk.CTkButton(loan_buttons_frame, text="Düzenle", command=edit_loan).pack(fill="x", pady=2)
ctk.CTkButton(loan_buttons_frame, text="Vadesi Geçmişler", command=filter_overdue).pack(fill="x", pady=2)
ctk.CTkButton(loan_buttons_frame, text="Bugün İade Edilecekler", command=filter_today).pack(fill="x", pady=2)
ctk.CTkButton(loan_buttons_frame, text="Tümünü Göster", command=show_all_loans).pack(fill="x", pady=2)

# Giriş alanları
entry_id = ctk.CTkEntry(left_frame, placeholder_text="Ürün ID")
entry_id.pack(pady=5)

entry_name = ctk.CTkEntry(left_frame, placeholder_text="Ürün Adı")
entry_name.pack(pady=5)

entry_quantity = ctk.CTkEntry(left_frame, placeholder_text="Miktar")
entry_quantity.pack(pady=5)

# Lokasyon seçeneklerini kolayca güncelleyebilmek için bir liste olarak tanımlayalım
LOCATION_OPTIONS = ["Dolap 1", "Dolap 2", "Araç", "Şifonyer", "Ofis Mesken", "Diğer"]

dropdown_location = ctk.CTkOptionMenu(left_frame, values=LOCATION_OPTIONS)
dropdown_location.set("Lokasyon")
dropdown_location.pack(pady=5)

# Butonlar
ctk.CTkButton(left_frame, text="Ürün Ekle", command=add_product).pack(pady=5)
ctk.CTkButton(left_frame, text="Stok Artır", command=lambda: update_stock(increase=True)).pack(pady=5)
ctk.CTkButton(left_frame, text="Stok Azalt", command=lambda: update_stock(increase=False)).pack(pady=5)
ctk.CTkButton(left_frame, text="Stok Güncelle", command=lambda: update_stock(increase=None)).pack(pady=5)
ctk.CTkButton(left_frame, text="Tüm Ürünleri Listele", command=list_products).pack(pady=5)
ctk.CTkButton(left_frame, text="Listeyi Boşalt", command=list_clear).pack(pady=5)
ctk.CTkButton(left_frame, text="Ürün Sil", command=delete_product).pack(pady=5)
ctk.CTkButton(left_frame, text="Ürün Ara", command=search_product).pack(pady=5)
ctk.CTkButton(left_frame, text="Ödünç Ver", command=loan_product).pack(pady=5)
# Ödünç butonları için açılır panel
toggle_btn = ctk.CTkButton(left_frame, text="Ödünç Araçları ▼", command=toggle_loan_buttons)
toggle_btn.pack(pady=5)
# Ana içerik alanı
main_frame = ctk.CTkFrame(app)
main_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

# Ürün listesi
tree_frame = ctk.CTkFrame(main_frame)
tree_frame.pack(fill="both", expand=True)

ctk.CTkLabel(tree_frame, text="Envanter Listesi").pack()

columns = ("ID", "Ürün Adı", "Miktar", "Lokasyon")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
tree.heading("ID", text="ID")
tree.heading("Ürün Adı", text="Ürün Adı")
tree.heading("Miktar", text="Miktar")
tree.heading("Lokasyon", text="Lokasyon")
tree.column("ID", width=50, anchor="center")
tree.column("Ürün Adı", width=250, anchor="center")
tree.column("Miktar", width=100, anchor="center")
tree.column("Lokasyon", width=150, anchor="center")
tree.pack(fill="both", expand=True)

# Ödünç verilen ürünlerin listesi
loan_frame = ctk.CTkFrame(main_frame)
loan_frame.pack(fill="both", expand=True)

ctk.CTkLabel(loan_frame, text="Ödünç Verilen Ürünler").pack()

loan_columns = ("Ürün Adı", "Verilen Miktar", "İsim", "Soyisim", "Telefon", "İade Tarihi")
loan_list = ttk.Treeview(loan_frame, columns=loan_columns, show="headings", height=5)
loan_list.heading("Ürün Adı", text="Ürün Adı")
loan_list.heading("Verilen Miktar", text="Verilen Miktar")
loan_list.heading("İsim", text="İsim")
loan_list.heading("Soyisim", text="Soyisim")
loan_list.heading("Telefon", text="Telefon")
loan_list.heading("İade Tarihi", text="İade Tarihi")
loan_list.pack(fill="both", expand=True)

# Başlangıçta listeleri yükle
list_products()
load_loans()

app.mainloop()

