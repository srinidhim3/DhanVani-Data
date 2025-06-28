import psycopg2
import logging
from typing import List, Tuple, Any, Callable
from pathlib import Path

import config

logger = logging.getLogger(__name__)

def setup_database(conn: psycopg2.extensions.connection):
    """Creates all necessary tables by executing .sql files from the 'sql' directory."""
    cursor = conn.cursor()
    logger.info("Setting up database tables...")

    sql_dir = Path(__file__).parent / "sql"
    if not sql_dir.is_dir():
        logger.critical(f"SQL directory not found at '{sql_dir}'. Cannot set up database.")
        raise FileNotFoundError(f"SQL directory not found: {sql_dir}")

    sql_files = sorted(list(sql_dir.glob("*.sql")))
    if not sql_files:
        logger.warning(f"No .sql files found in '{sql_dir}'. No tables will be created.")
        return

    for sql_file in sql_files:
        logger.info(f"Executing schema from {sql_file.name}...")
        with open(sql_file, 'r') as f:
            sql_script = f.read()
            try:
                cursor.execute(sql_script)
                logger.info(f"Successfully executed {sql_file.name}.")
            except psycopg2.Error as e:
                logger.error(f"Error executing {sql_file.name}: {e}")
                raise

def insert_data(conn: psycopg2.extensions.connection, entries: List[Any], sql_insert: str, parser_func: Callable[[Any], Tuple]):
    """
    Generic function to insert new entries into a PostgreSQL database table.
    Skips entries that already exist based on the 'guid' (via INSERT ON CONFLICT DO NOTHING).
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
        except psycopg2.Error as e:
            guid = parsed_data[0] if parsed_data else "N/A"
            logger.error(f"Could not insert entry with GUID '{guid}'. Error: {e}")

    table_name = sql_insert.split("INTO")[1].strip().split()[0]
    logger.info(f"Processed {len(entries)} entries. Inserted {new_entries_count} new records into {table_name}.")