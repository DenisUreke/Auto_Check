import sqlite3
from pathlib import Path
from openpyxl import Workbook

DB_PATH = Path("saw_monitor.db")
EXCEL_PATH = Path(r"C:\Users\Denis.Ureke\OneDrive - Nobia AB\Skrivbordet\ping_log.xlsx")


def export_to_excel():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            target_name,
            url,
            checked_at,
            response_time_ms,
            success,
            status_code,
            response_text,
            error_text
        FROM ping_log
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Call Saw Log"

    headers = [
        "ID",
        "Target Name",
        "URL",
        "Checked At",
        "Response Time (ms)",
        "Success",
        "Status Code",
        "Response Text",
        "Error Text",
    ]

    ws.append(headers)

    for row in rows:
        ws.append(row)

    wb.save(EXCEL_PATH)

    print(f"Excel exported to: {EXCEL_PATH.resolve()}")

if __name__ == "__main__":
    export_to_excel()