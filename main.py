import logging
import psycopg2
import requests
import concurrent.futures
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

import config
import database
import fetcher
import reporting

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to orchestrate the fetching and storing process for all feeds.
    """
    if not config.DB_CONNECTION_STRING:
        logger.critical("DB_CONNECTION_STRING environment variable not set. The application cannot connect to the database.")
        logger.critical("For local development, create a .env file from .env.example.")
        logger.critical("For production, set the environment variable in your deployment environment.")
        return
    processing_stats = {}
    conn = None
    try:
        conn = psycopg2.connect(config.DB_CONNECTION_STRING)
        conn.autocommit = True  # Set connection to autocommit mode
        logger.info(f"Successfully connected to database.")

        # Ensure all tables are created before proceeding
        # database.setup_database(conn)
        with requests.Session() as session:
            # Fetch all feeds concurrently for better performance
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(config.FEEDS_TO_PROCESS)) as executor:
                future_to_feed_config = {
                    executor.submit(fetcher.fetch_and_parse_feed, session, feed_config['url']): feed_config
                    for feed_config in config.FEEDS_TO_PROCESS
                }

                for future in concurrent.futures.as_completed(future_to_feed_config):
                    feed_config = future_to_feed_config[future]
                    feed_name = feed_config['name']
                    try:
                        feed = future.result()
                        if feed and feed.entries:
                            logger.info(f"--- Inserting data for: {feed_name} ---")
                            inserted_count = database.insert_data(
                                conn=conn,
                                entries=feed.entries,
                                sql_insert=feed_config['sql'],
                                parser_func=feed_config['parser']
                            )
                            processing_stats[feed_name] = inserted_count
                        else:
                            logger.warning(f"No entries found or failed to fetch feed for {feed_config['name']}.")
                            processing_stats[feed_name] = 0
                    except Exception as exc:
                        logger.error(f"Error processing feed {feed_name}: {exc}")
                        processing_stats[feed_name] = "Failed"
        # Generate and send the report after all feeds are processed
        logger.info("All feeds processed. Generating and sending email report...")
        if not reporting.send_email_report(processing_stats):
            logger.warning("Could not send the final email report.")
    except psycopg2.Error as e:
        logger.critical(f"A critical database error occurred: {e}. The application will exit.")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}. The application will exit.")
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
    logger.info("\nProcess finished.")

if __name__ == "__main__":
    main()