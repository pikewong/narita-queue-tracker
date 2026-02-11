import requests
from bs4 import BeautifulSoup
import re
import csv
import os
from datetime import datetime

URL = "https://www.narita-airport.jp/en/airport/congestion/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
CSV_FILE = "narita_immigration_wait_times.csv"


def extract_wait_times():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    page_text = soup.get_text(separator=" ")

    # Match ranges like: 0-20 min or 10–30 min
    pattern = r"(Japanese|Foreign|Visitor).*?(\d+\s*[-–]\s*\d+\s*min)"
    matches = re.findall(pattern, page_text, re.IGNORECASE)

    japanese_wait = None
    visitor_wait = None

    for label, time in matches:
        label_lower = label.lower()
        if "japanese" in label_lower:
            japanese_wait = time.strip()
        elif "foreign" in label_lower or "visitor" in label_lower:
            visitor_wait = time.strip()

    return japanese_wait, visitor_wait


def extract_max_minutes(wait_string):
    """
    Convert range like '0-20 min' or '10–30 min' into numeric maximum (20, 30).
    Also handles single values like '15 min'.
    """
    if not wait_string:
        return None

    # Range case
    range_match = re.search(r"(\d+)\s*[-–]\s*(\d+)", wait_string)
    if range_match:
        return int(range_match.group(2))

    # Single number case (e.g., '15 min')
    single_match = re.search(r"(\d+)", wait_string)
    if single_match:
        return int(single_match.group(1))

    return None


def write_to_csv(run_time, japanese_wait, visitor_wait):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["run time", "japanese wait time", "Visitor wait time"])

        writer.writerow([run_time, japanese_wait, visitor_wait])


if __name__ == "__main__":
    try:
        run_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        japanese_range, visitor_range = extract_wait_times()

        # ✅ Convert to numeric maximum minutes
        japanese_max = extract_max_minutes(japanese_range)
        visitor_max = extract_max_minutes(visitor_range)

        write_to_csv(run_time, japanese_max, visitor_max)

        print("Data saved successfully.")
        print("Run time:", run_time)
        print("Japanese wait time (max minutes):", japanese_max)
        print("Visitor wait time (max minutes):", visitor_max)

    except Exception as e:
        print("Error:", e)


