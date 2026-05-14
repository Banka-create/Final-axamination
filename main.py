import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер задач")
        self.root.geometry("800x500")
        
        # Заголовок
        title_label = tk.Label(root, text="Менеджер задач", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)
        
        # Кнопки
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="➕ Добавить задачу", command=self.add_task, 
                  bg="green", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="🗑️ Удалить задачу", command=self.delete_task,
                  bg="red", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="✅ Изменить статус", command=self.change_status,
                  bg="blue", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Список задач
        columns = ("ID", "Название", "Статус", "Приоритет")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Статус", text="Статус")
        self.tree.heading("Приоритет", text="Приоритет")
        self.tree.column("ID", width=50)
        self.tree.column("Название", width=400)
        self.tree.column("Статус", width=150)
        self.tree.column("Приоритет", width=100)
        self.tree.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Статус бар
        self.status_label = tk.Label(root, text="Готов", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Данные задач
        self.tasks = []
        self.next_id = 1
        self.load_tasks()
        self.refresh_list()
    
    def add_task(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить задачу")
        dialog.geometry("400x300")
        
        tk.Label(dialog, text="Название задачи:", font=("Arial", 10, "bold")).pack(pady=(20,5))
        title_entry = tk.Entry(dialog, width=40)
        title_entry.pack(pady=5)
        
        tk.Label(dialog, text="Приоритет:", font=("Arial", 10, "bold")).pack(pady=(10,5))
        priority_var = tk.StringVar(value="Средний")
        tk.Radiobutton(dialog, text="Низкий", variable=priority_var, value="Низкий").pack()
        tk.Radiobutton(dialog, text="Средний", variable=priority_var, value="Средний").pack()
        tk.Radiobutton(dialog, text="Высокий", variable=priority_var, value="Высокий").pack()
        
        def save():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Ошибка", "Введите название задачи")
                return
            
            self.tasks.append({
                'id': self.next_id,
                'title': title,
                'status': 'Ожидает',
                'priority': priority_var.get()
            })
            self.next_id += 1
            self.save_tasks()
            self.refresh_list()
            dialog.destroy()
            messagebox.showinfo("Успех", "Задача добавлена!")
        
        tk.Button(dialog, text="Сохранить", command=save, bg="green", fg="white", padx=20).pack(pady=20)
    
    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу")
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Удалить задачу?"):
            self.tasks = [t for t in self.tasks if t['id'] != task_id]
            self.save_tasks()
            self.refresh_list()
            messagebox.showinfo("Успех", "Задача удалена!")
    
    def change_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу")
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        
        if task:
            dialog = tk.Toplevel(self.root)
            dialog.title("Изменить статус")
            dialog.geometry("300x200")
            
            tk.Label(dialog, text=f"Задача: {task['title']}", font=("Arial", 10, "bold")).pack(pady=20)
            tk.Label(dialog, text="Новый статус:").pack()
            
            status_var = tk.StringVar(value=task['status'])
            tk.Radiobutton(dialog, text="Ожидает", variable=status_var, value="Ожидает").pack()
            tk.Radiobutton(dialog, text="В процессе", variable=status_var, value="В процессе").pack()
            tk.Radiobutton(dialog, text="Выполнена", variable=status_var, value="Выполнена").pack()
            
            def save():
                task['status'] = status_var.get()
                self.save_tasks()
                self.refresh_list()
                dialog.destroy()
                messagebox.showinfo("Успех", "Статус обновлён!")
            
            tk.Button(dialog, text="Сохранить", command=save, bg="blue", fg="white", padx=20).pack(pady=20)
    
    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for task in self.tasks:
            self.tree.insert("", tk.END, values=(task['id'], task['title'], task['status'], task['priority']))
        
        self.status_label.config(text=f"Всего задач: {len(self.tasks)}")
    
    def save_tasks(self):
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r", encoding="utf-8") as f:
                self.tasks = json.load(f)
                if self.tasks:
                    self.next_id = max(t['id'] for t in self.tasks) + 1

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()