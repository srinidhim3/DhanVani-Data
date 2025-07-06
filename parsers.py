import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import functools
import hashlib
import requests
logger = logging.getLogger(__name__)
FeedEntry = Dict[str, Any]

@functools.lru_cache(maxsize=256)
def get_symbol_from_name(company_name):
    url = f"https://www.nseindia.com/api/search/autocomplete?q={company_name}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com"
    }

    session = requests.Session()
    session.headers.update(headers)

    # Hit the homepage first to get cookies set
    session.get("https://www.nseindia.com", timeout=5)

    # Now hit the API
    response = session.get(url, timeout=5)
    if response.ok:
        results = response.json()
        for item in results.get("symbols", []):
            symbol_info = item.get("symbol_info", "").lower()
            symbol = item.get("symbol", "")
            if company_name.lower() in symbol_info:
                return symbol
    return None

def _parse_datetime(date_str: str, formats: List[str]) -> Optional[datetime]:
    """Try parsing a date string with a list of possible formats."""
    if not date_str:
        return None # Return None for empty or None date_str
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    return None


def parse_announcement_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'announcements' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    title = entry.get("title")
    if not title:
        logger.warning("Skipping entry with no title.")
        return None

    published_dt = None
    if entry.get("published_parsed"):
        published_dt = datetime.fromtimestamp(time.mktime(entry.published_parsed)) # type: ignore
    elif entry.get("published"):
        published_dt = _parse_datetime(entry.published, ["%d-%b-%Y %H:%M:%S"])

    if not published_dt:
        logger.warning(f"Skipping entry with unparsable/missing date: '{title}' (Raw date: '{entry.get('published')}')")
        return None

    published_iso = published_dt.isoformat()
    link = entry.get("link")
    guid = link if link else f"{title}-{published_iso}"
    company_symbol = get_symbol_from_name(title)
    summary = ""

    return (
        guid,
        title,
        link,
        entry.get("description"),
        published_iso,
        company_symbol,
        summary
    )


def parse_annual_report_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'annual_reports' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping annual report with no link or title: '{title}'")
        return None

    report_date_str = entry.get("description", "").replace("AS ON DATE :", "").strip()
    report_dt = _parse_datetime(report_date_str, ["%d-%b-%y"])
    if not report_dt:
        logger.warning(f"Skipping annual report with no valid date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (guid, title, guid, report_dt.date().isoformat(), company_symbol, summary)


def parse_board_meeting_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'board_meetings' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping board meeting with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping board meeting with no valid published date: '{title}'")
        return None

    description_parts = entry.get("description", "").split("|")
    meeting_date_str = ""
    if len(description_parts) > 1 and "Meeting Date:" in description_parts[1]:
        meeting_date_str = description_parts[1].replace("Meeting Date:", "").strip()

    meeting_dt = _parse_datetime(meeting_date_str, ["%d-%b-%Y"])
    if not meeting_dt:
        logger.warning(f"Skipping board meeting with no valid meeting date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""

    return (guid, title, guid, meeting_dt.date().isoformat(), published_dt.isoformat(), company_symbol, summary)


def parse_brsr_report_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'brsr' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping BRSR entry with no link or title: '{title}'")
        return None

    link_parts = guid.split()
    pdf_link = link_parts[0] if link_parts else None
    xml_link_name = link_parts[1] if len(link_parts) > 1 else None

    submission_date_str = entry.get("description", "").replace("ORIGINAL SUBMISSION DATE :", "").strip()
    submission_dt = _parse_datetime(submission_date_str, ["%d-%b-%y %I.%M.%S.%f %p"])
    if not submission_dt:
        logger.warning(f"Could not parse submission date: '{submission_date_str}' for title: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (guid, title, pdf_link, xml_link_name, submission_dt.isoformat(), company_symbol, summary)


def parse_corporate_action_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'corporate_actions' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    title = entry.get("title")
    description = entry.get("description")
    if not title or not description:
        logger.warning(f"Skipping corporate action with no title or description: '{title}'")
        return None

    # Parse description fields into a dictionary for easy access
    desc_dict = {}
    for item in description.split('|'):
        parts = item.split(':', 1)
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            if value and value != '-':
                desc_dict[key] = value

    record_date_str = desc_dict.get("RECORD DATE")
    if not record_date_str:
        logger.warning(f"Skipping corporate action with no record date: '{title}'")
        return None

    # Create a unique GUID from title and record date to avoid duplicates
    guid = f"{title}-{record_date_str}"

    # Parse dates
    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping corporate action with no valid published date: '{title}'")
        return None

    record_dt = _parse_datetime(record_date_str, ["%d-%b-%Y"])
    if not record_dt:
        logger.warning(f"Skipping corporate action with no valid record date: '{title}'")
        return None

    ex_date_str = ""
    if "Ex-Date:" in title:
        ex_date_str = title.split("Ex-Date:")[1].strip()
    ex_dt = _parse_datetime(ex_date_str, ["%d-%b-%Y"])

    # Parse other fields
    face_value_str = desc_dict.get("FACE VALUE")
    face_value = float(face_value_str) if face_value_str and face_value_str.replace('.', '', 1).isdigit() else None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (
        guid, title, entry.get("link"), description, published_dt.isoformat(),
        ex_dt.date().isoformat() if ex_dt else None, desc_dict.get("SERIES"),
        desc_dict.get("PURPOSE"), face_value, record_dt.date().isoformat(),
        company_symbol, summary
    )


def parse_insider_trading_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'insider_trading' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping insider trading entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M"])
    if not published_dt:
        logger.warning(f"Skipping insider trading entry with no valid published date: '{title}'")
        return None

    security_type = None
    description = entry.get("description", "")
    if "TYPE OF SECURITY :" in description:
        security_type = description.split(":", 1)[1].strip()
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (
        guid,
        title,
        guid,
        security_type,
        published_dt.isoformat(),
        company_symbol,
        summary
    )


def parse_investor_complaint_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'investor_complaints' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping investor complaint entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping investor complaint entry with no valid published date: '{title}'")
        return None

    quarter_ending_dt = None
    description = entry.get("description", "")
    if "FOR QUARTER ENDING :" in description:
        date_str = description.split(":", 1)[1].strip()
        quarter_ending_dt = _parse_datetime(date_str, ["%d-%b-%y"])

    if not quarter_ending_dt:
        logger.warning(f"Skipping investor complaint entry with no valid quarter ending date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (guid, title, guid, quarter_ending_dt.date().isoformat(), published_dt.isoformat(), company_symbol, summary)


def parse_offer_document_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'offer_documents' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping offer document entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y"])
    if not published_dt:
        logger.warning(f"Skipping offer document entry with no valid published date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (
        guid,
        title,
        guid,
        entry.get("description"),
        published_dt.date().isoformat(),
        company_symbol,
        summary
    )


def parse_related_party_transaction_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'related_party_transactions' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping related party transaction entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping related party transaction entry with no valid published date: '{title}'")
        return None

    period_end_dt = None
    description = entry.get("description", "")
    if "PERIOD END DATE :" in description:
        date_str = description.split(":", 1)[1].strip()
        period_end_dt = _parse_datetime(date_str, ["%d-%b-%Y"])
    if not period_end_dt:
        logger.warning(f"Skipping related party transaction entry with no valid period end date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (guid, title, guid, period_end_dt.date().isoformat(), published_dt.isoformat(), company_symbol, summary)


def parse_regulation31_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'regulation31' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping Regulation 31 entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping Regulation 31 entry with no valid published date: '{title}'")
        return None

    promoter_or_pacs_name = None
    description = entry.get("description", "")
    if "NAME OF PROMOTER(S) OR PACS WITH HIM :" in description:
        promoter_or_pacs_name = description.split(":", 1)[1].strip()
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (
        guid, title, guid, promoter_or_pacs_name, published_dt.isoformat(), company_symbol, summary
    )


def parse_regulation29_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'regulation29' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping Regulation 29 entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M"])
    if not published_dt:
        logger.warning(f"Skipping Regulation 29 entry with no valid published date: '{title}'")
        return None

    acquirer_name = None
    description = entry.get("description", "")
    if "NAME(S)OF THE ACQUIRER AND ITS(PAC) :" in description:
        acquirer_name = description.split(":", 1)[1].strip()
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (
        guid, title, guid, acquirer_name, published_dt.isoformat(), company_symbol, summary
    )


def parse_reason_for_encumbrance_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'reason_for_encumbrance' table.
    Handles entries with potentially empty link and pubDate tags.
    """
    title = entry.get("title")
    description = entry.get("description")
    if not title or not description:
        logger.warning(f"Skipping Reason for Encumbrance entry with no title or description: '{title}'")
        return None

    # Create a stable GUID from content as link is empty
    guid = hashlib.sha256(f"{title}{description}".encode()).hexdigest()

    # Handle potentially empty link
    link = entry.get("link")

    # Handle potentially empty pubDate
    published_dt = None
    if entry.get("published_parsed"):
        published_dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
    elif entry.get("published"):
        published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S", "%d-%b-%Y %H:%M"])

    published_iso = published_dt.isoformat() if published_dt else None

    promoter_name = None
    if "NAME OF THE PROMOTER(S) / PACS WHOSE SHARES HAVE BEEN ENCUMBERED :" in description:
        promoter_name = description.split(":", 1)[1].strip()
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (guid, title, link, promoter_name, published_iso, company_symbol, summary)


def parse_secretarial_compliance_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'secretarial_compliance' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping Secretarial Compliance entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M"])
    if not published_dt:
        logger.warning(f"Skipping Secretarial Compliance entry with no valid published date: '{title}'")
        return None

    # Parse link for PDF and XML parts
    link_parts = guid.split()
    pdf_link = link_parts[0] if link_parts else None
    xml_link = link_parts[1] if len(link_parts) > 1 else None

    # Parse description for financial year and submission type
    financial_year = None
    submission_type = None
    description = entry.get("description", "")
    desc_parts = [part.strip() for part in description.split(',')]
    for part in desc_parts:
        if "FINANCIAL YEAR :" in part:
            financial_year = part.split(":", 1)[1].strip()
        elif "SUBMISSION TYPE:" in part:
            submission_type = part.split(":", 1)[1].strip()
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (
        guid, title, pdf_link, xml_link, financial_year,
        submission_type, published_dt.isoformat(), company_symbol, summary
    )


def parse_share_transfer_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'share_transfers' table.
    Handles entries with potentially empty link tags.
    """
    title = entry.get("title")
    description = entry.get("description")
    if not title or not description:
        logger.warning(f"Skipping Share Transfer entry with no title or description: '{title}'")
        return None

    # Create a stable GUID from content as link is empty
    guid = hashlib.sha256(f"{title}{description}".encode()).hexdigest()

    # Handle potentially empty link
    link = entry.get("link")

    # Parse published date
    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M"])
    if not published_dt:
        logger.warning(f"Skipping Share Transfer entry with no valid published date: '{title}'")
        return None

    # Parse period end date from description
    period_end_dt = None
    if "PERIOD ENDED :" in description:
        date_str = description.split(":", 1)[1].strip()
        period_end_dt = _parse_datetime(date_str, ["%d-%b-%Y"])

    if not period_end_dt:
        logger.warning(f"Skipping Share Transfer entry with no valid period end date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (
        guid, title, link, period_end_dt.date().isoformat(), published_dt.isoformat(), company_symbol, summary
    )


def parse_shareholding_pattern_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'shareholding_pattern' table.
    """
    guid = entry.get("link")
    title = entry.get("title")
    description = entry.get("description")

    if not guid or not title or not description:
        logger.warning(f"Skipping Shareholding Pattern entry with missing link, title, or description: '{title}'")
        return None

    # Parse description fields into a dictionary
    desc_dict = {}
    for item in description.split('|'):
        parts = item.split(':', 1)
        if len(parts) == 2:
            key = parts[0].strip().upper().replace(' ', '_')
            value = parts[1].strip()
            if value and value != '-':
                desc_dict[key] = value

    # Parse dates
    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping Shareholding Pattern entry with no valid published date: '{title}'")
        return None

    as_on_dt = _parse_datetime(desc_dict.get("AS_ON_DATE"), ["%d-%b-%Y"])
    if not as_on_dt:
        logger.warning(f"Skipping Shareholding Pattern entry with no valid 'as on' date: '{title}'")
        return None

    submission_dt = _parse_datetime(desc_dict.get("SUBMISSION_DT"), ["%d-%b-%Y"])
    if not submission_dt:
        logger.warning(f"Skipping Shareholding Pattern entry with no valid submission date: '{title}'")
        return None

    revision_dt = _parse_datetime(desc_dict.get("REVISION_DT"), ["%d-%b-%Y"])

    # Helper to safely convert string to float
    def to_float(val: Optional[str]) -> Optional[float]:
        if val is None: return None
        try: return float(val)
        except (ValueError, TypeError): return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (
        guid, title, guid, as_on_dt.date().isoformat(),
        to_float(desc_dict.get("PR_AND_PRGRP")), to_float(desc_dict.get("PUBLIC_VAL")),
        to_float(desc_dict.get("EMPTR")), desc_dict.get("NDS_REVISED_STATUS"),
        submission_dt.date().isoformat(), revision_dt.date().isoformat() if revision_dt else None,
        published_dt.isoformat(), company_symbol, summary
    )


def parse_statement_of_deviation_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'statement_of_deviation' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping statement of deviation entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping statement of deviation entry with no valid published date: '{title}'")
        return None

    period_end_dt = None
    description = entry.get("description", "")
    if "PERIOD END DATE :" in description:
        date_str = description.split(":", 1)[1].strip()
        period_end_dt = _parse_datetime(date_str, ["%d-%b-%Y"])

    if not period_end_dt:
        logger.warning(f"Skipping statement of deviation entry with no valid period end date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (guid, title, guid, period_end_dt.date().isoformat(), published_dt.isoformat(), company_symbol, summary)


def parse_unit_holding_pattern_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'unit_holding_pattern' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping unit holding pattern entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping unit holding pattern entry with no valid published date: '{title}'")
        return None

    as_on_dt = None
    description = entry.get("description", "")
    if "AS ON DATE :" in description:
        date_str = description.split(":", 1)[1].strip()
        as_on_dt = _parse_datetime(date_str, ["%d-%b-%Y"])

    if not as_on_dt:
        logger.warning(f"Skipping unit holding pattern entry with no valid as on date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (guid, title, guid, as_on_dt.date().isoformat(), published_dt.isoformat(), company_symbol, summary)


def parse_voting_results_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'voting_results' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping voting results entry with no link or title: '{title}'")
        return None

    published_dt = _parse_datetime(entry.get("published"), ["%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping voting results entry with no valid published date: '{title}'")
        return None

    meeting_dt = None
    description = entry.get("description", "")
    if "MEETING DATE :" in description:
        date_str = description.split(":", 1)[1].strip()
        meeting_dt = _parse_datetime(date_str, ["%d-%b-%Y"])

    if not meeting_dt:
        logger.warning(f"Skipping voting results entry with no valid meeting date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    return (guid, title, guid, meeting_dt.date().isoformat(), published_dt.isoformat(), company_symbol, summary)


def parse_circular_entry(entry: FeedEntry) -> Optional[Tuple]:
    """
    Parses a single feed entry for the 'circulars' table.
    Returns a tuple of values for insertion or None if parsing fails.
    """
    guid = entry.get("link")
    title = entry.get("title")
    if not guid or not title:
        logger.warning(f"Skipping circular entry with no link or title: '{title}'")
        return None

    # The pubDate format for Circulars is "Thu, 26 Jun 2025 00:00:00 +0530"
    published_dt = _parse_datetime(entry.get("published"), ["%a, %d %b %Y %H:%M:%S %z", "%d-%b-%Y %H:%M:%S"])
    if not published_dt:
        logger.warning(f"Skipping circular entry with no valid published date: '{title}'")
        return None
    company_symbol = get_symbol_from_name(title)
    summary = ""
    # The description field is empty for circulars, so we don't parse it.
    # The link is the GUID and also the actual link.
    return (guid, title, guid, published_dt.isoformat(), company_symbol, summary)