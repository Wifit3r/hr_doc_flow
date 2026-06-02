"""All user-facing output and input prompts live here.

Single responsibility: translate between Python objects and the terminal.
No business logic — that belongs in orchestrator.py.
"""

from typing import Optional

import questionary
from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.logger import console
from models import Employee, OrderType


# ─── questionary colour scheme (Swiss: minimal, blue accent) ──────────────────

_STYLE = questionary.Style(
    [
        ("qmark",       "fg:#5f87ff bold"),
        ("question",    "bold"),
        ("answer",      "fg:#5f87ff bold"),
        ("pointer",     "fg:#5f87ff bold"),
        ("highlighted", "fg:#5f87ff bold"),
        ("selected",    "fg:#5f87ff"),
        ("separator",   "fg:#555555"),
        ("instruction", "fg:#555555 italic"),
    ]
)


# ─── Banner ───────────────────────────────────────────────────────────────────

def display_banner() -> None:
    """Print the application welcome panel."""
    title = Text("HR DOC FLOW", style="bold #5f87ff")
    subtitle = Text(
        "Система автоматизованого кадрового документообігу",
        style="dim white",
    )
    content = Align.center(Text.assemble(title, "\n", subtitle))
    console.print(Panel(content, border_style="#5f87ff", padding=(1, 8)))
    console.print()


# ─── Main menu ────────────────────────────────────────────────────────────────

def display_main_menu() -> Optional[str]:
    """
    Render the main action menu.

    Returns one of: 'list' | 'create' | 'search' | 'exit' | None (Ctrl+C).
    """
    return questionary.select(
        "Оберіть дію:",
        choices=[
            questionary.Choice("  Список працівників", value="list"),
            questionary.Choice("  Створити наказ",     value="create"),
            questionary.Choice("  Знайти працівника",  value="search"),
            questionary.Separator(),
            questionary.Choice("  Вихід",              value="exit"),
        ],
        style=_STYLE,
        use_indicator=True,
    ).ask()


# ─── Employee prompts ─────────────────────────────────────────────────────────

def prompt_select_employee(employees: list[Employee]) -> Optional[Employee]:
    """
    Let the user pick one employee from a list.

    Returns None if the list is empty or the user presses Ctrl+C.
    """
    if not employees:
        display_info("Список працівників порожній.")
        return None

    return questionary.select(
        "Оберіть працівника:",
        choices=[
            questionary.Choice(title=str(emp), value=emp) for emp in employees
        ],
        style=_STYLE,
        use_indicator=True,
    ).ask()


def prompt_select_order_type() -> Optional[OrderType]:
    """Let the user pick an order type."""
    return questionary.select(
        "Тип наказу:",
        choices=[
            questionary.Choice(title=ot.label(), value=ot) for ot in OrderType
        ],
        style=_STYLE,
        use_indicator=True,
    ).ask()


def prompt_confirm(message: str) -> bool:
    """Binary yes/no confirmation. Defaults to No."""
    result = questionary.confirm(message, style=_STYLE, default=False).ask()
    return bool(result)


def prompt_search_query() -> str:
    """Free-text input for employee search."""
    result = questionary.text(
        "Пошуковий запит (прізвище або ID):",
        style=_STYLE,
    ).ask()
    return result or ""


# ─── Display helpers ──────────────────────────────────────────────────────────

def display_employees_table(employees: list[Employee]) -> None:
    """Render a list of employees as a Rich table."""
    table = Table(
        box=box.SIMPLE_HEAD,
        border_style="dim",
        header_style="bold #5f87ff",
        show_edge=False,
        pad_edge=True,
        row_styles=["", "dim"],   # alternating row brightness
    )
    table.add_column("ID",             style="dim",  width=10)
    table.add_column("ПІБ",                          min_width=26)
    table.add_column("Посада",                       min_width=22)
    table.add_column("Відділ",                       min_width=14)
    table.add_column("Прийнятий",      style="dim",  width=12)

    for emp in employees:
        table.add_row(
            emp.employee_id,
            emp.full_name,
            emp.position,
            emp.department,
            emp.hire_date.strftime("%d.%m.%Y"),
        )

    console.print()
    console.print(table)


def display_success(message: str) -> None:
    console.print(f"\n[bold green]  {message}[/bold green]\n")


def display_error(message: str) -> None:
    console.print(f"\n[bold red]  {message}[/bold red]\n")


def display_info(message: str) -> None:
    console.print(f"  [dim]{message}[/dim]")
