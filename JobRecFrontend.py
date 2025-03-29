"""
JobRecFrontend.py

This module implements the graphical user interface (GUI) for the JobRec system.
Built using Tkinter, the GUI allows users to input up to 5 skills and receive relevant job
recommendations based on live data from the Findwork API.

Features:
- Dark mode UI
- Skill input with validation
- Popup window to display detailed job listings
- Match scoring with color-coded labels
- "Search Again" functionality to reset inputs
"""
import tkinter as tk
from tkinter import messagebox, Toplevel
import threading
import time
import python_ta
from  JobrecBackend import load_api_key, fetch_jobs, build_graph, recommend_jobs


class JobRecApp:
    """
    A GUI application for recommending jobs based on user-inputted skills.
    Fetches jobs using a live API, builds a graph to assess relevance, and
    displays results in a popup window with match scoring and job details.
    """
    def __init__(self, root):
        """
        Initialize the main window of the application.

        Parameters:
            root (tk.Tk): The root window of the application.
        """
        self.root = root
        self.root.title("JobRec - Job Recommendation System")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e1e")

        self.jobs_raw = []

        # Colors
        self.bg = "#1e1e1e"
        self.fg = "#ffffff"
        self.entry_bg = "#2e2e2e"
        self.button_color = "#3399ff"
        self.match_colors = {"High": "#00ff99", "Medium": "#ffaa00", "Low": "#999999"}

        # Title
        self.title_label = tk.Label(root, text="🔍 JobRec - Smart Job Recommendations",
                                    font=("Segoe UI", 18, "bold"), bg=self.bg, fg=self.fg)
        self.title_label.pack(pady=20)

        # Instructions
        self.instruction = tk.Label(root, text="Enter up to 5 skills:",
                                    font=("Segoe UI", 12), bg=self.bg, fg=self.fg)
        self.instruction.pack()

        # Skill entries
        self.skill_entries = []
        for _ in range(5):
            entry = tk.Entry(root, width=40, font=("Segoe UI", 12),
                             bg=self.entry_bg, fg=self.fg, insertbackground=self.fg)
            entry.pack(pady=5)
            self.skill_entries.append(entry)

        # Buttons
        self.search_button = tk.Button(root, text="🚀 Find Jobs", font=("Segoe UI", 13),
                                       command=self.start_search,
                                       bg=self.button_color, fg="white")
        self.search_button.pack(pady=15)

        self.loading_label = tk.Label(root, text="", font=("Segoe UI", 11),
                                      bg=self.bg, fg=self.fg)
        self.loading_label.pack()

    def start_search(self):
        """
        Begin the job search process by collecting skills and launching a background thread
        to fetch and process job recommendations.
        """
        self.loading_label.config(text="Fetching jobs...")
        self.search_button.config(state="disabled")
        threading.Thread(target=self.perform_search).start()

    def perform_search(self):
        """
        Perform the full job recommendation pipeline:
        - Collect user skills
        - Load API key and fetch jobs
        - Build a graph and recommend jobs
        - Display results in a new window
        """
        skills = [entry.get().strip() for entry in self.skill_entries if entry.get().strip()]
        if not skills:
            messagebox.showerror("Error", "Please enter at least one skill.")
            self.loading_label.config(text="")
            self.search_button.config(state="normal")
            return

        api_key = load_api_key()
        if not api_key:
            messagebox.showerror("Error", "API key not found. Check your .env file.")
            return

        self.jobs_raw = fetch_jobs(" ".join(skills), api_key)
        graph = build_graph(skills, self.jobs_raw)
        top_jobs = recommend_jobs(graph, skills)

        time.sleep(1)
        self.loading_label.config(text="")
        self.search_button.config(state="normal")
        self.show_results_window(top_jobs)

    def reset_fields(self):
        """
        Clear all skill entries to allow a new search.
        """
        for entry in self.skill_entries:
            entry.delete(0, tk.END)

    def show_results_window(self, jobs):
        """
        Display the recommended jobs in a new popup window with detailed information.

        Parameters:
            jobs (list of tuple[str, int]): List of (job_title, match_score) pairs.
        """
        result_win = Toplevel(self.root)
        result_win.title("Recommended Jobs")
        result_win.configure(bg=self.bg)
        result_win.geometry("700x600")

        tk.Label(result_win, text="Top Recommended Jobs:", font=("Segoe UI", 14, "bold"),
                 bg=self.bg, fg=self.fg).pack(pady=10)

        frame = tk.Frame(result_win, bg=self.bg)
        frame.pack(fill="both", expand=True)

        if not jobs:
            tk.Label(frame, text="No jobs found.", font=("Segoe UI", 12),
                     bg=self.bg, fg=self.fg).pack(pady=10)
        else:
            for i, (job, score) in enumerate(jobs, 1):
                job_details = next((j for j in self.jobs_raw if f"{j['role']} at {j['company_name']}" in job), {})
                location = job_details.get("location", "N/A")
                job_type = job_details.get("employment_type", "N/A")
                date_posted = job_details.get("date_posted", "N/A")

                if "[Low Match]" in job:
                    label = "Low"
                elif score >= 6:
                    label = "High"
                elif score >= 3:
                    label = "Medium"
                else:
                    label = "Low"

                match_color = self.match_colors[label]

                info = (
                    f"{i}. {job}\n"
                    f"   📍 Location: {location} | 🧾 Type: {job_type} | 📅 Posted: {date_posted}\n"
                    f"   🔎 Match Level: {label}"
                )

                tk.Label(frame, text=info, font=("Segoe UI", 11),
                         fg=match_color, bg=self.bg, justify="left", wraplength=660).pack(
                    anchor="w", padx=20, pady=10)

                tk.Button(
                    result_win, text="🔄 Search Again", font=("Segoe UI", 11),
                    bg=self.button_color, fg="white",
                    command=lambda: [result_win.destroy(), self.reset_fields()]
                ).pack(pady=20)

# CHATGPT and Excersize 3/4 were both used in assisting our implementation for creating our GUI/ FrontEnd Module

if __name__ == '__main__':
    root = tk.Tk()
    app = JobRecApp(root)
    root.mainloop()

