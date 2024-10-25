import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class CreditSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Créditos")
        
        # Facebook colors
        self.fb_blue = "#1877F2"
        self.fb_grey = "#F0F2F5"
        self.fb_dark = "#1C1E21"
        
        # Configure root
        self.root.configure(bg=self.fb_grey)
        
        # Database initialization
        self.init_database()
        
        # Create main frames
        self.create_frames()
        self.create_customer_form()
        self.create_payment_form()
        self.create_customer_list()
        
    def init_database(self):
        self.conn = sqlite3.connect('creditos.db')
        self.c = self.conn.cursor()
        
        # Create tables
        self.c.execute('''CREATE TABLE IF NOT EXISTS customers
                         (id INTEGER PRIMARY KEY,
                          nombre TEXT,
                          telefono TEXT,
                          credito_total REAL,
                          credito_restante REAL)''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS payments
                         (id INTEGER PRIMARY KEY,
                          customer_id INTEGER,
                          monto REAL,
                          fecha TEXT,
                          FOREIGN KEY (customer_id) REFERENCES customers(id))''')
        self.conn.commit()
        
    def create_frames(self):
        # Customer Form Frame
        self.customer_frame = tk.LabelFrame(self.root, text="Nuevo Cliente", bg=self.fb_grey)
        self.customer_frame.pack(padx=10, pady=5, fill="x")
        
        # Payment Frame
        self.payment_frame = tk.LabelFrame(self.root, text="Registrar Abono", bg=self.fb_grey)
        self.payment_frame.pack(padx=10, pady=5, fill="x")
        
        # List Frame
        self.list_frame = tk.LabelFrame(self.root, text="Clientes", bg=self.fb_grey)
        self.list_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
    def create_customer_form(self):
        # Customer Form
        labels = ['Nombre:', 'Teléfono:', 'Crédito Total:']
        self.customer_entries = {}
        
        for i, label in enumerate(labels):
            tk.Label(self.customer_frame, text=label, bg=self.fb_grey).grid(row=i, column=0, padx=5, pady=2)
            entry = tk.Entry(self.customer_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.customer_entries[label] = entry
            
        tk.Button(self.customer_frame, text="Guardar Cliente", 
                 command=self.save_customer,
                 bg=self.fb_blue, fg="white").grid(row=len(labels), column=0, columnspan=2, pady=5)
        
    def create_payment_form(self):
        # Payment Form
        tk.Label(self.payment_frame, text="Cliente:", bg=self.fb_grey).grid(row=0, column=0, padx=5, pady=2)
        self.customer_var = tk.StringVar()
        self.customer_select = ttk.Combobox(self.payment_frame, textvariable=self.customer_var)
        self.customer_select.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(self.payment_frame, text="Monto:", bg=self.fb_grey).grid(row=1, column=0, padx=5, pady=2)
        self.payment_amount = tk.Entry(self.payment_frame)
        self.payment_amount.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Button(self.payment_frame, text="Registrar Abono",
                 command=self.register_payment,
                 bg=self.fb_blue, fg="white").grid(row=2, column=0, columnspan=2, pady=5)
        
        self.update_customer_list()
        
    def create_customer_list(self):
        # Treeview for customer list
        columns = ('ID', 'Nombre', 'Teléfono', 'Crédito Total', 'Crédito Restante')
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.pack(padx=5, pady=5, fill="both", expand=True)
        self.update_customer_table()
        
    def save_customer(self):
        try:
            nombre = self.customer_entries['Nombre:'].get()
            telefono = self.customer_entries['Teléfono:'].get()
            credito = float(self.customer_entries['Crédito Total:'].get())
            
            if not nombre or not telefono or credito <= 0:
                messagebox.showerror("Error", "Por favor complete todos los campos correctamente")
                return
                
            self.c.execute('''INSERT INTO customers (nombre, telefono, credito_total, credito_restante)
                             VALUES (?, ?, ?, ?)''', (nombre, telefono, credito, credito))
            self.conn.commit()
            
            self.update_customer_table()
            self.update_customer_list()
            
            # Clear entries
            for entry in self.customer_entries.values():
                entry.delete(0, tk.END)
                
            messagebox.showinfo("Éxito", "Cliente guardado correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "El crédito debe ser un número válido")
            
    def register_payment(self):
        try:
            selected_customer = self.customer_var.get()
            if not selected_customer:
                messagebox.showerror("Error", "Por favor seleccione un cliente")
                return
                
            customer_id = int(selected_customer.split('-')[0])
            amount = float(self.payment_amount.get())
            
            if amount <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a cero")
                return
                
            # Get current credit
            self.c.execute("SELECT credito_restante FROM customers WHERE id=?", (customer_id,))
            current_credit = self.c.fetchone()[0]
            
            if amount > current_credit:
                messagebox.showerror("Error", "El monto es mayor al crédito restante")
                return
                
            # Register payment
            new_credit = current_credit - amount
            self.c.execute("UPDATE customers SET credito_restante=? WHERE id=?", (new_credit, customer_id))
            self.c.execute("INSERT INTO payments (customer_id, monto, fecha) VALUES (?, ?, ?)",
                         (customer_id, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.conn.commit()
            
            self.update_customer_table()
            self.payment_amount.delete(0, tk.END)
            
            messagebox.showinfo("Éxito", "Abono registrado correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
            
    def update_customer_table(self):
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get and insert customers
        self.c.execute("SELECT * FROM customers")
        for customer in self.c.fetchall():
            self.tree.insert('', 'end', values=customer)
            
    def update_customer_list(self):
        self.c.execute("SELECT id, nombre FROM customers")
        customers = self.c.fetchall()
        self.customer_select['values'] = [f"{id}-{nombre}" for id, nombre in customers]

if __name__ == "__main__":
    root = tk.Tk()
    app = CreditSystem(root)
    root.mainloop()