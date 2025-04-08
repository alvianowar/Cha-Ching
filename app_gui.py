
import tkinter as tk
from tkinter import ttk, messagebox
from auth import Authentication
from expenses import ExpenseTracker
from file_manager import load_data, save_data
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cha-Ching $$")
        self.geometry("700x500")
        self.center_window()

        self.configure(bg="#2e2e2e")
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background="#2e2e2e")
        style.configure("TLabel", background="#2e2e2e", foreground="#eeeeee", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 11), padding=6)
        style.configure("Accent.TButton", background="#21c064", foreground="white")
        style.map("Accent.TButton",
                  background=[("active", "#1ba558"), ("pressed", "#188e4d")])

        self.auth = Authentication()
        self.current_tracker = None

        self.frames = {}
        for F in (HomePage, LoginPage, RegisterPage, AdminDashboard, UserDashboard):
            frame = F(self, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def center_window(self):
        self.update_idletasks()
        w, h = 700, 500
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def show_frame(self, frame):
        self.frames[frame].tkraise()

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Cha-Ching $$", font=("Segoe UI", 24)).pack(pady=40)
        ttk.Button(self, text="Login", style="Accent.TButton", command=lambda: controller.show_frame(LoginPage)).pack(pady=10)
        ttk.Button(self, text="Register", command=lambda: controller.show_frame(RegisterPage)).pack(pady=5)

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Login", font=("Segoe UI", 20)).pack(pady=20)
        self.username = ttk.Entry(self)
        self.username.pack(pady=5)
        self.username.insert(0, "Username")

        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5)
        self.password.insert(0, "Password")

        ttk.Button(self, text="Login", style="Accent.TButton", command=self.login).pack(pady=15)

    def login(self):
        user = self.username.get()
        pwd = self.password.get()
        if self.controller.auth.login(user, pwd):
            u = self.controller.auth.get_current_user()
            self.controller.current_tracker = ExpenseTracker(u)
            if u.role == "admin":
                self.controller.show_frame(AdminDashboard)
            else:
                self.controller.show_frame(UserDashboard)
        else:
            messagebox.showerror("Error", "Invalid login")

class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Register", font=("Segoe UI", 20)).pack(pady=20)
        self.username = ttk.Entry(self)
        self.username.pack(pady=5)
        self.username.insert(0, "Username")

        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5)
        self.password.insert(0, "Password")

        ttk.Button(self, text="Register", style="Accent.TButton", command=self.register).pack(pady=15)

    def register(self):
        user = self.username.get()
        pwd = self.password.get()
        if self.controller.auth.register(user, pwd):
            messagebox.showinfo("Success", "User registered")
            self.controller.show_frame(LoginPage)
        else:
            messagebox.showerror("Error", "Username already exists")

class AdminDashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Admin Dashboard", font=("Segoe UI", 18)).pack(pady=10)

        self.cat_name = ttk.Entry(self)
        self.cat_name.pack(pady=5)
        self.cat_name.insert(0, "New Category Name")

        ttk.Button(self, text="Create Category", command=self.create_category).pack(pady=5)
        ttk.Button(self, text="Delete Category", command=self.delete_category).pack(pady=5)

        self.cat_list = ttk.Combobox(self)
        self.cat_list.pack(pady=10)

        self.refresh_categories()
        ttk.Button(self, text="Logout", command=self.logout).pack(pady=20)

    def refresh_categories(self):
        data = load_data()
        cats = data.get("categories", {})
        items = [f"{k}: {v['name']}" for k, v in cats.items()]
        self.cat_list["values"] = items

    def create_category(self):
        name = self.cat_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Category name cannot be empty.")
            return
        data = load_data()
        new_id = max(map(int, data.get("categories", {}).keys()), default=0) + 1
        data["categories"][new_id] = {"name": name, "user_id": 1}
        save_data(data)
        messagebox.showinfo("Success", "Category created.")
        self.refresh_categories()

    def delete_category(self):
        selected = self.cat_list.get()
        if ":" not in selected:
            return
        cat_id = int(selected.split(":")[0])
        data = load_data()
        if cat_id in data["categories"]:
            del data["categories"][cat_id]
            save_data(data)
            messagebox.showinfo("Deleted", "Category deleted.")
            self.refresh_categories()

    def logout(self):
        self.controller.auth.logout()
        self.controller.show_frame(HomePage)

class UserDashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="User Dashboard", font=("Segoe UI", 18)).pack(pady=10)

        ttk.Button(self, text="Add Expense", command=self.add_expense).pack(pady=5)
        ttk.Button(self, text="View Expenses", command=self.view_expenses).pack(pady=5)
        ttk.Button(self, text="View Summary", command=self.view_summary).pack(pady=5)
        ttk.Button(self, text="Set Budget", command=self.set_budget).pack(pady=5)
        ttk.Button(self, text="Logout", command=self.logout).pack(pady=20)

    def view_summary(self):
        user = self.controller.auth.get_current_user()
        data = load_data()
        expenses = data.get("expenses", {}).get(str(user.user_id), [])
        budget_data = data.get("budgets", {}).get(str(user.user_id), {})

        win = tk.Toplevel(self)
        win.title("Summary")
        win.geometry("600x550")
        win.configure(bg="#2e2e2e")

        ttk.Label(win, text="Monthly Summary", font=("Segoe UI", 16)).pack(pady=10)

        # Month Selector
        month_frame = ttk.Frame(win)
        month_frame.pack(pady=5)
        ttk.Label(month_frame, text="Select Month (YYYY-MM):").pack(side="left", padx=5)

        month_var = tk.StringVar()
        default_month = datetime.datetime.now().strftime("%Y-%m")
        month_entry = ttk.Entry(month_frame, textvariable=month_var, width=10)
        month_var.set(default_month)
        month_entry.pack(side="left", padx=5)

        def update_summary():
            for widget in result_frame.winfo_children():
                widget.destroy()

            current_month = month_var.get().strip()
            if not current_month or len(current_month) != 7:
                messagebox.showerror("Error", "Please enter a valid month in YYYY-MM format.")
                return

            month_expenses = [e for e in expenses if e["date"].startswith(current_month)]
            total_spent = sum(e["amount"] for e in month_expenses)
            budget = budget_data.get(current_month, None)
            remaining = (budget - total_spent) if budget else None

            ttk.Label(result_frame, text=f"Month: {current_month}").pack()
            ttk.Label(result_frame, text=f"Total Expenses: ${total_spent:.2f}").pack()
            if budget is not None:
                ttk.Label(result_frame, text=f"Budget: ${budget:.2f}").pack()
                ttk.Label(result_frame, text=f"Remaining: ${remaining:.2f}").pack()
                if remaining < 0:
                    ttk.Label(result_frame, text="⚠️ Budget exceeded!", foreground="red").pack()
            else:
                ttk.Label(result_frame, text="No budget set for this month.", foreground="orange").pack()

            # Plot graph
            fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
            labels = ["Expenses", "Budget"]
            values = [total_spent, budget if budget is not None else 0]
            colors = ["#f54242", "#42f55a"]

            ax.bar(labels, values, color=colors)
            ax.set_title("Expenses vs Budget")
            ax.set_ylabel("Amount ($)")
            ax.grid(True, axis='y')

            canvas = FigureCanvasTkAgg(fig, master=result_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

        ttk.Button(month_frame, text="Show Summary", style="Accent.TButton", command=update_summary).pack(side="left",
                                                                                                          padx=10)

        result_frame = ttk.Frame(win)
        result_frame.pack(pady=10)

        update_summary()

    def view_expenses(self):
        user = self.controller.auth.get_current_user()
        data = load_data()
        full_expenses = data.get("expenses", {}).get(str(user.user_id), [])

        win = tk.Toplevel(self)
        win.title("Your Expenses")
        win.geometry("750x550")
        win.configure(bg="#2e2e2e")

        ttk.Label(win, text="Your Expenses", font=("Segoe UI", 14)).pack(pady=10)

        # Month filter
        filter_frame = ttk.Frame(win)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Month (YYYY-MM):").pack(side="left", padx=5)
        month_var = tk.StringVar()
        default_month = datetime.datetime.now().strftime("%Y-%m")
        month_entry = ttk.Entry(filter_frame, textvariable=month_var, width=10)
        month_var.set(default_month)
        month_entry.pack(side="left", padx=5)

        tree = ttk.Treeview(win, columns=("Date", "Category", "Amount", "Description"), show="headings", height=15)
        for col in ("Date", "Category", "Amount", "Description"):
            tree.heading(col, text=col)
            tree.column(col, width=140 if col != "Description" else 220)

        tree.pack(pady=10, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        id_map = {}

        def populate_table(month):
            tree.delete(*tree.get_children())
            id_map.clear()
            for exp in full_expenses:
                if exp["date"].startswith(month):
                    tree_id = tree.insert("", "end", values=(
                    exp["date"], exp["category"], f"{exp['amount']:.2f}", exp["description"]))
                    id_map[tree_id] = exp["expense_id"]

        def filter_by_month():
            month = month_var.get().strip()
            if not month or len(month) != 7 or "-" not in month:
                messagebox.showerror("Invalid Input", "Enter a valid month in YYYY-MM format.")
                return
            populate_table(month)

        filter_button = ttk.Button(filter_frame, text="Filter", command=filter_by_month)
        filter_button.pack(side="left", padx=10)

        def delete_expense():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select Expense", "Please select an expense to delete.")
                return
            tree_id = selected[0]
            expense_id = id_map[tree_id]

            confirm = messagebox.askyesno("Confirm", "Delete this expense?")
            if not confirm:
                return

            data["expenses"][str(user.user_id)] = [
                exp for exp in data["expenses"][str(user.user_id)]
                if exp["expense_id"] != expense_id
            ]
            save_data(data)
            tree.delete(tree_id)
            messagebox.showinfo("Deleted", "Expense deleted successfully.")

        def edit_expense():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select Expense", "Please select an expense to edit.")
                return
            tree_id = selected[0]
            expense_id = id_map[tree_id]

            for exp in data["expenses"][str(user.user_id)]:
                if exp["expense_id"] == expense_id:
                    open_edit_window(exp, tree_id)
                    break

        def open_edit_window(expense, tree_id):
            ewin = tk.Toplevel(win)
            ewin.title("Edit Expense")
            ewin.geometry("400x400")
            ewin.configure(bg="#2e2e2e")

            ttk.Label(ewin, text="Edit Expense", font=("Segoe UI", 14)).pack(pady=10)

            categories = data.get("categories", {})
            category_var = tk.StringVar()
            cat_dropdown = ttk.Combobox(ewin, textvariable=category_var)
            cat_dropdown["values"] = [f"{cid}: {cat['name']}" for cid, cat in categories.items()]
            current_cat = next(
                (f"{cid}: {cat['name']}" for cid, cat in categories.items() if cat["name"] == expense["category"]), "")
            cat_dropdown.set(current_cat)
            cat_dropdown.pack(pady=5)

            ttk.Label(ewin, text="Description").pack()
            desc_entry = ttk.Entry(ewin)
            desc_entry.insert(0, expense["description"])
            desc_entry.pack(pady=5)

            ttk.Label(ewin, text="Amount").pack()
            amt_entry = ttk.Entry(ewin)
            amt_entry.insert(0, str(expense["amount"]))
            amt_entry.pack(pady=5)

            ttk.Label(ewin, text="Date").pack()
            date_picker = DateEntry(ewin, width=16, background="darkgreen", foreground="white", borderwidth=2,
                                    date_pattern='yyyy-mm-dd')
            date_picker.set_date(expense["date"])
            date_picker.pack(pady=5)

            def save_changes():
                try:
                    selected = category_var.get()
                    if ":" not in selected:
                        raise ValueError("Please select a valid category.")
                    cat_id = int(selected.split(":")[0])
                    cat_name = categories[str(cat_id)]["name"]

                    new_desc = desc_entry.get().strip()
                    new_amt = float(amt_entry.get().strip())
                    new_date = date_picker.get_date().strftime("%Y-%m-%d")

                    expense["category"] = cat_name
                    expense["description"] = new_desc
                    expense["amount"] = new_amt
                    expense["date"] = new_date
                    save_data(data)

                    tree.item(tree_id, values=(new_date, cat_name, f"{new_amt:.2f}", new_desc))
                    messagebox.showinfo("Success", "Expense updated.")
                    ewin.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not update expense: {e}")

            ttk.Button(ewin, text="Save Changes", style="Accent.TButton", command=save_changes).pack(pady=15)

        ttk.Button(win, text="Edit Selected", command=edit_expense).pack(side="left", padx=30, pady=10)
        ttk.Button(win, text="Delete Selected", command=delete_expense).pack(side="right", padx=30, pady=10)

        populate_table(default_month)


    def logout(self):
        self.controller.auth.logout()
        self.controller.show_frame(HomePage)

    def set_budget(self):
        user = self.controller.auth.get_current_user()
        win = tk.Toplevel(self)
        win.title("Set Budget")
        win.geometry("350x250")
        win.configure(bg="#2e2e2e")

        ttk.Label(win, text="Set Monthly Budget", font=("Segoe UI", 14)).pack(pady=10)

        ttk.Label(win, text="Month (YYYY-MM):").pack(pady=5)
        month_entry = ttk.Entry(win)
        month_entry.insert(0, datetime.datetime.now().strftime("%Y-%m"))
        month_entry.pack()

        ttk.Label(win, text="Budget Amount:").pack(pady=5)
        amount_entry = ttk.Entry(win)
        amount_entry.pack()

        def submit_budget():
            try:
                month = month_entry.get().strip()
                amount = float(amount_entry.get().strip())
                if not month or amount <= 0:
                    raise ValueError("Invalid inputs.")

                data = load_data()
                if str(user.user_id) not in data["budgets"]:
                    data["budgets"][str(user.user_id)] = {}
                data["budgets"][str(user.user_id)][month] = amount
                save_data(data)

                messagebox.showinfo("Success", f"Budget set for {month}")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not set budget: {e}")

        ttk.Button(win, text="Save", style="Accent.TButton", command=submit_budget).pack(pady=15)

    def add_expense(self):
        user = self.controller.auth.get_current_user()
        data = load_data()
        categories = data.get("categories", {})
        cat_options = [(cid, cat["name"]) for cid, cat in categories.items()]

        win = tk.Toplevel(self)
        win.title("Add Expense")
        win.geometry("400x400")
        win.configure(bg="#2e2e2e")

        ttk.Label(win, text="Add Expense", font=("Segoe UI", 16)).pack(pady=10)

        # Category Dropdown
        ttk.Label(win, text="Category").pack()
        category_var = tk.StringVar()
        cat_dropdown = ttk.Combobox(win, textvariable=category_var)
        cat_dropdown["values"] = [f"{cid}: {name}" for cid, name in cat_options]
        cat_dropdown.pack(pady=5)

        # Description
        ttk.Label(win, text="Description").pack()
        desc_entry = ttk.Entry(win)
        desc_entry.pack(pady=5)

        # Amount
        ttk.Label(win, text="Amount").pack()
        amt_entry = ttk.Entry(win)
        amt_entry.pack(pady=5)

        # Date Picker
        ttk.Label(win, text="Date").pack()
        date_picker = DateEntry(win, width=16, background="darkgreen", foreground="white", borderwidth=2,
                                date_pattern='yyyy-mm-dd')
        date_picker.pack(pady=5)

        def submit_expense():
            try:
                selected = category_var.get()
                if ":" not in selected:
                    raise ValueError("Please select a valid category.")
                cat_id = int(selected.split(":")[0])
                cat_name = categories[str(cat_id)]["name"]

                desc = desc_entry.get().strip()
                if not desc:
                    raise ValueError("Description is required.")

                amount = float(amt_entry.get())
                if amount <= 0:
                    raise ValueError("Amount must be a positive number.")

                date = date_picker.get_date().strftime("%Y-%m-%d")

                expense = {
                    "expense_id": next(ExpenseTracker.expense_id_counter),
                    "amount": amount,
                    "category": cat_name,
                    "description": desc,
                    "user_id": user.user_id,
                    "date": date
                }

                if str(user.user_id) not in data["expenses"]:
                    data["expenses"][str(user.user_id)] = []
                data["expenses"][str(user.user_id)].append(expense)
                save_data(data)

                messagebox.showinfo("Success", "Expense added successfully.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add expense: {e}")

        ttk.Button(win, text="Submit", style="Accent.TButton", command=submit_expense).pack(pady=10)

        def submit_expense():
            try:
                selected = category_var.get()
                if ":" not in selected:
                    raise ValueError("Invalid category selection")
                cat_id = int(selected.split(":")[0])
                cat_name = categories[str(cat_id)]["name"]

                amount = float(amt_entry.get())
                desc = desc_entry.get()
                date = date_entry.get()

                expense = {
                    "expense_id": next(ExpenseTracker.expense_id_counter),
                    "amount": amount,
                    "category": cat_name,
                    "description": desc,
                    "user_id": user.user_id,
                    "date": date
                }

                if str(user.user_id) not in data["expenses"]:
                    data["expenses"][str(user.user_id)] = []
                data["expenses"][str(user.user_id)].append(expense)
                save_data(data)

                messagebox.showinfo("Success", "Expense added successfully.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add expense: {e}")

        ttk.Button(win, text="Submit", style="Accent.TButton", command=submit_expense).pack(pady=10)




if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()
