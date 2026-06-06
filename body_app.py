"""
Body App - A comprehensive body and fitness tracking application.
Track workouts, body measurements, BMI, calories, and muscle groups.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
import math

# ─── Data persistence ────────────────────────────────────────────────
DATA_FILE = "body_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "workouts": [],
        "measurements": [],
        "daily_water": {},
        "daily_calories": {},
        "goals": {},
    }


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ─── Main Application ────────────────────────────────────────────────
class BodyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💪 Body App – Fitness Tracker")
        self.geometry("950x680")
        self.configure(bg="#1e1e2e")
        self.resizable(True, True)
        self.data = load_data()

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._configure_styles()

        # Sidebar
        self.sidebar = tk.Frame(self, bg="#181825", width=220)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(
            self.sidebar,
            text="💪 BODY APP",
            font=("Segoe UI", 16, "bold"),
            bg="#181825",
            fg="#cdd6f4",
            pady=20,
        ).pack()

        self.content = tk.Frame(self, bg="#1e1e2e")
        self.content.pack(side="left", fill="both", expand=True)

        self.buttons = {}
        pages = [
            ("Dashboard", self.show_dashboard),
            ("Workout Log", self.show_workouts),
            ("Body Measurements", self.show_measurements),
            ("BMI Calculator", self.show_bmi),
            ("Calorie Tracker", self.show_calories),
            ("Water Tracker", self.show_water),
            ("Muscle Groups", self.show_muscles),
            ("Goals", self.show_goals),
            ("Exercise Library", self.show_exercises),
        ]

        for name, cmd in pages:
            btn = tk.Button(
                self.sidebar,
                text=name,
                font=("Segoe UI", 12),
                fg="#cdd6f4",
                bg="#313244",
                activebackground="#45475a",
                activeforeground="#cdd6f4",
                bd=0,
                padx=15,
                pady=10,
                anchor="w",
                command=cmd,
            )
            btn.pack(fill="x", padx=8, pady=3)
            self.buttons[name] = btn

        self.show_dashboard()

    # ── Styles ───────────────────────────────────────────────────────
    def _configure_styles(self):
        self.style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#cba6f7")
        self.style.configure("Card.TFrame", background="#313244", relief="flat")
        self.style.configure("TButton", font=("Segoe UI", 11), padding=6)
        self.style.configure("Accent.TButton", background="#89b4fa", foreground="#1e1e2e")
        self.style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _highlight_button(self, name):
        for btn_name, btn in self.buttons.items():
            btn.configure(bg="#313244")
        if name in self.buttons:
            self.buttons[name].configure(bg="#cba6f7")

    def _header_label(self, parent, text):
        """Helper to create a header label without using ttk style on tk.Label."""
        return tk.Label(parent, text=text, font=("Segoe UI", 18, "bold"), bg="#1e1e2e", fg="#cba6f7")

    # ── Dashboard ────────────────────────────────────────────────────
    def show_dashboard(self):
        self._clear_content()
        self._highlight_button("Dashboard")

        self._header_label(self.content, "📊 Dashboard").pack(pady=20, anchor="w", padx=20)

        cards_frame = tk.Frame(self.content, bg="#1e1e2e")
        cards_frame.pack(fill="x", padx=20, pady=10)

        total_workouts = len(self.data["workouts"])
        total_measurements = len(self.data["measurements"])
        total_water = sum(self.data["daily_water"].values()) if self.data["daily_water"] else 0
        today = datetime.now().strftime("%Y-%m-%d")
        today_water = self.data["daily_water"].get(today, 0)
        today_cal = self.data["daily_calories"].get(today, 0)

        stats = [
            ("🏋️ Total Workouts", str(total_workouts)),
            ("📏 Measurements", str(total_measurements)),
            ("💧 Today Water (ml)", str(today_water)),
            ("🔥 Today Calories", str(today_cal)),
            ("💧 Total Water (ml)", str(total_water)),
        ]

        for i, (label, value) in enumerate(stats):
            card = tk.Frame(cards_frame, bg="#313244", padx=20, pady=15, bd=0, highlightthickness=1, highlightbackground="#45475a")
            card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=label, font=("Segoe UI", 10), bg="#313244", fg="#a6adc8").pack()
            tk.Label(card, text=value, font=("Segoe UI", 24, "bold"), bg="#313244", fg="#f5c2e7").pack(pady=5)

        # Recent activity
        tk.Label(self.content, text="🕐 Recent Activity", font=("Segoe UI", 14, "bold"), bg="#1e1e2e", fg="#cba6f7").pack(pady=(25, 10), anchor="w", padx=20)

        recent_frame = tk.Frame(self.content, bg="#313244", bd=0, highlightthickness=1, highlightbackground="#45475a")
        recent_frame.pack(fill="both", expand=True, padx=20, pady=10)

        activity = []
        for w in self.data["workouts"][-5:]:
            activity.append(f"🏋️  {w['date']} – {w['exercise']} ({w['sets']}×{w['reps']} @ {w['weight']}kg)")
        for m in self.data["measurements"][-3:]:
            activity.append(f"📏  {m['date']} – Chest: {m['chest']}cm, Waist: {m['waist']}cm, Weight: {m['weight']}kg")

        if not activity:
            activity.append("No recent activity. Start logging!")

        for i, text in enumerate(activity[-8:]):
            tk.Label(recent_frame, text=text, font=("Segoe UI", 11), bg="#313244", fg="#cdd6f4", anchor="w").pack(fill="x", padx=15, pady=4)

    # ── Workout Log ──────────────────────────────────────────────────
    def show_workouts(self):
        self._clear_content()
        self._highlight_button("Workout Log")

        self._header_label(self.content, "🏋️ Workout Log").pack(pady=15, anchor="w", padx=20)

        form = tk.Frame(self.content, bg="#313244", padx=15, pady=15, bd=0, highlightthickness=1, highlightbackground="#45475a")
        form.pack(fill="x", padx=20, pady=10)

        fields = {}
        labels = ["Exercise", "Sets", "Reps", "Weight (kg)", "Duration (min)", "Notes"]
        defaults = ["", "3", "10", "", "", ""]
        for i, (lbl, default) in enumerate(zip(labels, defaults)):
            tk.Label(form, text=lbl, bg="#313244", fg="#a6adc8", font=("Segoe UI", 10)).grid(row=i // 3, column=(i % 3) * 2, sticky="w", padx=5, pady=4)
            entry = tk.Entry(form, font=("Segoe UI", 10), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=18)
            entry.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=5, pady=4)
            entry.insert(0, default)
            fields[lbl] = entry

        def add_workout():
            exercise = fields["Exercise"].get().strip()
            if not exercise:
                messagebox.showwarning("Warning", "Exercise name is required.")
                return
            workout = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "exercise": exercise,
                "sets": fields["Sets"].get(),
                "reps": fields["Reps"].get(),
                "weight": fields["Weight (kg)"].get(),
                "duration": fields["Duration (min)"].get(),
                "notes": fields["Notes"].get(),
            }
            self.data["workouts"].append(workout)
            save_data(self.data)
            messagebox.showinfo("Success", f"Workout '{exercise}' logged!")
            for entry in fields.values():
                entry.delete(0, tk.END)
            show_table()

        tk.Button(form, text="➕ Add Workout", font=("Segoe UI", 11, "bold"), bg="#a6e3a1", fg="#1e1e2e", bd=0, padx=15, pady=5, command=add_workout).grid(row=3, column=0, columnspan=6, pady=10)

        # Table
        table_frame = tk.Frame(self.content, bg="#1e1e2e")
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols = ("Date", "Exercise", "Sets", "Reps", "Weight", "Duration", "Notes")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120)
        tree.pack(fill="both", expand=True)

        def show_table():
            for item in tree.get_children():
                tree.delete(item)
            for w in reversed(self.data["workouts"][-50:]):
                tree.insert("", "end", values=(w["date"], w["exercise"], w["sets"], w["reps"], w["weight"], w["duration"], w["notes"]))

        def delete_selected():
            sel = tree.selection()
            if not sel:
                return
            idx = len(self.data["workouts"]) - 1 - tree.index(sel[0])
            if 0 <= idx < len(self.data["workouts"]):
                self.data["workouts"].pop(idx)
                save_data(self.data)
                show_table()

        tk.Button(table_frame, text="🗑️ Delete Selected", font=("Segoe UI", 10), bg="#f38ba8", fg="#1e1e2e", bd=0, padx=10, pady=4, command=delete_selected).pack(pady=5)
        show_table()

    # ── Body Measurements ────────────────────────────────────────────
    def show_measurements(self):
        self._clear_content()
        self._highlight_button("Body Measurements")

        self._header_label(self.content, "📏 Body Measurements").pack(pady=15, anchor="w", padx=20)

        form = tk.Frame(self.content, bg="#313244", padx=15, pady=15, bd=0, highlightthickness=1, highlightbackground="#45475a")
        form.pack(fill="x", padx=20, pady=10)

        fields = {}
        labels = ["Weight (kg)", "Height (cm)", "Chest (cm)", "Waist (cm)", "Hips (cm)", "Bicep (cm)", "Thigh (cm)", "Body Fat %"]
        for i, lbl in enumerate(labels):
            tk.Label(form, text=lbl, bg="#313244", fg="#a6adc8", font=("Segoe UI", 10)).grid(row=i // 4, column=(i % 4) * 2, sticky="w", padx=5, pady=4)
            entry = tk.Entry(form, font=("Segoe UI", 10), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=14)
            entry.grid(row=i // 4, column=(i % 4) * 2 + 1, padx=5, pady=4)
            fields[lbl] = entry

        def add_measurement():
            weight = fields["Weight (kg)"].get().strip()
            if not weight:
                messagebox.showwarning("Warning", "Weight is required.")
                return
            m = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "weight": weight,
                "height": fields["Height (cm)"].get(),
                "chest": fields["Chest (cm)"].get(),
                "waist": fields["Waist (cm)"].get(),
                "hips": fields["Hips (cm)"].get(),
                "bicep": fields["Bicep (cm)"].get(),
                "thigh": fields["Thigh (cm)"].get(),
                "body_fat": fields["Body Fat %"].get(),
            }
            self.data["measurements"].append(m)
            save_data(self.data)
            messagebox.showinfo("Success", "Measurement recorded!")
            show_measurements_table()

        tk.Button(form, text="➕ Record Measurement", font=("Segoe UI", 11, "bold"), bg="#a6e3a1", fg="#1e1e2e", bd=0, padx=15, pady=5, command=add_measurement).grid(row=2, column=0, columnspan=8, pady=10)

        table_frame = tk.Frame(self.content, bg="#1e1e2e")
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols = ("Date", "Weight", "Height", "Chest", "Waist", "Hips", "Bicep", "Thigh", "Body Fat")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill="both", expand=True)

        def show_measurements_table():
            for item in tree.get_children():
                tree.delete(item)
            for m in reversed(self.data["measurements"][-30:]):
                tree.insert("", "end", values=(
                    m["date"], m["weight"], m.get("height", ""), m.get("chest", ""),
                    m.get("waist", ""), m.get("hips", ""), m.get("bicep", ""),
                    m.get("thigh", ""), m.get("body_fat", ""),
                ))

        show_measurements_table()

    # ── BMI Calculator ───────────────────────────────────────────────
    def show_bmi(self):
        self._clear_content()
        self._highlight_button("BMI Calculator")

        self._header_label(self.content, "⚖️ BMI Calculator").pack(pady=15, anchor="w", padx=20)

        card = tk.Frame(self.content, bg="#313244", padx=25, pady=25, bd=0, highlightthickness=1, highlightbackground="#45475a")
        card.pack(padx=40, pady=20, anchor="w")

        tk.Label(card, text="Weight (kg):", bg="#313244", fg="#a6adc8", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=8)
        weight_entry = tk.Entry(card, font=("Segoe UI", 12), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=20)
        weight_entry.grid(row=0, column=1, padx=10, pady=8)

        tk.Label(card, text="Height (cm):", bg="#313244", fg="#a6adc8", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", pady=8)
        height_entry = tk.Entry(card, font=("Segoe UI", 12), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=20)
        height_entry.grid(row=1, column=1, padx=10, pady=8)

        result_label = tk.Label(card, text="", bg="#313244", fg="#cdd6f4", font=("Segoe UI", 14, "bold"))
        result_label.grid(row=3, column=0, columnspan=2, pady=15)

        category_label = tk.Label(card, text="", bg="#313244", font=("Segoe UI", 12))
        category_label.grid(row=4, column=0, columnspan=2)

        def calculate_bmi():
            try:
                w = float(weight_entry.get())
                h = float(height_entry.get()) / 100
                bmi = w / (h * h)
                result_label.config(text=f"BMI: {bmi:.1f}")
                if bmi < 18.5:
                    category_label.config(text="Category: Underweight", fg="#89b4fa")
                elif bmi < 25:
                    category_label.config(text="Category: Normal weight", fg="#a6e3a1")
                elif bmi < 30:
                    category_label.config(text="Category: Overweight", fg="#f9e2af")
                else:
                    category_label.config(text="Category: Obese", fg="#f38ba8")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")

        tk.Button(card, text="Calculate BMI", font=("Segoe UI", 12, "bold"), bg="#89b4fa", fg="#1e1e2e", bd=0, padx=20, pady=6, command=calculate_bmi).grid(row=2, column=0, columnspan=2, pady=12)

    # ── Calorie Tracker ──────────────────────────────────────────────
    def show_calories(self):
        self._clear_content()
        self._highlight_button("Calorie Tracker")

        self._header_label(self.content, "🔥 Calorie Tracker").pack(pady=15, anchor="w", padx=20)

        form = tk.Frame(self.content, bg="#313244", padx=15, pady=15, bd=0, highlightthickness=1, highlightbackground="#45475a")
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Food Item:", bg="#313244", fg="#a6adc8").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        food_entry = tk.Entry(form, font=("Segoe UI", 11), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=25)
        food_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Calories:", bg="#313244", fg="#a6adc8").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        cal_entry = tk.Entry(form, font=("Segoe UI", 11), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=12)
        cal_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form, text="Meal:", bg="#313244", fg="#a6adc8").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        meal_var = tk.StringVar(value="Breakfast")
        meal_menu = ttk.Combobox(form, textvariable=meal_var, values=["Breakfast", "Lunch", "Dinner", "Snack"], width=12, state="readonly")
        meal_menu.grid(row=0, column=5, padx=5, pady=5)

        def add_calories():
            food = food_entry.get().strip()
            cal = cal_entry.get().strip()
            if not food or not cal:
                messagebox.showwarning("Warning", "Food and calories are required.")
                return
            today = datetime.now().strftime("%Y-%m-%d")
            self.data["daily_calories"][today] = self.data["daily_calories"].get(today, 0) + int(cal)
            save_data(self.data)
            messagebox.showinfo("Success", f"Added {cal} cal for '{food}'")
            food_entry.delete(0, tk.END)
            cal_entry.delete(0, tk.END)
            show_cal_summary()

        tk.Button(form, text="➕ Add", font=("Segoe UI", 11, "bold"), bg="#a6e3a1", fg="#1e1e2e", bd=0, padx=12, pady=4, command=add_calories).grid(row=0, column=6, padx=10)

        summary = tk.Frame(self.content, bg="#313244", padx=20, pady=20, bd=0, highlightthickness=1, highlightbackground="#45475a")
        summary.pack(fill="x", padx=20, pady=10)

        cal_display = tk.Label(summary, text="", font=("Segoe UI", 20, "bold"), bg="#313244", fg="#f9e2af")
        cal_display.pack()

        bar_frame = tk.Frame(summary, bg="#45475a", height=25, bd=0)
        bar_frame.pack(fill="x", pady=10)
        bar_fill = tk.Frame(bar_frame, bg="#a6e3a1", height=25)
        bar_fill.place(x=0, y=0, relheight=1.0)

        goal_label = tk.Label(summary, text="Daily Goal: 2000 cal", bg="#313244", fg="#a6adc8", font=("Segoe UI", 10))
        goal_label.pack()

        def show_cal_summary():
            today = datetime.now().strftime("%Y-%m-%d")
            today_cal = self.data["daily_calories"].get(today, 0)
            cal_display.config(text=f"Today: {today_cal} / 2000 calories")
            pct = min(today_cal / 2000, 1.0)
            bar_fill.place(x=0, y=0, relheight=1.0)
            bar_fill.configure(width=int(pct * 500))

        show_cal_summary()

        # Weekly history
        tk.Label(self.content, text="📅 Last 7 Days", font=("Segoe UI", 12, "bold"), bg="#1e1e2e", fg="#cba6f7").pack(pady=(20, 5), anchor="w", padx=20)

        for i in range(7):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            cal = self.data["daily_calories"].get(day, 0)
            row = tk.Frame(self.content, bg="#313244", padx=15, pady=6, bd=0, highlightthickness=1, highlightbackground="#45475a")
            row.pack(fill="x", padx=20, pady=2)
            tk.Label(row, text=day, bg="#313244", fg="#a6adc8", font=("Segoe UI", 10), width=15, anchor="w").pack(side="left")
            tk.Label(row, text=f"{cal} cal", bg="#313244", fg="#f9e2af", font=("Segoe UI", 11, "bold")).pack(side="right")

    # ── Water Tracker ────────────────────────────────────────────────
    def show_water(self):
        self._clear_content()
        self._highlight_button("Water Tracker")

        self._header_label(self.content, "💧 Water Tracker").pack(pady=15, anchor="w", padx=20)

        card = tk.Frame(self.content, bg="#313244", padx=30, pady=30, bd=0, highlightthickness=1, highlightbackground="#45475a")
        card.pack(padx=40, pady=20)

        today = datetime.now().strftime("%Y-%m-%d")
        today_water = self.data["daily_water"].get(today, 0)
        goal = 3000  # ml

        big_label = tk.Label(card, text=f"{today_water} ml", font=("Segoe UI", 36, "bold"), bg="#313244", fg="#89dceb")
        big_label.pack()

        tk.Label(card, text=f"Goal: {goal} ml", bg="#313244", fg="#a6adc8", font=("Segoe UI", 11)).pack()

        # Progress bar
        bar_bg = tk.Frame(card, bg="#45475a", height=30, width=400)
        bar_bg.pack(pady=15)
        bar_bg.pack_propagate(False)
        pct = min(today_water / goal, 1.0)
        bar_fg = tk.Frame(bar_bg, bg="#89dceb", height=30)
        bar_fg.place(x=0, y=0, relheight=1.0)
        bar_fg.configure(width=int(pct * 400))

        pct_label = tk.Label(card, text=f"{int(pct * 100)}% complete", bg="#313244", fg="#a6adc8", font=("Segoe UI", 10))
        pct_label.pack()

        add_frame = tk.Frame(card, bg="#313244")
        add_frame.pack(pady=15)

        amounts = [150, 250, 500, 750]

        def add_water(amount):
            self.data["daily_water"][today] = self.data["daily_water"].get(today, 0) + amount
            save_data(self.data)
            self.show_water()

        for amt in amounts:
            tk.Button(add_frame, text=f"+{amt} ml", font=("Segoe UI", 11), bg="#45475a", fg="#89dceb", bd=0, padx=15, pady=8, command=lambda a=amt: add_water(a)).pack(side="left", padx=6)

        tk.Button(add_frame, text="Custom", font=("Segoe UI", 11), bg="#45475a", fg="#f5c2e7", bd=0, padx=15, pady=8, command=lambda: self._custom_water_add(today)).pack(side="left", padx=6)

        # Weekly view
        tk.Label(self.content, text="📅 Weekly Water Intake", font=("Segoe UI", 12, "bold"), bg="#1e1e2e", fg="#cba6f7").pack(pady=(20, 5), anchor="w", padx=20)

        for i in range(7):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            water = self.data["daily_water"].get(day, 0)
            row = tk.Frame(self.content, bg="#313244", padx=15, pady=6, bd=0, highlightthickness=1, highlightbackground="#45475a")
            row.pack(fill="x", padx=20, pady=2)
            tk.Label(row, text=day, bg="#313244", fg="#a6adc8", font=("Segoe UI", 10), width=15, anchor="w").pack(side="left")
            tk.Label(row, text=f"{water} ml", bg="#313244", fg="#89dceb", font=("Segoe UI", 11, "bold")).pack(side="right")

    def _custom_water_add(self, today):
        popup = tk.Toplevel(self)
        popup.title("Custom Water")
        popup.geometry("300x150")
        popup.configure(bg="#1e1e2e")
        tk.Label(popup, text="Enter amount (ml):", bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 12)).pack(pady=10)
        entry = tk.Entry(popup, font=("Segoe UI", 12), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=15)
        entry.pack()

        def submit():
            try:
                amt = int(entry.get())
                self.data["daily_water"][today] = self.data["daily_water"].get(today, 0) + amt
                save_data(self.data)
                popup.destroy()
                self.show_water()
            except ValueError:
                messagebox.showerror("Error", "Enter a valid number.")

        tk.Button(popup, text="Add", font=("Segoe UI", 11, "bold"), bg="#a6e3a1", fg="#1e1e2e", bd=0, padx=15, pady=5, command=submit).pack(pady=15)

    # ── Muscle Groups ────────────────────────────────────────────────
    def show_muscles(self):
        self._clear_content()
        self._highlight_button("Muscle Groups")

        self._header_label(self.content, "💪 Muscle Groups").pack(pady=15, anchor="w", padx=20)

        muscles = {
            "Chest": {"exercises": ["Bench Press", "Incline Dumbbell Press", "Cable Flyes", "Push-ups"], "color": "#f38ba8"},
            "Back": {"exercises": ["Deadlift", "Pull-ups", "Barbell Row", "Lat Pulldown"], "color": "#89b4fa"},
            "Shoulders": {"exercises": ["Overhead Press", "Lateral Raises", "Front Raises", "Face Pulls"], "color": "#cba6f7"},
            "Biceps": {"exercises": ["Barbell Curl", "Hammer Curl", "Preacher Curl", "Concentration Curl"], "color": "#a6e3a1"},
            "Triceps": {"exercises": ["Tricep Pushdown", "Skull Crushers", "Dips", "Close-Grip Bench"], "color": "#f9e2af"},
            "Legs": {"exercises": ["Squats", "Leg Press", "Lunges", "Leg Curl", "Calf Raises"], "color": "#94e2d5"},
            "Core": {"exercises": ["Planks", "Crunches", "Leg Raises", "Russian Twists"], "color": "#fab387"},
            "Glutes": {"exercises": ["Hip Thrusts", "Glute Bridge", "Bulgarian Split Squat"], "color": "#f5c2e7"},
        }

        grid = tk.Frame(self.content, bg="#1e1e2e")
        grid.pack(fill="both", expand=True, padx=20, pady=10)

        for i, (muscle, info) in enumerate(muscles.items()):
            card = tk.Frame(grid, bg="#313244", padx=12, pady=12, bd=0, highlightthickness=2, highlightbackground=info["color"])
            card.grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="nsew")
            grid.columnconfigure(i % 4, weight=1)
            grid.rowconfigure(i // 4, weight=1)

            tk.Label(card, text=muscle, font=("Segoe UI", 13, "bold"), bg="#313244", fg=info["color"]).pack(anchor="w")

            for ex in info["exercises"]:
                tk.Label(card, text=f"• {ex}", font=("Segoe UI", 10), bg="#313244", fg="#a6adc8", anchor="w").pack(fill="x", pady=1)

            # Count workouts for this muscle group
            count = sum(1 for w in self.data["workouts"] if w["exercise"].lower() in [e.lower() for e in info["exercises"]])
            tk.Label(card, text=f"Logged: {count}x", font=("Segoe UI", 9), bg="#313244", fg="#6c7086").pack(anchor="e", pady=(5, 0))

    # ── Goals ────────────────────────────────────────────────────────
    def show_goals(self):
        self._clear_content()
        self._highlight_button("Goals")

        self._header_label(self.content, "🎯 Fitness Goals").pack(pady=15, anchor="w", padx=20)

        form = tk.Frame(self.content, bg="#313244", padx=15, pady=15, bd=0, highlightthickness=1, highlightbackground="#45475a")
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Goal Name:", bg="#313244", fg="#a6adc8").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = tk.Entry(form, font=("Segoe UI", 11), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=25)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Target Value:", bg="#313244", fg="#a6adc8").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        target_entry = tk.Entry(form, font=("Segoe UI", 11), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=12)
        target_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form, text="Unit:", bg="#313244", fg="#a6adc8").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        unit_entry = tk.Entry(form, font=("Segoe UI", 11), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=10)
        unit_entry.grid(row=0, column=5, padx=5, pady=5)

        def add_goal():
            name = name_entry.get().strip()
            target = target_entry.get().strip()
            unit = unit_entry.get().strip()
            if not name or not target:
                messagebox.showwarning("Warning", "Goal name and target are required.")
                return
            goal = {
                "name": name,
                "target": target,
                "unit": unit,
                "current": "0",
                "created": datetime.now().strftime("%Y-%m-%d"),
            }
            self.data["goals"].setdefault("list", []).append(goal)
            save_data(self.data)
            messagebox.showinfo("Success", f"Goal '{name}' added!")
            name_entry.delete(0, tk.END)
            target_entry.delete(0, tk.END)
            unit_entry.delete(0, tk.END)
            show_goals_list()

        tk.Button(form, text="➕ Add Goal", font=("Segoe UI", 11, "bold"), bg="#a6e3a1", fg="#1e1e2e", bd=0, padx=12, pady=5, command=add_goal).grid(row=0, column=6, padx=10)

        goals_container = tk.Frame(self.content, bg="#1e1e2e")
        goals_container.pack(fill="both", expand=True, padx=20, pady=10)

        def show_goals_list():
            for w in goals_container.winfo_children():
                w.destroy()

            goals = self.data["goals"].get("list", [])
            if not goals:
                tk.Label(goals_container, text="No goals set yet. Create one above!", bg="#1e1e2e", fg="#6c7086", font=("Segoe UI", 12)).pack(pady=30)
                return

            for idx, g in enumerate(goals):
                card = tk.Frame(goals_container, bg="#313244", padx=15, pady=12, bd=0, highlightthickness=1, highlightbackground="#45475a")
                card.pack(fill="x", pady=4)

                tk.Label(card, text=f"🎯 {g['name']}", bg="#313244", fg="#cba6f7", font=("Segoe UI", 12, "bold")).pack(anchor="w")
                tk.Label(card, text=f"Target: {g['target']} {g['unit']}  |  Current: {g['current']} {g['unit']}  |  Since: {g['created']}", bg="#313244", fg="#a6adc8", font=("Segoe UI", 10)).pack(anchor="w")

                # Progress bar
                try:
                    pct = min(float(g["current"]) / float(g["target"]), 1.0)
                except (ValueError, ZeroDivisionError):
                    pct = 0

                bar_bg = tk.Frame(card, bg="#45475a", height=15)
                bar_bg.pack(fill="x", pady=5)
                bar_fg = tk.Frame(bar_bg, bg="#a6e3a1", height=15, width=max(1, int(pct * 400)))
                bar_fg.place(x=0, y=0, relheight=1.0)

                # Update button
                def make_update(i=i):
                    return lambda: self._update_goal(i)

                tk.Button(card, text="Update Progress", font=("Segoe UI", 9), bg="#45475a", fg="#a6e3a1", bd=0, padx=8, pady=2, command=make_update(idx)).pack(anchor="e", pady=(3, 0))

        show_goals_list()

    def _update_goal(self, idx):
        goals = self.data["goals"].get("list", [])
        if idx >= len(goals):
            return
        popup = tk.Toplevel(self)
        popup.title("Update Goal")
        popup.geometry("300x150")
        popup.configure(bg="#1e1e2e")
        g = goals[idx]
        tk.Label(popup, text=f"Update '{g['name']}' progress:", bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 12)).pack(pady=10)
        entry = tk.Entry(popup, font=("Segoe UI", 12), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=15)
        entry.insert(0, g["current"])
        entry.pack()

        def submit():
            try:
                self.data["goals"]["list"][idx]["current"] = entry.get()
                save_data(self.data)
                popup.destroy()
                self.show_goals()
            except Exception:
                messagebox.showerror("Error", "Invalid value.")

        tk.Button(popup, text="Save", font=("Segoe UI", 11, "bold"), bg="#a6e3a1", fg="#1e1e2e", bd=0, padx=15, pady=5, command=submit).pack(pady=15)

    # ── Exercise Library ─────────────────────────────────────────────
    def show_exercises(self):
        self._clear_content()
        self._highlight_button("Exercise Library")

        self._header_label(self.content, "📚 Exercise Library").pack(pady=15, anchor="w", padx=20)

        library = {
            "Bench Press": {"muscle": "Chest", "equipment": "Barbell", "difficulty": "Intermediate", "calories_per_min": 7},
            "Squats": {"muscle": "Legs", "equipment": "Barbell", "difficulty": "Intermediate", "calories_per_min": 8},
            "Deadlift": {"muscle": "Back", "equipment": "Barbell", "difficulty": "Advanced", "calories_per_min": 10},
            "Pull-ups": {"muscle": "Back", "equipment": "Bodyweight", "difficulty": "Intermediate", "calories_per_min": 8},
            "Overhead Press": {"muscle": "Shoulders", "equipment": "Barbell", "difficulty": "Intermediate", "calories_per_min": 6},
            "Barbell Curl": {"muscle": "Biceps", "equipment": "Barbell", "difficulty": "Beginner", "calories_per_min": 5},
            "Tricep Pushdown": {"muscle": "Triceps", "equipment": "Cable", "difficulty": "Beginner", "calories_per_min": 4},
            "Lunges": {"muscle": "Legs", "equipment": "Dumbbell", "difficulty": "Beginner", "calories_per_min": 6},
            "Planks": {"muscle": "Core", "equipment": "Bodyweight", "difficulty": "Beginner", "calories_per_min": 4},
            "Hip Thrusts": {"muscle": "Glutes", "equipment": "Barbell", "difficulty": "Intermediate", "calories_per_min": 6},
            "Cable Flyes": {"muscle": "Chest", "equipment": "Cable", "difficulty": "Intermediate", "calories_per_min": 5},
            "Leg Press": {"muscle": "Legs", "equipment": "Machine", "difficulty": "Beginner", "calories_per_min": 7},
            "Lat Pulldown": {"muscle": "Back", "equipment": "Cable", "difficulty": "Beginner", "calories_per_min": 5},
            "Lateral Raises": {"muscle": "Shoulders", "equipment": "Dumbbell", "difficulty": "Beginner", "calories_per_min": 4},
            "Crunches": {"muscle": "Core", "equipment": "Bodyweight", "difficulty": "Beginner", "calories_per_min": 3},
            "Dips": {"muscle": "Triceps", "equipment": "Bodyweight", "difficulty": "Intermediate", "calories_per_min": 7},
            "Russian Twists": {"muscle": "Core", "equipment": "Bodyweight", "difficulty": "Beginner", "calories_per_min": 4},
            "Calf Raises": {"muscle": "Legs", "equipment": "Machine", "difficulty": "Beginner", "calories_per_min": 3},
            "Face Pulls": {"muscle": "Shoulders", "equipment": "Cable", "difficulty": "Beginner", "calories_per_min": 3},
            "Preacher Curl": {"muscle": "Biceps", "equipment": "Barbell", "difficulty": "Intermediate", "calories_per_min": 4},
        }

        # Filter
        filter_frame = tk.Frame(self.content, bg="#313244", padx=10, pady=10, bd=0, highlightthickness=1, highlightbackground="#45475a")
        filter_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(filter_frame, text="Filter:", bg="#313244", fg="#a6adc8", font=("Segoe UI", 10)).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=search_var, font=("Segoe UI", 11), bg="#45475a", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, width=20)
        search_entry.pack(side="left", padx=10)

        muscle_var = tk.StringVar(value="All")
        muscles_list = sorted(set(v["muscle"] for v in library.values()))
        muscle_menu = ttk.Combobox(filter_frame, textvariable=muscle_var, values=["All"] + muscles_list, width=15, state="readonly")
        muscle_menu.pack(side="left", padx=5)

        # Table
        table_frame = tk.Frame(self.content, bg="#1e1e2e")
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols = ("Exercise", "Muscle", "Equipment", "Difficulty", "Cal/min")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=140)
        tree.pack(fill="both", expand=True)

        def refresh_table(*args):
            for item in tree.get_children():
                tree.delete(item)
            search = search_var.get().lower()
            muscle_filter = muscle_var.get()
            for name, info in library.items():
                if search and search not in name.lower():
                    continue
                if muscle_filter != "All" and info["muscle"] != muscle_filter:
                    continue
                tree.insert("", "end", values=(name, info["muscle"], info["equipment"], info["difficulty"], info["calories_per_min"]))

        search_var.trace_add("write", refresh_table)
        muscle_var.trace_add("write", refresh_table)
        refresh_table()


# ─── Run ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = BodyApp()
    app.mainloop()