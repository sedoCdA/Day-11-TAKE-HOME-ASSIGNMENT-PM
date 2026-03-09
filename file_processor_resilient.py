import csv
import json
import logging
import time
import traceback
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    filename="file_processor.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)


def parse_csv(file_path):
    with open(file_path, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"'{file_path.name}' is empty.")
    return rows


def calculate_total_revenue(rows):
    return sum(int(r["qty"]) * float(r["price"]) for r in rows)


def process_file(file_path, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            rows    = parse_csv(file_path)
            revenue = calculate_total_revenue(rows)
            return {"file": file_path.name, "rows": len(rows), "revenue": round(revenue, 2)}
        except PermissionError as e:
            logging.error(f"Attempt {attempt} — PermissionError on '{file_path.name}': {e}")
            print(f"Permission error on '{file_path.name}', retrying ({attempt}/{max_attempts})...")
            time.sleep(1)
        except (ValueError, KeyError, OSError) as e:
            logging.error(f"Failed to process '{file_path.name}':\n{traceback.format_exc()}")
            print(f"Skipping '{file_path.name}': {e}")
            return None
    logging.error(f"'{file_path.name}' failed after {max_attempts} attempts.")
    print(f"Giving up on '{file_path.name}' after {max_attempts} attempts.")
    return None


def export_report(results, errors, output_path):
    report = {
        "generated_at":    datetime.now().isoformat(timespec="seconds"),
        "files_processed": len(results),
        "files_failed":    len(errors),
        "error_details":   errors,
        "results":         results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to '{output_path}'.")


def main():
    data_dir    = Path("data")
    output_path = Path("output/processing_report.json")
    output_path.parent.mkdir(exist_ok=True)

    results, errors = [], []

    for file in sorted(data_dir.glob("*.csv")):
        result = process_file(file)
        if result:
            results.append(result)
            print(f"Processed '{file.name}': {result['rows']} rows, revenue {result['revenue']}")
        else:
            errors.append({"file": file.name, "reason": "See file_processor.log for details."})

    export_report(results, errors, output_path)
    print(f"\nDone. {len(results)} succeeded, {len(errors)} failed.")


if __name__ == "__main__":
    main()
