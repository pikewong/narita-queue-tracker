import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

URL = "https://www.narita-airport.jp/en/airport/congestion/"
headers = {"User-Agent": "Mozilla/5.0"}

def get_foreigner_wait_time():
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    for text in soup.find_all(string=True):
        if "Foreign" in text:
            return text.strip()

    return "Not found"

def save_to_csv(wait_time):
    file_exists = os.path.isfile("narita_queue_log.csv")

    with open("narita_queue_log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "wait_time"])
        writer.writerow([datetime.utcnow(), wait_time])

if __name__ == "__main__":
    wait_time = get_foreigner_wait_time()
    print(wait_time)
    save_to_csv(wait_time)
