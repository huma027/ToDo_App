import json
import os
from datetime import datetime

# =====================================================================
# 1. MODEL (DATA LOGIC & PERSISTENCE)
# =====================================================================

DATA_FILE = "tasks.json"

def load_tasks(filepath=DATA_FILE):
    """Loads JSON data into volatile memory with fallback defaults."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tasks = json.load(f)
            # Ensure backward compatibility for older JSON structures
            for task in tasks:
                if "priority" not in task or not task["priority"]:
                    task["priority"] = "MED"
                if "category" not in task or not task["category"]:
                    task["category"] = "General"
            return tasks
    except (json.JSONDecodeError, IOError):
        return []

def save_tasks(tasks, filepath=DATA_FILE):
    """Persists memory array into local JSON storage."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)
        return True
    except IOError:
        return False

def add_task(tasks, title, category="General", priority="MED"):
    """Appends structured task record with metadata to array."""
    next_id = max([t.get("id", 0) for t in tasks], default=0) + 1
    task = {
        "id": next_id,
        "title": title.strip(),
        "category": category.strip().capitalize() if category.strip() else "General",
        "priority": priority.upper() if priority.upper() in ["HIGH", "MED", "LOW"] else "MED",
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    tasks.append(task)
    return task

def mark_completed(tasks, display_idx):
    """Updates completion status by list position."""
    if 0 <= display_idx < len(tasks):
        tasks[display_idx]["completed"] = True
        return tasks[display_idx]
    return None

def delete_task(tasks, display_idx):
    """Removes single task record by list position."""
    if 0 <= display_idx < len(tasks):
        return tasks.pop(display_idx)
    return None

def clear_completed(tasks):
    """Batch removes all tasks marked completed."""
    initial_count = len(tasks)
    tasks[:] = [t for t in tasks if not t.get("completed", False)]
    return initial_count - len(tasks)

def search_tasks(tasks, query):
    """Filters task records matching keyword search."""
    q = query.lower()
    return [
        t for t in tasks 
        if q in t.get("title", "").lower() or q in t.get("category", "").lower()
    ]

def get_statistics(tasks):
    """Computes runtime state metrics."""
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("completed", False))
    pending = total - completed
    high_prio = sum(1 for t in tasks if t.get("priority") == "HIGH" and not t.get("completed", False))
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "high_priority": high_prio
    }


# =====================================================================
# 2. VIEW (PRESENTATION & USER INTERFACE)
# =====================================================================

def render_top_dashboard(tasks):
    """Renders a sleek top metric bar."""
    stats = get_statistics(tasks)
    print("\n" + "═" * 78)
    print(f" DECODELABS ENGINE │ Total: {stats['total']} │ Pending: {stats['pending']} │ Completed: {stats['completed']} │ High Priority: {stats['high_priority']}")
    print("═" * 78)

def render_compact_menu():
    """Displays streamlined non-intrusive action toolbar."""
    print(" [1] List All   [2] Add Task    [3] Complete    [4] Search Task")
    print(" [5] Delete     [6] Clear Done  [7] Analytics   [8] Save & Exit")
    print("─" * 78)

def display_task_table(task_list, title_header="CURRENT TASKS"):
    """Renders structured Unicode table representation of tasks."""
    print(f"\n┌── {title_header} " + "─" * (72 - len(title_header)) + "┐")
    if not task_list:
        print("│  (No task records found)                                                    │")
        print("└" + "─" * 76 + "┘")
        return

    print(f"│ {'#':<3} │ {'STATUS':<9} │ {'PRIORITY':<8} │ {'CATEGORY':<10} │ {'TASK DESCRIPTION':<35} │")
    print("├" + "─"*5 + "┼" + "─"*11 + "┼" + "─"*10 + "┼" + "─"*12 + "┼" + "─"*37 + "┤")

    for idx, t in enumerate(task_list, start=1):
        status = "✓ DONE" if t.get("completed") else "  PENDING"
        prio_val = str(t.get("priority") or "MED").upper()
        prio = f"[{prio_val:<4}]"
        cat = str(t.get("category") or "General")[:10]
        desc = str(t.get("title") or "")
        if len(desc) > 35:
            desc = desc[:32] + "..."
        print(f"│ {idx:<3} │ {status:<9} │ {prio:<8} │ {cat:<10} │ {desc:<35} │")

    print("└" + "─" * 76 + "┘")


# =====================================================================
# 3. CONTROLLER (CORE APP LOOP WITH ERROR HANDLING)
# =====================================================================

def main():
    tasks = load_tasks()

    try:
        while True:
            render_top_dashboard(tasks)
            render_compact_menu()
            choice = input("Option [1-8] > ").strip()

            if choice == "1":
                display_task_table(tasks)

            elif choice == "2":
                title = input("▸ Description: ").strip()
                if not title:
                    print("⚠ Description cannot be blank.")
                    continue
                category = input("▸ Category [Default: General]: ").strip() or "General"
                priority = input("▸ Priority (HIGH / MED / LOW) [Default: MED]: ").strip().upper() or "MED"
                
                new_item = add_task(tasks, title, category, priority)
                save_tasks(tasks)
                print(f"✓ Task '{new_item['title']}' added successfully.")

            elif choice == "3":
                if not tasks:
                    print("⚠ Task list is empty.")
                    continue
                display_task_table(tasks)
                try:
                    num = int(input("▸ Select display # to complete: "))
                    done_item = mark_completed(tasks, num - 1)
                    if done_item:
                        save_tasks(tasks)
                        print(f"✓ Task '{done_item['title']}' marked DONE.")
                    else:
                        print("⚠ Invalid selection number.")
                except ValueError:
                    print("⚠ Enter a valid integer.")

            elif choice == "4":
                query = input("▸ Enter search keyword/category: ").strip()
                if query:
                    results = search_tasks(tasks, query)
                    display_task_table(results, f"SEARCH RESULTS FOR '{query}'")
                else:
                    print("⚠ Search query cannot be blank.")

            elif choice == "5":
                if not tasks:
                    print("⚠ Task list is empty.")
                    continue
                display_task_table(tasks)
                try:
                    num = int(input("▸ Select display # to delete: "))
                    removed = delete_task(tasks, num - 1)
                    if removed:
                        save_tasks(tasks)
                        print(f"✓ Deleted task '{removed['title']}'.")
                    else:
                        print("⚠ Invalid selection number.")
                except ValueError:
                    print("⚠ Enter a valid integer.")

            elif choice == "6":
                cleared = clear_completed(tasks)
                if cleared > 0:
                    save_tasks(tasks)
                    print(f"✓ Cleared {cleared} completed task(s).")
                else:
                    print("⚠ No completed tasks available to clear.")

            elif choice == "7":
                stats = get_statistics(tasks)
                print("\n┌── SYSTEM METRICS ──────────────────────────────────────────────────────────┐")
                print(f"│ Total Tasks Registered : {stats['total']:<49} │")
                print(f"│ Pending Tasks          : {stats['pending']:<49} │")
                print(f"│ Completed Tasks        : {stats['completed']:<49} │")
                print(f"│ High Priority Pending  : {stats['high_priority']:<49} │")
                print("└────────────────────────────────────────────────────────────────────────────┘")

            elif choice == "8":
                save_tasks(tasks)
                print("\n✓ Database state synchronized to storage. Application terminated.")
                break

            else:
                print("⚠ Invalid option selection.")

    except (KeyboardInterrupt, EOFError):
        save_tasks(tasks)
        print("\n\n✓ Program interrupted. Application state saved safely. Exiting...")


if __name__ == "__main__":
    main()