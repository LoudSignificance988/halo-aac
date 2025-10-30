import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from tkinter import ttk
import json
import os
import threading
import pyttsx3
from PIL import Image, ImageTk  # For handling custom images

PROFILE_FILE = "profiles.json"

# Load or create profiles
if os.path.exists(PROFILE_FILE):
    try:
        with open(PROFILE_FILE, "r") as f:
            profiles = json.load(f)
    except:
        profiles = {}
else:
    profiles = {}

# Default categories with emoji
CATEGORIES = {
    "Core": {
        "I": "👤", "You": "🫵", "He": "👨", "She": "👩",
        "We": "👥", "They": "👥", "Go": "🏃", "Want": "🤲",
        "Need": "✋", "Eat": "🍎", "Drink": "🥤",
        "Food": "🍽️", "Toilet": "🚽", "Help": "🆘", "Stop": "✋",
        "Yes": "✅", "No": "❌", "Hello": "👋", "Goodbye": "👋",
        "Thank you": "🙏"
    },
    "Food": {"Apple": "🍎", "Bread": "🍞", "Milk": "🥛", "Water": "💧", "Juice": "🧃"},
    "Feelings": {"Happy": "😊", "Sad": "😢", "Angry": "😡", "Tired": "😴", "Excited": "🤩"},
    "Places": {"Home": "🏠", "School": "🏫", "Park": "🏞️", "Bathroom": "🚽", "Kitchen": "🍳"}
}

class HaloAAC(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Halo AAC")
        self.geometry("650x650")

        self.current_user = None
        self.user_words = {}  # word -> emoji or custom image path

        # Profile selection
        self.profile_var = tk.StringVar()
        self.profile_menu = ttk.Combobox(self, textvariable=self.profile_var)
        self.profile_menu.pack(pady=5)
        self.update_profiles()
        self.profile_menu.bind("<<ComboboxSelected>>", self.load_profile)

        # Category selection
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(self, textvariable=self.category_var, values=list(CATEGORIES.keys()))
        self.category_menu.current(0)
        self.category_menu.pack(pady=5)
        self.category_menu.bind("<<ComboboxSelected>>", self.update_grid)

        # Word grid
        self.word_frame = tk.Frame(self)
        self.word_frame.pack(pady=10)

        # Message builder
        self.message_box = tk.Text(self, height=2, width=50)
        self.message_box.pack(pady=5)

        self.speak_button = tk.Button(self, text="Speak Message", command=self.speak_message)
        self.speak_button.pack(pady=2)

        self.clear_button = tk.Button(self, text="Clear Message", command=lambda: self.message_box.delete("1.0", tk.END))
        self.clear_button.pack(pady=2)

        # Add new word button
        self.add_word_button = tk.Button(self, text="Add New Word", command=self.add_word)
        self.add_word_button.pack(pady=5)

      

    def update_profiles(self):
        profile_list = list(profiles.keys()) + ["Create New Profile"]
        self.profile_menu['values'] = profile_list
        if profile_list:
            self.profile_menu.current(0)

    def load_profile(self, event=None):
        selected = self.profile_var.get()
        if selected == "Create New Profile":
            self.create_profile()
        else:
            self.current_user = selected
            self.user_words = profiles[self.current_user].get("favorite_words", {})
            self.update_grid()

    def create_profile(self):
        name = simpledialog.askstring("New Profile", "What's your name?")
        if not name:
            return
        profiles[name] = {"favorite_words": {}}
        self.current_user = name
        self.user_words = {}
        with open(PROFILE_FILE, "w") as f:
            json.dump(profiles, f, indent=2)
        self.update_profiles()
        self.update_grid()
        messagebox.showinfo("Profile Created", f"Profile '{name}' created!")

    def update_grid(self, event=None):
        for widget in self.word_frame.winfo_children():
            widget.destroy()

        category = self.category_var.get()
        default_words = CATEGORIES.get(category, {})
        all_words = {**default_words, **self.user_words}

        for i, (word, icon) in enumerate(all_words.items()):
            if icon.endswith(('.png', '.jpg', '.gif')):
                # custom image
                img = Image.open(icon)
                img = img.resize((40, 40))
                photo = ImageTk.PhotoImage(img)
                btn = tk.Button(self.word_frame, image=photo, text=word, compound="top",
                                command=lambda w=word: self.add_to_message(w))
                btn.image = photo  # keep reference
            else:
                # emoji
                btn = tk.Button(self.word_frame, text=f"{icon} {word}", width=12, height=2,
                                command=lambda w=word: self.add_to_message(w))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)

    def add_to_message(self, word):
        current_text = self.message_box.get("1.0", tk.END).strip()
        new_text = (current_text + " " + word).strip()
        self.message_box.delete("1.0", tk.END)
        self.message_box.insert(tk.END, new_text)

    def speak_message(self):
        message = self.message_box.get("1.0", tk.END).strip()
        if message:
            threading.Thread(target=self._speak_thread, args=(message,)).start()

    def _speak_thread(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()

    def add_word(self):
        if not self.current_user:
            messagebox.showwarning("No Profile", "Please select or create a profile first!")
            return
        word = simpledialog.askstring("Add Word", "Enter the new word:")
        if not word:
            return
        use_image = messagebox.askyesno("Custom Image", "Do you want to add a custom image for this word?")
        icon = ""
        if use_image:
            icon_path = filedialog.askopenfilename(title="Select image",
                                                   filetypes=[("Image Files", "*.png *.jpg *.gif")])
            if icon_path:
                icon = icon_path
            else:
                icon = "❓"  # fallback
        else:
            icon = "❓"  # fallback emoji if none selected

        self.user_words[word] = icon
        profiles[self.current_user]["favorite_words"] = self.user_words
        with open(PROFILE_FILE, "w") as f:
            json.dump(profiles, f, indent=2)
        self.update_grid()

if __name__ == "__main__":
    app = HaloAAC()
    app.mainloop()
