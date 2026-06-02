"""Entry point. Wires all modules together and drives the main menu loop."""

import sys
import logging

from dotenv import load_dotenv

from core.logger import get_logger
from core.orchestrator import Orchestrator
from core import ui


# ─── Dependency injection: real modules or mocks ─────────────────────────────
# When Andrii / Misha finish their modules, replace these imports.
# The Orchestrator only cares about the Protocol interface, not the class name.

try:
    from api.drive import DriveClient as _ApiClient          # type: ignore[import]
    _MOCK_API = False
except ImportError:
    from mocks.mock_api import MockApiClient as _ApiClient   # type: ignore[assignment]
    _MOCK_API = True

try:
    from data.scanner import DataManager as _DataManager         # type: ignore[import]
    _MOCK_DATA = False
except ImportError:
    from mocks.mock_data import MockDataManager as _DataManager  # type: ignore[assignment]
    _MOCK_DATA = True


# ─── Action handlers ──────────────────────────────────────────────────────────

def _action_list(orchestrator: Orchestrator) -> None:
    employees = orchestrator.list_employees()
    if employees:
        ui.display_employees_table(employees)
    else:
        ui.display_info("Список працівників порожній.")


def _action_create(orchestrator: Orchestrator) -> None:
    employees = orchestrator.list_employees()

    employee = ui.prompt_select_employee(employees)
    if employee is None:
        return

    order_type = ui.prompt_select_order_type()
    if order_type is None:
        return

    confirmed = ui.prompt_confirm(
        f"Створити «{order_type.label()}» для {employee.short_name}?"
    )
    if not confirmed:
        ui.display_info("Скасовано.")
        return

    try:
        doc_url = orchestrator.generate_order(employee, order_type)
        ui.display_success(f"Документ створено: {doc_url}")
    except ValueError as exc:
        ui.display_error(str(exc))
    except Exception as exc:
        logging.getLogger("hr_doc_flow").exception("Unexpected error during order creation")
        ui.display_error(f"Помилка: {exc}")


def _action_search(orchestrator: Orchestrator) -> None:
    query = ui.prompt_search_query()
    if not query:
        return

    employees = orchestrator.list_employees()
    results = orchestrator.search_employees(query, employees)

    if results:
        ui.display_employees_table(results)
    else:
        ui.display_info(f"Не знайдено за запитом: «{query}»")


_ACTIONS = {
    "list":   _action_list,
    "create": _action_create,
    "search": _action_search,
}


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    load_dotenv()
    log = get_logger()

    orchestrator = Orchestrator(
        data_manager=_DataManager(),
        api_client=_ApiClient(),
    )

    ui.display_banner()

    if _MOCK_API or _MOCK_DATA:
        log.warning(
            "Running in [bold yellow]mock mode[/bold yellow] — "
            "no Google Drive connection. "
            f"({'api' if _MOCK_API else ''}"
            f"{' + ' if _MOCK_API and _MOCK_DATA else ''}"
            f"{'data' if _MOCK_DATA else ''} module(s) missing)"
        )

    log.info("System ready.")

    while True:
        choice = ui.display_main_menu()

        if choice is None or choice == "exit":
            log.info("Session ended.")
            break

        handler = _ACTIONS.get(choice)
        if handler:
            handler(orchestrator)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
