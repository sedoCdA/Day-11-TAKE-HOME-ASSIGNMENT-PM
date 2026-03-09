# Interview Answers — Day 11 PM (Exception Handling)

---

## Q1 — try / except / else / finally Execution Flow

### When each block runs

| Block | Runs when |
|-------|-----------|
| try | Always — contains the code that might fail |
| except | Only if an exception was raised in try |
| else | Only if NO exception was raised in try |
| finally | Always — whether or not an exception occurred |

### Code example using all four blocks
```python
def read_file(path):
    try:
        f = open(path, "r")
        data = f.read()
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except OSError as e:
        print(f"OS error: {e}")
    else:
        print("File read successfully.")
        return data
    finally:
        print("Finished attempt to read file.")
```

### Execution flows

Success path:
```
try runs → no exception → else runs → finally runs
```

Failure path:
```
try runs → exception raised → except runs → finally runs → else skipped
```

### What happens if an exception occurs inside else

The else block is not protected by the except clause above it.
If an exception occurs inside else, it propagates up to the caller
and the except block does NOT catch it.
```python
try:
    x = 1
except ValueError:
    print("won't run")
else:
    int("bad")   # raises ValueError — NOT caught by except above
finally:
    print("this still runs")
```

---

## Q2 — safe_json_load()
```python
import json
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)

def safe_json_load(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        print(f"Error: '{filepath}' does not exist.")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in '{filepath}': {e}")
        print(f"Error: '{filepath}' contains invalid JSON.")
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
        print(f"Error: No permission to read '{filepath}'.")
    return None

# Tests
data = safe_json_load("output/revenue_summary.json")
print(data)

print(safe_json_load("nonexistent.json"))
print(safe_json_load("data/data1.csv"))
```

---

## Q3 — Debug Problem

### Buggy code
```python
def process_data(data_list):
    results = []
    for item in data_list:
        try:
            value = int(item)
            results.append(value * 2)
        except:
            print("Error occurred")
            continue
        finally:
            return results
    return results
```

### Bug 1 — Bare except

`except:` catches every exception including KeyboardInterrupt and
SystemExit which should never be silently swallowed.
Always catch specific exceptions.

### Bug 2 — return inside finally

`finally` runs after every iteration of the loop — including the
first one. Putting `return results` inside finally causes the
function to return after processing only the first item, completely
ignoring the rest of the list.
Remove return from finally entirely.

### Bug 3 — Uninformative error message

`print("Error occurred")` tells the developer nothing about what
failed or which value caused the problem. Include the exception
and the offending value in the message.

### Fixed version
```python
def process_data(data_list):
    results = []
    for item in data_list:
        try:
            value = int(item)
            results.append(value * 2)
        except ValueError as e:
            print(f"Skipping '{item}': {e}")
            continue
    return results

# Tests
print(process_data(["1", "2", "abc", "4"]))   # [2, 4, 8]
print(process_data([]))                        # []
print(process_data(["x", "y"]))               # [] with messages
