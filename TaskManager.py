import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as file:
                self.tasks = json.load(file)
        except FileNotFoundError:
            self.tasks = []

    def save_tasks(self):
        with open('tasks.json', 'w') as file:
            json.dump(self.tasks, file)

    def add_task(self, description, priority):
        task = {
            'id': len(self.tasks) + 1,
            'description': description,
            'priority': priority,
            'completed': False,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.tasks.append(task)
        self.save_tasks()

    def complete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task['id'] != task_id]
        self.save_tasks()

class TaskManagerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Gestionnaire de Tâches")
        self.task_manager = TaskManager()

        # Nouvelle palette de couleurs
        self.bg_color = "#f5f5f5"
        self.fg_color = "#333333"
        self.button_color = "#3498db"
        self.button_text_color = "white"
        self.high_priority_color = "#e74c3c"
        self.medium_priority_color = "#f39c12"
        self.low_priority_color = "#2ecc71"

        self.master.configure(bg=self.bg_color)
        self.create_widgets()
        self.refresh_task_list()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')  # Utilisation d'un thème plus moderne

        # Configuration des styles
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        style.configure("TButton", background=self.button_color, foreground=self.button_text_color, padding=5,
                        relief="flat")
        style.map("TButton", background=[('active', '#2980b9')])

        # Frame pour l'ajout de tâches
        add_frame = ttk.Frame(self.master, padding="10")
        add_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        ttk.Label(add_frame, text="Description:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.description_entry = ttk.Entry(add_frame, width=40, font=('Helvetica', 10))
        self.description_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(add_frame, text="Priorité:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.priority_combobox = ttk.Combobox(add_frame, values=["Basse", "Moyenne", "Haute"], state="readonly",
                                              font=('Helvetica', 10))
        self.priority_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.priority_combobox.set("Moyenne")

        ttk.Button(add_frame, text="Ajouter Tâche", command=self.add_task).grid(row=2, column=1, sticky=tk.E, pady=10)

        # Frame pour la liste de tâches
        list_frame = ttk.Frame(self.master, padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        # Configuration du Treeview
        style.configure("Treeview", background="white", foreground=self.fg_color, rowheight=25, fieldbackground="white")
        style.map('Treeview', background=[('selected', '#bdd2e6')])

        self.task_tree = ttk.Treeview(list_frame, columns=("ID", "Description", "Priorité", "Statut"), show="headings",
                                      style="Treeview")
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Description", text="Description")
        self.task_tree.heading("Priorité", text="Priorité")
        self.task_tree.heading("Statut", text="Statut")
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(list_frame, style="TFrame")
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        ttk.Button(button_frame, text="Marquer comme terminé", command=self.complete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_task).pack(side=tk.RIGHT, padx=5)

    def add_task(self):
        description = self.description_entry.get()
        priority = self.priority_combobox.get()
        if description:
            self.task_manager.add_task(description, priority)
            self.description_entry.delete(0, tk.END)
            self.refresh_task_list()
        else:
            messagebox.showwarning("Attention", "Veuillez entrer une description pour la tâche.")

    def complete_task(self):
        selection = self.task_tree.selection()
        if selection:
            task_id = int(self.task_tree.item(selection[0])['values'][0])
            if self.task_manager.complete_task(task_id):
                self.refresh_task_list()
        else:
            messagebox.showinfo("Info", "Veuillez sélectionner une tâche à marquer comme terminée.")

    def delete_task(self):
        selection = self.task_tree.selection()
        if selection:
            task_id = int(self.task_tree.item(selection[0])['values'][0])
            self.task_manager.delete_task(task_id)
            self.refresh_task_list()
        else:
            messagebox.showinfo("Info", "Veuillez sélectionner une tâche à supprimer.")

    def refresh_task_list(self):
        for i in self.task_tree.get_children():
            self.task_tree.delete(i)
        for task in self.task_manager.tasks:
            status = "Terminé" if task['completed'] else "En cours"
            tags = ()
            if task['priority'] == "Haute":
                tags = ("high_priority",)
            elif task['priority'] == "Moyenne":
                tags = ("medium_priority",)
            elif task['priority'] == "Basse":
                tags = ("low_priority",)
            self.task_tree.insert("", "end", values=(task['id'], task['description'], task['priority'], status),
                                  tags=tags)

        self.task_tree.tag_configure("high_priority", background=self.high_priority_color)
        self.task_tree.tag_configure("medium_priority", background=self.medium_priority_color)
        self.task_tree.tag_configure("low_priority", background=self.low_priority_color)
def main():
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()