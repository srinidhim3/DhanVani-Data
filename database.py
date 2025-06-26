import sqlite3
import logging
from typing import List, Tuple, Any, Callable

import config

logger = logging.getLogger(__name__)


def setup_database(conn: sqlite3.Connection):
    """Creates all necessary tables in the database if they don't exist."""
    cursor = conn.cursor()
    logger.info("Setting up database tables...")

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_ANNOUNCEMENTS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            description TEXT,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_ANNUAL_REPORTS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            report_date TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_BOARD_MEETINGS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            meeting_date TEXT NOT NULL,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_BRSR} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            pdf_link TEXT,
            xml_link_name TEXT,
            submission_date TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_CORPORATE_ACTIONS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            description TEXT,
            published_at TEXT NOT NULL,
            ex_date TEXT,
            series TEXT,
            purpose TEXT,
            face_value REAL,
            record_date TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_INSIDER_TRADING} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            security_type TEXT,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_INVESTOR_COMPLAINTS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            quarter_ending_date TEXT NOT NULL,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_RELATED_PARTY_TRANSACTIONS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            period_end_date TEXT NOT NULL,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_REGULATION29} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            acquirer_name TEXT,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_REASON_FOR_ENCUMBRANCE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT, -- Made nullable
            promoter_name TEXT,
            published_at TEXT -- Made nullable
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_REGULATION31} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            promoter_or_pacs_name TEXT,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_SECRETARIAL_COMPLIANCE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            pdf_link TEXT,
            xml_link TEXT,
            financial_year TEXT,
            submission_type TEXT,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_OFFER_DOCUMENTS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            description TEXT,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_SHARE_TRANSFERS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            period_end_date TEXT NOT NULL,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_SHAREHOLDING_PATTERN} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            as_on_date TEXT NOT NULL,
            promoter_holding REAL,
            public_holding REAL,
            employee_trust_holding REAL,
            revised_status TEXT,
            submission_date TEXT NOT NULL,
            revision_date TEXT,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_STATEMENT_OF_DEVIATION} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            period_end_date TEXT NOT NULL,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_UNIT_HOLDING_PATTERN} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            as_on_date TEXT NOT NULL,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_VOTING_RESULTS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            meeting_date TEXT NOT NULL,
            published_at TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NSE_CIRCULARS} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            link TEXT,
            published_at TEXT NOT NULL
        )
    """)

    conn.commit()
    logger.info("Database tables are ready.")


def insert_data(conn: sqlite3.Connection, entries: List[Any], sql_insert: str, parser_func: Callable[[Any], Tuple]):
    """
    Generic function to insert new entries into a database table.
    Skips entries that already exist based on the 'guid' (via INSERT OR IGNORE).
    """
    cursor = conn.cursor()
    new_entries_count = 0

    for entry in entries:
        parsed_data = parser_func(entry)
        if not parsed_data:
            continue

        try:
            cursor.execute(sql_insert, parsed_data)
            if cursor.rowcount > 0:
                new_entries_count += 1
        except sqlite3.Error as e:
            guid = parsed_data[0] if parsed_data else "N/A"
            logger.error(f"Could not insert entry with GUID '{guid}'. Error: {e}")

    conn.commit()
    table_name = sql_insert.split("INTO")[1].strip().split()[0]
    logger.info(f"Processed {len(entries)} entries. Inserted {new_entries_count} new records into {table_name}.")