"""
Project 2: Expense Tracker — Production Edition
DecodeLabs Python Internship — Industrial Training Kit

A command-line expense tracker that demonstrates:
    - The Accumulator Pattern (total = total + new_expense)
    - Defensive coding / input validation ("the Gatekeeper")
    - A sentinel-value controlled main loop ("the Kill Switch")
    - Separation of logic (Model) from display (View) — Phase 3 of the brief
    - Persistent logging of the session to a CSV file

Run with:
    python expense_tracker_pro.py
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
EXIT_COMMANDS = {"done", "exit", "quit"}
LOG_FILENAME = "expense_log.csv"


# ---------------------------------------------------------------------------
# MODEL — pure logic and state. No print()/input() calls live here, so this
# class could just as easily power a web API or a GUI without modification.
# ---------------------------------------------------------------------------
@dataclass
class Expense:
    """A single recorded expense entry."""

    amount: float
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


class ExpenseTracker:
    """Encapsulates all state and business logic for the expense tracker."""

    def __init__(self) -> None:
        self._history: List[Expense] = []

    # -- accumulation -------------------------------------------------------
    def add_expense(self, amount: float) -> None:
        """
        Record a new expense.

        Args:
            amount: A non-negative expense amount.

        Raises:
            ValueError: if amount is negative.
        """
        if amount < 0:
            raise ValueError("Expense amount cannot be negative.")
        self._history.append(Expense(amount=amount))

    # -- derived state (read-only) -------------------------------------------
    @property
    def total(self) -> float:
        """Running total of all recorded expenses — the accumulator."""
        total = 0.0
        for expense in self._history:
            total += expense.amount  # total = total + new_expense
        return total

    @property
    def count(self) -> int:
        """Number of expenses recorded so far."""
        return len(self._history)

    @property
    def average(self) -> float:
        """Average expense amount. Returns 0.0 if nothing recorded yet."""
        return self.total / self.count if self.count else 0.0

    @property
    def history(self) -> List[Expense]:
        """A copy of the recorded expenses, in entry order."""
        return list(self._history)

    # -- persistence ----------------------------------------------------------
    def save_to_file(self, filename: str = LOG_FILENAME) -> str:
        """
        Write the full expense history and summary to a CSV file.

        Args:
            filename: Destination file name (relative or absolute).

        Returns:
            The absolute path of the file written.
        """
        filepath = os.path.abspath(filename)
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["#", "Timestamp", "Amount"])
            for i, expense in enumerate(self._history, start=1):
                writer.writerow([i, expense.timestamp, f"{expense.amount:.2f}"])
            writer.writerow([])
            writer.writerow(["Total transactions", self.count])
            writer.writerow(["Total spent", f"{self.total:.2f}"])
            writer.writerow(["Average expense", f"{self.average:.2f}"])
        return filepath


# ---------------------------------------------------------------------------
# PARSING / VALIDATION — "the Gatekeeper". Kept separate from the class so
# it can be unit-tested in isolation from any state.
# ---------------------------------------------------------------------------
def is_exit_command(raw_text: str) -> bool:
    """Return True if raw_text is a recognized sentinel/exit command."""
    return raw_text.strip().lower() in EXIT_COMMANDS


def parse_expense(raw_text: str) -> float:
    """
    Convert raw user input into a validated, non-negative float.

    Args:
        raw_text: The raw string typed by the user.

    Returns:
        The parsed expense amount.

    Raises:
        ValueError: if the text is empty, not numeric, or negative.
    """
    cleaned = raw_text.strip()
    if not cleaned:
        raise ValueError("Input cannot be empty.")
    amount = float(cleaned)  # ValueError is raised automatically if non-numeric
    if amount < 0:
        raise ValueError("Expense amount cannot be negative.")
    return amount


# ---------------------------------------------------------------------------
# VIEW — every print()/input() call lives here, isolated from the Model.
# ---------------------------------------------------------------------------
def display_welcome() -> None:
    print("=" * 46)
    print("     DecodeLabs Expense Tracker — Pro Edition")
    print("=" * 46)
    print(f"Enter an expense amount, or type one of "
          f"{sorted(EXIT_COMMANDS)} to finish.\n")


def prompt_for_expense(entry_number: int) -> str:
    return input(f"Expense #{entry_number}: ")


def display_success(amount: float, running_total: float) -> None:
    print(f"\u2705  Added ${amount:.2f}  |  Running total: ${running_total:.2f}\n")


def display_error(message: str) -> None:
    print(f"\u26a0\ufe0f  {message} Please try again.\n")


def display_summary(tracker: ExpenseTracker) -> None:
    print("\n" + "=" * 46)
    print("                FINAL REPORT")
    print("=" * 46)
    print(f"Transactions recorded : {tracker.count}")
    print(f"Total spent           : ${tracker.total:.2f}")
    print(f"Average expense       : ${tracker.average:.2f}")
    print("=" * 46)


def display_saved(filepath: str) -> None:
    print(f"\n\U0001F4C1  Log saved to: {filepath}")


# ---------------------------------------------------------------------------
# CONTROLLER — wires Model and View together via the main program loop.
# ---------------------------------------------------------------------------
def run() -> None:
    """Run the interactive expense tracker session end-to-end."""
    tracker = ExpenseTracker()
    display_welcome()

    while True:
        try:
            raw_text = prompt_for_expense(tracker.count + 1)
        except (EOFError, KeyboardInterrupt):
            # Handles Ctrl+D / Ctrl+C without an ugly traceback, and still
            # falls through to the summary below.
            print("\n\nSession interrupted by user.")
            break

        if is_exit_command(raw_text):
            break

        try:
            amount = parse_expense(raw_text)
        except ValueError as exc:
            display_error(str(exc))
            continue  # Skip accumulation, re-prompt without crashing

        tracker.add_expense(amount)
        display_success(amount, tracker.total)

    display_summary(tracker)

    if tracker.count > 0:
        filepath = tracker.save_to_file()
        display_saved(filepath)


if __name__ == "__main__":
    run()
