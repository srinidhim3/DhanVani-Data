import logging
import requests
import feedparser
from typing import Optional

import config

logger = logging.getLogger(__name__)


def fetch_and_parse_feed(session: requests.Session, rss_url: str) -> Optional[feedparser.FeedParserDict]:
    """
    Fetches the RSS feed from the given URL and parses it.
    Returns the parsed feed object.
    """
    headers = {'User-Agent': config.USER_AGENT}
    logger.info(f"Fetching RSS feed from: {rss_url}")
    try:
        response = session.get(rss_url, headers=headers, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        logger.info(f"Successfully fetched and parsed feed with {len(feed.entries)} entries.")
        return feed
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching RSS feed from {rss_url}: {e}")
        return None