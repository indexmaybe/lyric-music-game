import tkinter as tk
from tkinter import messagebox
import json
import os

# ====================================================
#              FILE SYSTEM CONFIGURATION
# ====================================================
DATA_FILE = "arcade_save.json"

def load_game_data():
    """Reads saved arcade metadata or initializes a fresh state."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"high_score": 0, "total_attempts": 0, "theme": "Arcade Purple"}

def save_game_data(data):
    """Saves telemetry data directly to a local configuration file."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error logging telemetry data: {e}")

# Load initial storage metrics
game_data = load_game_data()

# ====================================================
#                  GAME TRACKERS
# ====================================================
lives = 3
score = 0
hint_clicks = 0

# ====================================================
#                  COLOR THEMES
# ====================================================
THEMES = {
    "Arcade Purple": {"bg": "#1e1e2e", "card": "#282a36", "accent": "#ff79c6", "text": "#f8f8f2", "btn": "#ffb86c", "success": "#50fa7b"},
    "Matrix Green":  {"bg": "#000000", "card": "#0d1117", "accent": "#00ff00", "text": "#00ff00", "btn": "#30363d", "success": "#00ff00"},
    "Cyberpunk Red": {"bg": "#0f0f1a", "card": "#1a1a2e", "accent": "#ff0055", "text": "#00ffff", "btn": "#ff0055", "success": "#00ffff"}
}
current_theme = game_data.get("theme", "Arcade Purple")

# ====================================================
#                  ENGINE LOGIC
# ====================================================

def check_answer(event=None):
    """Evaluates the input field against the correct lyric."""
    global lives, score
    
    # If game is already inactive, block evaluations
    if lives <= 0 or submit_button["state"] == "disabled":
        return

    user_input = answer_entry.get().strip().lower()
    
    if user_input == "alive":
        score += 10
        if score > game_data["high_score"]:
            game_data["high_score"] = score
        
        save_game_data(game_data)
        
        # Immediate UI layout state update
        update_dashboard_display()
        messagebox.showinfo("🎉 CORRECT!", "Awesome job, Belal! You got it right! (+10 pts)")
        
        # Set clean finish state across inputs
        submit_button.config(state="disabled")
        answer_entry.config(state="disabled", fg=THEMES[current_theme]["success"])
        action_feedback_label.config(text="🏆 STAGE COMPLETE!.", fg=THEMES[current_theme]["success"])
        
    else:
        lives -= 1
        update_dashboard_display()
        action_feedback_label.config(text=f"⚠️ Negative match. Attempts remaining: {lives}", fg="#ff5555")
        
        if lives > 0:
            messagebox.showwarning("❌ WRONG", f"Oops! That's not the right lyric. You lost a life!")
            answer_entry.delete(0, tk.END)
        else:
            execute_game_over()

def execute_game_over():
    """Locks inputs down, updates logs, and shows game over elements."""
    game_data["total_attempts"] += 1
    save_game_data(game_data)
    
    stats_label.config(text=f"PLAYER: Belal  |  💀 LIVES: 0/3  |  🏆 SCORE: {score:04d}", fg="#ff5555")
    action_feedback_label.config(text="💀 INSERT COIN TO CONTINUE. GAME OVER.", fg="#ff5555")
    
    submit_button.config(state="disabled")
    answer_entry.config(state="disabled")
    restart_button.pack(pady=10)

def show_hint():
    """Handles incremental clue generation across user triggers."""
    global hint_clicks
    hint_clicks += 1
    
    if hint_clicks == 1:
        hint_label.config(text="💡 HINT 1: The song title contains the exact word missing here.")
    elif hint_clicks == 2:
        hint_label.config(text="💡 HINT 2: The word has 5 letters and ends with 'E'.")
    else:
        hint_label.config(text="💡 HINT 3: Rhymes with 'Arrive', starts with 'A'.")
        hint_button.config(state="disabled")

def reset_game_loop():
    """Restores data variables and active elements back to original states."""
    global lives, score, hint_clicks
    lives = 3
    score = 0
    hint_clicks = 0
    
    # Reset internal entry tracking states
    answer_entry.config(state="normal", fg=THEMES[current_theme]["text"])
    answer_entry.delete(0, tk.END)
    answer_entry.focus()
    
    submit_button.config(state="normal")
    hint_button.config(state="normal")
    
    # Hide and clear overlay texts
    restart_button.pack_forget()
    hint_label.config(text="")
    action_feedback_label.config(text="System online. Awaiting data parsing...", fg=THEMES[current_theme]["text"])
    
    update_dashboard_display()

def update_dashboard_display():
    """Triggers visual layout redraws to display matching tracking telemetry."""
    heart_display = "❤️" * lives if lives > 0 else "💀"
    stats_label.config(
        text=f"PLAYER: Belal  |  LIVES: {heart_display} ({lives}/3)  |  🏆 SCORE: {score:04d}",
        fg=THEMES[current_theme]["success"] if lives > 1 else "#ff5555"
    )
    meta_logs_label.config(
        text=f"📊 Session Diagnostics -> All-Time Best: {game_data['high_score']:04d} | Global Failures: {game_data['total_attempts']}"
    )

def apply_theme_selection(selected_name):
    """Changes colors across all UI components dynamically."""
    global current_theme
    current_theme = selected_name
    colors = THEMES[selected_name]
    
    # Save selection state
    game_data["theme"] = selected_name
    save_game_data(game_data)
    
    # Redraw main window containers
    root.configure(bg=colors["bg"])
    header_label.configure(bg=colors["bg"], fg=colors["accent"])
    song_title.configure(bg=colors["bg"], fg=colors["accent"])
    lyrics_prompt.configure(bg=colors["bg"], fg=colors["text"])
    hint_label.configure(bg=colors["bg"])
    action_feedback_label.configure(bg=colors["bg"])
    meta_logs_label.configure(bg=colors["card"], fg=colors["text"])
    
    # Redraw widgets and entry interfaces
    stats_label.configure(bg=colors["card"])
    answer_entry.configure(bg=colors["card"], fg=colors["text"], insertbackground=colors["text"])
    submit_button.configure(bg=colors["btn"], activebackground=colors["accent"])
    
    # Refresh stats layout safely
    update_dashboard_display()

# ====================================================
#              UI WINDOW ARCHITECTURE
# ====================================================
root = tk.Tk()
root.title("Horizons Custom Arcade Engine v3.0")
root.geometry("600x650")
root.resizable(False, False)


top_menu_bar = tk.Frame(root, bg="#282a36", height=30)
top_menu_bar.pack(fill="x", side="top")

theme_var = tk.StringVar(root)
theme_var.set(current_theme)
theme_dropdown = tk.OptionMenu(top_menu_bar, theme_var, *THEMES.keys(), command=apply_theme_selection)
theme_dropdown.config(bg="#44475a", fg="#ffffff", activebackground="#6272a4", highlightthickness=0, font=("Helvetica", 8))
theme_dropdown.pack(side="right", padx=10, pady=2)

theme_menu_label = tk.Label(top_menu_bar, text="🎨 ENGINE SKIN:", font=("Helvetica", 8, "bold"), fg="#ffffff", bg="#282a36")
theme_menu_label.pack(side="right", pady=2)


header_label = tk.Label(root, text="🎵 HORIZONS LYRIC ARCADE 🎵", font=("Courier", 18, "bold"))
header_label.pack(pady=15)

stats_label = tk.Label(root, text="", font=("Courier", 11, "bold"), padx=12, pady=6)
stats_label.pack(pady=5)

song_title = tk.Label(root, text="NOW PLAYING: Stayin' Alive - Bee Gees", font=("Helvetica", 11, "italic"))
song_title.pack(pady=10)

lyrics_prompt = tk.Label(
    root, 
    text="\"Whether you're a brother or whether you're a mother,\nyou're stayin' ______\"", 
    font=("Helvetica", 13), 
    justify="center"
)
lyrics_prompt.pack(pady=15)


answer_entry = tk.Entry(root, font=("Courier", 14, "bold"), justify="center", width=22, bd=2, relief="groove")
answer_entry.pack(pady=10)
answer_entry.bind("<Return>", check_answer) # Pressing Enter key submits the text box automatically

action_feedback_label = tk.Label(root, text="System online. Awaiting data parsing...", font=("Helvetica", 9, "italic"))
action_feedback_label.pack(pady=5)

# Functional Interactive Buttons
submit_button = tk.Button(root, text="SUBMIT TRACK ENTRY", font=("Helvetica", 11, "bold"), command=check_answer, padx=15, pady=6, cursor="hand2")
submit_button.pack(pady=10)

hint_button = tk.Button(root, text="🔍 DECODE CLUE HINT", font=("Helvetica", 9, "bold"), bg="#6272a4", fg="#ffffff", command=show_hint, cursor="hand2")
hint_button.pack(pady=5)

hint_label = tk.Label(root, text="", font=("Helvetica", 10, "italic"), fg="#f1fa8c", wraplength=450)
hint_label.pack(pady=8)

restart_button = tk.Button(root, text="🔄 REBOOT SESSION (PLAY AGAIN)", font=("Helvetica", 11, "bold"), bg="#ff5555", fg="#ffffff", command=reset_game_loop)

# Footer analytical status bars
meta_logs_label = tk.Label(root, text="", font=("Courier", 9), pady=4, relief="sunken", bd=1)
meta_logs_label.pack(fill="x", side="bottom")

# Boot up operations
apply_theme_selection(current_theme)
reset_game_loop()
#           window toggle 

is_wide_view = False 

is_wide_view = False

def toggle_window_layout():
    """Toggles the app geometry between compact view and widescreen mode."""
    global is_wide_view
    if not is_wide_view:
        root.geometry("900x650")  # Expand window width
        layout_toggle_btn.config(text="🖥️ SWITCH TO COMPACT VIEW")
        action_feedback_label.config(text="Layout modified: Widescreen mode active.", fg=THEMES[current_theme]["success"])
        is_wide_view = True
    else:
        root.geometry("600x650")  # Return to original size
        layout_toggle_btn.config(text="🖥️ SWITCH TO WIDESCREEN VIEW")
        action_feedback_label.config(text="Layout modified: Compact mode active.", fg=THEMES[current_theme]["text"])
        is_wide_view = False


layout_toggle_btn = tk.Button(
    root, 
    text="🖥️ SWITCH TO WIDESCREEN VIEW", 
    font=("Helvetica", 9, "bold"), 
    bg="#44475a", 
    fg="#ffffff", 
    command=toggle_window_layout,
    cursor="hand2"
)

layout_toggle_btn.pack(pady=5, before=meta_logs_label)

def simulate_telemetry_connection():
    """Simulates a background system sync handshake for the dashboard."""
    action_feedback_label.config(text="📡 SYNCING TELEMETRY METRICS WITH HORIZONS...", fg="#ffb86c")
    root.after(3000, finalize_connection_status)

def finalize_connection_status():
    """Updates the UI once the simulated handshake is complete."""
    action_feedback_label.config(text="✅ HORIZONS TELEMETRY SYNCED SUCCESSFULLY.", fg=THEMES[current_theme]["success"])

# 
root.after(1500, simulate_telemetry_connection)

# ====================================================
#                  ⏱️ TIMER TRACKERS
# ====================================================
time_left = 30 
time_running = False 

# ====================================================
#                  ⚙️ TIMER ENGINE LOGIC
# ====================================================
def start_countdown_engine():
    """Initializes and loops the countdown timer mechanics."""
    global time_left, time_running
    if time_running:
        return  
    time_running = True
    countdown_tick_loop()
    
def countdown_tick_loop():
    """Handles individual second deductions and updates layout metrics."""
    global time_left, time_running

    # Stop counting if player won or lost
    if lives <= 0 or submit_button["state"] == "disabled":
        time_running = False
        return

    if time_left > 0:
        time_left -= 1
        # Update our visible UI widget text
        timer_ui_label.config(text=f"⏰ CLOCK: {time_left:02d}s")
        
        # Change color to red if time is running low
        time_color = "#ff5555" if time_left <= 10 else "#f1fa8c"
        timer_ui_label.config(fg=time_color)
        
        root.after(1000, countdown_tick_loop)
    else: 
        time_running = False
        timer_ui_label.config(text="⏰ CLOCK: 00s", fg="#ff5555")
        execute_time_out()

def execute_time_out():
    """Triggered instantly when the countdown timer reaches zero."""
    global lives, time_running
    lives = 0
    time_running = False
    update_dashboard_display()

    action_feedback_label.config(text="⏳ TIME OUT - You ran out of time! Game over.", fg="#ff5555")
    submit_button.config(state="disabled")
    answer_entry.config(state="disabled")
    restart_button.pack(pady=10)

def inject_timer_reset():
    """Resets timer values and starts the countdown after a short delay."""
    global time_left, time_running
    time_left = 30
    time_running = False
    timer_ui_label.config(text="⏰ CLOCK: 30s", fg="#f1fa8c")
    root.after(2000, start_countdown_engine)

# ====================================================
#                  🖥️ VISIBLE TIMER UI
# ====================================================
timer_ui_label = tk.Label(
    root,
    text="⏰ CLOCK: 30s",
    font=("Courier", 14, "bold"),
    bg="#282a36",
    fg="#f1fa8c",
    padx=15,
    pady=5,
    relief="ridge",
    bd=2
)
# Place it neatly under the main stats panel
timer_ui_label.pack(pady=5)

def update_timer_theme_colors():
    """Syncs the timer panel with whichever engine skin is currently selected."""
    colors = THEMES[current_theme]
    timer_ui_label.config(bg=colors["card"]) 
    root.after(500, update_timer_theme_colors)

# ====================================================
#                  🚀 RUN ENGINE LOOPS
# ====================================================
# Start the theme sync loop
update_timer_theme_colors()

# Start the actual countdown engine initialization sequence
root.after(100, inject_timer_reset)

root.mainloop()