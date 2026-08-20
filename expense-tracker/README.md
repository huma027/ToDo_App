# DecodeLabs Expense Tracker — Project 2

A command-line Python application that continuously accepts expense entries,
validates them, accumulates a running total, and produces a session summary
— built as Project 2 of the DecodeLabs Python Programming Internship
(Industrial Training Kit, Batch 2026).

## Features

- **Continuous input loop** — enter as many expenses as you like, one per line
- **Accumulator pattern** — maintains a running total (`total += expense`)
- **Sentinel-value exit** — type `done`, `exit`, or `quit` to finish
- **Defensive input handling** — non-numeric, empty, and negative input are
  rejected with a helpful message instead of crashing the program
- **Session history** — every valid expense is stored with a timestamp
- **Summary statistics** — total spent, transaction count, and average expense
- **Persistent logging** — the full session is saved to `expense_log.csv`
- **Model/View separation** — all business logic (`ExpenseTracker`) is
  isolated from all display code (`print`/`input`), so the core logic could
  be reused behind a web API or GUI without changes

## Requirements

- Python 3.8 or later
- No third-party dependencies (standard library only: `csv`, `os`,
  `dataclasses`, `datetime`, `typing`)

## Usage

```bash
python expense_tracker_pro.py
```

You'll be prompted to enter one expense at a time:

```
Expense #1: 100
Expense #2: 50
Expense #3: done
```

When you type an exit command, the program prints a final report and saves
`expense_log.csv` in the same directory.

## Sample Run

```
==============================================
     DecodeLabs Expense Tracker — Pro Edition
==============================================
Enter an expense amount, or type one of ['done', 'exit', 'quit'] to finish.

Expense #1: 100
✅  Added $100.00  |  Running total: $100.00

Expense #2: 50
✅  Added $50.00  |  Running total: $150.00

Expense #3: ten
⚠️  could not convert string to float: 'ten' Please try again.

Expense #3: 20
✅  Added $20.00  |  Running total: $170.00

Expense #4: done

==============================================
                FINAL REPORT
==============================================
Transactions recorded : 3
Total spent           : $170.00
Average expense       : $56.67
==============================================

📁  Log saved to: /path/to/expense_log.csv
```

## Project Structure

```
.
├── expense_tracker_pro.py   # Main application
├── expense_log.csv          # Generated automatically after a session
└── README.md                # This file
```

## Architecture Notes

| Layer          | Responsibility                                   | Where it lives                                  |
|----------------|---------------------------------------------------|--------------------------------------------------|
| **Model**      | State + business rules (accumulate, validate)     | `Expense`, `ExpenseTracker`                       |
| **Parsing**    | Convert/validate raw strings ("the Gatekeeper")   | `parse_expense`, `is_exit_command`                |
| **View**       | All user-facing I/O                               | `display_*`, `prompt_for_expense`                 |
| **Controller** | Wires Model + View together                       | `run()`                                            |

Keeping these layers separate means the validation logic and the accumulator
can be unit-tested with plain function calls — no `input()` mocking required.

## Possible Extensions

- Categorize expenses (`Food`, `Transport`, `Rent`) using a dictionary of
  running totals instead of a single number
- Add a monthly/weekly budget limit with a warning when exceeded
- Load a previous `expense_log.csv` on startup to resume a session
- Add `argparse` support for a `--file` flag to choose the log destination
- Write `pytest` unit tests for `parse_expense` and `ExpenseTracker`

## Author

DecodeLabs Python Programming Internship — Batch 2026
Contact: decodelabs.tech@gmail.com
