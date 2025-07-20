"""
Appointment Slot Tracker for Indian Embassy Netherlands

Features:
- Checks appointment availability for Aug-Dec 2025
- Prints color code counts per month in a table
- Refreshes every 5 minutes
- Plays alert sound if any green slot is available

Required packages:
- requests
- beautifulsoup4
- tabulate
- pygame

Install with:
  pip install requests beautifulsoup4 tabulate pygame
"""
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import time
import os
import pygame
import datetime

BASE_URL = "https://www.indianembassynetherlands.gov.in/apt/appointment.php"
MONTHS = [
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December")
]
PARAMS = {
    "apttype": "Submission",
    "locationid": "2",
    "serviceid": "2"
}
ALERT_SOUND = "alert.mp3"  # Place a short mp3 file named alert.mp3 in the same folder

COLOR_MAP = {
    "red_booked": "RED - Already Booked",
    "red_noservice": "RED - No Service",
    "grey": "Grey - Not opened",
    "green": "Green/Others - Check if slot is open"
}


def fetch_month(month, year=2025):
    params = PARAMS.copy()
    params["month"] = str(month)
    params["year"] = str(year)  # Fixed unmatched bracket
    try:
        # Print the final URL before making the request
        req = requests.Request('GET', BASE_URL, params=params).prepare()
        print(f"Fetching URL: {req.url}")
        resp = requests.get(BASE_URL, params=params, timeout=20)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Error fetching {month}/{year}: {e}")
        return None


def parse_colors(html):
    soup = BeautifulSoup(html, "html.parser")
    color_counts = {c: 0 for c in COLOR_MAP}
    green_dates = []
    for ul in soup.find_all("ul", class_="dates"):
        for a in ul.find_all("a"):
            href = a.get("href", "")
            # Skip date=0 and date > 31
            if "date=0" in href:
                continue
            import re
            match = re.search(r"date=(\d+)", href)
            if match:
                day = int(match.group(1))
                if day > 31:
                    continue
            else:
                day = None
            li = a.find("li")
            if not li:
                continue
            class_attr = li.get("class")
            if class_attr:
                class_str = " ".join(class_attr).strip()
            else:
                class_str = ""
            if "a_full" in class_str:
                color = "red_booked"
            elif class_str == "" or class_str == " " or class_str == "end" or class_str == " end ":
                color = "red_noservice"
            elif "a_disable" in class_str:
                color = "grey"
            else:
                color = "green"
                if day is not None:
                    green_dates.append(day)
            color_counts[color] += 1
    return color_counts, green_dates


def print_table(results):
    headers = ["Month"] + [COLOR_MAP[c] for c in COLOR_MAP]
    table = []
    for month, counts in results.items():
        row = [month] + [counts[c] for c in COLOR_MAP]
        table.append(row)
    print(tabulate(table, headers=headers, tablefmt="grid"))


def play_alert():
    if os.path.exists(ALERT_SOUND):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(ALERT_SOUND)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            print("Press any key to continue checking further...")
            # Wait for key press
            import sys
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error playing alert sound: {e}")
    else:
        print("Alert sound file not found.")


def main():
    while True:
        results = {}
        green_found = False
        green_slots = {}
        for m, mname in MONTHS:
            html = fetch_month(m)
            if html:
                counts, green_dates = parse_colors(html)
                results[mname] = counts
                if counts["green"] > 0:
                    green_found = True
                    green_slots[mname] = green_dates
            else:
                results[mname] = {c: "Error" for c in COLOR_MAP}
        os.system("clear")
        print_table(results)
        if green_found:
            print("\nGreen slot available! Please check the embassy website.")
            # print the website link of the respective month e.g., this is for September https://www.indianembassynetherlands.gov.in/apt/appointment.php?month=09&year=2025&apttype=Submission&locationid=2&serviceid=2#dw
            print("\nGreen slots found:")
            # Print the website link for each month with green slots
            for m, mname in MONTHS:
                if mname in green_slots:
                    month_str = f"{m:02d}"
                    year_str = "2025"
                    link = f"https://www.indianembassynetherlands.gov.in/apt/appointment.php?month={month_str}&year={year_str}&apttype=Submission&locationid=2&serviceid=2#dw"
                    print(f"Month: {mname}, Link: {link}")
            for mname, dates in green_slots.items():
                if dates:
                    print(f"Month: {mname}, Dates: {', '.join(str(d) for d in dates)}")
            play_alert()
        else:
            print("\nNo green slots found.")
        print("\nNext refresh in:")
        for remaining in range(300, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer = f"{mins:02d}:{secs:02d}"
            print(f"\r{timer}", end="", flush=True)
            time.sleep(1)
        print()


if __name__ == "__main__":
    main()
