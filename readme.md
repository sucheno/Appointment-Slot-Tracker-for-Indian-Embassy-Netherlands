# Appointment Slot Tracker for Indian Embassy Netherlands

This script checks appointment slot availability for the Indian Embassy in the Netherlands for the months August to December 2025.

## Features
- Checks appointment availability for Aug-Dec 2025
- Prints color-coded slot counts per month in a table
- Refreshes every 5 minutes
- Plays alert sound if any green slot is available
- Shows available dates and direct links to the embassy website for booking

## Requirements
- Python 3.x
- requests
- beautifulsoup4
- tabulate
- pygame

Install dependencies with:
```bash
pip install requests beautifulsoup4 tabulate pygame
```

## Usage
Run the script:
```bash
python appointment_tracker.py
```

The script will display a table of slot availability and alert you if any green slot is found. Press any key to continue checking further when alerted.

## Notes
- The script refreshes every 5 minutes automatically.
- Direct links to the embassy website for each month with available slots are shown when green slots are found.
