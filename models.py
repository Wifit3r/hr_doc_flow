from dataclasses import dataclass
from typing import Optional

@dataclass
class Employee:
    employee_id: str
    first_name: str
    last_name: str
    position: str
    department: str
    # Опціональні поля, якщо вони є не у всіх
    hire_date: Optional[str] = None
    email: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


def get_employee_mock(emp_id: str) -> Employee:
    """
    Тимчасова функція-заглушка для тестування генерації документів,
    поки не готова справжня логіка читання з Google Drive.
    """
    return Employee(
        employee_id=emp_id,
        first_name="Іван",
        last_name="Франко",
        position="Junior QA",
        department="Engineering",
        hire_date="2026-06-01"
    )