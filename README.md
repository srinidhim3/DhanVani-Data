# DhanVani-Data

DhanVani-Data is a Python-based data pipeline that fetches corporate data from various National Stock Exchange (NSE) of India RSS feeds and stores it in a local SQLite database.

It is designed to be a simple, robust, and extensible tool for collecting financial announcements, reports, and other corporate actions.

## Features

- Fetches data from multiple NSE RSS feeds:
  - Corporate Announcements
  - Annual Reports
  - Board Meetings
  - Business Responsibility and Sustainability Reports (BRSR)
- Parses the RSS feed data into a structured format.
- Stores the structured data in a SQLite database, avoiding duplicates.
- Modular and easily extensible to include more data sources.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/srinidhim3/DhanVani-Data.git
    cd DhanVani-Data
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```

This will create a `DhanVani.db` file in the project root containing the fetched data.