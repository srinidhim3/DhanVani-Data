import logging
import os
import psycopg2
from dotenv import load_dotenv

from ai_summarizer import AISummarizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This configuration tells the script which tables to check, what the primary key is,
# and which column contains the document URL.
TABLES_TO_SUMMARIZE = [
    {"name": "nse_announcements", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_annual_reports", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_board_meetings", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_brsr", "pk_col": "guid", "url_col": "pdf_link"},
    {"name": "nse_corporate_actions", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_insider_trading", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_investor_complaints", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_offer_documents", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_related_party_transactions", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_regulation31", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_regulation29", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_reason_for_encumbrance", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_secretarial_compliance", "pk_col": "guid", "url_col": "pdf_link"},
    {"name": "nse_share_transfers", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_shareholding_pattern", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_statement_of_deviation", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_unit_holding_pattern", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_voting_results", "pk_col": "guid", "url_col": "link"},
    {"name": "nse_circulars", "pk_col": "guid", "url_col": "link"},
]

def get_db_connection():
    """Establishes and returns a database connection."""
    load_dotenv()
    db_connection_string = os.getenv("DB_CONNECTION_STRING")
    if not db_connection_string:
        logger.critical("DB_CONNECTION_STRING not found in .env file or environment variables.")
        raise ValueError("DB_CONNECTION_STRING is not set.")
    return psycopg2.connect(db_connection_string)

def process_table(conn, summarizer, table_config):
    """
    Fetches unsummarized records from a table, generates summaries,
    and updates the database.
    """
    table_name = table_config["name"]
    pk_col = table_config["pk_col"]
    url_col = table_config["url_col"]
    summary_col = "summary"  # Assuming the column is always named 'summary'

    logger.info(f"Checking for unsummarized articles in '{table_name}'...")
    updated_count = 0

    # Using 'with' for the cursor ensures it's closed properly
    with conn.cursor() as cur:
        query = f"""
            SELECT {pk_col}, {url_col}
            FROM {table_name}
            WHERE ({summary_col} IS NULL OR {summary_col} = '')
              AND {url_col} IS NOT NULL AND {url_col} <> ''
        """
        try:
            cur.execute(query)
            records_to_process = cur.fetchall()

            if not records_to_process:
                logger.info(f"No unsummarized articles found in '{table_name}'.")
                return

            logger.info(f"Found {len(records_to_process)} articles to summarize in '{table_name}'.")

            for pk_val, url in records_to_process:
                if not url:
                    continue

                logger.info(f"Summarizing URL: {url}")
                try:
                    summary = summarizer.summarize(url)
                    logger.info(f"Generated summary: {summary}")
                    if summary:
                        update_query = f"""
                            UPDATE {table_name}
                            SET {summary_col} = %s
                            WHERE {pk_col} = %s;
                        """
                        cur.execute(update_query, (summary, pk_val))
                        conn.commit()
                        updated_count += 1
                        logger.info(f"Successfully updated summary for table {table_name} with PK: {pk_val}")
                    else:
                        # Mark the record as failed so we don't try it again.
                        logger.warning(f"Failed to generate summary for URL: {url} (PK: {pk_val}). Marking as failed.")
                        update_query = f"""
                            UPDATE {table_name}
                            SET {summary_col} = '[SUMMARY_FAILED]'
                            WHERE {pk_col} = %s;
                        """
                        cur.execute(update_query, (pk_val,))
                        conn.commit()
                except Exception as e:
                    logger.error(f"An unexpected error occurred while summarizing {url} (PK: {pk_val}): {e}")

            logger.info(f"Committed {updated_count} summary updates for table '{table_name}'.")

        except psycopg2.Error as e:
            logger.error(f"Database error while processing table '{table_name}': {e}")
            conn.rollback() # Rollback any partial changes from the failed transaction

def main():
    """Main function to orchestrate the summarization process."""
    logger.info("--- Starting AI Summarization Process ---")
    conn = None
    try:
        summarizer = AISummarizer()
        conn = get_db_connection()

        for table_config in TABLES_TO_SUMMARIZE:
            process_table(conn, summarizer, table_config)

    except (ValueError, psycopg2.Error) as e:
        logger.critical(f"A critical setup error occurred: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred in the main process: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
    logger.info("--- AI Summarization Process Finished ---")

if __name__ == "__main__":
    main()