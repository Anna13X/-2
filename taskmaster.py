#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskMaster Pro - Умный планировщик задач
Все классы в одном файле для удобства проекта
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict

#  ENUM КЛАССЫ 

class TaskPriority(Enum):
    """Приоритет задачи"""
    HIGH = "🔴 Высокий"
    MEDIUM = "🟡 Средний" 
    LOW = "🟢 Низкий"


class TaskStatus(Enum):
    """Статус задачи"""
    ACTIVE = "Активна"
    COMPLETED = "✅ Выполнена"
    POSTPONED = "⏰ Отложена"


class TaskCategory(Enum):
    """Категория задачи"""
    WORK = "💼 Работа"
    STUDY = "📚 Учеба"
    PERSONAL = "🏠 Личное"
    HEALTH = "🏃 Здоровье"
    OTHER = "📌 Другое"


#  АБСТРАКТНЫЙ БАЗОВЫЙ КЛАСС 

class BaseEntity(ABC):
    """Абстрактный базовый класс - демонстрация абстракции"""
    
    def __init__(self, id, title):
        self._id = id
        self._title = title
        self._created_at = datetime.now()
    
    @abstractmethod
    def get_info(self):
        """Абстрактный метод - полиморфизм"""
        pass
    
    @property
    def id(self):
        return self._id
    
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        if value and value.strip():
            self._title = value
        else:
            raise ValueError("Название не может быть пустым")


#  КЛАСС ЗАДАЧИ 

class Task(BaseEntity):
    """Класс задачи - наследуется от BaseEntity"""
    
    def __init__(self, id, title, description="", 
                 priority=TaskPriority.MEDIUM, 
                 category=TaskCategory.OTHER,
                 deadline=None):
        super().__init__(id, title)
        self._description = description
        self._priority = priority
        self._category = category
        self._status = TaskStatus.ACTIVE
        self._deadline = deadline if deadline else datetime.now() + timedelta(days=7)
    
    # Инкапсуляция через свойства
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        self._description = value
    
    @property
    def priority(self):
        return self._priority
    
    @priority.setter
    def priority(self, value):
        self._priority = value
    
    @property
    def category(self):
        return self._category
    
    @property
    def status(self):
        return self._status
    
    def complete(self):
        """Метод для завершения задачи"""
        self._status = TaskStatus.COMPLETED
    
    def postpone(self):
        """Метод для откладывания задачи"""
        self._status = TaskStatus.POSTPONED
    
    def activate(self):
        """Метод для активации задачи"""
        self._status = TaskStatus.ACTIVE
    
    def get_info(self):
        """Реализация абстрактного метода"""
        return f"{self._title} ({self._priority.value}) - {self._status.value}"
    
    @property
    def deadline(self):
        return self._deadline
    
    def to_dict(self):
        """Сериализация в словарь"""
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "priority": self._priority.value,
            "category": self._category.value,
            "status": self._status.value,
            "deadline": self._deadline.strftime("%Y-%m-%d %H:%M"),
            "created_at": self._created_at.strftime("%Y-%m-%d %H:%M")
        }
    
    @classmethod
    def from_dict(cls, data):
        """Десериализация из словаря"""
        task = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            priority=TaskPriority(data["priority"]),
            category=TaskCategory(data["category"]),
            deadline=datetime.strptime(data["deadline"], "%Y-%m-%d %H:%M")
        )
        task._status = TaskStatus(data["status"])
        task._created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M")
        return task


#  СЕРВИС РАБОТЫ С ДАННЫМИ 

class DataService:
    """Класс для работы с данными - изоляция ввода-вывода"""
    
    def __init__(self, filename="tasks.json"):
        self._filename = filename
    
    def load(self):
        """Загрузка задач из файла"""
        if not os.path.exists(self._filename):
            return []
        
        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [Task.from_dict(task_data) for task_data in data]
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return []
    
    def save(self, tasks):
        """Сохранение задач в файл"""
        try:
            data = [task.to_dict() for task in tasks]
            with open(self._filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False


#  СЕРВИС АНАЛИТИКИ 

class AnalyticsService:
    """Класс для аналитики задач"""
    
    def __init__(self, tasks):
        self._tasks = tasks
    
    def get_stats_by_status(self):
        """Статистика по статусам"""
        stats = {status: 0 for status in TaskStatus}
        for task in self._tasks:
            stats[task.status] += 1
        return stats
    
    def get_stats_by_category(self):
        """Статистика по категориям"""
        stats = {category: 0 for category in TaskCategory}
        for task in self._tasks:
            stats[task.category] += 1
        return stats
    
    def get_stats_by_priority(self):
        """Статистика по приоритетам"""
        stats = {priority: 0 for priority in TaskPriority}
        for task in self._tasks:
            stats[task.priority] += 1
        return stats
    
    def get_completion_rate(self):
        """Процент выполненных задач"""
        if not self._tasks:
            return 0
        completed = sum(1 for t in self._tasks if t.status == TaskStatus.COMPLETED)
        return (completed / len(self._tasks)) * 100
    
    def get_overdue_tasks(self):
        """Просроченные задачи"""
        now = datetime.now()
        return [t for t in self._tasks if t.deadline < now and t.status == TaskStatus.ACTIVE]
    
    def get_active_tasks(self):
        """Активные задачи"""
        return [t for t in self._tasks if t.status == TaskStatus.ACTIVE]


#  ГЛАВНОЕ ПРИЛОЖЕНИЕ 

class TaskManagerApp:
    """Главный класс приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📋 TaskMaster Pro - Умный планировщик")
        self.root.geometry("1100x650")
        self.root.configure(bg='#f5f5f5')
        
        # Инициализация сервисов
        self.data_service = DataService()
        self.tasks = self.data_service.load()
        self.analytics = AnalyticsService(self.tasks)
        self.next_id = max([t.id for t in self.tasks], default=0) + 1
        
        self._create_ui()
        self._refresh_display()
    
    def _create_ui(self):
        """Создание интерфейса"""
        # Заголовок
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="📋 TASKMASTER PRO", 
                font=('Arial', 24, 'bold'),
                fg='white', bg='#2c3e50').pack(expand=True)
        
        tk.Label(title_frame, text="Управляй своими задачами эффективно",
                font=('Arial', 10), fg='#bdc3c7', bg='#2c3e50').pack()
        
        # Основной контейнер
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Левая панель - статистика
        left_panel = tk.Frame(main_container, bg='#f5f5f5', width=250)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self._create_stats_panel(left_panel)
        
        # Правая панель - список задач
        right_panel = tk.Frame(main_container, bg='#f5f5f5')
        right_panel.pack(side='right', fill='both', expand=True)
        
        self._create_task_list(right_panel)
        
        # Нижняя панель с кнопками
        self._create_button_panel()
    
    def _create_stats_panel(self, parent):
        """Создание панели статистики"""
        stats_frame = tk.Frame(parent, bg='white', relief='groove', bd=1)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(stats_frame, text="📊 Статистика", 
                font=('Arial', 12, 'bold'),
                bg='white').pack(pady=10)
        
        self.stats_labels = {}
        stats_items = [
            ("Всего задач", "0"),
            ("Выполнено", "0"),
            ("Активно", "0"),
            ("Отложено", "0"),
            ("Просрочено", "0"),
            ("Прогресс", "0%")
        ]
        
        for label, value in stats_items:
            frame = tk.Frame(stats_frame, bg='white')
            frame.pack(fill='x', padx=15, pady=5)
            
            tk.Label(frame, text=label, bg='white', 
                    font=('Arial', 10)).pack(side='left')
            
            value_label = tk.Label(frame, text=value, bg='white',
                                  font=('Arial', 10, 'bold'))
            value_label.pack(side='right')
            self.stats_labels[label] = value_label
    
    def _create_task_list(self, parent):
        """Создание списка задач"""
        # Фильтры
        filter_frame = tk.Frame(parent, bg='#f5f5f5')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Фильтр:", bg='#f5f5f5').pack(side='left')
        
        self.filter_var = tk.StringVar(value="Все")
        filters = ["Все", "Активна", "Выполнена", "Отложена"]
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                    values=filters, state='readonly', width=15)
        filter_combo.pack(side='left', padx=10)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_display())
        
        # Таблица задач
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set,
                                 selectmode='browse', height=15)
        self.tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Колонки
        columns = ('priority', 'title', 'category', 'status', 'deadline')
        self.tree['columns'] = columns
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('priority', width=80, anchor='center')
        self.tree.column('title', width=300, anchor='w')
        self.tree.column('category', width=120, anchor='center')
        self.tree.column('status', width=100, anchor='center')
        self.tree.column('deadline', width=150, anchor='center')
        
        self.tree.heading('priority', text='Приоритет')
        self.tree.heading('title', text='Название')
        self.tree.heading('category', text='Категория')
        self.tree.heading('status', text='Статус')
        self.tree.heading('deadline', text='Дедлайн')
        
        # Цвета для приоритетов
        self.tree.tag_configure('high', foreground='red')
        self.tree.tag_configure('medium', foreground='orange')
        self.tree.tag_configure('low', foreground='green')
        
        # Двойной клик для просмотра
        self.tree.bind('<Double-Button-1>', self._view_task)
    
    def _create_button_panel(self):
        """Создание панели кнопок"""
        button_frame = tk.Frame(self.root, bg='#f5f5f5')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        buttons = [
            ("➕ Добавить задачу", self._add_task, '#2ecc71'),
            ("✅ Выполнить", self._complete_task, '#3498db'),
            ("⏰ Отложить", self._postpone_task, '#f39c12'),
            ("🗑 Удалить", self._delete_task, '#e74c3c'),
            ("📊 Аналитика", self._show_analytics, '#9b59b6')
        ]
        
        for text, command, color in buttons:
            tk.Button(button_frame, text=text, command=command,
                     bg=color, fg='white', font=('Arial', 10, 'bold'),
                     padx=15, pady=5).pack(side='left', padx=5)
    
    def _refresh_display(self):
        """Обновление отображения"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтрация задач
        filter_status = self.filter_var.get()
        filtered_tasks = self.tasks
        if filter_status != "Все":
            status_map = {"Активна": TaskStatus.ACTIVE, 
                         "Выполнена": TaskStatus.COMPLETED,
                         "Отложена": TaskStatus.POSTPONED}
            filtered_tasks = [t for t in self.tasks if t.status == status_map[filter_status]]
        
        # Заполнение таблицы
        for task in sorted(filtered_tasks, key=lambda x: (x.status.value, x.priority.value)):
            priority_tag = {'🔴 Высокий': 'high', '🟡 Средний': 'medium', '🟢 Низкий': 'low'}[task.priority.value]
            
            self.tree.insert('', 'end', values=(
                task.priority.value,
                task.title,
                task.category.value,
                task.status.value,
                task.deadline.strftime("%d.%m.%Y %H:%M")
            ), tags=(priority_tag,), iid=str(task.id))
        
        # Обновление статистики
        self.analytics = AnalyticsService(self.tasks)
        stats = self.analytics.get_stats_by_status()
        
        self.stats_labels["Всего задач"].config(text=str(len(self.tasks)))
        self.stats_labels["Выполнено"].config(text=str(stats[TaskStatus.COMPLETED]))
        self.stats_labels["Активно"].config(text=str(stats[TaskStatus.ACTIVE]))
        self.stats_labels["Отложено"].config(text=str(stats[TaskStatus.POSTPONED]))
        self.stats_labels["Просрочено"].config(text=str(len(self.analytics.get_overdue_tasks())))
        self.stats_labels["Прогресс"].config(text=f"{self.analytics.get_completion_rate():.0f}%")
    
    def _add_task(self):
        """Диалог добавления задачи"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новая задача")
        dialog.geometry("500x550")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Заголовок
        tk.Label(dialog, text="➕ Создание новой задачи", 
                font=('Arial', 14, 'bold'),
                bg='white', fg='#2c3e50').pack(pady=20)
        
        # Поля ввода
        fields_frame = tk.Frame(dialog, bg='white')
        fields_frame.pack(padx=30, pady=10, fill='both', expand=True)
        
        # Название
        tk.Label(fields_frame, text="Название *", bg='white', 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        title_var = tk.StringVar()
        title_entry = tk.Entry(fields_frame, textvariable=title_var, 
                               font=('Arial', 11), width=40)
        title_entry.pack(pady=(0, 10), fill='x')
        
        # Описание
        tk.Label(fields_frame, text="Описание", bg='white',
                font=('Arial', 10, 'bold')).pack(anchor='w')
        desc_text = tk.Text(fields_frame, height=4, font=('Arial', 10))
        desc_text.pack(pady=(0, 10), fill='x')
        
        # Категория
        tk.Label(fields_frame, text="Категория", bg='white',
                font=('Arial', 10, 'bold')).pack(anchor='w')
        category_var = tk.StringVar(value=TaskCategory.WORK.value)
        category_combo = ttk.Combobox(fields_frame, textvariable=category_var,
                                      values=[c.value for c in TaskCategory],
                                      state='readonly', width=30)
        category_combo.pack(pady=(0, 10), fill='x')
        
        # Приоритет
        tk.Label(fields_frame, text="Приоритет", bg='white',
                font=('Arial', 10, 'bold')).pack(anchor='w')
        priority_var = tk.StringVar(value=TaskPriority.MEDIUM.value)
        priority_combo = ttk.Combobox(fields_frame, textvariable=priority_var,
                                      values=[p.value for p in TaskPriority],
                                      state='readonly', width=30)
        priority_combo.pack(pady=(0, 10), fill='x')
        
        # Дедлайн
        tk.Label(fields_frame, text="Дедлайн", bg='white',
                font=('Arial', 10, 'bold')).pack(anchor='w')
        deadline_frame = tk.Frame(fields_frame, bg='white')
        deadline_frame.pack(fill='x', pady=(0, 10))
        
        year_var = tk.StringVar(value=str(datetime.now().year))
        month_var = tk.StringVar(value=str(datetime.now().month))
        day_var = tk.StringVar(value=str(datetime.now().day))
        hour_var = tk.StringVar(value="23")
        minute_var = tk.StringVar(value="59")
        
        ttk.Spinbox(deadline_frame, from_=2024, to=2030, 
                   textvariable=year_var, width=6).pack(side='left')
        tk.Label(deadline_frame, text="/", bg='white').pack(side='left')
        ttk.Spinbox(deadline_frame, from_=1, to=12,
                   textvariable=month_var, width=3).pack(side='left')
        tk.Label(deadline_frame, text="/", bg='white').pack(side='left')
        ttk.Spinbox(deadline_frame, from_=1, to=31,
                   textvariable=day_var, width=3).pack(side='left')
        tk.Label(deadline_frame, text="  ", bg='white').pack(side='left')
        ttk.Spinbox(deadline_frame, from_=0, to=23,
                   textvariable=hour_var, width=3).pack(side='left')
        tk.Label(deadline_frame, text=":", bg='white').pack(side='left')
        ttk.Spinbox(deadline_frame, from_=0, to=59,
                   textvariable=minute_var, width=3).pack(side='left')
        
        def save():
            if not title_var.get().strip():
                messagebox.showerror("Ошибка", "Введите название задачи")
                return
            
            # Определение приоритета и категории
            priority = [p for p in TaskPriority if p.value == priority_var.get()][0]
            category = [c for c in TaskCategory if c.value == category_var.get()][0]
            
            # Создание дедлайна
            try:
                deadline = datetime(
                    int(year_var.get()), int(month_var.get()), int(day_var.get()),
                    int(hour_var.get()), int(minute_var.get())
                )
            except:
                deadline = datetime.now() + timedelta(days=7)
            
            # Создание задачи
            task = Task(
                id=self.next_id,
                title=title_var.get(),
                description=desc_text.get("1.0", "end-1c"),
                priority=priority,
                category=category,
                deadline=deadline
            )
            
            self.tasks.append(task)
            self.next_id += 1
            self.data_service.save(self.tasks)
            self._refresh_display()
            dialog.destroy()
        
        # Кнопки
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Сохранить", command=save,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Отмена", command=dialog.destroy,
                 bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side='left', padx=10)
        
        title_entry.focus()
    
    def _view_task(self, event):
        """Просмотр задачи"""
        selected = self.tree.selection()
        if not selected:
            return
        
        task_id = int(selected[0])
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return
        
        info = f"📌 Задача: {task.title}\n\n"
        info += f"📝 Описание: {task.description if task.description else 'Нет описания'}\n\n"
        info += f"📂 Категория: {task.category.value}\n"
        info += f"⚡ Приоритет: {task.priority.value}\n"
        info += f"📊 Статус: {task.status.value}\n"
        info += f"⏰ Дедлайн: {task.deadline.strftime('%d.%m.%Y %H:%M')}\n"
        info += f"📅 Создана: {task._created_at.strftime('%d.%m.%Y %H:%M')}"
        
        messagebox.showinfo("Информация о задаче", info)
    
    def _complete_task(self):
        """Завершение задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу")
            return
        
        task_id = int(selected[0])
        task = next((t for t in self.tasks if t.id == task_id), None)
        
        if task and task.status != TaskStatus.COMPLETED:
            task.complete()
            self.data_service.save(self.tasks)
            self._refresh_display()
            messagebox.showinfo("Успех", f"Задача '{task.title}' выполнена! 🎉")
    
    def _postpone_task(self):
        """Откладывание задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу")
            return
        
        task_id = int(selected[0])
        task = next((t for t in self.tasks if t.id == task_id), None)
        
        if task and task.status == TaskStatus.ACTIVE:
            task.postpone()
            self.data_service.save(self.tasks)
            self._refresh_display()
            messagebox.showinfo("Успех", f"Задача '{task.title}' отложена")
    
    def _delete_task(self):
        """Удаление задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную задачу?"):
            task_id = int(selected[0])
            self.tasks = [t for t in self.tasks if t.id != task_id]
            self.data_service.save(self.tasks)
            self._refresh_display()
    
    def _show_analytics(self):
        """Показ аналитики"""
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Аналитика задач")
        analytics_window.geometry("600x500")
        analytics_window.configure(bg='white')
        
        tk.Label(analytics_window, text="📊 Статистика задач", 
                font=('Arial', 16, 'bold'),
                bg='white', fg='#2c3e50').pack(pady=20)
        
        # Статистика
        stats_frame = tk.Frame(analytics_window, bg='white')
        stats_frame.pack(padx=30, pady=10, fill='both', expand=True)
        
        stats = self.analytics.get_stats_by_status()
        
        # Прогресс-бар
        completion = self.analytics.get_completion_rate()
        tk.Label(stats_frame, text=f"Общий прогресс: {completion:.1f}%", 
                font=('Arial', 12), bg='white').pack(pady=5)
        
        # Простая визуализация прогресса
        progress_frame = tk.Frame(stats_frame, bg='white')
        progress_frame.pack(fill='x', pady=10)
        
        canvas = tk.Canvas(progress_frame, width=400, height=30, bg='#ecf0f1')
        canvas.pack()
        canvas.create_rectangle(0, 0, 400 * completion / 100, 30, fill='#2ecc71')
        canvas.create_text(200, 15, text=f"{completion:.0f}%", fill='black')
        
        # Статистика по статусам
        tk.Label(stats_frame, text="\nРаспределение по статусам:", 
                font=('Arial', 12, 'bold'), bg='white').pack(pady=10)
        
        status_colors = {
            TaskStatus.ACTIVE: '#3498db',
            TaskStatus.COMPLETED: '#2ecc71',
            TaskStatus.POSTPONED: '#f39c12'
        }
        
        for status, count in stats.items():
            if count > 0:
                frame = tk.Frame(stats_frame, bg='white')
                frame.pack(fill='x', pady=5)
                
                tk.Label(frame, text=f"{status.value}:", bg='white',
                        font=('Arial', 10)).pack(side='left')
                tk.Label(frame, text=str(count), bg='white',
                        font=('Arial', 10, 'bold')).pack(side='right')
                
                # Мини-прогресс
                percent = (count / len(self.tasks)) * 100 if self.tasks else 0
                mini_canvas = tk.Canvas(frame, width=200, height=10, bg='#ecf0f1')
                mini_canvas.pack(side='right', padx=10)
                mini_canvas.create_rectangle(0, 0, 200 * percent / 100, 10, fill=status_colors[status])
        
        # Просроченные задачи
        overdue = self.analytics.get_overdue_tasks()
        if overdue:
            tk.Label(stats_frame, text=f"\n⚠️ Просроченные задачи ({len(overdue)}):", 
                    font=('Arial', 10, 'bold'), fg='red', bg='white').pack(pady=5)
            for task in overdue[:5]:
                tk.Label(stats_frame, text=f"  • {task.title}", 
                        bg='white', fg='red').pack(anchor='w')
        
        # Кнопка закрытия
        tk.Button(analytics_window, text="Закрыть", command=analytics_window.destroy,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(pady=20)
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


#  ТОЧКА ВХОДА 

if __name__ == "__main__":
    app = TaskManagerApp()
    app.run()
