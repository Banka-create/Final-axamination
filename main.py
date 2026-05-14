#!/usr/bin/env python3
"""Менеджер задач - консольное приложение
Автор: Иван Иванов
"""

import json
import os
import random
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict


# ==================== МОДЕЛИ ДАННЫХ ====================

class TaskType(Enum):
    """Тип задачи."""
    SIMPLE = "Простая"
    COMPLEX = "Сложная"
    URGENT = "Срочная"


class Priority(Enum):
    """Приоритет задачи."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Status(Enum):
    """Статус выполнения задачи."""
    PENDING = "Ожидает"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Выполнена"


class Task:
    """Базовый класс задачи."""
    
    def __init__(self, task_id: int, title: str, description: str = "",
                 priority: Priority = Priority.MEDIUM,
                 status: Status = Status.PENDING,
                 task_type: TaskType = TaskType.SIMPLE):
        self._id = task_id
        self._title = title
        self._description = description
        self._priority = priority
        self._status = status
        self._task_type = task_type
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, value: str):
        if not value or not value.strip():
            raise ValueError("Название задачи не может быть пустым")
        if len(value) > 200:
            raise ValueError("Название не может превышать 200 символов")
        self._title = value.strip()
        self._updated_at = datetime.now()
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str):
        self._description = value.strip() if value else ""
        self._updated_at = datetime.now()
    
    @property
    def priority(self) -> Priority:
        return self._priority
    
    @priority.setter
    def priority(self, value: Priority):
        self._priority = value
        self._updated_at = datetime.now()
    
    @property
    def status(self) -> Status:
        return self._status
    
    @status.setter
    def status(self, value: Status):
        self._status = value
        self._updated_at = datetime.now()
    
    @property
    def task_type(self) -> TaskType:
        return self._task_type
    
    def get_complexity(self) -> int:
        """Возвращает сложность задачи (для фильтрации)."""
        return self._priority.value
    
    def to_dict(self) -> dict:
        return {
            'id': self._id,
            'title': self._title,
            'description': self._description,
            'priority': self._priority.value,
            'priority_name': self._priority.name,
            'status': self._status.value,
            'task_type': self._task_type.value,
            'task_type_name': self._task_type.name,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        task = cls(
            task_id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            priority=Priority(data['priority']),
            status=Status(data['status']),
            task_type=TaskType(data.get('task_type', 'Простая'))
        )
        task._created_at = datetime.fromisoformat(data['created_at'])
        task._updated_at = datetime.fromisoformat(data['updated_at'])
        return task
    
    def __str__(self) -> str:
        priority_icon = {1: "🟢", 2: "🟡", 3: "🔴"}[self._priority.value]
        return f"[{self._id}] {priority_icon} {self._title} [{self._task_type.value}] - {self._status.value}"


class ComplexTask(Task):
    """Сложная задача (наследник)."""
    
    def __init__(self, task_id: int, title: str, description: str = "",
                 priority: Priority = Priority.MEDIUM,
                 estimated_hours: int = 0):
        super().__init__(task_id, title, description, priority, task_type=TaskType.COMPLEX)
        self._estimated_hours = estimated_hours
        self._subtasks = []
    
    @property
    def estimated_hours(self) -> int:
        return self._estimated_hours
    
    @estimated_hours.setter
    def estimated_hours(self, value: int):
        if value < 0:
            raise ValueError("Часы не могут быть отрицательными")
        self._estimated_hours = value
    
    def add_subtask(self, subtask: str):
        self._subtasks.append(subtask)
    
    def get_complexity(self) -> int:
        """Переопределение: сложность = приоритет * часы."""
        return self._priority.value * max(1, self._estimated_hours // 10)
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data['estimated_hours'] = self._estimated_hours
        data['subtasks'] = self._subtasks
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ComplexTask':
        task = cls(
            task_id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            priority=Priority(data['priority']),
            estimated_hours=data.get('estimated_hours', 0)
        )
        task._status = Status(data['status'])
        task._created_at = datetime.fromisoformat(data['created_at'])
        task._updated_at = datetime.fromisoformat(data['updated_at'])
        task._subtasks = data.get('subtasks', [])
        return task
    
    def __str__(self) -> str:
        base = super().__str__()
        return f"{base} ⏱️ {self._estimated_hours}ч"


class UrgentTask(Task):
    """Срочная задача (наследник)."""
    
    def __init__(self, task_id: int, title: str, description: str = "",
                 priority: Priority = Priority.HIGH, deadline: Optional[datetime] = None):
        super().__init__(task_id, title, description, priority, task_type=TaskType.URGENT)
        self._deadline = deadline
    
    @property
    def deadline(self) -> Optional[datetime]:
        return self._deadline
    
    @deadline.setter
    def deadline(self, value: Optional[datetime]):
        self._deadline = value
        self._updated_at = datetime.now()
    
    def is_overdue(self) -> bool:
        if not self._deadline:
            return False
        return datetime.now() > self._deadline and self.status != Status.COMPLETED
    
    def get_complexity(self) -> int:
        """Переопределение: сложность = приоритет * срочность."""
        urgency = 2 if self._deadline and datetime.now() > self._deadline else 1
        return self._priority.value * urgency
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data['deadline'] = self._deadline.isoformat() if self._deadline else None
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UrgentTask':
        deadline = datetime.fromisoformat(data['deadline']) if data.get('deadline') else None
        task = cls(
            task_id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            priority=Priority(data['priority']),
            deadline=deadline
        )
        task._status = Status(data['status'])
        task._created_at = datetime.fromisoformat(data['created_at'])
        task._updated_at = datetime.fromisoformat(data['updated_at'])
        return task
    
    def __str__(self) -> str:
        base = super().__str__()
        if self._deadline:
            base += f" ⏰ {self._deadline.strftime('%d.%m %H:%M')}"
        if self.is_overdue():
            base += " ⚠️ ПРОСРОЧЕНО!"
        return base


# ==================== ПАТТЕРН FACTORY ====================

class TaskFactory:
    """Фабрика для создания задач."""
    
    @staticmethod
    def create_task(task_type: str, task_id: int, title: str, 
                   description: str = "", **kwargs) -> Task:
        """Создаёт задачу указанного типа."""
        
        task_type_lower = task_type.lower()
        
        if task_type_lower == "simple" or task_type_lower == "простая":
            priority_str = kwargs.get('priority', 'medium')
            priority_map = {'low': Priority.LOW, 'medium': Priority.MEDIUM, 'high': Priority.HIGH}
            priority = priority_map.get(priority_str.lower(), Priority.MEDIUM)
            return Task(task_id, title, description, priority)
        
        elif task_type_lower == "complex" or task_type_lower == "сложная":
            estimated_hours = kwargs.get('estimated_hours', 0)
            priority_str = kwargs.get('priority', 'medium')
            priority_map = {'low': Priority.LOW, 'medium': Priority.MEDIUM, 'high': Priority.HIGH}
            priority = priority_map.get(priority_str.lower(), Priority.MEDIUM)
            return ComplexTask(task_id, title, description, priority, estimated_hours)
        
        elif task_type_lower == "urgent" or task_type_lower == "срочная":
            deadline_str = kwargs.get('deadline', None)
            deadline = None
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    pass
            return UrgentTask(task_id, title, description, Priority.HIGH, deadline)
        
        else:
            raise ValueError(f"Неизвестный тип задачи: {task_type}")
    
    @staticmethod
    def create_random_task(task_id: int) -> Task:
        """Создаёт случайную задачу."""
        
        titles = [
            "Купить продукты", "Сдать отчёт", "Позвонить клиенту",
            "Написать код", "Сделать уборку", "Заплатить налоги",
            "Сходить к врачу", "Прочитать книгу", "Выучить урок",
            "Сделать зарядку", "Провести встречу", "Написать статью"
        ]
        
        descriptions = [
            "Важная задача, требующая внимания",
            "Можно сделать сегодня", "Не срочно, но важно",
            "Требуется согласование", "Сделать до конца недели"
        ]
        
        task_types = ["simple", "complex", "urgent"]
        priorities = ["low", "medium", "high"]
        
        task_type = random.choice(task_types)
        title = random.choice(titles) + f" #{random.randint(1, 999)}"
        description = random.choice(descriptions)
        priority = random.choice(priorities)
        
        kwargs = {'priority': priority}
        
        if task_type == "complex":
            kwargs['estimated_hours'] = random.randint(1, 20)
        elif task_type == "urgent":
            # Случайная дата от вчера до +7 дней
            days_offset = random.randint(-1, 7)
            deadline_date = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
            from datetime import timedelta
            deadline_date += timedelta(days=days_offset)
            kwargs['deadline'] = deadline_date.strftime("%Y-%m-%d %H:%M")
        
        return TaskFactory.create_task(task_type, task_id, title, description, **kwargs)


# ==================== ХРАНИЛИЩЕ ====================

class TaskStorage:
    """Класс для работы с файловым хранилищем."""
    
    def __init__(self, filename: str = "tasks.json"):
        self._filename = filename
    
    def save_tasks(self, tasks: List[Task]) -> bool:
        """Сохраняет задачи в файл с обработкой ошибок."""
        try:
            data = [task.to_dict() for task in tasks]
            with open(self._filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except PermissionError:
            print("❌ Ошибка: Нет прав для записи в файл")
            return False
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
            return False
    
    def load_tasks(self) -> List[Task]:
        """Загружает задачи из файла с обработкой ошибок."""
        if not os.path.exists(self._filename):
            return []
        
        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tasks = []
            for item in data:
                task_type = item.get('task_type', 'Простая')
                if task_type == 'Сложная':
                    tasks.append(ComplexTask.from_dict(item))
                elif task_type == 'Срочная':
                    tasks.append(UrgentTask.from_dict(item))
                else:
                    tasks.append(Task.from_dict(item))
            return tasks
        except json.JSONDecodeError:
            print("❌ Ошибка: Файл повреждён, создаём новый")
            return []
        except Exception as e:
            print(f"❌ Ошибка при загрузке: {e}")
            return []


# ==================== МЕНЕДЖЕР ЗАДАЧ ====================

class TaskManager:
    """Менеджер задач с бизнес-логикой."""
    
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id: int = 1
    
    def add_task(self, task: Task) -> Task:
        """Добавляет задачу."""
        self._tasks.append(task)
        self._next_id = max(self._next_id, task.id + 1)
        return task
    
    def add_task_from_input(self, task_type: str, title: str, 
                           description: str = "", **kwargs) -> Task:
        """Создаёт и добавляет задачу через фабрику."""
        task = TaskFactory.create_task(task_type, self._next_id, title, description, **kwargs)
        self._tasks.append(task)
        self._next_id += 1
        return task
    
    def generate_random_tasks(self, count: int) -> List[Task]:
        """Генерирует указанное количество случайных задач."""
        generated = []
        for _ in range(count):
            task = TaskFactory.create_random_task(self._next_id)
            self._tasks.append(task)
            generated.append(task)
            self._next_id += 1
        return generated
    
    def remove_task(self, task_id: int) -> bool:
        """Удаляет задачу по ID."""
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                del self._tasks[i]
                return True
        return False
    
    def update_task_status(self, task_id: int, new_status: str) -> bool:
        """Обновляет статус задачи."""
        status_map = {
            "1": Status.PENDING,
            "2": Status.IN_PROGRESS,
            "3": Status.COMPLETED,
            "ожидает": Status.PENDING,
            "в процессе": Status.IN_PROGRESS,
            "выполнена": Status.COMPLETED
        }
        
        status_key = new_status.lower()
        if status_key not in status_map:
            raise ValueError("Некорректный статус. Доступны: 1-Ожидает, 2-В процессе, 3-Выполнена")
        
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        task.status = status_map[status_key]
        return True
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Возвращает задачу по ID."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> List[Task]:
        """Возвращает все задачи."""
        return self._tasks.copy()
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Возвращает задачи по статусу."""
        status_map = {"ожидает": Status.PENDING, "в процессе": Status.IN_PROGRESS, "выполнена": Status.COMPLETED}
        status_value = status_map.get(status.lower())
        if not status_value:
            return []
        return [task for task in self._tasks if task.status == status_value]
    
    def get_tasks_by_type(self, task_type: str) -> List[Task]:
        """Возвращает задачи по типу."""
        type_map = {"простая": TaskType.SIMPLE, "сложная": TaskType.COMPLEX, "срочная": TaskType.URGENT}
        type_value = type_map.get(task_type.lower())
        if not type_value:
            return []
        return [task for task in self._tasks if task.task_type == type_value]
    
    def get_tasks_by_complexity(self, min_complexity: int, max_complexity: int) -> List[Task]:
        """Фильтрует задачи по сложности (от min до max)."""
        return [task for task in self._tasks if min_complexity <= task.get_complexity() <= max_complexity]
    
    def search_tasks(self, query: str) -> List[Task]:
        """Поиск задач по названию или описанию."""
        if not query or not query.strip():
            return []
        query_lower = query.strip().lower()
        return [
            task for task in self._tasks
            if query_lower in task.title.lower() or
               query_lower in task.description.lower()
        ]
    
    def get_statistics(self) -> dict:
        """Возвращает статистику по задачам."""
        total = len(self._tasks)
        if total == 0:
            return {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0, 
                   'completion_rate': 0.0, 'by_type': {}, 'by_priority': {}}
        
        completed = sum(1 for task in self._tasks if task.status == Status.COMPLETED)
        pending = sum(1 for task in self._tasks if task.status == Status.PENDING)
        in_progress = sum(1 for task in self._tasks if task.status == Status.IN_PROGRESS)
        
        by_type = {}
        for task_type in TaskType:
            count = sum(1 for task in self._tasks if task.task_type == task_type)
            by_type[task_type.value] = count
        
        by_priority = {}
        for priority in Priority:
            count = sum(1 for task in self._tasks if task.priority == priority)
            by_priority[priority.name] = count
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'completion_rate': (completed / total) * 100 if total > 0 else 0,
            'by_type': by_type,
            'by_priority': by_priority
        }
    
    def load_tasks(self, tasks: List[Task]):
        """Загружает задачи из хранилища."""
        self._tasks = tasks
        if tasks:
            self._next_id = max(task.id for task in tasks) + 1
        else:
            self._next_id = 1


# ==================== КОНСОЛЬНЫЙ ИНТЕРФЕЙС ====================

def print_menu():
    """Выводит главное меню."""
    print("\n" + "=" * 60)
    print("          МЕНЕДЖЕР ЗАДАЧ")
    print("=" * 60)
    print("1. 📋 Показать все задачи")
    print("2. ➕ Добавить задачу (ручной ввод)")
    print("3. 🎲 Сгенерировать случайные задачи")
    print("4. ✏️ Обновить статус задачи")
    print("5. 🗑️ Удалить задачу")
    print("6. 🔍 Поиск задач")
    print("7. 🏷️ Фильтр по статусу")
    print("8. 📂 Фильтр по типу (простая/сложная/срочная)")
    print("9. 📊 Фильтр по сложности")
    print("10. 📈 Статистика")
    print("0. 💾 Выход и сохранение")
    print("=" * 60)


def print_tasks(tasks: List[Task], title: str = "Список задач"):
    """Выводит список задач."""
    if not tasks:
        print(f"\n📭 {title}: Нет задач")
        return
    
    print(f"\n📌 {title}:")
    print("-" * 70)
    for task in tasks:
        print(task)
        if task.description:
            desc = task.description[:60] + "..." if len(task.description) > 60 else task.description
            print(f"      📝 {desc}")
    print("-" * 70)
    print(f"📊 Всего: {len(tasks)} задач")


def get_valid_int_input(prompt: str, min_val: int = None, max_val: int = None) -> Optional[int]:
    """Получает валидный целочисленный ввод."""
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                return None
            num = int(value)
            if min_val is not None and num < min_val:
                print(f"❌ Значение должно быть >= {min_val}")
                continue
            if max_val is not None and num > max_val:
                print(f"❌ Значение должно быть <= {max_val}")
                continue
            return num
        except ValueError:
            print("❌ Введите целое число")


def add_task_interactive(manager: TaskManager):
    """Интерактивное добавление задачи."""
    print("\n--- Добавление новой задачи ---")
    
    # Выбор типа задачи
    print("\nТип задачи:")
    print("1. Простая")
    print("2. Сложная")
    print("3. Срочная")
    
    type_choice = input("Выберите тип (1-3): ").strip()
    type_map = {"1": "simple", "2": "complex", "3": "urgent"}
    
    if type_choice not in type_map:
        print("❌ Неверный выбор")
        return
    
    task_type = type_map[type_choice]
    
    # Ввод названия
    while True:
        title = input("\nНазвание задачи: ").strip()
        if not title:
            print("❌ Название не может быть пустым")
            continue
        if len(title) > 200:
            print("❌ Название не может превышать 200 символов")
            continue
        break
    
    description = input("Описание (необязательно): ").strip()
    
    kwargs = {}
    
    if task_type == "complex":
        hours = get_valid_int_input("Оценочное время (часы): ", min_val=0)
        if hours is not None:
            kwargs['estimated_hours'] = hours
    
    elif task_type == "urgent":
        print("\nФормат даты: ГГГГ-ММ-ДД ЧЧ:ММ (пример: 2026-12-31 23:59)")
        deadline = input("Дедлайн (оставьте пустым, если нет): ").strip()
        if deadline:
            kwargs['deadline'] = deadline
    
    if task_type != "urgent":
        print("\nПриоритет:")
        print("1. Низкий")
        print("2. Средний")
        print("3. Высокий")
        priority_choice = input("Выберите (1-3) [2]: ").strip()
        priority_map = {"1": "low", "2": "medium", "3": "high"}
        kwargs['priority'] = priority_map.get(priority_choice, "medium")
    
    try:
        task = manager.add_task_from_input(task_type, title, description, **kwargs)
        print(f"\n✅ Задача добавлена! ID: {task.id}")
        print(f"   Тип: {task.task_type.value}")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")


def generate_random_tasks(manager: TaskManager):
    """Генерация случайных задач."""
    print("\n--- Генерация случайных задач ---")
    
    count = get_valid_int_input("Количество задач для генерации (1-50): ", min_val=1, max_val=50)
    if not count:
        return
    
    tasks = manager.generate_random_tasks(count)
    print(f"\n✅ Сгенерировано {len(tasks)} случайных задач:")
    for task in tasks:
        print(f"   {task}")


def update_status_interactive(manager: TaskManager):
    """Интерактивное обновление статуса."""
    print("\n--- Обновление статуса задачи ---")
    
    task_id = get_valid_int_input("ID задачи: ", min_val=1)
    if not task_id:
        return
    
    task = manager.get_task_by_id(task_id)
    if not task:
        print(f"❌ Задача с ID {task_id} не найдена")
        return
    
    print(f"\n📌 Текущая задача: {task}")
    print("\nДоступные статусы:")
    print("1. Ожидает")
    print("2. В процессе")
    print("3. Выполнена")
    
    status_choice = input("Выберите новый статус (1-3): ").strip()
    status_map = {"1": "Ожидает", "2": "В процессе", "3": "Выполнена"}
    
    if status_choice not in status_map:
        print("❌ Неверный выбор")
        return
    
    try:
        if manager.update_task_status(task_id, status_map[status_choice]):
            print("✅ Статус обновлён!")
        else:
            print("❌ Задача не найдена")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")


def delete_task_interactive(manager: TaskManager):
    """Интерактивное удаление задачи."""
    print("\n--- Удаление задачи ---")
    
    task_id = get_valid_int_input("ID задачи для удаления: ", min_val=1)
    if not task_id:
        return
    
    task = manager.get_task_by_id(task_id)
    if not task:
        print(f"❌ Задача с ID {task_id} не найдена")
        return
    
    print(f"\n⚠️ Задача: {task}")
    confirm = input("Подтвердите удаление (да/нет): ").strip().lower()
    
    if confirm in ["да", "yes", "y", "д"]:
        if manager.remove_task(task_id):
            print("✅ Задача удалена!")
        else:
            print("❌ Ошибка при удалении")
    else:
        print("❌ Удаление отменено")


def search_interactive(manager: TaskManager):
    """Интерактивный поиск."""
    query = input("\n🔍 Введите текст для поиска: ").strip()
    if not query:
        print("❌ Пустой поисковый запрос")
        return
    
    results = manager.search_tasks(query)
    print_tasks(results, f"Результаты поиска по '{query}'")


def filter_by_status_interactive(manager: TaskManager):
    """Фильтрация по статусу."""
    print("\n--- Фильтр по статусу ---")
    print("1. Ожидает")
    print("2. В процессе")
    print("3. Выполнена")
    
    choice = input("Выберите статус (1-3): ").strip()
    status_map = {"1": "Ожидает", "2": "В процессе", "3": "Выполнена"}
    
    if choice not in status_map:
        print("❌ Неверный выбор")
        return
    
    tasks = manager.get_tasks_by_status(status_map[choice])
    print_tasks(tasks, f"Задачи со статусом '{status_map[choice]}'")


def filter_by_type_interactive(manager: TaskManager):
    """Фильтрация по типу задачи."""
    print("\n--- Фильтр по типу ---")
    print("1. Простые")
    print("2. Сложные")
    print("3. Срочные")
    
    choice = input("Выберите тип (1-3): ").strip()
    type_map = {"1": "Простая", "2": "Сложная", "3": "Срочная"}
    
    if choice not in type_map:
        print("❌ Неверный выбор")
        return
    
    tasks = manager.get_tasks_by_type(type_map[choice])
    print_tasks(tasks, f"Задачи типа '{type_map[choice]}'")


def filter_by_complexity_interactive(manager: TaskManager):
    """Фильтрация по сложности."""
    print("\n--- Фильтр по сложности ---")
    print("Сложность вычисляется автоматически на основе приоритета и других факторов")
    
    min_val = get_valid_int_input("Минимальная сложность (0-100): ", min_val=0, max_val=100)
    max_val = get_valid_int_input("Максимальная сложность (0-100): ", min_val=0, max_val=100)
    
    if min_val is None or max_val is None:
        return
    
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    
    tasks = manager.get_tasks_by_complexity(min_val, max_val)
    print_tasks(tasks, f"Задачи со сложностью от {min_val} до {max_val}")


def show_statistics(manager: TaskManager):
    """Показывает статистику."""
    stats = manager.get_statistics()
    
    print("\n" + "=" * 50)
    print("            СТАТИСТИКА ЗАДАЧ")
    print("=" * 50)
    print(f"📊 Всего задач:        {stats['total']}")
    print(f"✅ Выполнено:          {stats['completed']}")
    print(f"🔄 В процессе:         {stats['in_progress']}")
    print(f"⏳ Ожидают:            {stats['pending']}")
    print(f"📈 Процент выполнения: {stats['completion_rate']:.1f}%")
    
    print("\n📂 По типам:")
    for task_type, count in stats['by_type'].items():
        print(f"   {task_type}: {count}")
    
    print("\n🎯 По приоритетам:")
    for priority, count in stats['by_priority'].items():
        print(f"   {priority}: {count}")
    
    print("=" * 50)


def main():
    """Главная функция приложения."""
    manager = TaskManager()
    storage = TaskStorage()
    
    # Загрузка сохранённых задач
    print("📂 Загрузка сохранённых задач...")
    saved_tasks = storage.load_tasks()
    manager.load_tasks(saved_tasks)
    print(f"✅ Загружено задач: {len(saved_tasks)}")
    
    while True:
        print_menu()
        choice = input("\n👉 Выберите действие: ").strip()
        
        if choice == "1":
            print_tasks(manager.get_all_tasks(), "📋 Все задачи")
        
        elif choice == "2":
            add_task_interactive(manager)
            storage.save_tasks(manager.get_all_tasks())
        
        elif choice == "3":
            generate_random_tasks(manager)
            storage.save_tasks(manager.get_all_tasks())
        
        elif choice == "4":
            update_status_interactive(manager)
            storage.save_tasks(manager.get_all_tasks())
        
        elif choice == "5":
            delete_task_interactive(manager)
            storage.save_tasks(manager.get_all_tasks())
        
        elif choice == "6":
            search_interactive(manager)
        
        elif choice == "7":
            filter_by_status_interactive(manager)
        
        elif choice == "8":
            filter_by_type_interactive(manager)
        
        elif choice == "9":
            filter_by_complexity_interactive(manager)
        
        elif choice == "10":
            show_statistics(manager)
        
        elif choice == "0":
            print("\n💾 Сохранение задач перед выходом...")
            storage.save_tasks(manager.get_all_tasks())
            print("👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
