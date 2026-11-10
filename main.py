import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import sqlite3

from database import Database


class DecisionLabApp:

    def __init__(self, root):

        self.root = root

        self.db = Database()

        self.current_decision = None

        self.decisions = []

        self.colors = {

            "background": "#101827",

            "sidebar": "#172235",

            "card": "#1E2C42",

            "primary": "#38BDF8",

            "text": "#F1F5F9",

            "muted": "#94A3B8",

            "green": "#34D399",

            "red": "#FB7185",

            "border": "#334155",

            "orange": "#FBBF24"

        }

        self.root.title(
            "DecisionLab 2.0 | Smart Decision Analysis"
        )


        self.root.geometry("1350x850")

        self.root.minsize(1150, 750)

        self.root.configure(
            bg=self.colors["background"]
        )

        self.setup_style()

        self.build_interface()

        self.refresh_all()

    # =================================
    # STYLE
    # =================================

    def setup_style(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(

            "Treeview",

            background=self.colors["card"],

            foreground=self.colors["text"],

            fieldbackground=self.colors["card"],

            rowheight=36,

            borderwidth=0,

            font=("Segoe UI", 10)

        )

        style.configure(

            "Treeview.Heading",

            background=self.colors["sidebar"],

            foreground=self.colors["primary"],

            font=("Segoe UI", 10, "bold"),

            relief="flat"

        )

        style.map(

            "Treeview",

            background=[

                ("selected", "#075985")

            ],

            foreground=[

                ("selected", "white")

            ]

        )

        style.configure(

            "TNotebook",

            background=self.colors["background"],

            borderwidth=0

        )

        style.configure(

            "TNotebook.Tab",

            background=self.colors["sidebar"],

            foreground=self.colors["text"],

            padding=(17, 11),

            font=("Segoe UI", 10, "bold")

        )

        style.map(

            "TNotebook.Tab",

            background=[

                ("selected", self.colors["card"])

            ],

            foreground=[

                ("selected", self.colors["primary"])

            ]

        )

        style.configure(

            "TCombobox",

            fieldbackground=self.colors["card"],

            background=self.colors["card"],

            foreground=self.colors["text"],

            padding=7

        )

        style.configure(

            "TSpinbox",

            fieldbackground=self.colors["card"],

            foreground=self.colors["text"],

            padding=7

        )

    # =================================
    # MAIN INTERFACE
    # =================================

    def build_interface(self):

        self.sidebar = tk.Frame(

            self.root,

            bg=self.colors["sidebar"],

            width=255

        )

        self.sidebar.pack(

            side="left",

            fill="y"

        )

        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(

            self.root,

            bg=self.colors["background"]

        )

        self.main_area.pack(

            side="right",

            fill="both",

            expand=True

        )

        self.build_sidebar()

        self.build_main_area()

    # =================================
    # SIDEBAR
    # =================================

    def build_sidebar(self):

        tk.Label(

            self.sidebar,

            text="DECISIONLAB",

            bg=self.colors["sidebar"],

            fg=self.colors["primary"],

            font=("Segoe UI", 20, "bold")

        ).pack(pady=(30, 5))

        tk.Label(

            self.sidebar,
            text="SMART DECISION SYSTEM",

            bg=self.colors["sidebar"],

            fg=self.colors["muted"],

            font=("Segoe UI", 8)

        ).pack(pady=(0, 30))

        tk.Label(

            self.sidebar,

            text="YOUR DECISIONS",

            bg=self.colors["sidebar"],

            fg=self.colors["muted"],

            font=("Segoe UI", 9, "bold")

        ).pack(

            anchor="w",

            padx=18,

            pady=(0, 10)

        )

        self.decision_list = tk.Listbox(

            self.sidebar,

            bg=self.colors["sidebar"],

            fg=self.colors["text"],

            selectbackground="#075985",

            selectforeground="white",

            font=("Segoe UI", 10),

            relief="flat",

            borderwidth=0,

            highlightthickness=0,

            activestyle="none"

        )

        self.decision_list.pack(

            fill="both",

            expand=True,

            padx=12,

            pady=5

        )

        self.decision_list.bind(

            "<<ListboxSelect>>",

            self.on_decision_select

        )

        self.make_button(

            self.sidebar,

            "+ New Decision",

            self.add_decision,

            self.colors["primary"],

            "#101827"

        ).pack(

            fill="x",

            padx=15,

            pady=(15, 7)

        )

        self.make_button(

            self.sidebar,

            "Delete Decision",

            self.delete_decision,

            self.colors["red"],

            "#101827"

        ).pack(

            fill="x",

            padx=15,

            pady=(0, 20)

        )

        tk.Label(

            self.sidebar,

            text="DecisionLab v2.0",

            bg=self.colors["sidebar"],

            fg=self.colors["muted"],

            font=("Segoe UI", 8)

        ).pack(pady=15)

    # =================================
    # MAIN AREA
    # =================================

    def build_main_area(self):

        header = tk.Frame(

            self.main_area,

            bg=self.colors["background"]

        )

        header.pack(

            fill="x",

            padx=30,

            pady=(25, 15)

        )

        tk.Label(

            header,

            text="Decision Intelligence",

            bg=self.colors["background"],

            fg=self.colors["text"],

            font=("Segoe UI", 23, "bold")

        ).pack(anchor="w")

        tk.Label(

            header,

            text=(

                "Analyze your options. "

                "Compare your criteria. "

                "Make smarter decisions."

            ),

            bg=self.colors["background"],

            fg=self.colors["muted"],

            font=("Segoe UI", 10)

        ).pack(

            anchor="w",

            pady=(5, 0)

        )

        self.stats_frame = tk.Frame(

            self.main_area,

            bg=self.colors["background"]

        )

        self.stats_frame.pack(

            fill="x",

            padx=30,

            pady=10

        )

        self.notebook = ttk.Notebook(

            self.main_area

        )

        self.notebook.pack(

            fill="both",

            expand=True,

            padx=30,

            pady=(10, 25)

        )

        self.build_overview_tab()

        self.build_alternatives_tab()

        self.build_criteria_tab()

        self.build_scores_tab()

        self.build_ranking_tab()

        self.build_analytics_tab()

    # =================================
    # BUTTON FACTORY
    # =================================

    def make_button(

        self,

        parent,

        text,

        command,

        bg=None,

        fg=None

    ):

        return tk.Button(

            parent,

            text=text,

            command=command,

            bg=bg or self.colors["card"],

            fg=fg or self.colors["text"],

            activebackground=self.colors["primary"],

            activeforeground="#101827",
            font=("Segoe UI", 10, "bold"),

            relief="flat",

            cursor="hand2",

            padx=12,

            pady=9

        )

    # =================================
    # STATISTICS
    # =================================

    def update_statistics(self):

        for widget in self.stats_frame.winfo_children():

            widget.destroy()

        stats = self.db.get_statistics()

        cards = [

            ("DECISIONS", stats["decisions"]),

            ("ALTERNATIVES", stats["alternatives"]),

            ("CRITERIA", stats["criteria"]),

            ("SCORES", stats["scores"])

        ]

        for title, value in cards:

            card = tk.Frame(

                self.stats_frame,

                bg=self.colors["card"],

                padx=18,

                pady=14

            )

            card.pack(

                side="left",

                fill="both",

                expand=True,

                padx=(0, 12)

            )

            tk.Label(

                card,

                text=title,

                bg=self.colors["card"],

                fg=self.colors["muted"],

                font=("Segoe UI", 9, "bold")

            ).pack(anchor="w")

            tk.Label(

                card,

                text=str(value),

                bg=self.colors["card"],

                fg=self.colors["primary"],

                font=("Segoe UI", 23, "bold")

            ).pack(

                anchor="w",

                pady=(5, 0)

            )

    # =================================
    # OVERVIEW TAB
    # =================================

    def build_overview_tab(self):

        self.overview_tab = tk.Frame(

            self.notebook,

            bg=self.colors["background"]

        )

        self.notebook.add(

            self.overview_tab,

            text="Overview"

        )

        self.overview_title = tk.Label(

            self.overview_tab,

            text="Welcome to DecisionLab",

            bg=self.colors["background"],

            fg=self.colors["primary"],

            font=("Segoe UI", 20, "bold")

        )

        self.overview_title.pack(

            anchor="w",

            padx=25,

            pady=(35, 15)

        )

        self.overview_description = tk.Label(

            self.overview_tab,

            text=(

                "Create a decision from the sidebar.\n\n"

                "Add alternatives, define criteria and assign weights.\n"

                "Evaluate your options and discover the best result."

            ),

            bg=self.colors["background"],

            fg=self.colors["muted"],

            font=("Segoe UI", 11),

            justify="left"

        )

        self.overview_description.pack(

            anchor="w",

            padx=25,

            pady=10

        )

        self.overview_info = tk.Label(

            self.overview_tab,

            text="No decision selected.",

            bg=self.colors["card"],

            fg=self.colors["text"],

            font=("Segoe UI", 11),

            padx=20,

            pady=20

        )

        self.overview_info.pack(

            fill="x",

            padx=25,

            pady=25

        )

    # =================================
    # ALTERNATIVES TAB
    # =================================

    def build_alternatives_tab(self):

        self.alternatives_tab = tk.Frame(

            self.notebook,

            bg=self.colors["background"]

        )

        self.notebook.add(

            self.alternatives_tab,

            text="Alternatives"

        )

        toolbar = tk.Frame(

            self.alternatives_tab,

            bg=self.colors["background"]

        )

        toolbar.pack(

            fill="x",

            padx=20,

            pady=15

        )

        self.make_button(

            toolbar,

            "+ Add Alternative",

            self.add_alternative,

            self.colors["primary"],

            "#101827"

        ).pack(

            side="left",
            padx=(0, 8)

        )

        self.make_button(

            toolbar,

            "Delete Selected",

            self.delete_alternative,

            self.colors["red"],

            "#101827"

        ).pack(side="left")

        self.alternatives_tree = self.create_tree(

            self.alternatives_tab,

            ("name", "description"),

            ("Alternative", "Description"),

            (230, 450)

        )

    # =================================
    # CRITERIA TAB
    # =================================

    def build_criteria_tab(self):

        self.criteria_tab = tk.Frame(

            self.notebook,

            bg=self.colors["background"]

        )

        self.notebook.add(

            self.criteria_tab,

            text="Criteria"

        )

        toolbar = tk.Frame(

            self.criteria_tab,

            bg=self.colors["background"]

        )

        toolbar.pack(

            fill="x",

            padx=20,

            pady=15

        )

        self.make_button(

            toolbar,

            "+ Add Criterion",

            self.add_criterion,

            self.colors["primary"],

            "#101827"

        ).pack(

            side="left",

            padx=(0, 8)

        )

        self.make_button(

            toolbar,

            "Delete Selected",

            self.delete_criterion,

            self.colors["red"],

            "#101827"

        ).pack(side="left")

        self.criteria_tree = self.create_tree(

            self.criteria_tab,

            ("name", "weight"),

            ("Criterion", "Weight"),

            (300, 150)

        )

    # =================================
    # SCORES TAB
    # =================================

    def build_scores_tab(self):

        self.scores_tab = tk.Frame(

            self.notebook,

            bg=self.colors["background"]

        )

        self.notebook.add(

            self.scores_tab,

            text="Scores"

        )

        toolbar = tk.Frame(

            self.scores_tab,

            bg=self.colors["background"]

        )

        toolbar.pack(

            fill="x",

            padx=20,

            pady=15

        )

        self.make_button(

            toolbar,

            "+ Add / Update Score",

            self.add_score,

            self.colors["primary"],

            "#101827"

        ).pack(side="left")

        self.scores_tree = self.create_tree(

            self.scores_tab,

            ("alternative", "criterion", "score"),

            ("Alternative", "Criterion", "Score"),

            (220, 220, 120)

        )

    # =================================
    # RANKING TAB
    # =================================

    def build_ranking_tab(self):

        self.ranking_tab = tk.Frame(

            self.notebook,

            bg=self.colors["background"]

        )

        self.notebook.add(

            self.ranking_tab,

            text="Ranking"

        )

        toolbar = tk.Frame(

            self.ranking_tab,

            bg=self.colors["background"]

        )

        toolbar.pack(

            fill="x",

            padx=20,

            pady=15

        )

        self.make_button(

            toolbar,

            "Refresh Ranking",

            self.refresh_ranking,

            self.colors["green"],

            "#101827"

        ).pack(side="left")

        self.ranking_tree = self.create_tree(

            self.ranking_tab,

            ("rank", "name", "score", "coverage", "status"),

            (

                "Rank",

                "Alternative",

                "Final Score",

                "Coverage",

                "Status"

            ),

            (90, 200, 130, 120, 140)

        )

    # =================================
    # ANALYTICS TAB
    # =================================

    def build_analytics_tab(self):

        self.analytics_tab = tk.Frame(

            self.notebook,

            bg=self.colors["background"]

        )

        self.notebook.add(

            self.analytics_tab,
            text="Analytics"

        )

        title = tk.Label(

            self.analytics_tab,

            text="Visual Analytics",

            bg=self.colors["background"],

            fg=self.colors["primary"],

            font=("Segoe UI", 18, "bold")

        )

        title.pack(

            anchor="w",

            padx=20,

            pady=(18, 5)

        )

        subtitle = tk.Label(

            self.analytics_tab,

            text="Explore your decision results through visual analysis.",

            bg=self.colors["background"],

            fg=self.colors["muted"],

            font=("Segoe UI", 9)

        )

        subtitle.pack(

            anchor="w",

            padx=20,

            pady=(0, 12)

        )

        self.insight_card = tk.Frame(

            self.analytics_tab,

            bg=self.colors["card"],

            padx=18,

            pady=14

        )

        self.insight_card.pack(

            fill="x",

            padx=20,

            pady=10

        )

        tk.Label(

            self.insight_card,

            text="SMART INSIGHTS",

            bg=self.colors["card"],

            fg=self.colors["primary"],

            font=("Segoe UI", 10, "bold")

        ).pack(anchor="w")

        self.insight_text = tk.Label(

            self.insight_card,

            text="Select a decision to generate insights.",

            bg=self.colors["card"],

            fg=self.colors["text"],

            font=("Segoe UI", 10),

            justify="left",

            wraplength=850

        )

        self.insight_text.pack(

            anchor="w",

            pady=(10, 0)

        )

        charts_frame = tk.Frame(

            self.analytics_tab,

            bg=self.colors["background"]

        )

        charts_frame.pack(

            fill="both",

            expand=True,

            padx=10,

            pady=3

        )

        left_panel = tk.Frame(

            charts_frame,

            bg=self.colors["card"]

        )

        left_panel.pack(

            side="left",

            fill="both",

            expand=True,

            padx=(0, 8)

        )

        right_panel = tk.Frame(

            charts_frame,

            bg=self.colors["card"]

        )

        right_panel.pack(

            side="left",

            fill="both",

            expand=True,

            padx=(8, 0)

        )

        tk.Label(

            left_panel,

            text="ALTERNATIVE COMPARISON",

            bg=self.colors["card"],

            fg=self.colors["primary"],

            font=("Segoe UI", 10, "bold")

        ).pack(

            anchor="w",

            padx=15,

            pady=12

        )

        tk.Label(

            right_panel,

            text="CRITERIA PERFORMANCE",

            bg=self.colors["card"],

            fg=self.colors["primary"],

            font=("Segoe UI", 10, "bold")

        ).pack(

            anchor="w",

            padx=15,

            pady=12

        )

        self.alternative_canvas = tk.Canvas(

            left_panel,

            bg=self.colors["card"],

            highlightthickness=0

        )

        self.alternative_canvas.pack(

            fill="both",

            expand=True,

            padx=10,

            pady=5

        )

        self.criteria_canvas = tk.Canvas(

            right_panel,

            bg=self.colors["card"],

            highlightthickness=0

        )

        self.criteria_canvas.pack(

            fill="both",

            expand=True,

            padx=10,

            pady=5

        )

        self.chart_results = []

        self.chart_criteria = []

        self.alternative_canvas.bind(

            "<Configure>",

            lambda event: self.draw_alternative_chart()

        )

        self.criteria_canvas.bind(

            "<Configure>",

            lambda event: self.draw_criteria_chart()

        )

    # =================================
    # TREEVIEW FACTORY
    # =================================

    def create_tree(

        self,
        parent,

        columns,

        headings,

        widths

    ):

        container = tk.Frame(

            parent,

            bg=self.colors["background"]

        )

        container.pack(

            fill="both",

            expand=True,

            padx=20,

            pady=(0, 20)

        )

        tree = ttk.Treeview(

            container,

            columns=columns,

            show="headings"

        )

        for column, heading, width in zip(

            columns,

            headings,

            widths

        ):

            tree.heading(

                column,

                text=heading

            )

            tree.column(

                column,

                width=width,

                anchor="center"

            )

        scrollbar = ttk.Scrollbar(

            container,

            orient="vertical",

            command=tree.yview

        )

        tree.configure(

            yscrollcommand=scrollbar.set

        )

        tree.pack(

            side="left",

            fill="both",

            expand=True

        )

        scrollbar.pack(

            side="right",

            fill="y"

        )

        return tree

    # =================================
    # REFRESH ALL
    # =================================

    def refresh_all(self):

        self.update_statistics()

        self.refresh_decisions()

        if self.current_decision is not None:

            exists = any(

                item["id"] == self.current_decision

                for item in self.decisions

            )

            if exists:

                self.load_workspace()

            else:

                self.current_decision = None

                self.clear_workspace()

        else:

            self.clear_workspace()

    # =================================
    # REFRESH DECISIONS
    # =================================

    def refresh_decisions(self):

        self.decision_list.delete(

            0,

            tk.END

        )

        self.decisions = self.db.get_decisions()

        for decision in self.decisions:

            self.decision_list.insert(

                tk.END,

                decision["title"]

            )

    # =================================
    # CLEAR TREE
    # =================================

    def clear_tree(self, tree):

        for item in tree.get_children():

            tree.delete(item)

    # =================================
    # LOAD WORKSPACE
    # =================================

    def load_workspace(self):

        if self.current_decision is None:

            return

        decision = next(

            (

                item for item in self.decisions

                if item["id"] == self.current_decision

            ),

            None

        )

        if decision is None:

            return

        self.overview_title.config(

            text=decision["title"]

        )

        self.overview_description.config(

            text=(

                decision["description"]

                or "No description provided."

            )

        )

        alternatives = self.db.get_alternatives(

            self.current_decision

        )

        criteria = self.db.get_criteria(

            self.current_decision

        )

        scores = self.db.get_scores(

            self.current_decision

        )

        self.clear_tree(

            self.alternatives_tree

        )

        for item in alternatives:

            self.alternatives_tree.insert(

                "",

                tk.END,

                iid=str(item["id"]),

                values=(

                    item["name"],

                    item["description"] or ""

                )

            )

        self.clear_tree(

            self.criteria_tree

        )

        for item in criteria:

            self.criteria_tree.insert(

                "",

                tk.END,

                iid=str(item["id"]),

                values=(

                    item["name"],
                    item["weight"]

                )

            )

        self.clear_tree(

            self.scores_tree

        )

        for item in scores:

            self.scores_tree.insert(

                "",

                tk.END,

                values=(

                    item["alternative"],

                    item["criterion"],

                    item["score"]

                )

            )

        self.overview_info.config(

            text=(

                f"Alternatives: {len(alternatives)}     |     "

                f"Criteria: {len(criteria)}     |     "

                f"Recorded Scores: {len(scores)}"

            )

        )

        self.refresh_ranking()

        self.refresh_analytics()

    # =================================
    # DECISION SELECTION
    # =================================

    def on_decision_select(self, event):

        selection = self.decision_list.curselection()

        if not selection:

            return

        index = selection[0]

        self.current_decision = self.decisions[index]["id"]

        self.load_workspace()

    # =================================
    # ADD DECISION
    # =================================

    def add_decision(self):

        title = simpledialog.askstring(

            "New Decision",

            "Enter decision title:",

            parent=self.root

        )

        if title is None:

            return

        title = title.strip()

        if not title:

            messagebox.showwarning(

                "Invalid Input",

                "Decision title cannot be empty."

            )

            return

        description = simpledialog.askstring(

            "Description",

            "Enter a short description:",

            parent=self.root

        )

        if description is None:

            description = ""

        try:

            decision_id = self.db.add_decision(

                title,

                description.strip()

            )

            self.current_decision = decision_id

            self.refresh_all()

            for index, item in enumerate(self.decisions):

                if item["id"] == decision_id:

                    self.decision_list.selection_set(index)

                    self.decision_list.see(index)

                    break

            self.load_workspace()

            messagebox.showinfo(

                "Success",

                "Decision created successfully."

            )

        except sqlite3.IntegrityError as error:

            messagebox.showerror(

                "Database Error",

                str(error)

            )

    # =================================
    # DELETE DECISION
    # =================================

    def delete_decision(self):

        if self.current_decision is None:

            messagebox.showwarning(

                "No Selection",

                "Select a decision first."

            )

            return

        confirm = messagebox.askyesno(

            "Confirm Deletion",

            "Delete this decision and all related data?"

        )

        if not confirm:

            return

        self.db.delete_decision(

            self.current_decision

        )

        self.current_decision = None

        self.refresh_all()

    # =================================
    # ADD ALTERNATIVE
    # =================================

    def add_alternative(self):

        if not self.check_decision():

            return

        name = simpledialog.askstring(

            "New Alternative",

            "Enter alternative name:",

            parent=self.root

        )

        if name is None:

            return

        name = name.strip()

        if not name:

            messagebox.showwarning(

                "Invalid Input",

                "Alternative name cannot be empty."

            )

            return

        description = simpledialog.askstring(

            "Description",

            "Enter alternative description:",

            parent=self.root

        )
        if description is None:

            description = ""

        try:

            self.db.add_alternative(

                self.current_decision,

                name,

                description.strip()

            )

            self.refresh_all()

        except sqlite3.IntegrityError:

            messagebox.showerror(

                "Duplicate Alternative",

                "This alternative already exists."

            )

    # =================================
    # DELETE ALTERNATIVE
    # =================================

    def delete_alternative(self):

        if not self.check_decision():

            return

        selected = self.alternatives_tree.selection()

        if not selected:

            messagebox.showwarning(

                "No Selection",

                "Select an alternative first."

            )

            return

        confirm = messagebox.askyesno(

            "Confirm Deletion",

            "Delete selected alternative and its scores?"

        )

        if confirm:

            self.db.delete_alternative(

                int(selected[0])

            )

            self.refresh_all()

    # =================================
    # ADD CRITERION
    # =================================

    def add_criterion(self):

        if not self.check_decision():

            return

        name = simpledialog.askstring(

            "New Criterion",

            "Enter criterion name:",

            parent=self.root

        )

        if name is None:

            return

        name = name.strip()

        if not name:

            messagebox.showwarning(

                "Invalid Input",

                "Criterion name cannot be empty."

            )

            return

        weight = simpledialog.askfloat(

            "Criterion Weight",

            "Enter weight (greater than zero):",

            parent=self.root,

            minvalue=0.01

        )

        if weight is None:

            return

        try:

            self.db.add_criterion(

                self.current_decision,

                name,

                weight

            )

            self.refresh_all()

        except sqlite3.IntegrityError:

            messagebox.showerror(

                "Duplicate Criterion",

                "This criterion already exists."

            )

    # =================================
    # DELETE CRITERION
    # =================================

    def delete_criterion(self):

        if not self.check_decision():

            return

        selected = self.criteria_tree.selection()

        if not selected:

            messagebox.showwarning(

                "No Selection",

                "Select a criterion first."

            )

            return

        confirm = messagebox.askyesno(

            "Confirm Deletion",

            "Delete selected criterion and its scores?"

        )

        if confirm:

            self.db.delete_criterion(

                int(selected[0])

            )

            self.refresh_all()

    # =================================
    # ADD / UPDATE SCORE
    # =================================

    def add_score(self):

        if not self.check_decision():

            return

        alternatives = self.db.get_alternatives(

            self.current_decision

        )

        criteria = self.db.get_criteria(

            self.current_decision

        )

        if not alternatives or not criteria:

            messagebox.showwarning(

                "Missing Data",

                "Add at least one alternative and one criterion first."

            )

            return

        window = tk.Toplevel(self.root)

        window.title("Add / Update Score")

        window.geometry("430x390")

        window.resizable(False, False)

        window.configure(

            bg=self.colors["background"]

        )

        window.transient(self.root)

        window.grab_set()

        tk.Label(

            window,

            text="EVALUATE ALTERNATIVE",
            bg=self.colors["background"],

            fg=self.colors["primary"],

            font=("Segoe UI", 16, "bold")

        ).pack(pady=(25, 20))

        tk.Label(

            window,

            text="Alternative",

            bg=self.colors["background"],

            fg=self.colors["text"]

        ).pack(anchor="w", padx=35)

        alternative_map = {

            f"{item['name']} (ID: {item['id']})":

            item["id"]

            for item in alternatives

        }

        alternative_box = ttk.Combobox(

            window,

            values=list(alternative_map.keys()),

            state="readonly",

            width=36

        )

        alternative_box.pack(

            padx=35,

            pady=(5, 15)

        )

        alternative_box.current(0)

        tk.Label(

            window,

            text="Criterion",

            bg=self.colors["background"],

            fg=self.colors["text"]

        ).pack(anchor="w", padx=35)

        criterion_map = {

            f"{item['name']} (ID: {item['id']})":

            item["id"]

            for item in criteria

        }

        criterion_box = ttk.Combobox(

            window,

            values=list(criterion_map.keys()),

            state="readonly",

            width=36

        )

        criterion_box.pack(

            padx=35,

            pady=(5, 15)

        )

        criterion_box.current(0)

        tk.Label(

            window,

            text="Score (0 - 10)",

            bg=self.colors["background"],

            fg=self.colors["text"]

        ).pack(anchor="w", padx=35)

        score_input = ttk.Spinbox(

            window,

            from_=0,

            to=10,

            increment=0.5,

            width=12

        )

        score_input.set(5)

        score_input.pack(

            padx=35,

            pady=8

        )

        def save():

            try:

                alternative_id = alternative_map[

                    alternative_box.get()

                ]

                criterion_id = criterion_map[

                    criterion_box.get()

                ]

                value = float(

                    score_input.get()

                )

                if not 0 <= value <= 10:

                    raise ValueError(

                        "Score must be between 0 and 10."

                    )

                self.db.save_score(

                    alternative_id,

                    criterion_id,

                    value

                )

                window.destroy()

                self.refresh_all()

                messagebox.showinfo(

                    "Success",

                    "Score saved successfully."

                )

            except (ValueError, sqlite3.Error) as error:

                messagebox.showerror(

                    "Invalid Score",

                    str(error),

                    parent=window

                )

        self.make_button(

            window,

            "Save Score",

            save,

            self.colors["primary"],

            "#101827"

        ).pack(

            fill="x",

            padx=35,

            pady=20

        )

    # =================================
    # RANKING
    # =================================

    def refresh_ranking(self):

        self.clear_tree(

            self.ranking_tree

        )

        if self.current_decision is None:

            return

        results = self.db.calculate_results(

            self.current_decision

        )

        for item in results:

            self.ranking_tree.insert(

                "",

                tk.END,

                values=(

                    item["rank"] or "—",

                    item["name"],

                    (

                        item["score"]

                        if item["score"] is not None

                        else "Pending"

                    ),

                    f"{item['coverage']}%",

                    item["status"]

                )
                )

    # =================================
    # ANALYTICS REFRESH
    # =================================

    def refresh_analytics(self):

        if self.current_decision is None:

            self.chart_results = []

            self.chart_criteria = []

            self.insight_text.config(

                text="Select a decision to generate insights."

            )

            self.draw_alternative_chart()

            self.draw_criteria_chart()

            return

        results = self.db.calculate_results(

            self.current_decision

        )

        insights = self.db.get_insights(

            self.current_decision

        )

        self.chart_results = [

            item for item in results

            if item["score"] is not None

        ]

        criteria = self.db.get_criteria(

            self.current_decision

        )

        matrix = self.db.get_score_matrix(

            self.current_decision

        )

        self.chart_criteria = []

        for criterion in criteria:

            values = [

                alternative["scores"][criterion["id"]]

                for alternative in matrix.values()

                if alternative["scores"][criterion["id"]]

                is not None

            ]

            if values:

                average = sum(values) / len(values)

                self.chart_criteria.append({

                    "name": criterion["name"],

                    "score": round(average, 2)

                })

        self.update_insight_text(insights)

        self.draw_alternative_chart()

        self.draw_criteria_chart()

    # =================================
    # INSIGHT TEXT
    # =================================

    def update_insight_text(self, insights):

        winner = insights["winner"]

        if winner is None:

            text = insights["message"]

            if insights["incomplete"]:

                text += (

                    "\n\nIncomplete alternatives: "

                    + ", ".join(

                        item["name"]

                        for item in insights["incomplete"]

                    )

                )

            self.insight_text.config(

                text=text

            )

            return

        text = (

            f"BEST OPTION: {winner['name']}\n"

            f"Final Score: {winner['score']} / 10\n"

            f"Coverage: {winner['coverage']}%\n"

        )

        if insights["runner_up"]:

            text += (

                f"\nSecond Place: "

                f"{insights['runner_up']['name']}\n"

                f"Score Difference: {insights['margin']} points\n"

            )

        if insights["best_criterion"]:

            text += (

                f"\nHighest Average Criterion: "

                f"{insights['best_criterion']['name']} "

                f"({insights['best_criterion']['average']}/10)"

            )

        if insights["incomplete"]:

            text += (

                "\n\nIncomplete Alternatives: "

                + ", ".join(

                    item["name"]

                    for item in insights["incomplete"]

                )

            )

        self.insight_text.config(

            text=text

        )

    # =================================
    # ALTERNATIVE BAR CHART
    # =================================

    def draw_alternative_chart(self):

        canvas = self.alternative_canvas

        canvas.delete("all")

        width = canvas.winfo_width()

        height = canvas.winfo_height()

        if width < 100 or height < 100:

            return

        canvas.create_text(

            15,

            15,

            text="Final Scores (0 - 10)",

            fill=self.colors["muted"],

            anchor="nw",

            font=("Segoe UI", 9)

        )

        if not self.chart_results:

            canvas.create_text(

                width / 2,

                height / 2,

                text="No complete results available",

                fill=self.colors["muted"],
                font=("Segoe UI", 10)

            )

            return

        top = 55

        bar_height = 24

        gap = 38

        left = 100

        right = width - 45

        chart_width = right - left

        for index, item in enumerate(self.chart_results):

            y = top + index * gap

            canvas.create_text(

                8,

                y + bar_height / 2,

                text=item["name"][:13],

                fill=self.colors["text"],

                anchor="w",

                font=("Segoe UI", 8)

            )

            canvas.create_rectangle(

                left,

                y,

                right,

                y + bar_height,

                fill=self.colors["border"],

                outline=""

            )

            bar_width = (

                chart_width * item["score"] / 10

            )

            bar_color = (

                self.colors["green"]

                if index == 0

                else self.colors["primary"]

            )

            canvas.create_rectangle(

                left,

                y,

                left + bar_width,

                y + bar_height,

                fill=bar_color,

                outline=""

            )

            canvas.create_text(

                right + 3,

                y + bar_height / 2,

                text=str(item["score"]),

                fill=self.colors["text"],

                anchor="w",

                font=("Segoe UI", 8, "bold")

            )

        canvas.create_text(

            left,

            height - 12,

            text="0",

            fill=self.colors["muted"],

            font=("Segoe UI", 8)

        )

        canvas.create_text(

            right,

            height - 12,

            text="10",

            fill=self.colors["muted"],

            font=("Segoe UI", 8)

        )

    # =================================
    # CRITERIA BAR CHART
    # =================================

    def draw_criteria_chart(self):

        canvas = self.criteria_canvas

        canvas.delete("all")

        width = canvas.winfo_width()

        height = canvas.winfo_height()

        if width < 100 or height < 100:

            return

        canvas.create_text(

            15,

            15,

            text="Average Scores (0 - 10)",

            fill=self.colors["muted"],

            anchor="nw",

            font=("Segoe UI", 9)

        )

        if not self.chart_criteria:

            canvas.create_text(

                width / 2,

                height / 2,

                text="No criterion data available",

                fill=self.colors["muted"],

                font=("Segoe UI", 10)

            )

            return

        top = 55

        bar_height = 24

        gap = 38

        left = 105

        right = width - 45

        chart_width = right - left

        for index, item in enumerate(self.chart_criteria):

            y = top + index * gap

            canvas.create_text(

                8,

                y + bar_height / 2,

                text=item["name"][:14],

                fill=self.colors["text"],

                anchor="w",

                font=("Segoe UI", 8)

            )

            canvas.create_rectangle(

                left,

                y,

                right,

                y + bar_height,

                fill=self.colors["border"],

                outline=""

            )

            bar_width = (

                chart_width * item["score"] / 10

            )

            canvas.create_rectangle(

                left,

                y,

                left + bar_width,

                y + bar_height,

                fill=self.colors["primary"],

                outline=""

            )

            canvas.create_text(

                right + 3,

                y + bar_height / 2,

                text=str(item["score"]),

                fill=self.colors["text"],

                anchor="w",

                font=("Segoe UI", 8, "bold")
                )

        canvas.create_text(

            left,

            height - 12,

            text="0",

            fill=self.colors["muted"],

            font=("Segoe UI", 8)

        )

        canvas.create_text(

            right,

            height - 12,

            text="10",

            fill=self.colors["muted"],

            font=("Segoe UI", 8)

        )

    # =================================
    # CLEAR WORKSPACE
    # =================================

    def clear_workspace(self):

        for tree in (

            self.alternatives_tree,

            self.criteria_tree,

            self.scores_tree,

            self.ranking_tree

        ):

            self.clear_tree(tree)

        self.overview_title.config(

            text="Welcome to DecisionLab"

        )

        self.overview_description.config(

            text="Create a decision from the sidebar to get started."

        )

        self.overview_info.config(

            text="No decision selected."

        )

        self.refresh_analytics()

    # =================================
    # VALIDATION
    # =================================

    def check_decision(self):

        if self.current_decision is None:

            messagebox.showwarning(

                "No Decision Selected",

                "Please create or select a decision first."

            )

            return False

        return True


# =================================
# APPLICATION ENTRY POINT
# =================================

if __name__ == "__main__":

    root = tk.Tk()
    root.title("DecisionLab 2.0 | Smart Decision Analysis")
    root.state("zoomed")
    root.minsize(1100 , 750)

    app = DecisionLabApp(root)

    root.mainloop()