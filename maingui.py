# Single source of truth for all game logic
import compscifootballgame as core
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import json
import os
import sys
import math
from typing import Dict, List, Tuple, Optional
import sys, io, builtins
from contextlib import contextmanager
from threading import Thread
import time

# Game data directory setup
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_PATH)

class FootballGameGUI:
    # Main GUI class for Pack to Pitch
    def __init__(self, root):
        self.root = root
        self.root.title("Pack to Pitch - Football Manager")
        self.root.state('zoomed')  # Start maximised
        self.root.resizable(True, True)

        # Game state variables
        self.edit = 1  # Current save slot
        self.coins = 0
        self.division = 10
        self.games_remaining = 10
        self.points = 0
        self.team_name = ""
        self.manager_name = ""
        self.manager_country = ""
        self.match_ratings = {}

        # Colour scheme for consistent design
        self.colors = {
            'bg': '#1a1a2e',
            'secondary': '#16213e',
            'accent': '#0f3460',
            'highlight': '#e94560',
            'text': '#ffffff',
            'subtext': '#c5c6c7',
            'success': '#00ff00',
            'warning': '#ffa500',
            'card_common': '#808080',
            'card_uncommon': '#00ff00',
            'card_rare': '#0066ff',
            'card_epic': '#9933ff',
            'card_legendary': '#ffaa00'
        }

        # Match speed multiplier (1.0 = normal speed) and per-tick delay
        self.match_speed_mult = 1.0   
        self.sim_speed = 1000        

        # Time delay between revealing cards in a pack (milliseconds)
        self.pack_speed = 350

        # Apply background colour
        self.root.configure(bg=self.colors['bg'])

        # Import role options directly from the core module
        self.role_options = core.role_options

        # Create save files and data if missing
        self.initialize_data_files()

        # Start with the main menu
        self.show_main_menu()

        # Keep track of where team management was opened from
        self.tm_return_to = "home"

    # Read team data using the original core function
    def read_team_data(self, place, edit_slot):
        return core.readteamdata(place, edit_slot)

    # Write team data using the original core function
    def write_team_data(self, new_data, place, edit_slot):
        return core.writeteamdata(new_data, place, edit_slot)

    # Remove the current opponent from the save file
    def remove_opponent(self):
        return core.removeopponent(self.edit)

    # Build an opponent using the same logic as the CLI version
    def build_opponent(self):
        # Sync key variables from CLI module
        core.edit = self.edit
        core.division = self.division
        core.role_options = core.role_options

        try:
            opponent_data = core.buildopponent()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to build opponent: {e}")
            return None

        # Save the opponent data to the current team slot
        self.write_team_data(opponent_data, "opponent", self.edit)
        return opponent_data

    def formation_switch(self, new_formation):
        # Use the formation switch logic from the core module
        return core.formationswitch(new_formation) 
    
    def compute_team_rating_from_players(self, players):
        # Calculate the average rating of the first eleven players
        return sum(int(p.get("rating", 0)) for p in players[:11]) // 11
    
    # Ratings and chemistry functions use the original CLI logic
    def role_rating(self, player_name, role):
        return core.rolerating(player_name, role)

    def team_rating(self):
        return core.teamrating()

    def team_chemistry(self, opponent=False):
        return core.teamchemistry(opponent)

    def chemistry(self, playername, opponent=False):
        return core.chemistry(playername, opponent)
   
    # Redirect standard output from CLI engine to the GUI text box
    @contextmanager
    def _redirect_stdio_to_gui(self, write_fn, input_provider=None):
        old_stdout, old_input = sys.stdout, builtins.input
        buf = io.StringIO()

        def fake_input(prompt=''):
            write_fn(str(prompt))
            return input_provider() if input_provider else ''

        try:
            sys.stdout = buf
            builtins.input = fake_input
            yield
        finally:
            sys.stdout, builtins.input = old_stdout, old_input

    def initialize_data_files(self):
        # Create default save files and data if missing
        for i in range(1, 5):
            filename = f"teamdata{i}.json"
            if not os.path.exists(filename):
                # Default squad for new saves
                default_squad = [
                    {"name": "Jack Thompson", "country": "England", "position": "GK", "rating": 50, "role": "Goalkeeper (Defend)"},
                    {"name": "Liam O'Connor", "country": "England", "position": "LB", "rating": 51, "role": "Fullback (Support)"},
                    {"name": "Ben Harris", "country": "England", "position": "CB", "rating": 52, "role": "Centreback (Defend)"},
                    {"name": "Charlie Moore", "country": "England", "position": "CB", "rating": 50, "role": "Centreback (Defend)"},
                    {"name": "Oscar Walker", "country": "England", "position": "RB", "rating": 51, "role": "Fullback (Support)"},
                    {"name": "George Wright", "country": "England", "position": "LW", "rating": 52, "role": "Winger (Support)"},
                    {"name": "Harvey Cooper", "country": "England", "position": "CM", "rating": 50, "role": "Central Midfielder (Support)"},
                    {"name": "Sam Allen", "country": "England", "position": "CM", "rating": 51, "role": "Central Midfielder (Support)"},
                    {"name": "Luke Richardson", "country": "England", "position": "RW", "rating": 52, "role": "Winger (Support)"},
                    {"name": "Tommy Evans", "country": "England", "position": "ST", "rating": 50, "role": "Advanced Forward (Attack)"},
                    {"name": "Joe Mitchell", "country": "England", "position": "ST", "rating": 51, "role": "Advanced Forward (Attack)"}
                ]
                data = {
                    "inuse": "no",
                    "team": "MyTeam",
                    "manager": "YourManagerName",
                    "manager country": "England",
                    "coins": "1000",
                    "division": "10",
                    "gamesremaining": "10",
                    "points": "0",
                    "formation": "4-4-2",
                    "squad": default_squad
                }
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
        
        # Create ratings and manager files if they do not exist
        if not os.path.exists("ratings.json"):
            self.create_sample_ratings()
        
        if not os.path.exists("managers.json"):
            self.create_sample_managers()
    
    def create_sample_ratings(self):
        # Create a basic ratings.json with a variety of players
        countries = ["England", "Spain", "Germany", "France", "Italy", "Brazil", "Argentina", "Portugal"]
        positions = ["GK", "LB", "CB", "RB", "CM", "LW", "RW", "ST"]
        
        players = []
        player_id = 1
        
        # Generate players across a range of ratings
        for rating in range(50, 95):
            for _ in range(3):
                country = random.choice(countries)
                position = random.choice(positions)
                base_stat = rating
                variance = 5
                
                player = {
                    "name": f"Player {player_id}",
                    "country": country,
                    "position": position,
                    "rating": rating,
                    "stats": {
                        "pace": max(30, min(99, base_stat + random.randint(-variance, variance))),
                        "shooting": max(30, min(99, base_stat + random.randint(-variance, variance))),
                        "passing": max(30, min(99, base_stat + random.randint(-variance, variance))),
                        "dribbling": max(30, min(99, base_stat + random.randint(-variance, variance))),
                        "defending": max(30, min(99, base_stat + random.randint(-variance, variance))),
                        "physical": max(30, min(99, base_stat + random.randint(-variance, variance)))
                    }
                }
                players.append(player)
                player_id += 1
        
        with open("ratings.json", 'w') as f:
            json.dump(players, f, indent=2)
    
    def create_sample_managers(self):
        # Create managers.json with realistic values for each division
        managers_data = []
        
        for div in range(1, 11):
            base_rating = 99 - (div - 1) * 5
            managers = []
            formations = ["4-4-2", "4-3-3", "4-5-1", "4-2-2-2", "5-3-2", "5-2-3", "5-4-1"]
            countries = ["England", "Spain", "Germany", "France", "Italy"]
            
            for i in range(5):
                manager = {
                    "name": f"Manager {div}-{i+1}",
                    "team": f"Team {div}-{i+1}",
                    "country": random.choice(countries),
                    "rating": base_rating + random.randint(-2, 2),
                    "formation": random.choice(formations)
                }
                managers.append(manager)
            
            managers_data.append({
                "division": div,
                "managers": managers
            })
        
        with open("managers.json", 'w') as f:
            json.dump(managers_data, f, indent=2)
    
    def clear_window(self):
        # Remove all widgets from the window
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_button(self, parent, text, command, width=20):
        # Create a styled button with hover effect
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 12, 'bold'),
            width=width,
            height=2,
            relief=tk.FLAT,
            cursor='hand2'
        )
        btn.bind('<Enter>', lambda e: btn.config(bg=self.colors['highlight']))
        btn.bind('<Leave>', lambda e: btn.config(bg=self.colors['accent']))
        return btn
    
    def open_team_management_from_play(self):
        # Open team management from the play screen
        self.tm_return_to = "play"
        self.show_squad_page()

    def open_team_management_from_home(self):
        # Open team management from the home screen
        self.tm_return_to = "home"
        self.show_squad_page()
    
    def create_label(self, parent, text, font_size=12, bold=False):
        # Create a styled label
        font_weight = 'bold' if bold else 'normal'
        return tk.Label(
            parent,
            text=text,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', font_size, font_weight)
        )
    
    def show_main_menu(self):
        # Build the main menu screen
        self.clear_window()
        
        # Title and subtitle
        title = self.create_label(self.root, "PACK TO PITCH", font_size=32, bold=True)
        title.pack(pady=50)
        subtitle = self.create_label(self.root, "Football Manager", font_size=16)
        subtitle.pack(pady=10)
        
        # Menu buttons
        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.pack(pady=50)
        self.create_button(button_frame, "Start New Game", self.start_new_game).pack(pady=10)
        self.create_button(button_frame, "Load Save Game", self.load_save_game).pack(pady=10)
        self.create_button(button_frame, "Exit", self.root.quit).pack(pady=10)
    
    def start_new_game(self):
        # Create a new save by collecting team and manager details, then writing to a free slot
        team_name = simpledialog.askstring("New Game", "Enter your team name:", parent=self.root)
        if not team_name:
            return
        
        manager_name = simpledialog.askstring("New Game", "Enter your manager's name:", parent=self.root)
        if not manager_name:
            return
        
        # Read available countries from ratings.json
        with open("ratings.json", 'r') as f:
            players_data = json.load(f)
        countries = sorted(set(p["country"] for p in players_data))
        
        # Country selection window
        country_dialog = tk.Toplevel(self.root)
        country_dialog.title("Select Nation")
        country_dialog.geometry("300x400")
        country_dialog.configure(bg=self.colors['bg'])
        
        selected_country = tk.StringVar()
        
        tk.Label(
            country_dialog,
            text="Select your manager's nationality:",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 12)
        ).pack(pady=10)
        
        # List of countries to choose from
        listbox = tk.Listbox(country_dialog, height=10)
        for country in countries:
            listbox.insert(tk.END, country)
        listbox.pack(pady=10, padx=20)
        
        # Confirm selection and close the window
        def confirm_country():
            selection = listbox.curselection()
            if selection:
                selected_country.set(countries[selection[0]])
                country_dialog.destroy()
        
        self.create_button(country_dialog, "Confirm", confirm_country, width=15).pack(pady=10)
        
        # Wait for the user to finish the dialog
        self.root.wait_window(country_dialog)
        
        # If nothing was chosen, cancel the flow
        if not selected_country.get():
            return

        # Find the first free save slot (1–4)
        for slot in range(1, 5):
            if self.read_team_data("inuse", slot) == "no":
                self.edit = slot
                core.edit = slot 
                
                # Set initial state for the new game
                self.team_name = team_name
                self.manager_name = manager_name
                self.manager_country = selected_country.get()
                self.coins = 1000
                self.division = 10
                self.games_remaining = 10
                self.points = 0
                self.match_speed_mult = 1.0
                self.sim_speed = 1000
                
                # Persist values using the core write path
                self.write_team_data("yes", "inuse", self.edit)
                self.write_team_data(self.team_name, "team", self.edit)
                self.write_team_data(self.manager_name, "manager", self.edit)
                self.write_team_data(self.manager_country, "manager country", self.edit)
                self.write_team_data(str(self.coins), "coins", self.edit)
                self.write_team_data(str(self.division), "division", self.edit)
                self.write_team_data(str(self.games_remaining), "gamesremaining", self.edit)
                self.write_team_data(str(self.points), "points", self.edit)
                self.write_team_data(self.match_speed_mult, "match speed", self.edit)
                
                # Move to the home page for this save
                messagebox.showinfo("Success", "Game created successfully!")
                self.show_home_page()
                return
        
        # If no slot was free, show an error
        messagebox.showerror("Error", "Maximum of 4 game slots reached")
    
    def load_save_game(self):
        # Load an existing save slot
        self.clear_window()
        
        title = self.create_label(self.root, "LOAD SAVE GAME", font_size=24, bold=True)
        title.pack(pady=30)
        
        # Gather all active saves
        saves = []
        for i in range(1, 5):
            if self.read_team_data("inuse", i) == "yes":
                team_name = self.read_team_data("team", i)
                saves.append((i, team_name))
        
        # No saves available
        if not saves:
            self.create_label(self.root, "No save games found").pack(pady=20)
            self.create_button(self.root, "Return", self.show_main_menu).pack(pady=20)
            return
        
        # Show each save with a load button and an always-visible delete menu button (⋮)
        for slot, team_name in saves:
            row = tk.Frame(self.root, bg=self.colors['bg'])
            row.pack(pady=10)

            # Load button
            btn = self.create_button(
                row,
                f"Save {slot}: {team_name}",
                lambda s=slot: self.load_slot(s),
                width=30
            )
            btn.pack(side=tk.LEFT)

            # Always-visible ⋮ menu for delete
            kebab = tk.Button(
                row,
                text="⋮",
                command=lambda s=slot, w=row: self._post_row_menu(s, w),
                bg=self.colors['accent'],
                fg=self.colors['text'],
                font=('Arial', 12, 'bold'),
                width=2,
                height=2,
                relief=tk.FLAT,
                cursor='hand2'
            )
            kebab.pack(side=tk.LEFT, padx=6)

            # Hover behaviour for both buttons
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.colors['highlight']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.colors['accent']))
            kebab.bind('<Enter>', lambda e, k=kebab: k.config(bg=self.colors['highlight']))
            kebab.bind('<Leave>', lambda e, k=kebab: k.config(bg=self.colors['accent']))
        
        self.create_button(self.root, "Return", self.show_main_menu).pack(pady=30)
        
    def _post_row_menu(self, slot, widget):
        # Context menu for a save row (currently only supports delete)
        menu = tk.Menu(widget, tearoff=0, bg="white")
        menu.add_command(label="Delete", command=lambda s=slot: self.confirm_delete_save(s))
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def confirm_delete_save(self, slot):
        # Confirm deletion of a save and refresh the list if accepted
        name = self.read_team_data("team", slot)
        if messagebox.askyesno("Delete Save", f"Delete save slot {slot} ({name})?"):
            self.delete_save_slot(slot)
            messagebox.showinfo("Deleted", f"Deleted slot {slot}")
            self.load_save_game()

    def delete_save_slot(self, idx):
        # Delete a save by shifting files up and resetting slot 4 to the default state
        import json, os, shutil

        # Shift teamdata{i+1}.json into teamdata{i}.json to close the gap
        for i in range(idx, 4):
            src = f"teamdata{i+1}.json"
            dst = f"teamdata{i}.json"
            if os.path.exists(src):
                shutil.copy(src, dst)

        # Reset the last slot (slot 4) to a default, unused save
        last = 4
        defaultsquad = [
            {"name": "Jack Thompson",   "country": "England", "position": "GK", "rating": 50, "role": "Goalkeeper"},
            {"name": "Liam O'Connor",   "country": "England", "position": "LB", "rating": 51, "role": "Fullback (Support)"},
            {"name": "Ben Harris",      "country": "England", "position": "CB", "rating": 52, "role": "Centreback (Defend)"},
            {"name": "Charlie Moore",   "country": "England", "position": "CB", "rating": 50, "role": "Centreback (Defend)"},
            {"name": "Oscar Walker",    "country": "England", "position": "RB", "rating": 51, "role": "Fullback (Support)"},
            {"name": "George Wright",   "country": "England", "position": "LW", "rating": 52, "role": "Winger (Support)"},
            {"name": "Harvey Cooper",   "country": "England", "position": "CM", "rating": 50, "role": "Central Midfielder (Support)"},
            {"name": "Sam Allen",       "country": "England", "position": "CM", "rating": 51, "role": "Central Midfielder (Support)"},
            {"name": "Luke Richardson", "country": "England", "position": "RW", "rating": 52, "role": "Winger (Support)"},
            {"name": "Tommy Evans",     "country": "England", "position": "ST", "rating": 50, "role": "Advanced Forward (Attack)"},
            {"name": "Joe Mitchell",    "country": "England", "position": "ST", "rating": 51, "role": "Advanced Forward (Attack)"}
        ]
        defaulttactics = {
            "directness": "Balanced",
            "tempo": "Balanced",
            "dribbling": "Balanced",
            "press": "Balanced",
            "defensive line": "Balanced",
            "defensive width": "Balanced",
            "approach": {"left": False, "middle": True, "right": False}
        }

        reset_data = {
            "inuse": "no",
            "team": "MyTeam",
            "manager": "YourManagerName",
            "manager country": "England",
            "formation": "4-4-2",
            "squad": defaultsquad,
            "coins": "1000",
            "division": "10",
            "gamesremaining": "10",
            "points": "0",
            "tactics": defaulttactics,
            "match speed": "1.0"
        }

        # Write the reset file for slot 4
        with open(f"teamdata{last}.json", "w") as f:
            json.dump(reset_data, f, indent=2)

        # Remove any cached opponent
        try:
            path = f"teamdata{last}.json"
            with open(path, "r") as f:
                data = json.load(f)
            data.pop("opponent", None)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

        # Refresh list so the screen updates
        self.load_save_game()
    
    def load_slot(self, slot):
        # Load a chosen save slot and go to its home page
        self.edit = slot
        core.edit = slot 
        self.team_name = self.read_team_data("team", slot)
        self.coins = int(self.read_team_data("coins", slot))
        self.division = int(self.read_team_data("division", slot))
        self.games_remaining = int(self.read_team_data("gamesremaining", slot))
        self.points = int(self.read_team_data("points", slot))
        self.manager_name = self.read_team_data("manager", slot)
        self.manager_country = self.read_team_data("manager country", slot)
        
        # Load match speed for this slot (default 1.0x if missing)
        try:
            saved_mult = self.read_team_data("match speed", slot)
            if isinstance(saved_mult, (int, float, str)):
                m = float(saved_mult)
            else:
                raise ValueError
        except Exception:
            m = 1.0
        m = max(0.5, min(4.0, m))
        self.match_speed_mult = m
        self.sim_speed = int(1000 / m)
        
        messagebox.showinfo("Success", f"Loaded {self.team_name}")
        self.show_home_page()
    
    def show_home_page(self):
        # Build the home page after a game is created or loaded
        self.clear_window()
        
        # Header bar
        header_frame = tk.Frame(self.root, bg=self.colors['secondary'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Refresh the team name from file so the header stays in sync
        try:
            team_rec = self.read_team_data("team", self.edit)
        except Exception:
            team_rec = None

        if isinstance(team_rec, dict):
            self.team_name = team_rec.get("name") or team_rec.get("team") or "My Team"
        elif isinstance(team_rec, str) and team_rec.strip():
            self.team_name = team_rec.strip()
        else:
            self.team_name = "My Team"
        
        title = tk.Label(
            header_frame,
            text=f"HOME - {self.team_name}",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 20, 'bold')
        )
        title.pack(side=tk.LEFT, padx=20, pady=20)
        
        coins_label = tk.Label(
            header_frame,
            text=f"💰 {self.coins} coins",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        )
        coins_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Main content area
        content_frame = tk.Frame(self.root, bg=self.colors['bg'])
        content_frame.pack(expand=True, fill=tk.BOTH, pady=50)
        
        # Main menu buttons
        button_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        button_frame.pack()
        
        self.create_button(button_frame, "⚽ Play", self.show_play_page).pack(pady=10)
        self.create_button(button_frame, "🛒 Store", self.show_store_page).pack(pady=10)
        self.create_button(button_frame, "👥 My Squad", self.open_team_management_from_home).pack(pady=10)
        self.create_button(button_frame, "⚙ Settings", self.show_settings).pack(pady=10)
        self.create_button(button_frame, "🏠 Main Menu", self.show_main_menu).pack(pady=10)

    def _load_managers_for_division(self, division_num: int):
        # Return a list of teams/managers for the given division from managers.json
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, "managers.json")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return []

        for block in data:
            if int(block.get("division", -1)) == int(division_num):
                out = []
                for m in block.get("managers", []):
                    out.append({
                        "team": m.get("team", "Unknown"),
                        "manager": m.get("name", "Unknown"),
                        "country": m.get("country", "Unknown"),
                        "rating": m.get("rating", "—"),
                        "formation": m.get("formation", ""),
                    })
                return out
        return []
    
    def show_play_page(self):
        # Build the play/division page
        self.clear_window()
        
        # Header bar
        header = tk.Frame(self.root, bg=self.colors['secondary'], height=60)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="PLAY",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 20, 'bold')
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        coins_label = tk.Label(
            header,
            text=f"💰 {self.coins} coins",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        )
        coins_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Division info box
        info_frame = tk.Frame(self.root, bg=self.colors['bg'])
        info_frame.pack(pady=30)
        
        self.create_label(info_frame, f"Division {self.division}", font_size=18, bold=True).pack(pady=5)
        self.create_label(info_frame, f"Current points: {self.points}", font_size=14).pack(pady=5)
        self.create_label(info_frame, f"Games remaining: {self.games_remaining}", font_size=14).pack(pady=5)
        
        tk.Label(info_frame, text="", bg=self.colors['bg']).pack(pady=10)
        
        # Thresholds for the league table
        relegation_threshold, promotion_threshold, title_threshold = \
            self._get_thresholds_for_division(self.division)
        self.create_label(info_frame, "Thresholds:", font_size=12, bold=True).pack(pady=5)
        if self.division < 10:
            self.create_label(info_frame, f"Relegation: {relegation_threshold} points", font_size=11).pack()
        if self.division > 1:
            self.create_label(info_frame, f"Promotion: {promotion_threshold} points", font_size=11).pack()
        self.create_label(info_frame, f"Title: {title_threshold} points", font_size=11).pack()
        
        # Buttons for match and league browsing
        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.pack(pady=30)
        
        self.create_button(button_frame, "Go to Match", self.show_match_page).pack(pady=10)
        self.create_button(button_frame, "View All Teams in Division", self.show_division_teams).pack(pady=10)
        self.create_button(button_frame, "Team Management", self.open_team_management_from_play).pack(pady=10)
        self.create_button(button_frame, "Return", self.show_home_page).pack(pady=10)

    def show_division_teams(self):
        # Show all teams in the current division using data from managers.json
        try:
            current_div = getattr(self, "division", None) or self.read_team_data("division", self.edit)
        except Exception:
            current_div = getattr(self, "division", None) or 1
        try:
            current_div = int(current_div)
        except Exception:
            current_div = 1

        # Load teams/managers for the division
        rows = self._load_managers_for_division(current_div)

        # New window to display the table
        win = tk.Toplevel(self.root)
        win.title(f"Division {current_div} – Teams")
        win.geometry("950x560")
        win.configure(bg=self.colors['bg'])
        win.transient(self.root)
        win.grab_set()

        # Title
        tk.Label(
            win,
            text=f"Division {current_div} – Teams",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=("Arial", 18, "bold")
        ).pack(pady=(16, 6))

        # Card-like container
        card = tk.Frame(win, bg=self.colors.get('card', self.colors['bg']), bd=0, highlightthickness=0)
        card.pack(fill="both", expand=True, padx=16, pady=8)

        # Treeview style
        style = ttk.Style(card)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "League.Treeview",
            background=self.colors.get('card', self.colors['bg']),
            fieldbackground=self.colors.get('card', self.colors['bg']),
            foreground=self.colors['text'],
            rowheight=30,
            borderwidth=0,
        )

        style.configure(
            "League.Treeview.Heading",
            background=self.colors.get('panel', '#1c2533'),
            foreground=self.colors['text'],
            font=("Arial", 11, "bold"),
            relief="flat",
        )
        style.layout("League.Treeview.Heading", [
            ("Treeheading.cell", {"sticky": "nswe"}),
            ("Treeheading.border", {"sticky": "nswe", "children": [
                ("Treeheading.padding", {"sticky": "nswe", "children": [
                    ("Treeheading.image", {"side": "right", "sticky": ""}),
                    ("Treeheading.text", {"sticky": "we"})
                ]})
            ]})
        ])

        style.map(
            "League.Treeview",
            background=[("selected", self.colors.get('accent', "#66aa77"))],
            foreground=[("selected", self.colors.get('bg', "#0b1f12"))]
        )

        # Table columns
        cols = ("team", "manager", "country", "rating")
        wrap = tk.Frame(card, bg=self.colors.get('card', self.colors['bg']))
        wrap.pack(fill="both", expand=True, padx=12, pady=12)

        tree = ttk.Treeview(wrap, columns=cols, show="headings", height=16, style="League.Treeview")
        tree.heading("team", text="Team")
        tree.heading("manager", text="Manager Name")
        tree.heading("country", text="Manager Country")
        tree.heading("rating", text="Manager Rating")

        tree.column("team",    width=320, minwidth=220, anchor="center", stretch=True)
        tree.column("manager", width=260, minwidth=200, anchor="center", stretch=True)
        tree.column("country", width=140, minwidth=120, anchor="center", stretch=False)
        tree.column("rating",  width=150, minwidth=120, anchor="center", stretch=False)
        tree.pack(side="left", fill="x", expand=True)

        # Row striping
        odd_bg = self.colors.get('bg')
        even_bg = self.colors.get('card', self.colors['bg'])
        tree.tag_configure("odd", background=odd_bg)
        tree.tag_configure("even", background=even_bg)

        # Populate rows
        if not rows:
            tree.insert("", "end", values=("No league data found for this division.", "", "", ""), tags=("odd",))
        else:
            def _rating(v):
                try:
                    return int(v.get("rating", 0))
                except Exception:
                    return -1
            rows_sorted = sorted(rows, key=lambda r: (-_rating(r), r.get("team", "")))

            for i, r in enumerate(rows_sorted):
                tag = "even" if i % 2 == 0 else "odd"
                tree.insert("", "end", values=(r["team"], r["manager"], r["country"], r["rating"]), tags=(tag,))
            tree.configure(height=min(len(rows_sorted), 12))

        # Close button
        self.create_button(win, "Return", win.destroy).pack(pady=12)
        
    def _pull_division_teams(self, division_num):
        # Try a few common locations/keys to find teams for a division in the save
        # Returns a list of dicts with team/manager info if found, else an empty list
        candidates = []

        # Option 1: a direct key like "division_3_teams"
        try:
            direct_key = f"division_{division_num}_teams"
            data = self.read_team_data(direct_key, self.edit)
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass

        # Option 2: nested league object with divisions["<num>"]["teams"]
        try:
            league = self.read_team_data("league", self.edit)
            div_key = str(division_num)
            maybe = (league.get("divisions", {}).get(div_key, {}) or
                     league.get("division", {}).get(div_key, {}))
            if isinstance(maybe, dict):
                teams = maybe.get("teams")
                if isinstance(teams, list) and teams:
                    return teams
        except Exception:
            pass

        # Option 3: flat list under "league_teams", filtered by division field
        try:
            flat = self.read_team_data("league_teams", self.edit)
            if isinstance(flat, list):
                for t in flat:
                    if isinstance(t, dict) and t.get("division") in (division_num, str(division_num)):
                        candidates.append(t)
                if candidates:
                    return candidates
        except Exception:
            pass

        # Not found
        return []
    
    def show_store_page(self):
        # Build the store page where players can buy packs
        self.clear_window()
        
        # Header bar
        header = tk.Frame(self.root, bg=self.colors['secondary'], height=60)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="STORE",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 20, 'bold')
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(
            header,
            text=f"💰 {self.coins} coins",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        ).pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Pack display
        content_frame = tk.Frame(self.root, bg=self.colors['bg'])
        content_frame.pack(expand=True, pady=50)
        
        packs = [
            ("Regular Pack", 300, {"common": 75, "uncommon": 20, "rare": 4, "epic": 1, "legendary": 0}),
            ("Prime Pack", 1000, {"common": 30, "uncommon": 45, "rare": 15, "epic": 7, "legendary": 3}),
            ("Premium Pack", 1500, {"common": 25, "uncommon": 40, "rare": 20, "epic": 11, "legendary": 4})
        ]
        
        for pack_name, cost, weights in packs:
            pack_frame = tk.Frame(content_frame, bg=self.colors['accent'], relief=tk.RAISED, bd=2)
            pack_frame.pack(pady=15, padx=50, fill=tk.X)
            
            tk.Label(
                pack_frame,
                text=pack_name,
                bg=self.colors['accent'],
                fg=self.colors['text'],
                font=('Arial', 16, 'bold')
            ).pack(pady=10)
            
            tk.Label(
                pack_frame,
                text=f"{cost} coins",
                bg=self.colors['accent'],
                fg=self.colors['text'],
                font=('Arial', 12)
            ).pack(pady=5)
            
            self.create_button(
                pack_frame,
                "Buy Pack",
                lambda c=cost, w=weights: self.open_pack(c, w),
                width=15
            ).pack(pady=10)
        
        # Button to browse the full player pool
        view_players_btn = self.create_button(
            self.root,
            "View All Possible Players",
            self.show_all_players,
            width=20
        )
        view_players_btn.pack(pady=5)
     
        self.create_button(self.root, "Return", self.show_home_page).pack(pady=20)
        
    def show_all_players(self):
        # Show the rating bands so the user can browse the player pool
        menu = tk.Toplevel(self.root)
        menu.title("View All Players")
        menu.geometry("500x500")
        menu.configure(bg=self.colors['bg'])
        menu.transient(self.root)
        menu.grab_set()

        tk.Label(
            menu, text="VIEW ALL PLAYERS", bg=self.colors['bg'],
            fg=self.colors['text'], font=('Arial', 16, 'bold')
        ).pack(pady=16)

        # Rating bands
        bands = [
            ("87–94 OVR", 87, 94),
            ("80–86 OVR", 80, 86),
            ("70–79 OVR", 70, 79),
            ("60–69 OVR", 60, 69),
            ("50–59 OVR", 50, 59)
        ]

        for label, low, high in bands:
            self.create_button(
                menu,
                label,
                lambda lo=low, hi=high, w=menu: [w.destroy(), self.open_player_browser(lo, hi)],
                width=22
            ).pack(pady=6)

        self.create_button(menu, "Return", menu.destroy, width=16).pack(pady=12)

    def open_player_browser(self, low, high):
        # Open the player browser for a given rating band (low - high)
        # Load all players, then filter to the requested band
        try:
            with open("ratings.json", "r") as f:
                all_players = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load ratings.json: {e}")
            return

        self._allplayers_band = [p for p in all_players if low <= int(p.get("rating", 0)) <= high]
        # Active filter sets 
        self._filter_countries = set()
        self._filter_positions = set()

        # Window shell
        win = tk.Toplevel(self.root)
        win.title(f"{low}–{high} OVR Players")
        win.geometry("850x700")
        win.configure(bg=self.colors['bg'])
        win.transient(self.root)
        win.grab_set()

        # Header
        header = tk.Frame(win, bg=self.colors['secondary'])
        header.pack(fill=tk.X)
        tk.Label(
            header, text=f"{low}–{high} OVR PLAYERS", bg=self.colors['secondary'],
            fg=self.colors['text'], font=('Arial', 16, 'bold')
        ).pack(pady=10)

        # Filter bar: Filter by Country / Filter by Position / Clear
        filt = tk.Frame(win, bg=self.colors['bg'])
        filt.pack(fill=tk.X, pady=(12, 0))

        def label_filters():
            c = ", ".join(sorted(self._filter_countries)) or "None"
            p = ", ".join(sorted(self._filter_positions)) or "None"
            return f"Country filters: {c}    |    Position filters: {p}"

        self._filters_var = tk.StringVar(value=label_filters())
        tk.Label(
            filt, textvariable=self._filters_var, bg=self.colors['bg'],
            fg=self.colors['subtext'], font=('Arial', 10)
        ).pack(pady=(0, 8))

        buttons = tk.Frame(filt, bg=self.colors['bg'])
        buttons.pack()
        self.create_button(
            buttons, "Filter by Country",
            lambda: self._toggle_country_filters(self._allplayers_band, win),
            width=20
        ).pack(side=tk.LEFT, padx=6)
        self.create_button(
            buttons, "Filter by Position",
            lambda: self._toggle_position_filters(self._allplayers_band, win),
            width=20
        ).pack(side=tk.LEFT, padx=6)
        self.create_button(
            buttons, "Clear Filters",
            lambda: self._clear_filters(win),
            width=16
        ).pack(side=tk.LEFT, padx=6)

        # Scrollable list container
        list_wrap = tk.Frame(win, bg=self.colors['bg'])
        list_wrap.pack(fill=tk.BOTH, expand=True, pady=12, padx=16)

        canvas = tk.Canvas(list_wrap, bg=self.colors['bg'], highlightthickness=0)
        vbar = tk.Scrollbar(list_wrap, orient=tk.VERTICAL, command=canvas.yview)
        frame = tk.Frame(canvas, bg=self.colors['bg'])

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=vbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Keep handles so we can re-render on filter changes
        win._players_canvas = canvas
        win._players_frame = frame

        # Bottom buttons
        bottom = tk.Frame(win, bg=self.colors['bg'])
        bottom.pack(pady=10)
        self.create_button(bottom, "Return", lambda: [win.destroy(), self.show_all_players()], width=16).pack()

        # Initial render
        self._render_player_list(win)

    def _filtered_players(self):
        # Apply country/position filters to the current rating band
        players = []
        for p in self._allplayers_band:
            ok_country = (not self._filter_countries) or (p.get("country") in self._filter_countries)
            ok_position = (not self._filter_positions) or (p.get("position") in self._filter_positions)
            if ok_country and ok_position:
                players.append(p)
        # Order by rating (descending) then name for a tidy list
        return sorted(players, key=lambda x: (int(x.get("rating", 0)), x.get("name", "")), reverse=True)

    def _render_player_list(self, win):
        # Render the scrollable list of players: rating - position - country - name 
        frame = win._players_frame
        for w in frame.winfo_children():
            w.destroy()

        players = self._filtered_players()

        if not players:
            tk.Label(
                frame, text="No players match the current filters.",
                bg=self.colors['bg'], fg=self.colors['warning'], font=('Arial', 12, 'bold')
            ).pack(pady=20)
            return

        for p in players:
            row = tk.Frame(frame, bg=self.colors['accent'], relief=tk.RAISED, bd=1)
            row.pack(fill=tk.X, padx=8, pady=4)

            # Left side (OVR, position, country)
            left_text = f"{p.get('rating')} OVR - {p.get('position')} - {p.get('country')}"
            right_text = p.get('name', '')
            spaces_needed = 60 - len(left_text) - len(right_text)
            if spaces_needed < 1:
                spaces_needed = 1
            text = left_text + (' ' * spaces_needed) + right_text

            btn = self.create_button(
                row,
                text,
                lambda pl=p, w=win: w._on_pick(pl) if hasattr(w, '_on_pick') else self.show_db_player_details(pl),
                width=70
            )
            btn.config(relief=tk.FLAT, anchor='w', height=1, bg=self.colors['accent'])
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.colors['highlight']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.colors['accent']))
            btn.pack(fill=tk.X, padx=12, pady=6)

        # Hover effect 
        def on_enter(e):
            btn.config(fg='red')

        def on_leave(e):
            btn.config(fg=self.colors['text'])

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _clear_filters(self, win):
        # Clear both filter sets and re-render
        self._filter_countries.clear()
        self._filter_positions.clear()
        self._filters_var.set("Country filters: None    |    Position filters: None")
        self._render_player_list(win)

    def _toggle_country_filters(self, players, parent_win):
        # Toggle country filters (tick to include)
        dlg = tk.Toplevel(parent_win)
        dlg.title("COUNTRY FILTERS (toggle)")
        dlg.geometry("350x460")
        dlg.configure(bg=self.colors['bg'])
        dlg.transient(parent_win)
        dlg.grab_set()

        countries = sorted(set(p.get("country") for p in players))
        vars_map = {}
        box = tk.Frame(dlg, bg=self.colors['bg'])
        box.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        canvas = tk.Canvas(box, bg=self.colors['bg'], highlightthickness=0)
        vbar = tk.Scrollbar(box, orient=tk.VERTICAL, command=canvas.yview)
        inner = tk.Frame(canvas, bg=self.colors['bg'])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        for c in countries:
            v = tk.BooleanVar(value=c in self._filter_countries)
            vars_map[c] = v
            tk.Checkbutton(
                inner, text=c, variable=v,
                bg=self.colors['bg'], fg=self.colors['text'],
                selectcolor=self.colors['secondary'],
                activebackground=self.colors['bg'],
                font=('Arial', 11)
            ).pack(anchor='w', padx=8, pady=2)

        def apply():
            self._filter_countries = {c for c, v in vars_map.items() if v.get()}
            self._filters_var.set(
                f"Country filters: {', '.join(sorted(self._filter_countries)) or 'None'}    |    "
                f"Position filters: {', '.join(sorted(self._filter_positions)) or 'None'}"
            )
            dlg.destroy()
            self._render_player_list(parent_win)

        self.create_button(dlg, "Apply", apply, width=12).pack(pady=6)
        self.create_button(dlg, "Cancel", dlg.destroy, width=12).pack(pady=4)

    def _toggle_position_filters(self, players, parent_win):
        # Toggle position filters in preferred order: GK, LB, CB, RB, CM, LW, RW, ST
        preferred = ["GK", "LB", "CB", "RB", "CM", "LW", "RW", "ST"]
        present = [pos for pos in preferred if any(p.get("position") == pos for p in players)]

        dlg = tk.Toplevel(parent_win)
        dlg.title("POSITION FILTERS (toggle)")
        dlg.geometry("320x420")
        dlg.configure(bg=self.colors['bg'])
        dlg.transient(parent_win)
        dlg.grab_set()

        vars_map = {}
        body = tk.Frame(dlg, bg=self.colors['bg'])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        for pos in present:
            v = tk.BooleanVar(value=pos in self._filter_positions)
            vars_map[pos] = v
            tk.Checkbutton(
                body, text=pos, variable=v,
                bg=self.colors['bg'], fg=self.colors['text'],
                selectcolor=self.colors['secondary'],
                activebackground=self.colors['bg'],
                font=('Arial', 12)
            ).pack(anchor='w', padx=8, pady=3)

        def apply():
            self._filter_positions = {pos for pos, v in vars_map.items() if v.get()}
            self._filters_var.set(
                f"Country filters: {', '.join(sorted(self._filter_countries)) or 'None'}    |    "
                f"Position filters: {', '.join(sorted(self._filter_positions)) or 'None'}"
            )
            dlg.destroy()
            self._render_player_list(parent_win)

        self.create_button(dlg, "Apply", apply, width=12).pack(pady=6)
        self.create_button(dlg, "Cancel", dlg.destroy, width=12).pack(pady=4)
   
    def open_pack(self, cost, weights):
        # Buy and open a pack with a step-by-step reveal
        if self.coins < cost:
            messagebox.showerror("Error", "Not enough coins!")
            return

        self.coins -= cost
        self.write_team_data(str(self.coins), "coins", self.edit)

        # Load player data
        with open("ratings.json", 'r') as f:
            players = json.load(f)

        # Split by rarity based on rating thresholds
        rarity_groups = {
            "common": [], "uncommon": [], "rare": [], "epic": [], "legendary": []
        }
        for p in players:
            r = p["rating"]
            if r <= 64:
                rarity_groups["common"].append(p)
            elif r <= 74:
                rarity_groups["uncommon"].append(p)
            elif r <= 82:
                rarity_groups["rare"].append(p)
            elif r <= 87:
                rarity_groups["epic"].append(p)
            else:
                rarity_groups["legendary"].append(p)

        # Weighted rarity choice
        rarity_pool = []
        for rarity, weight in weights.items():
            rarity_pool.extend([rarity] * weight)

        selected_rarity = random.choice(rarity_pool)
        candidates = rarity_groups[selected_rarity]
        if not candidates:
            messagebox.showerror("Error", f"No players for rarity '{selected_rarity}'")
            return
        selected_player = random.choice(candidates)

        # Run the reveal flow
        self.show_pack_reveal_sequence(selected_player)

    def show_pack_reveal_sequence(self, player):
        # Step-by-step reveal flow with Skip and Continue controls
        dialog = tk.Toplevel(self.root)
        dialog.title("Pack Opening")
        dialog.geometry("520x720")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        # Header
        header = tk.Frame(dialog, bg=self.colors['secondary'], height=56)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="OPENING PACK…", bg=self.colors['secondary'],
            fg=self.colors['text'], font=('Arial', 16, 'bold')
        ).pack(pady=10)

        # Body
        body = tk.Frame(dialog, bg=self.colors['bg'])
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        status_var = tk.StringVar(value="Loading")
        tk.Label(
            body, textvariable=status_var, bg=self.colors['bg'],
            fg=self.colors['subtext'], font=('Arial', 12)
        ).pack(pady=(6, 18))

        # Card frame 
        card_frame = tk.Frame(body, bg=self.colors['accent'], relief=tk.RAISED, bd=5)

        # Footer
        footer = tk.Frame(dialog, bg=self.colors['bg'])
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=8)

        skip_state = {"skipped": False, "finished": False}
        def skip():
            if skip_state["finished"]:
                return
            skip_btn.configure(state=tk.DISABLED, text="Skipping…")
            skip_state["skipped"] = True

        skip_btn = self.create_button(footer, "Skip ▶", skip, width=12)
        skip_btn.pack(pady=(0, 6))

        cont_btn_holder = tk.Frame(footer, bg=self.colors['bg'])
        cont_btn_holder.pack()

        # Choose rarity colour/name
        rating = player.get("rating", 0)
        if rating <= 64:
            rarity_color, rarity_name = self.colors['card_common'], "COMMON"
        elif rating <= 74:
            rarity_color, rarity_name = self.colors['card_uncommon'], "UNCOMMON"
        elif rating <= 82:
            rarity_color, rarity_name = self.colors['card_rare'], "RARE"
        elif rating <= 87:
            rarity_color, rarity_name = self.colors['card_epic'], "EPIC"
        else:
            rarity_color, rarity_name = self.colors['card_legendary'], "LEGENDARY"

        # Read attributes with sensible fallbacks
        def _attr_from_stats(primary_key, *fallback_top_level):
            stats = player.get("stats") or {}
            v = stats.get(primary_key)
            if v not in (None, ""):
                return v
            for k in fallback_top_level:
                v2 = player.get(k)
                if v2 not in (None, ""):
                    return v2
            return "-"

        steps = []

        # Loading dots
        def make_dot_step(i):
            def _s():
                status_var.set("Loading" + "." * (i % 4))
            return _s
        for i in range(12):
            steps.append(make_dot_step(i))

        # Found card
        def found():
            status_var.set("Found a card!")
        steps.append(found)

        # Mount card frame
        def mount_card():
            status_var.set("Revealing…")
            card_frame.configure(bg=rarity_color)
            card_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        steps.append(mount_card)

        # Rarity
        def reveal_rarity():
            tk.Label(card_frame, text=rarity_name, bg=rarity_color,
                     fg=self.colors['text'], font=('Arial', 14, 'bold')).pack(pady=8)
        steps.append(reveal_rarity)

        # OVR
        def reveal_ovr():
            tk.Label(card_frame, text=f"{player.get('rating', 0)} OVR", bg=rarity_color,
                     fg=self.colors['text'], font=('Arial', 28, 'bold')).pack(pady=6)
        steps.append(reveal_ovr)

        # Name
        def reveal_name():
            tk.Label(card_frame, text=player.get('name', 'Unknown'), bg=rarity_color,
                     fg=self.colors['text'], font=('Arial', 18, 'bold')).pack(pady=6)
        steps.append(reveal_name)

        # Position and country
        def reveal_pos_country():
            pos = player.get('position', '?')
            cty = player.get('country', '?')
            tk.Label(card_frame, text=f"{pos} | {cty}", bg=rarity_color,
                     fg=self.colors['text'], font=('Arial', 12)).pack(pady=6)
        steps.append(reveal_pos_country)

        # Attribute lines
        def reveal_attributes():
            attrs = {
                "Pace":      _attr_from_stats("pace", "PAC", "pace", "Pace"),
                "Shooting":  _attr_from_stats("shooting", "SHO", "shooting", "Shooting"),
                "Passing":   _attr_from_stats("passing", "PAS", "passing", "Passing"),
                "Dribbling": _attr_from_stats("dribbling", "DRI", "dribbling", "Dribbling"),
                "Defending": _attr_from_stats("defending", "DEF", "defending", "Defending"),
                "Physical":  _attr_from_stats("physical", "PHY", "physical", "Physical"),
            }
            stats_wrap = tk.Frame(card_frame, bg=rarity_color)
            stats_wrap.pack(pady=(8, 4))
            for label in ["Pace", "Shooting", "Passing", "Dribbling", "Defending", "Physical"]:
                val = attrs[label] if attrs[label] not in (None, "") else "-"
                row = tk.Frame(stats_wrap, bg=rarity_color)
                row.pack(anchor='center')
                tk.Label(row, text=f"{label}: ", bg=rarity_color,
                         fg=self.colors['text'], font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
                tk.Label(row, text=str(val), bg=rarity_color,
                         fg=self.colors['text'], font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        steps.append(reveal_attributes)

        # Inventory handling / duplicate outcome
        def resolve_inventory():
            squad = self.read_team_data("squad", self.edit)
            already_owned = any(p["name"] == player["name"] for p in squad)

            if not already_owned:
                new_player = {
                    "name": player["name"],
                    "country": player["country"],
                    "position": player["position"],
                    "rating": player["rating"],
                    "role": self.role_options[player["position"]][0]
                }
                squad.append(new_player)
                self.write_team_data(squad, "squad", self.edit)
                tk.Label(
                    card_frame, text="✓ NEW PLAYER ADDED!",
                    bg=rarity_color, fg=self.colors['text'],
                    font=('Arial', 14, 'bold')
                ).pack(pady=(12, 6))
            else:
                quicksell_value = self.quick_sell_value(player["rating"])
                self.coins += quicksell_value
                self.write_team_data(str(self.coins), "coins", self.edit)
                tk.Label(
                    card_frame, text="Duplicate card — will be quicksold",
                    bg=rarity_color, fg=self.colors['text'],
                    font=('Arial', 12, 'bold')
                ).pack(pady=(12, 2))
                tk.Label(
                    card_frame, text=f"+{quicksell_value} coins",
                    bg=rarity_color, fg=self.colors['text'],
                    font=('Arial', 14, 'bold')
                ).pack(pady=(0, 8))
        steps.append(resolve_inventory)

        # Continue button and disable Skip
        def show_continue():
            skip_state["finished"] = True
            try:
                skip_btn.configure(state=tk.DISABLED, text="Skip (finished)")
            except Exception:
                pass
            for w in cont_btn_holder.winfo_children():
                w.destroy()
            self.create_button(cont_btn_holder, "Continue", dialog.destroy, width=15).pack()
            status_var.set("Revealed")
        steps.append(show_continue)

        # Run the reveal, supporting Skip
        def run_steps(idx=0):
            if idx >= len(steps):
                return
            if skip_state["skipped"]:
                # If skipped, mount and reveal everything essential at once
                if not card_frame.winfo_manager():
                    mount_card()
                for fn in [reveal_rarity, reveal_ovr, reveal_name,
                           reveal_pos_country, reveal_attributes,
                           resolve_inventory, show_continue]:
                    fn()
                skip_state["skipped"] = False
                return
            steps[idx]()
            dialog.after(self.pack_speed, lambda: run_steps(idx + 1))

        run_steps()
        self.root.wait_window(dialog)
        self.write_team_data(str(self.coins), "coins", self.edit)
        self.show_store_page()

    def show_pack_reveal(self, player):
        # Simpler reveal dialog (alternative to the step-by-step sequence)
        dialog = tk.Toplevel(self.root)
        dialog.title("Pack Opening")
        dialog.geometry("400x500")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Rarity colour and label
        rating = player["rating"]
        if rating <= 64:
            rarity_color = self.colors['card_common']
            rarity_name = "COMMON"
        elif rating <= 74:
            rarity_color = self.colors['card_uncommon']
            rarity_name = "UNCOMMON"
        elif rating <= 82:
            rarity_color = self.colors['card_rare']
            rarity_name = "RARE"
        elif rating <= 87:
            rarity_color = self.colors['card_epic']
            rarity_name = "EPIC"
        else:
            rarity_color = self.colors['card_legendary']
            rarity_name = "LEGENDARY"
        
        # Card frame
        card_frame = tk.Frame(dialog, bg=rarity_color, relief=tk.RAISED, bd=5)
        card_frame.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)
        
        tk.Label(
            card_frame, text=rarity_name, bg=rarity_color,
            fg=self.colors['text'], font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        tk.Label(
            card_frame, text=f"{player['rating']} OVR", bg=rarity_color,
            fg=self.colors['text'], font=('Arial', 24, 'bold')
        ).pack(pady=10)
        
        tk.Label(
            card_frame, text=player['name'], bg=rarity_color,
            fg=self.colors['text'], font=('Arial', 18, 'bold')
        ).pack(pady=10)
        
        tk.Label(
            card_frame, text=f"{player['position']} | {player['country']}",
            bg=rarity_color, fg=self.colors['text'], font=('Arial', 12)
        ).pack(pady=10)
        
        # Own/duplicate handling
        squad = self.read_team_data("squad", self.edit)
        already_owned = any(p["name"] == player["name"] for p in squad)
        
        if not already_owned:
            new_player = {
                "name": player["name"],
                "country": player["country"],
                "position": player["position"],
                "rating": player["rating"],
                "role": self.role_options[player["position"]][0]
            }
            squad.append(new_player)
            self.write_team_data(squad, "squad", self.edit)
            tk.Label(
                card_frame, text="✓ NEW PLAYER ADDED!",
                bg=rarity_color, fg=self.colors['text'], font=('Arial', 14, 'bold')
            ).pack(pady=20)
        else:
            quicksell_value = self.quick_sell_value(player["rating"])
            self.coins += quicksell_value
            self.write_team_data(str(self.coins), "coins", self.edit)
            tk.Label(
                card_frame, text="Already Owned - Quicksold",
                bg=rarity_color, fg=self.colors['warning'], font=('Arial', 12, 'bold')
            ).pack(pady=10)
            tk.Label(
                card_frame, text=f"+{quicksell_value} coins",
                bg=rarity_color, fg=self.colors['text'], font=('Arial', 14, 'bold')
            ).pack(pady=5)
        
        self.create_button(dialog, "Continue", dialog.destroy, width=15).pack(pady=20)
        self.root.wait_window(dialog)
        self.show_store_page()
    
    # Formation pitch rendering helpers
    def _row_x_positions(self, n):
        # Evenly space n items across 0 - 1 (exclusive of edges)
        if n <= 0:
            return []
        step = 1.0 / (n + 1)
        return [(i + 1) * step for i in range(n)]

    def _layout_from_formation(self, formation):
        # Compute a list of rows from top (forwards) to bottom (GK),
        # each row is a list of (x_norm, y_norm). Supports common shapes.
        W = lambda n: self._row_x_positions(n)
        rows = []
        f = formation.strip()
        if f in ("4-4-2", "4-3-3", "4-5-1", "5-3-2", "5-2-3", "5-4-1"):
            d, m, a = [int(x) for x in f.split("-")]
            rows = [W(a), W(m), W(d)]
            rows.append([0.5])  # GK row
        elif f == "4-2-2-2":
            rows = [W(2), W(2), W(2), W(4), [0.5]]
        else:
            # Generic parse
            parts = [int(x) for x in f.split("-") if x.isdigit()]
            rows = [W(parts[-1])] + [W(p) for p in parts[-2::-1]] + [[0.5]]

        # Map rows to y bands (top to bottom)
        band = {0: 0.12, 1: 0.30, 2: 0.52, 3: 0.74, 4: 0.90}
        coords = []
        for r, xs in enumerate(rows):
            y = band[min(r, 4)]
            coords.extend([(x, y) for x in xs])
        return coords  # forwards … defenders … GK

    def _compute_edges(self, coords):
        # Build simple chemistry edges: neighbours in the same row and nearest in adjacent rows
        from collections import defaultdict
        rows = defaultdict(list)
        for i, (x, y) in enumerate(coords):
            rows[round(y, 2)].append(i)
        y_keys = sorted(rows.keys())

        edges = set()

        # Same-row neighbours
        for k in y_keys:
            row = rows[k]
            row_sorted = sorted(row, key=lambda i: coords[i][0])
            for a, b in zip(row_sorted, row_sorted[1:]):
                edges.add(tuple(sorted((a, b))))

        # Cross-row nearest connections
        for a_idx, (ax, ay) in enumerate(coords):
            above = [k for k in y_keys if k < round(ay, 2)]
            below = [k for k in y_keys if k > round(ay, 2)]
            if above:
                r = rows[above[-1]]
                b_idx = min(r, key=lambda j: abs(coords[j][0] - ax))
                edges.add(tuple(sorted((a_idx, b_idx))))
            if below:
                r = rows[below[0]]
                b_idx = min(r, key=lambda j: abs(coords[j][0] - ax))
                edges.add(tuple(sorted((a_idx, b_idx))))

        return sorted(edges)

    def _draw_team_on_pitch(self, canvas, squad, formation, player_slots, player_links, width, height, on_click_player=None):
        # Draw the pitch, chemistry lines, and player cards for the starting XI
        pad = 30
        W, H = width - 2 * pad, height - 2 * pad

        # Pitch background
        canvas.create_rectangle(
            pad, pad, pad + W, pad + H,
            outline="#0b5136",
            fill="#0b3d2f",
            tags=("pitch",)
        )
        canvas.create_line(
            pad, pad + H / 2, pad + W, pad + H / 2,
            fill="#1aa36b",
            width=2,
            tags=("pitch",)
        )
        canvas.create_oval(
            pad + W / 2 - 12, pad + H / 2 - 12,
            pad + W / 2 + 12, pad + H / 2 + 12,
            outline="#1aa36b",
            width=2,
            tags=("pitch",)
        )
        canvas.tag_lower("pitch")

        # Slot coordinates for formation
        coords = self._coords_in_slot_order(formation, player_slots)

        # Links from formation (slots 1 - 11 to neighbours)
        edges = sorted({tuple(sorted((a - 1, b - 1)))
                        for a, nbrs in player_links.items()
                        for b in nbrs
                        if 0 <= a - 1 < 11 and 0 <= b - 1 < 11})

        # Build XI list from squad, filling missing slots
        xi = []
        for i in range(1, 12):
            slot_pos = player_slots[i]["position"]
            pl = squad[i - 1] if i - 1 < len(squad) else {
                "name": "[Empty]", "country": "", "rating": 0, "position": slot_pos
            }
            xi.append(pl)

        # Chemistry lines (green if same country, red otherwise)
        def same_country(i, j):
            a, b = xi[i], xi[j]
            return a.get("country") and a.get("country") == b.get("country")

        card_w, card_h = 120, 70
        half_w, half_h = card_w / 2.0, card_h / 2.0
        margin = 5
        min_gap_each_end = 6

        for i, j in edges:
            (x1n, y1n), (x2n, y2n) = coords[i], coords[j]
            x1c, y1c = pad + x1n * W, pad + y1n * H
            x2c, y2c = pad + x2n * W, pad + y2n * H

            dx, dy = (x2c - x1c), (y2c - y1c)
            L = max((dx ** 2 + dy ** 2) ** 0.5, 1e-6)
            ux, uy = dx / L, dy / L

            proj_half = abs(ux) * half_w + abs(uy) * half_h
            trim_req = proj_half + margin
            trim_cap = max(0.0, (L / 2.0) - min_gap_each_end)
            trim = min(trim_req, trim_cap)
            if trim < 0:
                trim = 0

            x1 = x1c + ux * trim
            y1 = y1c + uy * trim
            x2 = x2c - ux * trim
            y2 = y2c - uy * trim

            color = self.colors['success'] if same_country(i, j) else self.colors['highlight']
            canvas.create_line(x1, y1, x2, y2, width=3, fill=color, capstyle=tk.ROUND, tags=("chem",))

        # Player cards and hover/click behaviour
        for i, ((xn, yn), pl) in enumerate(zip(coords, xi)):
            cx, cy = pad + xn * W, pad + yn * H
            x0, y0 = cx - card_w / 2, cy - card_h / 2
            x1, y1 = cx + card_w / 2, cy + card_h / 2
            tag = f"card{i}"
            bg_tag = f"{tag}_bg"

            slot_pos = player_slots[i + 1]["position"]
            natural_pos = pl.get("position", slot_pos)
            out_of_pos = (pl.get("name") not in (None, "[Empty]")) and (natural_pos != slot_pos)

            outline_colour = self.colors["warning"] if out_of_pos else self.colors["text"]

            canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=self.colors["accent"],
                outline=outline_colour,
                tags=(bg_tag, tag, "card")
            )

            top_line = f"{slot_pos} • {pl.get('rating', 0)} OVR"
            canvas.create_text(
                cx, y0 + 16,
                text=top_line,
                fill=self.colors["success"],
                font=('Arial', 10, 'bold'),
                tags=(tag, "card")
            )

            if out_of_pos:
                canvas.create_text(
                    cx + 50, y0 + 16,
                    text="!",
                    fill="#ffeb3b",
                    font=('Arial', 12, 'bold'),
                    tags=(tag, "card")
                )

            canvas.create_text(
                cx, y0 + 34,
                text=pl.get("name", "[Empty]"),
                fill=self.colors["text"],
                font=('Arial', 11, 'bold'),
                tags=(tag, "card")
            )

            canvas.create_text(
                cx, y0 + 52,
                text=pl.get("country", ""),
                fill=self.colors["subtext"],
                font=('Arial', 9),
                tags=(tag, "card")
            )

            if pl.get("name") and pl.get("name") != "[Empty]":
                def open_details(p=pl, idx=i + 1, sp=slot_pos):
                    return lambda e: (
                        on_click_player(p, idx)
                        if on_click_player
                        else self.show_player_details(p, idx, sp)
                    )
                canvas.tag_bind(tag, "<Button-1>", open_details())

                def _enter(e, bt=bg_tag):
                    canvas.itemconfigure(bt, fill=self.colors['highlight'])
                    canvas.config(cursor="hand2")

                def _leave(e, bt=bg_tag):
                    canvas.itemconfigure(bt, fill=self.colors['accent'])
                    canvas.config(cursor="")

                canvas.tag_bind(tag, "<Enter>", _enter)
                canvas.tag_bind(tag, "<Leave>", _leave)

        # Ensure lines are below cards but above the pitch
        canvas.tag_raise("chem", "pitch")
        canvas.tag_raise("card", "chem")

    def _draw_team_on_pitch_match_view(self, canvas, squad, formation, player_slots, player_links, width, height):
        # Same pitch + chemistry lines as _draw_team_on_pitch, but cards show Name + OVR + Match rating
        pad = 30
        W, H = width - 2 * pad, height - 2 * pad

        # Pitch
        canvas.create_rectangle(pad, pad, pad + W, pad + H, outline="#0b5136", fill="#0b3d2f", tags=("pitch",))
        canvas.create_line(pad, pad + H / 2, pad + W, pad + H / 2, fill="#1aa36b", width=2, tags=("pitch",))
        canvas.create_oval(
            pad + W / 2 - 12, pad + H / 2 - 12,
            pad + W / 2 + 12, pad + H / 2 + 12,
            outline="#1aa36b", width=2, tags=("pitch",)
        )
        canvas.tag_lower("pitch")

        # Slot coords in XI order
        coords = self._coords_in_slot_order(formation, player_slots)

        # Links from formation (1 - 11 neighbours) - keep chemistry lines
        edges = sorted({tuple(sorted((a - 1, b - 1)))
                        for a, nbrs in player_links.items()
                        for b in nbrs
                        if 0 <= a - 1 < 11 and 0 <= b - 1 < 11})

        # Build XI list (fill empties if needed)
        xi = []
        for i in range(1, 12):
            slot_pos = player_slots[i]["position"]
            pl = squad[i - 1] if i - 1 < len(squad) else {"name": "[Empty]", "position": slot_pos, "rating": 0}
            xi.append(pl)

        def same_country(i, j):
            a, b = xi[i], xi[j]
            return a.get("country") and a.get("country") == b.get("country")

        # Draw chemistry lines
        card_w, card_h = 120, 70
        half_w, half_h = card_w / 2.0, card_h / 2.0
        margin = 5
        min_gap_each_end = 6
        for i, j in edges:
            (x1n, y1n), (x2n, y2n) = coords[i], coords[j]
            x1c, y1c = pad + x1n * W, pad + y1n * H
            x2c, y2c = pad + x2n * W, pad + y2n * H
            dx, dy = (x2c - x1c), (y2c - y1c)
            L = max((dx ** 2 + dy ** 2) ** 0.5, 1e-6)
            ux, uy = dx / L, dy / L
            proj_half = abs(ux) * half_w + abs(uy) * half_h
            trim_req = proj_half + margin
            trim_cap = max(0.0, (L / 2.0) - min_gap_each_end)
            trim = min(trim_req, trim_cap)
            x1 = x1c + ux * trim
            y1 = y1c + uy * trim
            x2 = x2c - ux * trim
            y2 = y2c - uy * trim
            color = self.colors['success'] if same_country(i, j) else self.colors['highlight']
            canvas.create_line(x1, y1, x2, y2, width=3, fill=color, capstyle=tk.ROUND, tags=("chem",))

        # Cards: Name + OVR + Match rating 
        for (xn, yn), pl in zip(coords, xi):
            cx, cy = pad + xn * W, pad + yn * H
            x0, y0 = cx - card_w / 2, cy - card_h / 2
            x1, y1 = cx + card_w / 2, cy + card_h / 2

            canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=self.colors["accent"],
                outline=self.colors["text"],
                tags=("card",)
            )

            key = pl.get("_match_key", pl.get("name", "[Empty]"))  
            name = pl.get("display", pl.get("name", "[Empty]"))    
            ovr = int(pl.get("rating", 0))
            mr = float(self.match_ratings.get(key, 6.6))

            goals = 0
            assists = 0
            if hasattr(self, "last_goal_counts"):
                goals = int(self.last_goal_counts.get(key, 0))
            if hasattr(self, "last_assist_counts"):
                assists = int(self.last_assist_counts.get(key, 0))

            icons = ""
            if goals > 0:
                icons += " " + ("⚽" * goals)      # goal icons
            if assists > 0:
                icons += " " + ("🅰" * assists)    # assist icons

            rating_text = f"{ovr} OVR  •  {mr:.1f}/10"
            icons_text = f"{icons}"

            canvas.create_text(
                cx, y0 + 22,
                text=name,
                fill=self.colors["text"],
                font=("Arial", 11, "bold"),
                tags=("card",)
            )
            canvas.create_text(
                cx, y0 + 46,
                text=rating_text,
                fill=self.colors["success"],
                font=("Arial", 10, "bold"),
                tags=("card",)
            )
            canvas.create_text(
                cx, y0 + 60,
                text=icons_text,
                fill=self.colors["success"],
                font=("Arial", 9, "bold"),
                tags=("card",)
            )

    def _coords_in_slot_order(self, formation, player_slots):
        # Return 11 (x, y) coords aligned to player_slots[1 - 11] for a given formation
        def even_row(n):
            if n <= 0:
                return []
            step = 1.0 / (n + 1)
            return [(i + 1) * step for i in range(n)]

        f = formation.strip()

        # Base y bands (top -> bottom)
        y_att_hi  = 0.20
        y_mid_hi  = 0.38
        y_mid_low = 0.48
        y_def     = 0.70
        y_gk      = 0.90
        xs_def = [0.18, 0.36, 0.64, 0.82]

        # Per-formation coordinates keyed by position label
        if f == "4-4-2":
            xs_st  = [0.40, 0.60]
            xs_mid = [0.20, 0.40, 0.60, 0.80]
            xs_def = [0.18, 0.36, 0.64, 0.82]

            y_st  = 0.18
            y_mid = 0.42
            y_def = 0.68
            y_gk  = 0.90

            pos_coords = {
                "GK": [(0.50, y_gk)],
                "LB": [(xs_def[0], y_def)],
                "CB": [(xs_def[1], y_def), (xs_def[2], y_def)],
                "RB": [(xs_def[3], y_def)],
                "LM": [(xs_mid[0], y_mid)],
                "CM": [(xs_mid[1], y_mid), (xs_mid[2], y_mid)],
                "RM": [(xs_mid[3], y_mid)],
                "LW": [(xs_mid[0], y_mid)],
                "RW": [(xs_mid[3], y_mid)],
                "ST": [(x, y_st) for x in xs_st],
            }

        elif f == "4-3-3":
            xs_att = [0.25, 0.50, 0.75]
            x_lcm, x_rcm, x_cdm = 0.35, 0.65, 0.50
            xs_def = [0.18, 0.36, 0.64, 0.82]

            pos_coords = {
                "GK": [(0.50, y_gk)],
                "LB": [(xs_def[0], y_def)],
                "CB": [(xs_def[1], y_def), (xs_def[2], y_def)],
                "RB": [(xs_def[3], y_def)],
                "CDM": [(x_cdm, y_mid_low)],
                "DM":  [(x_cdm, y_mid_low)],
                "CM":  [(x_lcm, y_mid_hi), (x_cdm, y_mid_low), (x_rcm, y_mid_hi)],
                "CAM": [(x_cdm, y_mid_low)],
                "LW": [(xs_att[0], y_att_hi)],
                "ST": [(xs_att[1], y_att_hi)],
                "RW": [(xs_att[2], y_att_hi)],
            }

        elif f == "4-5-1":
            xs_mid5 = even_row(5)
            xs_def  = [0.18, 0.36, 0.64, 0.82]
            x_st    = 0.50

            y_att_hi  = 0.22
            y_mid_hi  = 0.42
            y_def     = 0.70
            y_gk      = 0.90

            pos_coords = {
                "GK": [(0.50, y_gk)],
                "LB": [(xs_def[0], y_def)],
                "CB": [(xs_def[1], y_def), (xs_def[2], y_def)],
                "RB": [(xs_def[3], y_def)],
                "LW": [(xs_mid5[0], y_mid_hi)],
                "CM": [(xs_mid5[1], y_mid_hi), (xs_mid5[2], y_mid_hi), (xs_mid5[3], y_mid_hi)],
                "RW": [(xs_mid5[4], y_mid_hi)],
                "ST": [(x_st, y_att_hi)],
            }

        elif f == "4-2-2-2":
            x_lb, x_lcb, x_rcb, x_rb = 0.18, 0.40, 0.60, 0.82
            xs_def = [x_lb, x_lcb, x_rcb, x_rb]
            x_col_l, x_col_r = x_lcb, x_rcb

            y_st  = 0.08
            y_am  = 0.28
            y_dm  = 0.52
            y_def = 0.76
            y_gk  = 0.94

            pos_coords = {
                "GK": [(0.50, y_gk)],
                "LB": [(x_lb,  y_def)],
                "CB": [(x_lcb, y_def), (x_rcb, y_def)],
                "RB": [(x_rb,  y_def)],
                "CM": [(x_col_l, y_dm), (x_col_r, y_dm),
                       (x_col_l, y_am), (x_col_r, y_am)],
                "ST": [(x_col_l, y_st), (x_col_r, y_st)],
            }

        elif f == "5-3-2":
            xs_def5 = [0.14, 0.32, 0.50, 0.68, 0.86]
            xs_mid3 = [0.34, 0.50, 0.66]
            xs_st2  = [0.42, 0.58]

            y_st  = 0.18
            y_mid = 0.40
            y_def = 0.66
            y_gk  = 0.90

            pos_coords = {
                "GK": [(0.50, y_gk)],
                "LB": [(xs_def5[0], y_def)],
                "CB": [(xs_def5[1], y_def), (xs_def5[2], y_def), (xs_def5[3], y_def)],
                "RB": [(xs_def5[4], y_def)],
                "CM": [(xs_mid3[0], y_mid), (xs_mid3[1], y_mid), (xs_mid3[2], y_mid)],
                "ST": [(xs_st2[0], y_st), (xs_st2[1], y_st)],
            }

        elif f == "5-2-3":
            xs_def5   = [0.12, 0.30, 0.50, 0.70, 0.88]
            xs_front3 = [0.30, 0.50, 0.70]
            xs_mid2   = [0.42, 0.58]

            y_front = 0.18
            y_mid   = 0.42
            y_def   = 0.70
            y_gk    = 0.92

            pos_coords = {
                "GK": [(0.50, y_gk)],
                "LB": [(xs_def5[0], y_def)],
                "CB": [(xs_def5[1], y_def), (xs_def5[2], y_def), (xs_def5[3], y_def)],
                "RB": [(xs_def5[4], y_def)],
                "CM": [(xs_mid2[0], y_mid), (xs_mid2[1], y_mid)],
                "LW": [(xs_front3[0], y_front)],
                "ST": [(xs_front3[1], y_front)],
                "RW": [(xs_front3[2], y_front)],
            }

        elif f == "5-4-1":
            xs_def5 = [0.12, 0.30, 0.50, 0.70, 0.88]
            xs_mid4 = [0.22, 0.42, 0.58, 0.78]
            x_st    = 0.50

            y_st  = 0.16
            y_mid = 0.40
            y_def = 0.70
            y_gk  = 0.92

            pos_coords = {
                "GK": [(0.50, y_gk)],
                "LB": [(xs_def5[0], y_def)],
                "CB": [(xs_def5[1], y_def), (xs_def5[2], y_def), (xs_def5[3], y_def)],
                "RB": [(xs_def5[4], y_def)],
                "LW": [(xs_mid4[0], y_mid)],
                "CM": [(xs_mid4[1], y_mid), (xs_mid4[2], y_mid)],
                "RW": [(xs_mid4[3], y_mid)],
                "ST": [(x_st, y_st)],
            }

        else:
            # Generic: parse d-m-a
            try:
                d, m, a = [int(x) for x in f.split("-")]
            except Exception:
                d, m, a = 4, 4, 2
            xs_att = even_row(a)
            xs_mid = even_row(m)
            xs_def = even_row(d)

            pos_coords = {
                "GK": [(0.50, y_gk)],
                "LB": [(xs_def[0], y_def)] if len(xs_def) >= 1 else [],
                "CB": ([(xs_def[1], y_def)] if len(xs_def) >= 2 else []) +
                      ([(xs_def[2], y_def)] if len(xs_def) >= 3 else []),
                "RB": [(xs_def[3], y_def)] if len(xs_def) >= 4 else [],
                "LM": [(xs_mid[0], y_mid_hi)] if len(xs_mid) >= 1 else [],
                "CM": ([(xs_mid[1], y_mid_hi)] if len(xs_mid) >= 2 else []) +
                      ([(xs_mid[2], y_mid_hi)] if len(xs_mid) >= 3 else []),
                "RM": [(xs_mid[3], y_mid_hi)] if len(xs_mid) >= 4 else [],
                "LW": [(xs_att[0], y_att_hi)] if len(xs_att) >= 1 else [],
                "ST": ([(xs_att[1], y_att_hi)] if len(xs_att) >= 2 else []) +
                      ([(xs_att[2], y_att_hi)] if len(xs_att) >= 3 else []),
                "RW": [(xs_att[3], y_att_hi)] if len(xs_att) >= 4 else [],
            }

        # Fallback pools by row when a position queue is empty
        row_pool = {
            "DEF": [(x, y_def) for x in xs_def],
            "MID": [(0.35, y_mid_hi), (0.50, y_mid_low), (0.65, y_mid_hi)],
            "ATT": ([(0.44, y_att_hi), (0.56, y_att_hi)]
                    if f == "4-4-2"
                    else [(0.25, y_att_hi), (0.50, y_att_hi), (0.75, y_att_hi)]),
            "GK1": [(0.50, y_gk)],
        }

        def row_of(pos):
            if pos in ("GK",): return "GK1"
            if pos in ("LB", "CB", "RB"): return "DEF"
            if pos in ("LM", "CM", "RM", "CDM", "DM", "CAM", "LW", "RW"): return "MID"
            if pos in ("ST",): return "ATT"
            return "MID"

        used = set()
        def take_from(queue, fallback_key):
            while queue:
                c = queue.pop(0)
                if c not in used:
                    used.add(c)
                    return c
            for c in row_pool.get(fallback_key, []):
                if c not in used:
                    used.add(c)
                    return c
            c = (0.5, 0.5)
            used.add(c)
            return c

        coords_in_order = []
        for idx in range(1, 12):
            pos = player_slots[idx]["position"]
            q = list(pos_coords.get(pos, []))
            coords_in_order.append(take_from(q, row_of(pos)))

        return coords_in_order

    # Show the team management page
    def show_squad_page(self):
        # Clear the window and draw the Team Management screen
        self.clear_window()
        
        # Header bar
        header = tk.Frame(self.root, bg=self.colors['secondary'], height=60)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="TEAM MANAGEMENT",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 20, 'bold')
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        coins_label = tk.Label(
            header,
            text=f"💰 {self.coins} coins",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        )
        coins_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Team stats (rating + chemistry)
        squad = self.read_team_data("squad", self.edit)
        team_rating = self.team_rating()
        team_chem = self.team_chemistry()
        
        stats_frame = tk.Frame(self.root, bg=self.colors['bg'])
        stats_frame.pack(pady=15)
        
        tk.Label(
            stats_frame,
            text=f"Team Rating: {team_rating} OVR  |  Team Chemistry: {team_chem}/100",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        ).pack()
        
        # Manager label (above the pitch)
        mgr_text = ""
        try:
            nm = self.read_team_data("manager", self.edit)
            ct = self.read_team_data("manager country", self.edit)
            if nm:
                mgr_text = f"Manager: {nm}" + (f" ({ct})" if ct else "")
        except Exception:
            pass
        if not mgr_text:
            mgr_text = "Manager: Unknown"

        tk.Label(
            stats_frame,
            text=mgr_text,
            bg=self.colors['bg'],
            fg=self.colors['subtext'],
            font=('Arial', 12, 'bold')
        ).pack(pady=(6, 0))

        # Formation and squad display
        formation = self.read_team_data("formation", self.edit)
        player_slots, player_links = self.formation_switch(formation)

        # Wrapper for the pitch canvas
        pitch_wrap = tk.Frame(self.root, bg=self.colors['bg'])
        pitch_wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        pitch = tk.Canvas(pitch_wrap, bg=self.colors['bg'], highlightthickness=0)
        pitch.pack(fill=tk.BOTH, expand=True)

        # Draw formation when first shown and on resize
        def _draw_now(event=None):
            pitch.delete("all")
            squad = self.read_team_data("squad", self.edit)
            w = pitch.winfo_width() or 1000
            h = pitch.winfo_height() or 600
            self._draw_team_on_pitch(pitch, squad, formation, player_slots, player_links, w, h)

        pitch.bind("<Configure>", _draw_now)
        
        # Bottom buttons 
        bottom_frame = tk.Frame(self.root, bg=self.colors['bg'])
        bottom_frame.pack(pady=12)

        row = tk.Frame(bottom_frame, bg=self.colors['bg'])
        row.pack()  

        # Actions
        self.create_button(row, "Change Formation", self.show_formation_menu).pack(side=tk.LEFT, padx=8)
        self.create_button(row, "Change Tactics", self.show_tactics_menu).pack(side=tk.LEFT, padx=8)
        self.create_button(row, "View All Owned Players", self.show_all_owned_players).pack(side=tk.LEFT, padx=8)
        if self.tm_return_to == "play":
            self.create_button(row, "Return", self.show_play_page).pack(side=tk.LEFT, padx=8)
        else:
            target = self.show_play_page if getattr(self, "tm_return_to", "home") == "play" else self.show_home_page
            self.create_button(row, "Return", target).pack(side=tk.LEFT, padx=8)

    # Show detailed player information (owned player)
    def show_player_details(self, player, index_in_xi, slot_pos):
        # Open a details window for the selected player from your XI
        dialog = tk.Toplevel(self.root)
        dialog.title("Player Details")
        dialog.geometry("450x800")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Player card
        info_frame = tk.Frame(dialog, bg=self.colors['accent'], relief=tk.RAISED, bd=3)
        info_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(
            info_frame,
            text=player['name'],
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 18, 'bold')
        ).pack(pady=10)
        
        tk.Label(
            info_frame,
            text=f"{player['rating']} OVR",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 16, 'bold')
        ).pack(pady=5)
        
        tk.Label(
            info_frame,
            text=f"{player['position']} | {player['country']}",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 12)
        ).pack(pady=5)
        
        role = player.get('role', 'No role assigned')
        tk.Label(
            info_frame,
            text=f"Role: {role}",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 11)
        ).pack(pady=5)
        
        # Chemistry for this player (from core.chemistry)
        chem, final_rating = self.chemistry(player["name"])
        tk.Label(
            info_frame,
            text=f"Chemistry: {chem}/10",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 11, 'bold')
        ).pack(pady=10)
        
        # Stats block (looked up from ratings.json)
        try:
            with open("ratings.json", 'r') as f:
                ratings_data = json.load(f)
            
            full_player = next((p for p in ratings_data if p["name"] == player["name"]), None)
            
            if full_player and "stats" in full_player:
                tk.Label(
                    info_frame,
                    text="Attributes:",
                    bg=self.colors['accent'],
                    fg=self.colors['text'],
                    font=('Arial', 12, 'bold')
                ).pack(pady=10)
                
                stats_frame = tk.Frame(info_frame, bg=self.colors['accent'])
                stats_frame.pack(pady=5)
                
                for stat, value in full_player["stats"].items():
                    stat_row = tk.Frame(stats_frame, bg=self.colors['accent'])
                    stat_row.pack(anchor='center', pady=2)
                    
                    tk.Label(
                        stat_row,
                        text=f"{stat.capitalize()}:",
                        bg=self.colors['accent'],
                        fg=self.colors['text'],
                        font=('Arial', 10),
                        width=12,
                        anchor='w'
                    ).pack(side=tk.LEFT)
                    
                    tk.Label(
                        stat_row,
                        text=str(value),
                        bg=self.colors['accent'],
                        fg=self.colors['text'],
                        font=('Arial', 10, 'bold'),
                        width=5,
                        anchor='e'
                    ).pack(side=tk.RIGHT)
        except:
            pass
        
        # Actions for owned player
        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(pady=10)
        
        quicksell_value = self.quick_sell_value(player['rating'])
        self.create_button(
            button_frame,
            f"Quicksell ({quicksell_value} coins)",
            lambda: self.quicksell_player(player, dialog),
            width=20
        ).pack(pady=5)
        
        self.create_button(
            button_frame,
            "Change Role",
            lambda: self.show_role_menu(player, index_in_xi, dialog, slot_pos),
            width=20
        ).pack(pady=5)
        
        self.create_button(
            button_frame,
            "Swap Player",
            lambda: self.show_swap_menu(player, index_in_xi, dialog),
            width=20
        ).pack(pady=5)
        
        self.create_button(button_frame, "Close", dialog.destroy, width=15).pack(pady=5)
    
    # Show opponent player details (read-only, same visual style as Team Management)
    def show_opponent_player_details(self, player, index_in_xi):
        # Read-only details for an opponent’s player from the match screen
        dialog = tk.Toplevel(self.root)
        dialog.title(player.get("name", "Player Details"))
        dialog.geometry("480x650")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        # Header bar
        header = tk.Frame(dialog, bg=self.colors['secondary'])
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text=player.get("name", "Player"),
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 18, 'bold')
        ).pack(pady=10)

        # Card area
        card = tk.Frame(dialog, bg=self.colors['accent'], relief=tk.RAISED, bd=3)
        card.pack(pady=15, padx=20, fill=tk.BOTH, expand=False)

        # OVR + info
        tk.Label(
            card,
            text=f"{player['rating']} OVR",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 16, 'bold')
        ).pack(pady=5)

        tk.Label(
            card,
            text=f"{player['position']} | {player['country']}",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 12)
        ).pack(pady=3)

        tk.Label(
            card,
            text=f"Role: {player.get('role', 'No role assigned')}",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 12)
        ).pack(pady=3)

        # Chemistry for the opponent’s player
        chem, _ = self.chemistry(player["name"], opponent=True)
        tk.Label(
            card,
            text=f"Chemistry: {chem}/10",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 12, 'bold')
        ).pack(pady=10)

        # Stats (same style as Team Management)
        tk.Label(
            card,
            text="Attributes:",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 12, 'bold')
        ).pack(pady=(8, 4))

        stats_frame = tk.Frame(card, bg=self.colors['accent'])
        stats_frame.pack(pady=5)
        
        # Load stats for this player (if present in ratings.json)
        try:
            with open("ratings.json", "r") as f:
                all_players = json.load(f)
            stats = next(
                (p.get("stats", {}) for p in all_players if p.get("name") == player.get("name")),
                {}
            )
        except Exception:
            stats = {}

        # Two-column aligned layout: name (left) / value (right)
        rows = [("Pace", "pace"), ("Shooting", "shooting"), ("Passing", "passing"),
                ("Dribbling", "dribbling"), ("Defending", "defending"), ("Physical", "physical")]

        for r, (label_txt, key) in enumerate(rows):
            name_label = tk.Label(
                stats_frame,
                text=f"{label_txt}:",
                bg=self.colors['accent'],
                fg=self.colors['text'],
                font=('Arial', 12),
                width=12,
                anchor="w"
            )
            name_label.grid(row=r, column=0, padx=(20, 10), pady=2)

            value_label = tk.Label(
                stats_frame,
                text=str(stats.get(key, "-")),
                bg=self.colors['accent'],
                fg=self.colors['text'],
                font=('Arial', 12, 'bold'),
                width=5,
                anchor="e"
            )
            value_label.grid(row=r, column=1, padx=(0, 20), pady=2)

        # Close button
        bottom = tk.Frame(dialog, bg=self.colors['bg'])
        bottom.pack(pady=20)
        self.create_button(bottom, "Close", dialog.destroy, width=14).pack()
    
    # Show read-only details for any database player (ratings.json)
    def show_db_player_details(self, player):
        # Read-only details pop-up for a player from ratings.json (not necessarily owned)
        dialog = tk.Toplevel(self.root)
        dialog.title(player.get("name", "Player Details"))
        dialog.geometry("480x650")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        # Header
        header = tk.Frame(dialog, bg=self.colors['secondary'])
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text=player.get("name", "Player"),
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 18, 'bold')
        ).pack(pady=10)

        # Rarity colour 
        rating = int(player.get("rating", 0))
        if rating <= 64:
            rarity_color = self.colors['card_common']; rarity_name = "COMMON"
        elif rating <= 74:
            rarity_color = self.colors['card_uncommon']; rarity_name = "UNCOMMON"
        elif rating <= 82:
            rarity_color = self.colors['card_rare']; rarity_name = "RARE"
        elif rating <= 87:
            rarity_color = self.colors['card_epic']; rarity_name = "EPIC"
        else:
            rarity_color = self.colors['card_legendary']; rarity_name = "LEGENDARY"

        # Player card
        card = tk.Frame(dialog, bg=rarity_color, relief=tk.RAISED, bd=3)
        card.pack(pady=15, padx=20, fill=tk.BOTH, expand=False)

        tk.Label(card, text=rarity_name, bg=rarity_color, fg=self.colors['text'],
                 font=('Arial', 12, 'bold')).pack(pady=(10, 4))
        tk.Label(card, text=f"{rating} OVR", bg=rarity_color, fg=self.colors['text'],
                 font=('Arial', 20, 'bold')).pack(pady=4)
        tk.Label(card, text=f"{player.get('position','?')} | {player.get('country','?')}",
                 bg=rarity_color, fg=self.colors['text'], font=('Arial', 12)).pack(pady=(0, 10))

        # Attributes (pulled from the player object, or looked up by name if missing)
        tk.Label(card, text="Attributes:", bg=rarity_color, fg=self.colors['text'],
                 font=('Arial', 12, 'bold')).pack(pady=(4, 2))
        stats_frame = tk.Frame(card, bg=rarity_color)
        stats_frame.pack(pady=6)

        stats = player.get("stats", {})
        if not stats:
            try:
                with open("ratings.json", "r") as f:
                    all_players = json.load(f)
                match = next((p for p in all_players if p.get("name") == player.get("name")), None)
                if match:
                    stats = match.get("stats", {})
            except Exception:
                stats = {}

        rows = [("Pace", "pace"), ("Shooting", "shooting"), ("Passing", "passing"),
                ("Dribbling", "dribbling"), ("Defending", "defending"), ("Physical", "physical")]
        for r, (label_txt, key) in enumerate(rows):
            tk.Label(stats_frame, text=f"{label_txt}:", bg=rarity_color, fg=self.colors['text'],
                     font=('Arial', 12), width=12, anchor="w").grid(row=r, column=0, padx=(20, 10), pady=2)
            tk.Label(stats_frame, text=str(stats.get(key, "-")), bg=rarity_color, fg=self.colors['text'],
                     font=('Arial', 12, 'bold'), width=5, anchor="e").grid(row=r, column=1, padx=(0, 20), pady=2)

        # Close action
        bottom = tk.Frame(dialog, bg=self.colors['bg'])
        bottom.pack(pady=16)
        self.create_button(bottom, "Close", dialog.destroy, width=14).pack()
    
    # Role change menu for an owned player
    def show_role_menu(self, player, index_in_xi, parent_dialog, slot_pos):
        # Close the parent details window and open a role picker for this player
        parent_dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Role")
        dialog.geometry("400x500")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text=f"Change Role for {player['name']}",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        ).pack(pady=20)
        
        pos = slot_pos
        role_options = core.role_options.get(pos, [])
        
        if not role_options:
            tk.Label(
                dialog,
                text="No roles available for this position",
                bg=self.colors['bg'],
                fg=self.colors['warning'],
                font=('Arial', 12)
            ).pack(pady=20)
            self.create_button(dialog, "Return", lambda: [dialog.destroy(), self.show_squad_page()]).pack(pady=20)
            return
        
        # List all roles for the player’s position
        for role in role_options:
            btn = tk.Button(
                dialog,
                text=role,
                command=lambda r=role: self.apply_role_change(player, index_in_xi, r, dialog),
                bg=self.colors['accent'],
                fg=self.colors['text'],
                font=('Arial', 10),
                width=35,
                cursor='hand2'
            )
            btn.pack(pady=5, padx=20)
        
        self.create_button(dialog, "Cancel", lambda: [dialog.destroy(), self.show_squad_page()], width=15).pack(pady=20)
    
    # Apply the selected role to the player in the XI
    def apply_role_change(self, player, index_in_xi, new_role, dialog):
        # Write the new role back to the save and refresh the page
        squad = self.read_team_data("squad", self.edit)
        squad[index_in_xi - 1]["role"] = new_role
        self.write_team_data(squad, "squad", self.edit)
        
        dialog.destroy()
        messagebox.showinfo("Success", f"Role changed to: {new_role}")
        self.show_squad_page()
    
    # Swap picker for replacing a player in the XI (matches the owned-players list look/filters)
    def show_swap_menu(self, current_player, index_in_xi, parent_dialog):
        # Build the dataset: all owned players except the current one
        squad = self.read_team_data("squad", self.edit)
        self._allplayers_band = [
            {"name": p.get("name",""),
             "country": p.get("country",""),
             "position": p.get("position",""),
             "rating": int(p.get("rating", 0))}
            for p in squad if p.get("name") != current_player.get("name")
        ]
        self._filter_countries = set()
        self._filter_positions = set()

        win = tk.Toplevel(self.root)
        win.title(f"Swap: choose replacement for {current_player.get('name','')}")
        win.geometry("850x700")
        win.configure(bg=self.colors['bg'])
        win.transient(self.root)
        win.grab_set()

        header = tk.Frame(win, bg=self.colors['secondary'])
        header.pack(fill=tk.X)
        tk.Label(
            header, text=f"SELECT SWAP FOR: {current_player.get('name','')}", bg=self.colors['secondary'],
            fg=self.colors['text'], font=('Arial', 16, 'bold')
        ).pack(pady=10)

        # Filters 
        filt = tk.Frame(win, bg=self.colors['bg'])
        filt.pack(fill=tk.X, pady=(12, 0))

        def label_filters():
            c = ", ".join(sorted(self._filter_countries)) or "None"
            p = ", ".join(sorted(self._filter_positions)) or "None"
            return f"Country filters: {c}    |    Position filters: {p}"

        self._filters_var = tk.StringVar(value=label_filters())
        tk.Label(filt, textvariable=self._filters_var, bg=self.colors['bg'], fg=self.colors['subtext'],
                 font=('Arial', 10)).pack(pady=(0, 8))

        buttons = tk.Frame(filt, bg=self.colors['bg'])
        buttons.pack()
        self.create_button(buttons, "Filter by Country",
                           lambda: self._toggle_country_filters(self._allplayers_band, win), width=20
        ).pack(side=tk.LEFT, padx=6)
        self.create_button(buttons, "Filter by Position",
                           lambda: self._toggle_position_filters(self._allplayers_band, win), width=20
        ).pack(side=tk.LEFT, padx=6)
        self.create_button(buttons, "Clear Filters",
                           lambda: self._clear_filters(win), width=16
        ).pack(side=tk.LEFT, padx=6)

        # Scrollable list of candidates
        list_wrap = tk.Frame(win, bg=self.colors['bg'])
        list_wrap.pack(fill=tk.BOTH, expand=True, pady=12, padx=16)
        canvas = tk.Canvas(list_wrap, bg=self.colors['bg'], highlightthickness=0)
        vbar = tk.Scrollbar(list_wrap, orient=tk.VERTICAL, command=canvas.yview)
        frame = tk.Frame(canvas, bg=self.colors['bg'])
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=vbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        win._players_canvas = canvas
        win._players_frame = frame

        # Clicking a row goes to confirm-swap
        def on_pick(candidate):
            self.confirm_player_swap_gui(current_player, candidate, index_in_xi, win, parent_dialog)
        win._on_pick = on_pick

        # Bottom buttons
        bottom = tk.Frame(win, bg=self.colors['bg'])
        bottom.pack(pady=10)
        self.create_button(bottom, "Cancel", win.destroy, width=16).pack()

        # First render
        self._render_player_list(win)

    # Confirm-and-apply swap
    def confirm_player_swap_gui(self, oldplayer, newplayer, index_in_xi, picker_win, parent_dialog):
        # Show both players side-by-side, then apply swap
        # (roles stay with XI positions and bench players lose any role when moved)
        try:
            with open("ratings.json", "r") as f:
                ratings_data = json.load(f)
            name_to_full = {p.get("name"): p for p in ratings_data}
        except Exception:
            name_to_full = {}

        full_old = name_to_full.get(oldplayer.get("name"), oldplayer)
        full_new = name_to_full.get(newplayer.get("name"), newplayer)

        dlg = tk.Toplevel(self.root)
        dlg.title("Confirm Swap")
        dlg.geometry("600x520")
        dlg.configure(bg=self.colors['bg'])
        dlg.transient(self.root)
        dlg.grab_set()

        header = tk.Frame(dlg, bg=self.colors['secondary'])
        header.pack(fill=tk.X)
        tk.Label(header, text="Confirm Player Swap", bg=self.colors['secondary'],
                 fg=self.colors['text'], font=('Arial', 16, 'bold')).pack(pady=10)

        body = tk.Frame(dlg, bg=self.colors['bg'])
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Left = current (to replace), Right = candidate (replacement)
        left = tk.Frame(body, bg=self.colors['accent'], relief=tk.RAISED, bd=2)
        right = tk.Frame(body, bg=self.colors['accent'], relief=tk.RAISED, bd=2)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        def render_card(frame, pl, title):
            tk.Label(frame, text=title, bg=self.colors['accent'], fg=self.colors['text'],
                     font=('Arial', 12, 'bold')).pack(pady=(8,4))
            tk.Label(frame, text=pl.get("name",""), bg=self.colors['accent'], fg=self.colors['text'],
                     font=('Arial', 14, 'bold')).pack()
            tk.Label(frame, text=f"{pl.get('rating', '-') } OVR  •  {pl.get('position','-')}  •  {pl.get('country','-')}",
                     bg=self.colors['accent'], fg=self.colors['text'], font=('Arial', 11)).pack(pady=(4,6))
            stats = pl.get("stats", {})
            if stats:
                # Block of label/value pairs
                stats_frame = tk.Frame(frame, bg=self.colors['accent'])
                stats_frame.pack(pady=6)

                rows = [
                    ("Pace", "pace"),
                    ("Shooting", "shooting"),
                    ("Passing", "passing"),
                    ("Dribbling", "dribbling"),
                    ("Defending", "defending"),
                    ("Physical", "physical"),
                ]
                for r, (label_txt, key) in enumerate(rows):
                    # Label column
                    tk.Label(
                        stats_frame,
                        text=f"{label_txt}:",
                        bg=self.colors['accent'],
                        fg=self.colors['text'],
                        font=('Arial', 12),
                        width=12,
                        anchor="e"
                    ).grid(row=r, column=0, padx=(0, 8), pady=2)

                    # Value column
                    tk.Label(
                        stats_frame,
                        text=str(stats.get(key, "-")),
                        bg=self.colors['accent'],
                        fg=self.colors['text'],
                        font=('Arial', 12, 'bold'),
                        width=5,
                        anchor="w"
                    ).grid(row=r, column=1, padx=(8, 0), pady=2)

        render_card(left, full_old, "Replace")
        render_card(right, full_new, "With")

        # Actions (confirm/cancel)
        actions = tk.Frame(dlg, bg=self.colors['bg'])
        actions.pack(pady=16)

        def do_swap():
            # Perform the role-preserving swap logic
            data = self.read_team_data("squad", self.edit)

            def idx_of(name):
                for i, pl in enumerate(data):
                    if pl.get("name") == name:
                        return i
                return None

            old_index = idx_of(oldplayer.get("name"))
            new_index = idx_of(newplayer.get("name"))
            if old_index is None or new_index is None:
                messagebox.showerror("Error", "Player not found in squad.")
                return

            xi_count = 11
            old_in_xi = old_index < xi_count
            new_in_xi = new_index < xi_count

            # Case 1: both in XI: roles stay with the positions
            if old_in_xi and new_in_xi:
                role_at_old = data[old_index].get("role")
                role_at_new = data[new_index].get("role")
                data[old_index], data[new_index] = data[new_index], data[old_index]
                if role_at_old is not None:
                    data[old_index]["role"] = role_at_old
                else:
                    data[old_index].pop("role", None)
                if role_at_new is not None:
                    data[new_index]["role"] = role_at_new
                else:
                    data[new_index].pop("role", None)

            # Case 2: one in XI, one on the bench: role stays with XI position, bench loses role
            elif old_in_xi != new_in_xi:
                xi_index = old_index if old_in_xi else new_index
                bench_index = new_index if old_in_xi else old_index
                role_to_keep = data[xi_index].get("role")
                data[old_index], data[new_index] = data[new_index], data[old_index]
                if role_to_keep is not None:
                    data[xi_index]["role"] = role_to_keep
                else:
                    data[xi_index].pop("role", None)
                data[bench_index].pop("role", None)

            # Case 3: both bench then simple swap
            else:
                data[old_index], data[new_index] = data[new_index], data[old_index]

            self.write_team_data(data, "squad", self.edit)

            # Close picker, dialog, and parent details if open
            try:
                if picker_win:
                    picker_win.destroy()
            except Exception:
                pass
            try:
                if dlg:
                    dlg.destroy()
            except Exception:
                pass
            try:
                if 'parent_dialog' in locals() and parent_dialog:
                    parent_dialog.destroy()
            except Exception:
                pass

            # Refresh Team Management so the swap is visible immediately
            self.show_squad_page()

        self.create_button(actions, "Confirm Swap", do_swap, width=18).pack(side=tk.LEFT, padx=8)
        self.create_button(actions, "Cancel", dlg.destroy, width=12).pack(side=tk.LEFT, padx=8)
    
    # Quicksell a player: blocks selling if you would drop to 11 or fewer players
    def quicksell_player(self, player, dialog):
        # Read current squad from the save
        squad = self.read_team_data("squad", self.edit)
        
        # You must always keep at least a full starting XI
        if len(squad) <= 11:
            messagebox.showerror("Error", "You must have more than 11 players to quicksell")
            return
        
        # Confirm sale
        if messagebox.askyesno("Confirm", f"Quicksell {player['name']}?"):
            # Remove the chosen player
            try:
                idx = squad.index(player)
            except ValueError:
                # Fallback: if the exact dict isn't found, match by name
                idx = next((i for i, p in enumerate(squad) if p.get("name") == player.get("name")), None)
            
            if idx is None:
                dialog.destroy()
                messagebox.showerror("Error", "Could not find player to quicksell")
                return

            # If possible, swap the target with player 12 so the XI indices stay fixed
            starter_role = None
            if idx < 11:
                starter_role = squad[idx].get("role")

            if len(squad) > 11:
                squad[idx], squad[11] = squad[11], squad[idx]

                # Give player 12 (now in the XI slot) the old starter's role
                if starter_role is not None and idx < 11:
                    squad[idx]["role"] = starter_role

                del squad[11]
            else:
                del squad[idx]

            self.write_team_data(squad, "squad", self.edit)
            
            # Add coins for the sale and persist
            value = self.quick_sell_value(player['rating'])
            self.coins += value
            self.write_team_data(str(self.coins), "coins", self.edit)
            
            # Close the dialog and refresh the squad view
            dialog.destroy()
            messagebox.showinfo("Success", f"{player['name']} quicksold for {value} coins")
            self.show_squad_page()
    
    # Open the formation picker and allow the user to change formation
    def show_formation_menu(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Formation")
        dialog.geometry("400x500")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="Choose Formation",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        # Read current formation to mark it in the list
        current_formation = self.read_team_data("formation", self.edit)
        
        formations = ["4-4-2", "4-3-3", "4-5-1", "4-2-2-2", "5-3-2", "5-2-3", "5-4-1"]
        
        # One button per formation: clicking applies and refreshes
        for formation in formations:
            is_current = " (Current)" if formation == current_formation else ""
            btn = tk.Button(
                dialog,
                text=formation + is_current,
                command=lambda f=formation: self.apply_formation_change(f, dialog),
                bg=self.colors['accent'],
                fg=self.colors['text'],
                font=('Arial', 12),
                width=25,
                cursor='hand2'
            )
            btn.pack(pady=8)
        
        self.create_button(dialog, "Cancel", dialog.destroy, width=15).pack(pady=20)

    # Edit the team tactics and save them back to the file
    def show_tactics_menu(self):
        # Load currently saved tactics, providing sensible defaults if missing
        tactics = self.read_team_data("tactics", self.edit) or {
            "directness": "Balanced",
            "tempo": "Balanced",
            "dribbling": "Balanced",
            "press": "Balanced",
            "defensive line": "Balanced",
            "defensive width": "Balanced", 
            "approach": {"left": False, "middle": False, "right": False},  # all False means neutral
        }

        # Fixed option sets used by the game
        options = {
            "directness": [
                "Much shorter",
                "Shorter",
                "Balanced",
                "More direct",
                "Much more direct",
            ],
            "tempo": [
                "Lower",
                "Slightly lower",
                "Balanced",
                "Slightly higher",
                "Higher",
            ],
            "dribbling": [
                "Dribble less",
                "Balanced",
                "Run at defence",
            ],
            "press": [
                "Much less often",
                "Less often",
                "Balanced",
                "More often",
                "Much more often",
            ],
            "defensive line": [
                "Much deeper",
                "Deeper",
                "Balanced",
                "Higher",
                "Much higher",
            ],
            "defensive width": [
                "Narrow",
                "Balanced",
                "Wide",
            ],
        }

        dlg = tk.Toplevel(self.root)
        dlg.title("Change Tactics")
        dlg.geometry("560x520")
        dlg.configure(bg=self.colors['bg'])
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(
            dlg, text="Tactics", bg=self.colors['bg'], fg=self.colors['text'],
            font=('Arial', 18, 'bold')
        ).pack(pady=(16, 10))

        card = tk.Frame(dlg, bg=self.colors.get('card', self.colors['bg']))
        card.pack(fill="both", expand=True, padx=16, pady=12)

        # Helper to make a labelled combobox row bound to a StringVar
        def add_combo(parent, label, key):
            row = tk.Frame(parent, bg=card['bg']); row.pack(fill="x", pady=8)
            tk.Label(
                row, text=label, bg=card['bg'], fg=self.colors['text'],
                font=('Arial', 12, 'bold')
            ).pack(side=tk.LEFT)
            var = tk.StringVar(value=tactics.get(key, options[key][2]))  # default to Balanced
            box = ttk.Combobox(row, values=options[key], textvariable=var, state="readonly", width=24)
            box.pack(side=tk.RIGHT, padx=6)
            return var

        # Four dropdowns for the main tactical choices
        direct_var = add_combo(card, "Passing Directness", "directness")
        tempo_var  = add_combo(card, "Tempo", "tempo")
        drib_var   = add_combo(card, "Dribbling", "dribbling")
        press_var  = add_combo(card, "Trigger Press", "press")
        dline_var  = add_combo(card, "Defensive Line", "defensive line")
        dwidth_var = add_combo(card, "Defensive Width", "defensive width")

        # Approach play: left / middle / right. Any combination valid. All off = neutral.
        block = tk.Frame(card, bg=card['bg'])
        block.pack(fill="x", pady=(14, 6))

        tk.Label(
            block, text="Approach Play", bg=card['bg'], fg=self.colors['text'],
            font=('Arial', 12, 'bold')
        ).pack(side=tk.LEFT)

        app = tactics.get("approach", {})
        left_v   = tk.BooleanVar(value=bool(app.get("left", False)))
        mid_v    = tk.BooleanVar(value=bool(app.get("middle", False)))
        right_v  = tk.BooleanVar(value=bool(app.get("right", False)))

        checks = tk.Frame(block, bg=card['bg'])
        checks.pack(side=tk.RIGHT, padx=6)

        tk.Checkbutton(
            checks, text="Focus Left", variable=left_v,
            bg=card['bg'], fg=self.colors['text'],
            selectcolor=self.colors['bg'], activebackground=card['bg']
        ).pack(side=tk.LEFT, padx=6)
        tk.Checkbutton(
            checks, text="Focus Middle", variable=mid_v,
            bg=card['bg'], fg=self.colors['text'],
            selectcolor=self.colors['bg'], activebackground=card['bg']
        ).pack(side=tk.LEFT, padx=6)
        tk.Checkbutton(
            checks, text="Focus Right", variable=right_v,
            bg=card['bg'], fg=self.colors['text'],
            selectcolor=self.colors['bg'], activebackground=card['bg']
        ).pack(side=tk.LEFT, padx=6)

        # Footer with Save / Cancel
        footer = tk.Frame(dlg, bg=self.colors['bg']); footer.pack(pady=10)
        center = tk.Frame(footer, bg=self.colors['bg']); center.pack()

        def do_save():
            # Build the updated tactics dictionary and write it back
            new_tactics = {
                "directness": direct_var.get(),
                "tempo":      tempo_var.get(),
                "dribbling":  drib_var.get(),
                "press":      press_var.get(),
                "defensive line":  dline_var.get(),
                "defensive width": dwidth_var.get(),
                "approach":   {"left": left_v.get(), "middle": mid_v.get(), "right": right_v.get()},
            }
            self.write_team_data(new_tactics, "tactics", self.edit)
            try:
                dlg.destroy()
            except Exception:
                pass
            # Return to the squad page to reflect the change
            self.show_squad_page()

        self.create_button(center, "Save", do_save, width=14).pack(side=tk.LEFT, padx=8)
        self.create_button(center, "Cancel", dlg.destroy, width=12).pack(side=tk.LEFT, padx=8)
    
    # Persist the chosen formation and refresh the team management page
    def apply_formation_change(self, formation, dialog):
        # Read current squad and old formation
        squad = self.read_team_data("squad", self.edit) or []
        old_formation = self.read_team_data("formation", self.edit)

        # Build position: roles from the old XI (roles belong to slots, not players)
        pos_to_roles = {}
        if old_formation:
            old_slots, _ = self.formation_switch(old_formation)
            for i in range(1, 12):
                pos = old_slots[i]["position"]
                role = (squad[i-1].get("role") if i-1 < len(squad) else None)
                if role:
                    pos_to_roles.setdefault(pos, []).append(role)

        # Defaults if a position didn’t exist previously
        def default_role_for(pos):
            opts = self.role_options.get(pos, [])
            if opts:
                return opts[0]
            fallback = {
                "GK": "Goalkeeper (Defend)",
                "LB": "Fullback (Support)",
                "RB": "Fullback (Support)",
                "CB": "Centreback (Defend)",
                "CM": "Central Midfielder (Support)",
                "LW": "Winger (Support)",
                "RW": "Winger (Support)",
                "ST": "Advanced Forward (Attack)",
            }
            return fallback.get(pos)

        # Compute new slots and reassign roles by slot position
        new_slots, _ = self.formation_switch(formation)
        used_idx = {p: 0 for p in pos_to_roles}
        for i in range(1, 12):
            if i-1 >= len(squad):
                break
            slot_pos = new_slots[i]["position"]
            if slot_pos in pos_to_roles and used_idx[slot_pos] < len(pos_to_roles[slot_pos]):
                role = pos_to_roles[slot_pos][used_idx[slot_pos]]
                used_idx[slot_pos] += 1
            else:
                role = default_role_for(slot_pos)
            if role:
                squad[i-1]["role"] = role
            else:
                squad[i-1].pop("role", None)

        # Bench shouldn’t carry roles
        for j in range(11, len(squad)):
            squad[j].pop("role", None)

        # Persist + refresh
        self.write_team_data(formation, "formation", self.edit)
        self.write_team_data(squad, "squad", self.edit)
        try:
            dialog.destroy()
        except Exception:
            pass
        messagebox.showinfo("Success", f"Formation changed to {formation}")
        self.show_squad_page()

    # Browser for all owned players
    def show_all_owned_players(self):
        # Load full squad (owned players)
        squad = self.read_team_data("squad", self.edit)
        starting_xi_names = {p.get("name") for p in squad[:11]}
        owned_not_xi = list(squad)

        # Normalise into the ratings.json-like shape expected by the shared renderer
        self._allplayers_band = [
            {
                "name": p.get("name", ""),
                "country": p.get("country", ""),
                "position": p.get("position", ""),
                "rating": int(p.get("rating", 0)),
            }
            for p in owned_not_xi
        ]

        # Reset filter state each time this browser opens
        self._filter_countries = set()
        self._filter_positions = set()

        # Window shell
        win = tk.Toplevel(self.root)
        win.title("All Owned Players")
        win.geometry("850x700")
        win.configure(bg=self.colors['bg'])
        win.transient(self.root)
        win.grab_set()

        # Header bar
        header = tk.Frame(win, bg=self.colors['secondary'])
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="ALL OWNED PLAYERS",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 16, 'bold')
        ).pack(pady=10)

        # Filter strip (label + three buttons)
        filt = tk.Frame(win, bg=self.colors['bg'])
        filt.pack(fill=tk.X, pady=(12, 0))

        def label_filters():
            c = ", ".join(sorted(self._filter_countries)) or "None"
            p = ", ".join(sorted(self._filter_positions)) or "None"
            return f"Country filters: {c}    |    Position filters: {p}"

        self._filters_var = tk.StringVar(value=label_filters())
        tk.Label(
            filt,
            textvariable=self._filters_var,
            bg=self.colors['bg'],
            fg=self.colors['subtext'],
            font=('Arial', 10)
        ).pack(pady=(0, 8))

        buttons = tk.Frame(filt, bg=self.colors['bg'])
        buttons.pack()

        self.create_button(
            buttons,
            "Filter by Country",
            lambda: self._toggle_country_filters(self._allplayers_band, win),
            width=20
        ).pack(side=tk.LEFT, padx=6)

        self.create_button(
            buttons,
            "Filter by Position",
            lambda: self._toggle_position_filters(self._allplayers_band, win),
            width=20
        ).pack(side=tk.LEFT, padx=6)

        self.create_button(
            buttons,
            "Clear Filters",
            lambda: self._clear_filters(win),
            width=16
        ).pack(side=tk.LEFT, padx=6)

        # Scrollable list surface
        list_wrap = tk.Frame(win, bg=self.colors['bg'])
        list_wrap.pack(fill=tk.BOTH, expand=True, pady=12, padx=16)

        canvas = tk.Canvas(list_wrap, bg=self.colors['bg'], highlightthickness=0)
        vbar = tk.Scrollbar(list_wrap, orient=tk.VERTICAL, command=canvas.yview)
        frame = tk.Frame(canvas, bg=self.colors['bg'])

        # Keep the canvas scroll region in sync with the inner frame size
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=vbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Store handles for the shared renderer
        win._players_canvas = canvas
        win._players_frame = frame

        # Bottom area with Return button
        bottom = tk.Frame(win, bg=self.colors['bg'])
        bottom.pack(pady=10)
        target = self.show_play_page if getattr(self, "tm_return_to", "home") == "play" else self.show_squad_page
        self.create_button(bottom, "Return", lambda: [win.destroy(), target()], width=16).pack()

        # Render the list using the same routine as the other player browser
        self._render_player_list(win)

    # Small loader window shown while the opponent is generated off the main thread
    def show_build_opponent_loader(self):
        loader = tk.Toplevel(self.root)
        loader.title("Preparing Match")
        loader.geometry("420x220")
        loader.configure(bg=self.colors['bg'])
        loader.transient(self.root)
        loader.grab_set()

        tk.Label(
            loader,
            text="Preparing opponent…",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 16, 'bold')
        ).pack(pady=(18, 8))

        status_var = tk.StringVar(value="Initialising data…")
        tk.Label(
            loader,
            textvariable=status_var,
            bg=self.colors['bg'],
            fg=self.colors['subtext'],
            font=('Arial', 12)
        ).pack(pady=(0, 10))

        # Indeterminate progress bar + rotating status messages
        bar = ttk.Progressbar(loader, mode='indeterminate', length=300)
        bar.pack(pady=6)
        bar.start(10)

        messages = [
            "Initialising managers…",
            "Generating opponent squad…",
            "Assigning roles and positions…",
            "Calculating chemistry…",
            "Picking formation and tactics…",
            "Finalising team…"
        ]
        idx = {"i": 0}

        def tick():
            status_var.set(messages[idx["i"] % len(messages)])
            idx["i"] += 1
            loader._tick_id = loader.after(5000, tick)
        tick()

        # Called once the worker completes (success or error)
        def done(success=True, err=None):
            try:
                bar.stop()
            except Exception:
                pass
            if hasattr(loader, "_tick_id"):
                loader.after_cancel(loader._tick_id)
            try:
                loader.destroy()
            except Exception:
                pass
            if not success:
                messagebox.showerror("Error", f"Failed to build opponent: {err}")
                self.show_play_page()
                return
            self.show_match_page()

        # Background worker that builds the opponent and then notifies the UI thread
        def worker():
            try:
                self.build_opponent()
                self.root.after(0, lambda: done(True))
            except Exception as e:
                self.root.after(0, lambda: done(False, str(e)))

        Thread(target=worker, daemon=True).start()
    
    # Match preparation page. If no opponent exists, switch to the loader and return
    def show_match_page(self):
        self.clear_window()
        
        # Ensure opponent exists. If not, show loader and exit early to keep UI responsive
        try:
            opponent = self.read_team_data("opponent", self.edit)
            if not opponent:
                raise KeyError
        except Exception:
            self.show_build_opponent_loader()
            return
        
        # Header bar
        header = tk.Frame(self.root, bg=self.colors['secondary'], height=60)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="MATCH",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 20, 'bold')
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        # Opponent summary
        info_frame = tk.Frame(self.root, bg=self.colors['bg'])
        info_frame.pack(pady=40)
        
        self.create_label(info_frame, "Upcoming Opponent", font_size=16, bold=True).pack(pady=10)
        self.create_label(info_frame, f"{opponent['team']}", font_size=20, bold=True).pack(pady=5)
        self.create_label(info_frame, f"Manager: {opponent['manager']} ({opponent['manager rating']} OVR)", font_size=12).pack(pady=5)
        self.create_label(info_frame, f"Team Rating: {opponent['team rating']} OVR", font_size=14).pack(pady=5)
        self.create_label(info_frame, f"Formation: {opponent['formation']}", font_size=12).pack(pady=5)
        
        # Main actions
        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.pack(pady=40)
        
        self.create_button(button_frame, "Play Match", lambda: self.play_match(opponent)).pack(pady=10)
        self.create_button(button_frame, "View Opponent Squad", lambda: self.show_opponent_squad(opponent)).pack(pady=10)
        self.create_button(button_frame, "Return", self.show_play_page).pack(pady=10)
    
    # Show the opponent XI on a pitch with the same UX as team management
    def show_opponent_squad(self, opponent):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{opponent['team']} - Squad")
        dialog.geometry("1000x800")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        # Header bar
        header = tk.Frame(dialog, bg=self.colors['secondary'])
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text=f"{opponent['team'].upper()} – OPPONENT SQUAD",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 18, 'bold')
        ).pack(pady=12)

        # Summary stats for the opponent
        stats_frame = tk.Frame(dialog, bg=self.colors['bg'])
        stats_frame.pack(pady=(10, 6))

        opp_chem = self.team_chemistry(opponent=True)
        display_rating = opponent.get("team rating", self.compute_team_rating_from_players(opponent["players"]))
        tk.Label(
            stats_frame,
            text=f"Team Rating: {display_rating} OVR  |  Team Chemistry: {opp_chem}/100",
            bg=self.colors['bg'],
            fg=self.colors['success'],
            font=('Arial', 14, 'bold')
        ).pack()

        # Manager details and formation line
        mgr_text = ""
        try:
            nm = opponent.get("manager", "")
            ct = opponent.get("manager country", "")
            rt = opponent.get("manager rating", "")
            parts = []
            if nm:
                parts.append(f"Manager: {nm}")
            if ct:
                parts.append(f"({ct})")
            if rt != "":
                parts.append(f"  |   Manager Rating: {rt}")
            mgr_text = " ".join(parts).strip()
        except Exception:
            pass
        if not mgr_text:
            mgr_text = "Manager: Unknown"

        tk.Label(
            stats_frame,
            text=f"{mgr_text}   |   Formation: {opponent.get('formation','?')}",
            bg=self.colors['bg'],
            fg=self.colors['subtext'],
            font=('Arial', 12, 'bold')
        ).pack(pady=(6, 0))

        # Pitch canvas
        pitch_wrap = tk.Frame(dialog, bg=self.colors['bg'])
        pitch_wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        pitch = tk.Canvas(pitch_wrap, bg=self.colors['bg'], highlightthickness=0)
        pitch.pack(fill=tk.BOTH, expand=True)

        # Build the layout and links according to the opponent formation
        formation = opponent['formation']
        player_slots, player_links = self.formation_switch(formation)

        # Redraw on resize
        def _draw_now(event=None):
            pitch.delete("all")
            squad = opponent['players'][:11]
            w = pitch.winfo_width() or 1000
            h = pitch.winfo_height() or 600
            self._draw_team_on_pitch(
                pitch,
                squad,
                formation,
                player_slots,
                player_links,
                w,
                h,
                on_click_player=lambda p, idx: self.show_opponent_player_details(p, idx)
            )

        pitch.bind("<Configure>", _draw_now)

        # Close button only
        btns = tk.Frame(dialog, bg=self.colors['bg'])
        btns.pack(pady=12)

        self.create_button(btns, "Close", dialog.destroy, width=15).pack()

    def show_match_ratings_pitch(self, is_opponent: bool):
        dialog = tk.Toplevel(self.root)
        dialog.title("Player Ratings (Formation View)")
        dialog.geometry("900x640")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        if is_opponent:
            opp = self.read_team_data("opponent", self.edit)
            team_name = opp.get("team", "Opponent")
            formation = opp.get("formation", "4-4-2")
            squad = (opp.get("players") or [])[:11]
        else:
            team_name = self.team_name or (self.read_team_data("team", self.edit) or "Your Team")
            formation = self.read_team_data("formation", self.edit)
            squad = (self.read_team_data("squad", self.edit) or [])[:11]
        # Make keys match the match engine ("Name (YOU)/(OPP)"), keep plain name for display
        for p in squad:
            base = p.get("name", "")
            p["display"] = base
            if is_opponent:
                p["_match_key"] = f"{base} (OPP)"
            else:
                p["_match_key"] = f"{base} (YOU)"

        tk.Label(
            dialog,
            text=f"{team_name} – Match ratings",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=("Arial", 16, "bold"),
        ).pack(pady=12)

        # Manager label
        if is_opponent:
            mgr_name = opp.get("manager", "Unknown")
            mgr_country = opp.get("manager country", "Unknown")
        else:
            mgr_name = self.read_team_data("manager", self.edit)
            mgr_country = self.read_team_data("manager country", self.edit)

        mgr_name = mgr_name if isinstance(mgr_name, str) else str(mgr_name)
        mgr_country = mgr_country if isinstance(mgr_country, str) else str(mgr_country)

        tk.Label(
            dialog,
            text=f"Manager: {mgr_name} ({mgr_country})",
            bg=self.colors['bg'],
            fg=self.colors['subtext'],
            font=("Arial", 11),
        ).pack(pady=(0, 6))

        # Pitch area
        wrap = tk.Frame(dialog, bg=self.colors['bg'])
        wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        canvas = tk.Canvas(wrap, bg=self.colors['bg'], highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        player_slots, player_links = self.formation_switch(formation)

        def _draw(event=None):
            canvas.delete("all")
            w = canvas.winfo_width() or 1000
            h = canvas.winfo_height() or 600
            self._draw_team_on_pitch_match_view(canvas, squad, formation, player_slots, player_links, w, h)

        canvas.bind("<Configure>", _draw)
        _draw()

        self.create_button(dialog, "Close", dialog.destroy, width=16).pack(pady=12)
    
    # Play the match and render commentary and live stats as it progresses
    def play_match(self, opponent):
        self.clear_window()
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['secondary'])
        header.pack(fill=tk.X, pady=(5, 0))

        your_team = self.team_name
        opp_team = opponent['team']

        # Grid layout
        header.grid_columnconfigure(0, weight=1, uniform="cols")
        header.grid_columnconfigure(1, weight=1, uniform="cols")
        header.grid_columnconfigure(2, weight=1, uniform="cols")

        # Score + minute
        score_var = tk.StringVar(value=f"{your_team} 0 - 0 {opp_team}")
        minute_var = tk.StringVar(value="Minute: 0")

        centre = tk.Frame(header, bg=self.colors['secondary'])
        centre.grid(row=0, column=1, pady=10)

        tk.Label(
            centre,
            textvariable=score_var,
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 20, 'bold')
        ).pack()

        tk.Label(
            centre,
            textvariable=minute_var,
            bg=self.colors['secondary'],
            fg=self.colors['subtext'],
            font=('Arial', 12)
        ).pack()

        # Pause / Continue button
        self.pause_btn = tk.Button(
            header,
            text="⏸",
            font=("Arial", 22, "bold"),
            width=3,
            height=1,
            bg=self.colors['accent'],
            fg=self.colors['text'],
            activebackground=self.colors['highlight'],
            activeforeground=self.colors['text'],
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
            command=self.toggle_pause
        )
        self.pause_btn.grid(row=0, column=2, padx=(0, 15), pady=10, sticky="e")

        # Hover effect
        self.pause_btn.bind('<Enter>', lambda e: self.pause_btn.config(bg=self.colors['highlight']))
        self.pause_btn.bind('<Leave>', lambda e: self.pause_btn.config(bg=self.colors['accent']))

        # Start state
        self.sim_paused = False
        self.fulltime_pending = False
        
        # Spacebar also toggles pause
        try:
            self.root.unbind_all("<space>")
        except Exception:
            pass
        self.root.bind_all("<space>", self.on_space)
        
        # Simple stats line (shots and xG)
        stats_frame = tk.Frame(self.root, bg=self.colors['bg'])
        stats_frame.pack(pady=20)
        
        shots_var = tk.StringVar(value="Shots: 0 - 0")
        xg_var = tk.StringVar(value="xG: 0.00 - 0.00")
        
        tk.Label(
            stats_frame,
            textvariable=shots_var,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 12)
        ).pack()
        
        tk.Label(
            stats_frame,
            textvariable=xg_var,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 12)
        ).pack()
        
        # Commentary box with a scrollbar
        commentary_frame = tk.Frame(self.root, bg=self.colors['accent'], relief=tk.SUNKEN, bd=2)
        commentary_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        tk.Label(
            commentary_frame,
            text="Match Commentary",
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        commentary_text = tk.Text(
            commentary_frame,
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 14),
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        commentary_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(commentary_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        commentary_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=commentary_text.yview)
        
        # Kick off the engine after a short delay so the UI renders first
        self.root.after(100, lambda: self.run_match_engine(
            opponent, score_var, minute_var, shots_var, xg_var, commentary_text
        ))

    # Pause button
    def toggle_pause(self):
        # At full time, use button as CONTINUE
        if getattr(self, "fulltime_pending", False):
            self.fulltime_pending = False
            args = getattr(self, "_fulltime_args", None)
            if args:
                (your_team, opp_team, score, shots, xg_total,
                 match_log, your_squad, opp_squad) = args
                self.show_fulltime_options(
                    your_team, opp_team, score, shots, xg_total,
                    match_log, your_squad, opp_squad
                )
            return

        # Normal pause/unpause
        self.sim_paused = not getattr(self, "sim_paused", False)
        try:
            self.pause_btn.config(
                text="▶" if self.sim_paused else "⏸",
                font=("Arial", 22, "bold"),
                bg=self.colors['accent'],
                fg=self.colors['text'],
                activebackground=self.colors['highlight'],
                activeforeground=self.colors['text'],
                relief=tk.RAISED,
                bd=2
            )
        except Exception:
            pass

    def on_space(self, event):
        self.toggle_pause()
        return "break"
    
    # Simulation loop: minute-by-minute, generates chances and commentary, updates live stats
    def run_match_engine(self, opponent, score_var, minute_var, shots_var, xg_var, commentary_text):
        random.seed(self.edit)
        your_team = self.team_name
        opp_team = opponent['team']

        # Basic tallies for scoreline, shots and xG
        score = {your_team: 0, opp_team: 0}
        shots = {your_team: 0, opp_team: 0}
        xg_total = {your_team: 0.0, opp_team: 0.0}
        match_log = []

        # Every player starts on 6.6, ratings move during the match
        your_squad = self.read_team_data("squad", self.edit)
        opp_squad = opponent["players"]
        # Force unique match keys but keep real name for display
        for p in your_squad:
            p["display"] = p["name"]
            p["name"] = p["name"] + " (YOU)"
        for p in opp_squad:
            p["display"] = p["name"]
            p["name"] = p["name"] + " (OPP)"
        self.match_ratings = {}
        for p in your_squad + opp_squad:
            self.match_ratings[p["name"]] = 6.6
        self.fulltime_pending = False
        self.last_goal_counts = {}
        self.last_assist_counts = {}

        # Read formations to group positions (def/mid/att) for chance selection
        your_formation = self.read_team_data("formation", self.edit)
        opp_formation = opponent['formation']
        your_slots, _ = self.formation_switch(your_formation)
        opp_slots, _ = self.formation_switch(opp_formation)

        # Position index sets by role (position + role-based multi-categories)
        def _slot_categories(slots, squad, idx):
            cats = set()
            pos = slots[idx]["position"]

            # Base categories
            if pos in ["LB", "CB", "RB"]:
                cats.add("DEF")
            if pos == "CM":
                cats.add("MID")
            if pos in ["LW", "RW", "ST"]:
                cats.add("ATT")

            # Read role string safely
            role = ""
            if 0 <= idx - 1 < len(squad):
                role = (squad[idx - 1].get("role") or "").strip()

            base = role
            style = ""
            if "(" in role and ")" in role:
                base = role.split("(", 1)[0].strip()
                style = role.split("(", 1)[1].strip(" )")

            # midfielder on attack -> MID + ATT
            if base == "Central Midfielder" and style == "Attack":
                cats.add("ATT")

            # box to box midfielder -> MID + DEF + ATT
            if base == "Box to Box Midfielder":
                cats.update(["DEF", "ATT"])

            # ball winning midfielder -> MID + DEF
            if base == "Ball Winning Midfielder":
                cats.add("DEF")
                
            # libero -> MID + DEF
            if base == "Libero":
                cats.add("MID")

            # fullback on attack -> DEF + MID
            if base == "Fullback" and style == "Attack":
                cats.add("MID")

            # inverted wingback on support/attack -> DEF + MID
            if base == "Inverted Wingback" and style in ("Support", "Attack"):
                cats.add("MID")

            # Wide playmaker on support/attack -> MID + ATT
            if base == "Wide Playmaker" and style in ("Support", "Attack"):
                cats.add("MID")  # LW/RW already give ATT from position

            # false nine -> ATT + MID
            if base == "False Nine":
                cats.add("MID")  # ST already gives ATT

            return cats

        your_def = [
            i for i in range(1, 12)
            if "DEF" in _slot_categories(your_slots, your_squad, i)
        ]
        opp_def = [
            i for i in range(1, 12)
            if "DEF" in _slot_categories(opp_slots, opp_squad, i)
        ]

        your_gk = next(i for i in range(1, 12) if your_slots[i]["position"] == "GK")
        opp_gk  = next(i for i in range(1, 12) if opp_slots[i]["position"] == "GK")

        your_mid = [
            i for i in range(1, 12)
            if "MID" in _slot_categories(your_slots, your_squad, i)
        ]
        opp_mid = [
            i for i in range(1, 12)
            if "MID" in _slot_categories(opp_slots, opp_squad, i)
        ]

        your_att = [
            i for i in range(1, 12)
            if "ATT" in _slot_categories(your_slots, your_squad, i)
        ]
        opp_att = [
            i for i in range(1, 12)
            if "ATT" in _slot_categories(opp_slots, opp_squad, i)
        ]

        # UI helpers
        def add_commentary(text, tag="you"):
            commentary_text.config(state=tk.NORMAL)
            commentary_text.insert(tk.END, text + "\n", tag)
            commentary_text.see(tk.END)
            commentary_text.config(state=tk.DISABLED)
            self.root.update()

        def update_display(minute):
            score_var.set(f"{your_team} {score[your_team]} - {score[opp_team]} {opp_team}")
            minute_var.set(f"Minute: {minute}")
            shots_var.set(f"Shots: {shots[your_team]} - {shots[opp_team]}")
            xg_var.set(f"xG: {xg_total[your_team]:.2f} - {xg_total[opp_team]:.2f}")
            self.root.update()

        # Colour tags for commentary
        commentary_text.tag_config("you", foreground="#155724")
        commentary_text.tag_config("opp", foreground="#7b1e1e")
        commentary_text.tag_config("default", foreground="#FFFFFF")
        add_commentary("Match starting...", "default")
        self.root.after(int(3 * self.sim_speed))

        # Tactics data
        your_tactics = self.read_team_data("tactics", self.edit) or {}
        opp_tactics  = opponent.get("tactics", {}) if isinstance(opponent, dict) else {}

        # Factor range helpers (attacking-only knobs: directness, tempo, dribbling)
        BASE_DIST  = (0.40, 2.00)
        BASE_PRESS = (0.60, 1.20)
        BASE_CHAOS = (0.75, 1.30)

        def _scale_about_mid(base_range, pct_change):
            low, high = base_range
            mid = (low + high) / 2.0
            k = 1.0 + float(pct_change)
            return (mid + (low - mid) * k, mid + (high - mid) * k)

        def _clamp_range(rng, hard_min=None):
            lo, hi = rng
            if hard_min is not None:
                lo = max(hard_min, lo)
            if hi < lo:
                lo, hi = hi, lo
            return (lo, hi)

        def _pct_from_attack_tactics(tac):
            # Only directness, tempo, dribbling affect the attacker’s factor ranges.
            dist_pct = press_pct = chaos_pct = 0.0

            # Directness: distance range width
            direct = (tac.get("directness") or "Balanced").lower()
            if "much shorter" in direct:
                dist_pct += -0.6
            elif "shorter" in direct:
                dist_pct += -0.3
            elif direct == "more direct":
                dist_pct += 0.3
            elif "much more" in direct:
                dist_pct += 0.6

            # Tempo: pressure + chaos range width
            tempo = (tac.get("tempo") or "Balanced").lower()
            if tempo == "lower":
                press_pct += -0.45; chaos_pct += -0.3
            elif tempo == "slightly lower":
                press_pct += -0.25; chaos_pct += -0.15
            elif tempo == "slightly higher":
                press_pct += +0.3; chaos_pct += +0.2
            elif tempo == "higher":
                press_pct += +0.5; chaos_pct += +0.4

            # Dribbling: chaos range width
            drib = (tac.get("dribbling") or "Balanced").lower()
            if "less" in drib:
                chaos_pct += -0.15
            elif "run at" in drib:
                chaos_pct += +0.15

            # clamp
            dist_pct  = max(-0.6, min(+0.6, dist_pct))
            press_pct = max(-0.45, min(+0.45, press_pct))
            chaos_pct = max(-0.15, min(+0.45, chaos_pct))
            return dist_pct, press_pct, chaos_pct

        # Precompute attacker ranges for both sides (press/line are not used here)
        y_dist_pct, y_press_pct, y_chaos_pct = _pct_from_attack_tactics(your_tactics)
        o_dist_pct, o_press_pct, o_chaos_pct = _pct_from_attack_tactics(opp_tactics)

        your_dist_range  = _clamp_range(_scale_about_mid(BASE_DIST,  y_dist_pct))
        your_press_range = _clamp_range(_scale_about_mid(BASE_PRESS, y_press_pct))
        your_chaos_range = _clamp_range(_scale_about_mid(BASE_CHAOS, y_chaos_pct))

        opp_dist_range   = _clamp_range(_scale_about_mid(BASE_DIST,  o_dist_pct))
        opp_press_range  = _clamp_range(_scale_about_mid(BASE_PRESS, o_press_pct))
        opp_chaos_range  = _clamp_range(_scale_about_mid(BASE_CHAOS, o_chaos_pct))

        # Defensive-only counters (press, defensive line) 
        def _rank_press(v):
            s = (v or "Balanced").lower()
            return {"much less often":0, "less often":1, "balanced":2, "more often":3, "much more often":4}.get(s, 2)

        def _rank_direct(v):
            s = (v or "Balanced").lower()
            if "much shorter" in s: return 0
            if "shorter" in s: return 1
            if "more direct" in s: return 3
            if "much more" in s:  return 4
            return 2

        def _rank_line(v):
            s = (v or "Balanced").lower()
            return {"much deeper":0, "deeper":1, "balanced":2, "higher":3, "much higher":4}.get(s, 2)
        
        def _rank_tempo(v):
            s = (v or "Balanced").lower()
            return {
                "lower": 0,
                "slightly lower": 1,
                "balanced": 2,
                "slightly higher": 3,
                "higher": 4
            }.get(s, 2)

        # Defensive width: direct xG counter to the attacker’s approach 
        def _approach_vs_width_factor(att_tac, def_tac):
            ap = (att_tac.get("approach") or {})
            lanes = [d for d in ("left","middle","right") if bool(ap.get(d, False))]
            if not lanes:  # no focus - neutral
                lanes = ["middle"]
            dw = (def_tac.get("defensive width") or "Balanced").lower()

            if dw == "narrow":
                lane_mult = {"left": 1.10, "middle": 0.80, "right": 1.10}
            elif dw == "wide":
                lane_mult = {"left": 0.80, "middle": 1.10, "right": 0.80}
            else:
                lane_mult = {"left": 1.00, "middle": 1.00, "right": 1.00}

            mod = sum(lane_mult[L] for L in lanes) / len(lanes)
            return max(0.75, min(1.15, mod))

        # Main minute loop (0 - 90)
        for match_min in range(91):
            while getattr(self, "sim_paused", False):
                # keep rechecking every 150 ms until unpaused
                self.root.update()
                self.root.after(150)
            update_display(match_min)

            # Chance generation roll affected by tempo
            chance_freq = 1000
            generate_chance = random.randint(1, chance_freq)
            your_tempo = _rank_tempo(your_tactics.get("tempo"))
            opp_tempo = _rank_tempo(opp_tactics.get("tempo"))
            match_intensity = 10 * (your_tempo + opp_tempo) / 2
            add = int((match_intensity - 2) * 3)
            your_chance = 100 + add
            opp_chance = 900 - add

            attacking_team = None
            midfielder = None
            mid_rating = 0
            mid_slot_idx = None

            if generate_chance <= your_chance and your_mid:
                idx = random.choice(your_mid)
                mid_slot_idx = idx
                midfielder = your_squad[idx - 1]
                _, mid_rating = self.chemistry(midfielder.get("display"))
                atttag = "you"
                deftag = "opp"
                attacking_team = your_team

            elif generate_chance >= opp_chance and opp_mid:
                idx = random.choice(opp_mid)
                mid_slot_idx = idx
                midfielder = opp_squad[idx - 1]
                _, mid_rating = self.chemistry(midfielder.get("display"), opponent=True)
                attacking_team = opp_team
                atttag = "opp"
                deftag = "you"

            # If a chance is created, resolve it with attacker vs defender and xG
            if attacking_team and midfielder:
                add_commentary(f"{match_min}': {midfielder.get('display', midfielder['name'])} on the ball for {attacking_team}...", atttag)
                self.root.after(int(1 * self.sim_speed))
                # Midfield duel setup
                if attacking_team == your_team:
                    def_mid_pool = opp_mid
                    def_squad = opp_squad
                    def_is_opp = True
                else:
                    def_mid_pool = your_mid
                    def_squad = your_squad
                    def_is_opp = False
                d_idx = random.choice(def_mid_pool)
                def_mid = def_squad[d_idx - 1]
                _, def_mid_rating = self.chemistry(def_mid.get("display"), opponent=def_is_opp)
                att_roll = random.randint(1, 60)
                def_roll = random.randint(1, 60)
                if att_roll - def_roll <= (mid_rating - def_mid_rating) *1.5:
                    add_commentary(f"{match_min}': {midfielder.get('display', midfielder['name'])} creates a chance...", atttag) 
                    self.match_ratings[midfielder["name"]] += 0.4
                    self.match_ratings[def_mid["name"]] -= 0.4 
                    self.root.after(int(1 * self.sim_speed))
                    
                    # Weighted attacker pick using approach play (+ optional steering by defending width)
                    if attacking_team == your_team:
                        # your attack, they defend
                        gk_involved = opp_gk
                        ap_src = your_tactics
                        ap = (ap_src.get("approach") or {})
                        ap_left  = bool(ap.get("left", False))
                        ap_mid   = bool(ap.get("middle", True))
                        ap_right = bool(ap.get("right", False))

                        pool = []
                        # optional steering: against narrow width, favour wide (LW/RW/side CM). Against wide width, favour central (ST/middle CM)
                        def_width = (opp_tactics.get("defensive width") or "Balanced").lower()
                        for slot_idx in your_att:
                            pos = your_slots[slot_idx]["position"]

                            if pos == "ST":
                                side = "middle"
                            elif pos == "LW":
                                side = "left"
                            elif pos == "RW":
                                side = "right"

                            elif pos == "CM":
                                # All CM slots that are actually in the attacking pool
                                cm_slots = [i for i in your_att if your_slots[i]["position"] == "CM"]
                                cm_slots = sorted(set(cm_slots))

                                if len(cm_slots) == 1:
                                    # Single CM → central
                                    side = "middle"

                                elif len(cm_slots) == 2:
                                    # Two CMs → lower index = left, higher = right
                                    side = "left" if slot_idx == cm_slots[0] else "right"

                                else:
                                    # Three or more CMs → leftmost, rightmost, rest middle
                                    left_idx  = cm_slots[0]
                                    right_idx = cm_slots[-1]
                                    if slot_idx == left_idx:
                                        side = "left"
                                    elif slot_idx == right_idx:
                                        side = "right"
                                    else:
                                        side = "middle"

                            else:
                                # Any other attacking-role player (FB/WB/AM that joins attack)
                                side = "right"

                            mult = 1
                            if ap_left and not ap_mid and not ap_right:
                                mult = 3 if side == "left" else 1
                            elif ap_mid and not ap_left and not ap_right:
                                mult = 3 if side == "middle" else 1
                            elif ap_right and not ap_left and not ap_mid:
                                mult = 3 if side == "right" else 1
                            elif ap_left and ap_mid and not ap_right:
                                mult = 2 if side in ("left", "middle") else 1
                            elif ap_mid and ap_right and not ap_left:
                                mult = 2 if side in ("middle", "right") else 1
                            else:
                                mult = 1

                            if def_width == "narrow":
                                if side == "middle":         mult = max(1, mult - 1)
                                else:                        mult += 1
                            elif def_width == "wide":
                                if side in ("left","right"): mult = max(1, mult - 1)
                                else:                         mult += 1

                            pool.extend([slot_idx] * mult)

                        att_slot = random.choice(pool) if pool else random.choice(your_att)
                        attacker = your_squad[att_slot - 1]
                        _, att_rating = self.chemistry(attacker.get("display"))
                        defender = opp_squad[random.choice(opp_def) - 1]
                        _, def_rating = self.chemistry(defender.get("display"), opponent=True)
                    else:
                        # their attack, you defend
                        gk_involved = your_gk
                        ap_src = opp_tactics if isinstance(opponent, dict) else {}
                        ap = (ap_src.get("approach") or {})
                        ap_left  = bool(ap.get("left", False))
                        ap_mid   = bool(ap.get("middle", True))
                        ap_right = bool(ap.get("right", False))

                        pool = []
                        def_width = (your_tactics.get("defensive width") or "Balanced").lower()
                        for slot_idx in opp_att:
                            pos  = opp_slots[slot_idx]["position"]

                            if pos == "ST":
                                side = "middle"
                            elif pos == "LW":
                                side = "left"
                            elif pos == "RW":
                                side = "right"
                            elif pos == "CM":
                                cm_slots = [i for i in opp_att if opp_slots[i]["position"] == "CM"]
                                cm_slots = sorted(set(cm_slots))

                                if len(cm_slots) == 1:
                                    side = "middle"
                                elif len(cm_slots) == 2:
                                    side = "left" if slot_idx == cm_slots[0] else "right"
                                else:
                                    left_idx  = cm_slots[0]
                                    right_idx = cm_slots[-1]
                                    if slot_idx == left_idx:
                                        side = "left"
                                    elif slot_idx == right_idx:
                                        side = "right"
                                    else:
                                        side = "middle"
                            else:
                                side = "right"

                            mult = 1
                            if ap_left and not ap_mid and not ap_right:
                                mult = 3 if side == "left" else 1
                            elif ap_mid and not ap_left and not ap_right:
                                mult = 3 if side == "middle" else 1
                            elif ap_right and not ap_left and not ap_mid:
                                mult = 3 if side == "right" else 1
                            elif ap_left and ap_mid and not ap_right:
                                mult = 2 if side in ("left", "middle") else 1
                            elif ap_mid and ap_right and not ap_left:
                                mult = 2 if side in ("middle", "right") else 1
                            else:
                                mult = 1

                            if def_width == "narrow":
                                if side in ("left","right"): mult = max(1, mult - 1)
                                else:                         mult += 1
                            elif def_width == "wide":
                                if side == "middle":         mult = max(1, mult - 1)
                                else:                        mult += 1

                            pool.extend([slot_idx] * mult)

                        att_slot = random.choice(pool) if pool else random.choice(opp_att)
                        attacker = opp_squad[att_slot - 1]
                        _, att_rating = self.chemistry(attacker.get("display"), opponent=True)
                        defender = your_squad[random.choice(your_def) - 1]
                        _, def_rating = self.chemistry(defender.get("display"))

                    # xG model with randomised factors to keep outcomes varied
                    mid_gap = mid_rating - def_mid_rating          # your CM vs their CM
                    mid_factor = 0.65 + 0.02 * mid_gap
                    mid_factor = max(0.6, min(1.4, mid_factor)) 

                    # pick attacker-side factor ranges
                    if attacking_team == your_team:
                        dlow, dhigh = your_dist_range
                        plow, phigh = your_press_range
                        clow, chigh = your_chaos_range
                        att_tac, def_tac = your_tactics, opp_tactics
                    else:
                        dlow, dhigh = opp_dist_range
                        plow, phigh = opp_press_range
                        clow, chigh = opp_chaos_range
                        att_tac, def_tac = opp_tactics, your_tactics

                    # neutral (medium) factors for this attacking setup
                    dmid = (dlow + dhigh) / 2.0
                    pmid = (plow + phigh) / 2.0
                    cmid = (clow + chigh) / 2.0

                    distance_factor = random.uniform(dlow, dhigh)
                    pressure_factor = random.uniform(plow, phigh)
                    chaos_factor    = random.uniform(clow, chigh)

                    # Defensive counters (press + defensive line) applied to attacker factors
                    # Press advantage trims pressure & chaos
                    press_delta = _rank_press(def_tac.get("press")) - _rank_press(att_tac.get("press"))
                    if press_delta >= 1:
                        pressure_factor *= max(0.80, 1.0 - 0.08 * press_delta)
                        chaos_factor    *= max(0.85, 1.0 - 0.05 * press_delta)

                    # Defensive line vs attacker directness: deep counters direct, high counters short
                    line_rank = _rank_line(def_tac.get("defensive line"))
                    direct_r  = _rank_direct(att_tac.get("directness"))
                    # line_rank: 0 - much deeper, 1 - deeper, 2 - balanced, 3 - higher, 4 - much higher
                    # direct_r: 0 - much shorter, 1 - less direct, 2 - balanced, 3 - more direct, 4 - much more direct 
                    if line_rank <= 1 and direct_r >= 3:  # Deep vs direct, defender boost 
                        if (line_rank == 0 and direct_r == 4):
                            distance_factor *= 0.7
                        elif (line_rank == 1 and direct_r == 3):
                            distance_factor *= 0.8
                        else:
                            distance_factor *= 0.9
                    elif line_rank >= 3 and direct_r <= 1:  # High vs short, defender boost
                        if (line_rank == 4 and direct_r == 0):
                            pressure_factor *= 0.75
                        elif (line_rank == 3 and direct_r == 1):
                            pressure_factor *= 0.85
                        else:
                            pressure_factor *= 0.93
                    elif line_rank <= 1 and direct_r <= 1:
                        if (line_rank == 0 and direct_r == 0):
                            pressure_factor *= 1.3
                        elif (line_rank == 1 and direct_r == 1):
                            pressure_factor *= 1.2
                        else:
                            pressure_factor *= 1.1
                    elif line_rank >= 3 and direct_r >= 3:
                        if (line_rank == 4 and direct_r == 4):
                            distance_factor *= 1.25
                        elif (line_rank == 3 and direct_r == 3):
                            distance_factor *= 1.15
                        else:
                            distance_factor *= 1.07
                    elif direct_r == 2 and line_rank != 2:
                        # Balanced directness vs non-balanced line: mixed effect
                        if line_rank <= 1:
                            # deeper / much deeper: slightly increase distance (distance down), slightly decrease pressure (pressure up)
                            if line_rank == 0:
                                distance_factor *= 0.95
                                pressure_factor *= 1.05
                            else:  # line_rank == 1
                                distance_factor *= 0.97
                                pressure_factor *= 1.02
                        elif line_rank >= 3:
                            # higher / much higher: slightly decrease distance (distance up), slightly increase pressure (pressure down)
                            if line_rank == 4:
                                distance_factor *= 1.04
                                pressure_factor *= 0.96
                            else:  # line_rank == 3
                                distance_factor *= 1.02
                                pressure_factor *= 0.98
                    elif line_rank == 2 and direct_r != 2:
                        # Balanced line vs non-balanced directness: small trade-off on distance & pressure
                        if direct_r <= 1:
                            # attacker plays short / much shorter:
                            # slightly further away (distance down) but also slightly less pressure (pressure up)
                            if direct_r == 0:
                                distance_factor *= 0.98
                                pressure_factor *= 1.02
                            else:  # direct_r == 1
                                distance_factor *= 0.99
                                pressure_factor *= 1.01
                        elif direct_r >= 3:
                            # attacker plays direct / much more direct:
                            # slightly more space in behind (distance up) but less time on ball (pressure down)
                            if direct_r == 4:
                                distance_factor *= 1.04
                                pressure_factor *= 0.96
                            else:  # direct_r == 3
                                distance_factor *= 1.02
                                pressure_factor *= 0.98

                    # Centre around the medium but allow very high ceilings
                    base_product   = max(1e-4, dmid * pmid * cmid)
                    actual_product = distance_factor * pressure_factor * chaos_factor
                    rel = actual_product / base_product

                    # Extremes: allow very low (0.25×) and very high (3.0×) around the medium
                    rel = max(0.25, min(3.0, rel))

                    # Neutral xG at this midfield strength
                    # Slightly bigger scale so top chances still hit around 0.9–0.95 after multipliers
                    xg_mid = 0.04 + 0.30 * mid_factor

                    xg = xg_mid * rel

                    # Defensive width vs approach: direct xG counter (after factors)
                    xg *= _approach_vs_width_factor(att_tac, def_tac)

                    # noise + clamps
                    xg += random.uniform(-0.05, 0.05)
                    xg = max(0.01, min(0.99, xg))

                    xg_total[attacking_team] += xg
                    shots[attacking_team] += 1

                    add_commentary(f"{match_min}': {attacker.get('display', attacker['name'])} shoots...", atttag)
                    self.root.after(int(1 * self.sim_speed))

                    att_role_rating = self.role_rating(attacker.get("display"), attacker["role"])
                    def_role_rating = self.role_rating(defender.get("display"), defender["role"])
                    if attacking_team == your_team:
                        # Their keeper is defending your attack
                        gk_player = opp_squad[gk_involved - 1]
                        _, gk_role_rating = self.chemistry(gk_player.get("display"), opponent=True)
                    else:
                        # Your keeper is defending their attack
                        gk_player = your_squad[gk_involved - 1]
                        _, gk_role_rating = self.chemistry(gk_player.get("display"), opponent=False)

                    # Difference between attacker and defender
                    involvement = random.randint(0, 10) / 10
                    def_involvement = def_role_rating *(1 - involvement)
                    gk_involvement = gk_role_rating * involvement
                    rating_gap = att_role_rating - (gk_involvement + def_involvement)

                    # Better attacker / defender scores/defends better chances
                    mult = 1 + 0.035 * rating_gap
                    goal_prob = xg * mult
                    
                    # Noise
                    goal_prob += random.uniform(-0.02, +0.06)

                    # Clamp final probability
                    goal_prob = max(0.01, min(0.99, goal_prob))

                    # Outcome: goal or save/block, ratings nudged accordingly
                    if xg < 0.05:
                        matchratingchange = 0.1
                    elif xg >= 0.95:
                        matchratingchange = 0.9
                    else:
                        matchratingchange = round(xg, 1)
                    if random.random() <= goal_prob:
                        score[attacking_team] += 1
                        # Track goals and assists for the ratings pitch view
                        try:
                            scorer_name = attacker["name"]
                            assister_name = midfielder["name"]
                            self.last_goal_counts[scorer_name] = self.last_goal_counts.get(scorer_name, 0) + 1
                            self.last_assist_counts[assister_name] = self.last_assist_counts.get(assister_name, 0) + 1
                        except Exception:
                            pass
                        msg = f"{match_min}': ⚽ GOAL FOR {attacking_team.upper()}! {attacker.get('display', attacker['name'])} SCORES! (xG: {xg:.2f})"
                        self.match_ratings[attacker["name"]] += 2 * (1 - matchratingchange)
                        self.match_ratings[defender["name"]] -= round(matchratingchange * (1-involvement), 1)
                        self.match_ratings[gk_player["name"]] -= round(matchratingchange * (1-involvement), 1)
                        self.root.after(int(1.5 * self.sim_speed))
                    else:
                        if involvement > 0.5:
                            action = "SAVED"
                            def_or_gk = gk_player.get("display", gk_player["name"])
                        elif involvement == 0.5:
                            if random.randint(1,2) == 1:
                                action = "SAVED"
                                def_or_gk = gk_player.get("display", gk_player["name"])               
                            else:
                                action = "BLOCKED"
                                def_or_gk = defender.get("display", defender["name"])
                        else:
                            action = "BLOCKED"
                            def_or_gk = defender.get("display", defender["name"]) 
                        msg = f"{match_min}': {action} BY {def_or_gk.upper()}! (xG: {xg:.2f})"
                        self.match_ratings[attacker["name"]] -= matchratingchange
                        self.match_ratings[defender["name"]] += round(2 * matchratingchange * (1-involvement), 1)
                        self.match_ratings[gk_player["name"]] += round(2 * matchratingchange * (1-involvement),1)
                        self.root.after(int(1 * self.sim_speed))
                        placeholder = atttag
                        atttag = deftag
                        deftag = placeholder
                    add_commentary(msg, atttag)
                    match_log.append(msg)
                    self.root.after(int(1 * self.sim_speed))
                else:
                    # Turnover if the creation roll fails
                    add_commentary(f"{match_min}': Dispossessed", deftag)
                    self.match_ratings[midfielder["name"]] -= 0.4
                    self.match_ratings[def_mid["name"]] += 0.4 
                    self.root.after(int(1 * self.sim_speed))

            # Small per-minute delay to avoid freezing the UI
            self.root.after(int(0.1 * self.sim_speed))

        # Clamp all ratings to 1 - 10 before finishing
        for name in self.match_ratings:
            self.match_ratings[name] = max(1, min(10, self.match_ratings[name]))

        # Final screen update and full time banner
        update_display(90)
        add_commentary("\n--- FULL TIME ---", "default")

        # Store full-time data and wait for user to press Continue
        self.fulltime_pending = True
        self._fulltime_args = (
            your_team, opp_team, score, shots, xg_total,
            match_log, your_squad, opp_squad
        )

        try:
            self.pause_btn.config(
                text="➤",
                font=("Arial", 22, "bold"),
                bg=self.colors['accent'],
                fg=self.colors['text'],
                activebackground=self.colors['highlight'],
                activeforeground=self.colors['text'],
                relief=tk.RAISED,
                bd=2
            )
        except Exception:
            pass
    
    # Ratings screen
    def show_match_ratings(self, is_opponent=False):
        # Load team and opponent records
        data = core.readteamdata("team", self.edit)
        opp = core.readteamdata("opponent", self.edit)
        yoursquad = data["players"]
        oppsquad = opp["players"]
        your = data["team"]
        their = opp["team"]

        # Pull last-match variables if they exist
        score = getattr(core, "last_score", {your: 0, their: 0})
        shots = getattr(core, "last_shots", {your: 0, their: 0})
        xg_total = getattr(core, "last_xg_total", {your: 0.0, their: 0.0})
        matchlog = getattr(core, "last_matchlog", [])
        matchratings = getattr(core, "matchratings", {})

        # Helper to write lines into the GUI commentary widget
        def write_to_gui(text):
            self.commentary_text.config(state=tk.NORMAL)
            self.commentary_text.insert(tk.END, text)
            self.commentary_text.see(tk.END)
            self.commentary_text.config(state=tk.DISABLED)
            self.root.update_idletasks()

        # Run the CLI print routine with stdout redirected into the widget
        with self._redirect_stdio_to_gui(write_to_gui):
            core.showratings(
                score, shots, xg_total, matchlog, matchratings,
                your, their, yoursquad, oppsquad,
                opponent=is_opponent
            )
    
    # Full-time options page: see ratings, then continue to rewards and league progression
    def show_fulltime_options(self, your_team, opp_team, score, shots, xg_total, match_log, your_squad, opp_squad):
        self.clear_window()
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['secondary'], height=80)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="FULL TIME",
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Arial', 24, 'bold')
        ).pack(pady=20)
        
        # Result lines
        result_frame = tk.Frame(self.root, bg=self.colors['bg'])
        result_frame.pack(pady=30)
        
        self.create_label(result_frame, f"{your_team} {score[your_team]} - {score[opp_team]} {opp_team}", font_size=20, bold=True).pack(pady=10)
        self.create_label(result_frame, f"Shots: {shots[your_team]} - {shots[opp_team]}", font_size=12).pack(pady=5)
        self.create_label(result_frame, f"xG: {xg_total[your_team]:.2f} - {xg_total[opp_team]:.2f}", font_size=12).pack(pady=5)
        
        # Buttons to view ratings or proceed
        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.pack(pady=20)
        
        self.create_button(button_frame, "View Player Ratings", lambda: self.show_match_ratings_pitch(False)).pack(pady=5)
        self.create_button(button_frame, "View Opponent Ratings", lambda: self.show_match_ratings_pitch(True)).pack(pady=5)
        self.create_button(button_frame, "Continue", lambda: self.process_match_rewards(score, your_team, opp_team)).pack(pady=5)
    
    # Modal listing of player ratings for either your XI or the opponent XI
    def show_match_ratings(self, squad, is_opponent):
        dialog = tk.Toplevel(self.root)
        dialog.title("Player Ratings")
        dialog.geometry("500x700")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        team_name = "Opponent" if is_opponent else self.team_name
        
        tk.Label(
            dialog,
            text=f"{team_name.upper()} PLAYER RATINGS",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        ).pack(pady=20)

        # Simple vertical stack: starting XI only
        ratings_frame = tk.Frame(dialog, bg=self.colors['bg'])
        ratings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for player in squad[:11]:
            rating = self.match_ratings.get(player.get("name", ""), 6.6)
            pos = player.get("position", "?")
            name = player.get("display", player.get("name", "?"))

            player_frame = tk.Frame(
                ratings_frame,
                bg=self.colors['accent'],
                relief=tk.RAISED,
                bd=1
            )
            player_frame.pack(pady=5, fill=tk.X)

            tk.Label(
                player_frame,
                text=f"{pos} – {rating:.1f}/10 – {name}",
                bg=self.colors['accent'],
                fg=self.colors['text'],
                font=('Arial', 11)
            ).pack(padx=15, pady=8)

        self.create_button(dialog, "Close", dialog.destroy, width=15).pack(pady=10)
    
    # After the match finishes, award coins and league points, then advance the season
    def process_match_rewards(self, score, your_team, opp_team):
        # Pull the starting elevens
        your_squad = self.read_team_data("squad", self.edit)[:11]
        opp_data = self.read_team_data("opponent", self.edit)
        opp_squad = opp_data.get("players", [])[:11]

        # Compute simple average OVRs for reward scaling
        your_team_rating = sum(p.get("rating", 0) for p in your_squad) / 11
        opp_team_rating  = sum(p.get("rating", 0) for p in opp_squad) / 11

        # Scoreline components
        goals_scored   = score[your_team]
        goals_conceded = score[opp_team]

        # League points (W=3, D=1, L=0)
        points_before = self.points
        if goals_scored > goals_conceded:
            self.points += 3
            result_text = "Win"
        elif goals_scored == goals_conceded:
            self.points += 1
            result_text = "Draw"
        else:
            result_text = "Loss"

        # Base coins depending on outcome and rating difference
        if goals_scored > goals_conceded:
            if your_team_rating > opp_team_rating:
                base_earned = 100
            elif abs(your_team_rating - opp_team_rating) < 1e-9:
                base_earned = 150
            else:
                base_earned = 200
        elif goals_scored == goals_conceded:
            if your_team_rating > opp_team_rating:
                base_earned = 25
            elif abs(your_team_rating - opp_team_rating) < 1e-9:
                base_earned = 50
            else:
                base_earned = 75
        else:
            base_earned = 0

        # Bonus for goals scored, penalty for goals conceded
        goals_for_bonus   = goals_scored * 10
        goals_against_pen = goals_conceded * 10

        # Calculate net coin change
        earned = base_earned + goals_for_bonus - goals_against_pen

        # Persist season progress (games remaining, points, coins)
        self.games_remaining -= 1
        coins_before = self.coins

        # Apply earnings and prevent negative balance
        self.coins += earned
        if self.coins < 0:
            self.coins = 0
        self.write_team_data(str(self.games_remaining), "gamesremaining", self.edit)
        self.write_team_data(str(self.points),         "points",        self.edit)
        self.write_team_data(str(self.coins),          "coins",         self.edit)

        # Clear the built opponent so a fresh one is made next time
        self.remove_opponent()

        # Rewards dialog summarising the week’s outcome
        dlg = tk.Toplevel(self.root)
        dlg.title("Match Rewards")
        dlg.geometry("450x450")
        dlg.configure(bg=self.colors['bg'])
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(
            dlg, text="REWARDS",
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Arial', 18, 'bold')
        ).pack(pady=16)

        def add_line(text, colour):
            tk.Label(dlg, text=text, bg=self.colors['bg'], fg=colour, font=('Arial', 13)).pack(anchor='w', padx=30, pady=2)

        add_line(f"Match result: +{base_earned} coins",
                self.colors['success'] if result_text == "Win" else self.colors['text'])

        add_line(f"Goals scored: +{goals_for_bonus} coins", self.colors['success'])
        add_line(f"Goals conceded: -{goals_against_pen} coins", self.colors['warning'])

        tk.Label(
            dlg,
            text=f"Total earned: {earned:+} coins",
            bg=self.colors['bg'],
            fg=(self.colors['success'] if earned >= 0 else "#ff4444"),
            font=('Arial', 14, 'bold'),
            anchor='center',
            justify='center'
        ).pack(pady=12)

        tk.Label(dlg, text="───────────────", bg=self.colors['bg'], fg=self.colors['subtext']).pack(pady=4)
        add_line(f"Points: {points_before} → {self.points}", self.colors['text'])
        add_line(f"Coins:  {coins_before} → {self.coins}",   self.colors['text'])
        add_line(f"Games remaining: {self.games_remaining}", self.colors['text'])

        def _close_and_continue():
            dlg.destroy()
            if self.games_remaining <= 0:
                self.process_end_of_season()
            else:
                self.show_play_page()

        self.create_button(dlg, "Continue", _close_and_continue, width=16).pack(pady=16)

    def _get_thresholds_for_division(self, division=None):
        # Division dependant thresholds
        if division is None:
            division = self.division

        # Relegation thresholds
        if division == 10:
            relegation_threshold = 7
        elif division == 9:
            relegation_threshold = 8
        elif division == 8:
            relegation_threshold = 8
        elif division == 7:
            relegation_threshold = 9
        elif division == 6:
            relegation_threshold = 9
        elif division == 5:
            relegation_threshold = 10
        elif division == 4:
            relegation_threshold = 10
        elif division == 3:
            relegation_threshold = 11
        elif division == 2:
            relegation_threshold = 11
        else: 
            relegation_threshold = 12

        # Promotion thresholds
        if division == 10:
            promotion_threshold = 14
        elif division == 9:
            promotion_threshold = 15
        elif division == 8:
            promotion_threshold = 15
        elif division == 7:
            promotion_threshold = 16
        elif division == 6:
            promotion_threshold = 16
        elif division == 5:
            promotion_threshold = 17
        elif division == 4:
            promotion_threshold = 17
        elif division == 3:
            promotion_threshold = 18
        elif division == 2:
            promotion_threshold = 18
        else: 
            promotion_threshold = 100 

        # Title thresholds
        if division == 10:
            title_threshold = 23
        elif division == 9:
            title_threshold = 24
        elif division == 8:
            title_threshold = 24
        elif division == 7:
            title_threshold = 24
        elif division == 6:
            title_threshold = 25
        elif division == 5:
            title_threshold = 25
        elif division == 4:
            title_threshold = 25
        elif division == 3:
            title_threshold = 26
        elif division == 2:
            title_threshold = 26
        else: 
            title_threshold = 26

        return relegation_threshold, promotion_threshold, title_threshold
    
    # End-of-season logic: promotion/relegation, rewards, and reset counters
    def process_end_of_season(self):
        relegation_threshold, promotion_threshold, title_threshold = \
            self._get_thresholds_for_division(self.division)
        end_of_season_rewards = 0
        message = ""

        # Relegation case
        if self.points < relegation_threshold:
            if self.division < 10:  # only relegate if there is a lower division
                self.division += 1
                message = f"You have been relegated to Division {self.division}"
                end_of_season_rewards = 0
            else:
                message = f"You have stayed in Division {self.division}"
                end_of_season_rewards = 500

        # Title + possible promotion
        elif self.points >= title_threshold:
            message = "You have won the title!"
            if self.division > 1:
                self.division -= 1
                message += f"\nYou have been promoted to Division {self.division}"
            rewards_by_div = {1: 3250, 2: 3000, 3: 2750, 4: 2500, 5: 2250, 6: 2000, 7: 1750, 8: 1500, 9: 1250}
            end_of_season_rewards = rewards_by_div.get(self.division, 1000)

        # Promotion without title
        elif self.points >= promotion_threshold:
            if self.division > 1:
                self.division -= 1
                message = f"You have been promoted to Division {self.division}"
            else:
                message = f"You have stayed in Division {self.division}"
            end_of_season_rewards = 1000

        # Neither promoted nor relegated
        else:
            message = f"You have stayed in Division {self.division}"
            if self.division == 1:
                end_of_season_rewards = 1000
            else:
                end_of_season_rewards = 500

        # Update totals for the new season
        self.coins += end_of_season_rewards
        self.games_remaining = 10
        self.points = 0

        # Clamp division into the valid range 1 - 10 before saving
        try:
            self.division = int(self.division)
        except Exception:
            pass
        self.division = max(1, min(10, self.division))

        # Persist new season state
        self.write_team_data(str(self.division), "division", self.edit)
        self.write_team_data(str(self.games_remaining), "gamesremaining", self.edit)
        self.write_team_data(str(self.points), "points", self.edit)
        self.write_team_data(str(self.coins), "coins", self.edit)

        # Summary dialog for season outcome and reward
        dialog = tk.Toplevel(self.root)
        dialog.title("End of Season")
        dialog.geometry("450x350")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="END OF SEASON",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 20, 'bold'),
            anchor='center',
            justify='center'
        ).pack(pady=30, anchor='center')

        tk.Label(
            dialog,
            text=message,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 12),
            anchor='center',
            justify='center'
        ).pack(pady=20, anchor='center')

        tk.Label(
            dialog,
            text=f"Season Rewards: +{end_of_season_rewards} coins",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold'),
            anchor='center',
            justify='center'
        ).pack(pady=15, anchor='center')

        self.create_button(dialog, "Continue", lambda: [dialog.destroy(), self.show_play_page()]).pack(pady=20)

    def show_settings(self):
        # Settings window:
        # - Stage team/manager name changes, only write to file when Save is pressed.
        # - Adjust match speed between 0.5× and 4.0× (lower delay per tick = faster sim).
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("560x400")
        win.configure(bg=self.colors['bg'])
        win.transient(self.root)
        win.grab_set()

        # Title
        tk.Label(
            win, text="Settings", bg=self.colors['bg'], fg=self.colors['text'],
            font=('Arial', 18, 'bold')
        ).pack(pady=(16, 8))

        # Card container for tidy layout
        card = tk.Frame(win, bg=self.colors.get('card', self.colors['bg']))
        card.pack(fill="both", expand=True, padx=16, pady=12)

        # Staged values (don’t write to file until Save is pressed)
        pending_team_name = None
        pending_manager_name = None

        def change_team_name():
            nonlocal pending_team_name
            # Fetch last-saved name, fall back to a sensible default
            try:
                team = self.read_team_data("team", self.edit)
            except Exception:
                team = None
            saved = "My Team"
            if isinstance(team, dict):
                saved = team.get("name") or team.get("team") or saved
            elif isinstance(team, str) and team.strip():
                saved = team.strip()

            # If already staged, use that as the initial value
            initial = pending_team_name if pending_team_name else saved

            new_name = simpledialog.askstring(
                "Change Team Name", "Enter new team name:",
                initialvalue=initial, parent=win
            )
            # Only stage on OK (Cancel leaves it unchanged)
            if new_name is not None and new_name.strip():
                pending_team_name = new_name.strip()

        def change_manager_name():
            nonlocal pending_manager_name
            # Read manager info 
            try:
                team = self.read_team_data("team", self.edit)
            except Exception:
                team = {}
            mi = team.get("manager_info") if isinstance(team, dict) else None
            if not isinstance(mi, dict):
                mi = {}
            saved_mgr = mi.get("name")
            if not saved_mgr:
                try:
                    saved_mgr = self.read_team_data("manager", self.edit)
                except Exception:
                    saved_mgr = None
            saved_mgr = saved_mgr or "Manager"

            initial = pending_manager_name if pending_manager_name else saved_mgr

            new_name = simpledialog.askstring(
                "Change Manager Name", "Enter new manager name:",
                initialvalue=initial, parent=win
            )
            # Only stage on OK
            if new_name is not None and new_name.strip():
                pending_manager_name = new_name.strip()

        # Name change buttons
        mid = tk.Frame(card, bg=card['bg'])
        mid.pack(fill="x", pady=6)
        mid.grid_columnconfigure(0, weight=1)
        inner = tk.Frame(mid, bg=card['bg'])
        inner.grid(row=0, column=0)
        self.create_button(inner, "Change Team Name", change_team_name).pack(pady=6)
        self.create_button(inner, "Change Manager Name", change_manager_name).pack(pady=6)

        # Match speed control (0.5× to 4.0×)
        row3 = tk.Frame(card, bg=card['bg'])
        row3.pack(fill="x", pady=12)

        tk.Label(
            row3, text="Match Speed", bg=card['bg'], fg=self.colors['subtext'],
            font=('Arial', 11, 'bold')
        ).pack(anchor="center")

        # Work out current multiplier from existing sim speed and clamp to a safe range
        # Try to load a previously saved match speed from team data
        try:
            saved_mult = self.read_team_data("match speed", self.edit)
        except Exception:
            saved_mult = None
        # If the saved value is sensible, use it; otherwise fall back to sim speed
        if isinstance(saved_mult, (int, float)):
            try:
                current_mult = float(saved_mult)
            except Exception:
                current_mult = 1.0
        else:
            # Work out current multiplier from existing sim speed and clamp to a safe range
            try:
                current_mult = float(1000.0 / float(self.sim_speed))
            except Exception:
                current_mult = 1.0
        mult_var = tk.DoubleVar(value=current_mult)
        info_var = tk.StringVar()

        def _update_info_label(*_):
            # Show the multiplier and the implied per-tick delay (lower delay = faster)
            m = round(mult_var.get(), 2)
            delay = int(1000 / m)
            info_var.set(f"x{m:.2f}  ({delay} ms/tick)")

        _update_info_label()

        tk.Scale(
            row3,
            variable=mult_var, from_=0.5, to=4.0, resolution=0.05,
            orient="horizontal", length=360,
            bg=card['bg'], highlightthickness=0,
            troughcolor=self.colors.get('panel', '#1c2533'),
            fg=self.colors['text'],
            command=lambda _e: _update_info_label()
        ).pack(anchor="center", pady=(4, 2))

        tk.Label(
            row3, textvariable=info_var, bg=card['bg'],
            fg=self.colors['subtext'], font=('Arial', 10, 'italic')
        ).pack(anchor="center")

        # Footer (Save applies staged changes, Cancel discards them)
        footer = tk.Frame(win, bg=self.colors['bg'])
        footer.pack(fill="x", padx=16, pady=10)
        center = tk.Frame(footer, bg=self.colors['bg'])
        center.pack()

        def _save_and_close():
            # Apply match speed (stored as delay per tick in milliseconds)
            m = max(0.5, min(4.0, mult_var.get()))
            self.sim_speed = int(1000 / m)
            
            # Save chosen match speed as multiplier, not milliseconds
            try:
                self.write_team_data(m, "match speed", self.edit)
            except Exception:
                pass

            # Persist team name if staged 
            if pending_team_name:
                try:
                    team = self.read_team_data("team", self.edit)
                except Exception:
                    team = None
                cleaned = pending_team_name
                if isinstance(team, dict):
                    team["name"] = cleaned
                    team["team"] = team["name"]
                    self.write_team_data(team, "team", self.edit)
                else:
                    self.write_team_data(cleaned, "team", self.edit)

            # Persist manager name if staged 
            if pending_manager_name:
                try:
                    team = self.read_team_data("team", self.edit)
                except Exception:
                    team = {}
                mi = team.get("manager_info") if isinstance(team, dict) else None
                if not isinstance(mi, dict):
                    mi = {}
                mi["name"] = pending_manager_name
                if isinstance(team, dict):
                    team["manager_info"] = mi
                    team["manager"] = mi["name"] 
                    self.write_team_data(team, "team", self.edit)
                self.write_team_data(pending_manager_name, "manager", self.edit)

            # Close settings and refresh Home so the header reflects any changes
            try:
                win.destroy()
            finally:
                # Re-read team name from file for accuracy
                try:
                    team_rec = self.read_team_data("team", self.edit)
                except Exception:
                    team_rec = None
                if isinstance(team_rec, dict):
                    self.team_name = team_rec.get("name") or team_rec.get("team") or "My Team"
                elif isinstance(team_rec, str) and team_rec.strip():
                    self.team_name = team_rec.strip()
                else:
                    self.team_name = "My Team"
                self.show_home_page()

        self.create_button(center, "Save", _save_and_close).pack(side="left", padx=8)
        self.create_button(center, "Cancel", win.destroy).pack(side="left", padx=8)


    def quick_sell_value(self, rating):
        # Convert a player’s rating into a quicksell coin value.
        rating = int(rating)
        if rating < 50:
            return 0
        elif rating <= 54:
            return 10 + (rating - 50) * 5
        elif rating <= 64:
            return 10 + (rating - 55) * 10
        elif rating <= 74:
            return 120 + (rating - 65) * 20
        elif rating <= 82:
            return 320 + (rating - 75) * 150
        elif rating <= 87:
            return 1000 + (rating - 83) * 500
        else:
            return 10000 + (rating - 88) * 5000

def main():
    root = tk.Tk()
    app = FootballGameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    # Allow running this file directly
    main()