import logging
import sqlite3
import requests
import concurrent.futures

import config
import database
import fetcher

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Main function to orchestrate the fetching and storing process for all feeds.
    """
    try:
        with sqlite3.connect(config.DB_FILE) as conn:
            logger.info(f"Successfully connected to database '{config.DB_FILE}'.")
            database.setup_database(conn)

            with requests.Session() as session:
                # Fetch all feeds concurrently for better performance
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(config.FEEDS_TO_PROCESS)) as executor:
                    future_to_feed_config = {
                        executor.submit(fetcher.fetch_and_parse_feed, session, feed_config['url']): feed_config
                        for feed_config in config.FEEDS_TO_PROCESS
                    }

                    for future in concurrent.futures.as_completed(future_to_feed_config):
                        feed_config = future_to_feed_config[future]
                        try:
                            feed = future.result()
                            if feed and feed.entries:
                                logger.info(f"--- Inserting data for: {feed_config['name']} ---")
                                database.insert_data(
                                    conn=conn,
                                    entries=feed.entries,
                                    sql_insert=feed_config['sql'],
                                    parser_func=feed_config['parser']
                                )
                            else:
                                logger.warning(f"No entries found or failed to fetch feed for {feed_config['name']}.")
                        except Exception as exc:
                            logger.error(f"Error processing feed {feed_config['name']}: {exc}")

    except sqlite3.Error as e:
        logger.critical(f"A critical database error occurred: {e}. The application will exit.")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}. The application will exit.")
    logger.info("\nProcess finished.")

if __name__ == "__main__":
    main()
