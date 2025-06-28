from pathlib import Path
import os

import parsers

# --- General Configuration ---
# It's recommended to use environment variables for sensitive data like connection strings.
# Set the DB_CONNECTION_STRING environment variable in your deployment environment.
DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
REQUEST_TIMEOUT = 15

# --- Database Table Names ---
TABLE_NSE_ANNOUNCEMENTS = "nse_announcements"
TABLE_NSE_ANNUAL_REPORTS = "nse_annual_reports"
TABLE_NSE_BOARD_MEETINGS = "nse_board_meetings"
TABLE_NSE_BRSR = "nse_brsr"
TABLE_NSE_CORPORATE_ACTIONS = "nse_corporate_actions"
TABLE_NSE_INSIDER_TRADING = "nse_insider_trading"
TABLE_NSE_INVESTOR_COMPLAINTS = "nse_investor_complaints"
TABLE_NSE_RELATED_PARTY_TRANSACTIONS = "nse_related_party_transactions"
TABLE_NSE_REGULATION29 = "nse_regulation29"
TABLE_NSE_REASON_FOR_ENCUMBRANCE = "nse_reason_for_encumbrance"
TABLE_NSE_REGULATION31 = "nse_regulation31"
TABLE_NSE_SECRETARIAL_COMPLIANCE = "nse_secretarial_compliance"
TABLE_NSE_SHARE_TRANSFERS = "nse_share_transfers"
TABLE_NSE_SHAREHOLDING_PATTERN = "nse_shareholding_pattern"
TABLE_NSE_STATEMENT_OF_DEVIATION = "nse_statement_of_deviation"
TABLE_NSE_UNIT_HOLDING_PATTERN = "nse_unit_holding_pattern"
TABLE_NSE_CIRCULARS = "nse_circulars"
TABLE_NSE_VOTING_RESULTS = "nse_voting_results"
TABLE_NSE_OFFER_DOCUMENTS = "nse_offer_documents"

# --- RSS Feed URLs ---
URL_ANNOUNCEMENTS = "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml"
URL_ANNUAL_REPORTS = "https://nsearchives.nseindia.com/content/RSS/Annual_Reports.xml"
URL_BOARD_MEETINGS = "https://nsearchives.nseindia.com/content/RSS/Board_Meetings.xml"
URL_BRSR = "https://nsearchives.nseindia.com/content/RSS/brsr.xml"
URL_CORPORATE_ACTIONS = "https://nsearchives.nseindia.com/content/RSS/Corporate_action.xml"
URL_INSIDER_TRADING = "https://nsearchives.nseindia.com/content/RSS/Insider_Trading.xml"
URL_INVESTOR_COMPLAINTS = "https://nsearchives.nseindia.com/content/RSS/Investor_Complaints.xml"
URL_REGULATION31 = "https://nsearchives.nseindia.com/content/RSS/Sast_Regulation31.xml"
URL_REASON_FOR_ENCUMBRANCE = "https://nsearchives.nseindia.com/content/RSS/Sast_ReasonForEncumbrance.xml"
URL_REGULATION29 = "https://nsearchives.nseindia.com/content/RSS/Sast_Regulation29.xml"
URL_SECRETARIAL_COMPLIANCE = "https://nsearchives.nseindia.com/content/RSS/Secretarial_Compliance.xml"
URL_RELATED_PARTY_TRANSACTIONS = "https://nsearchives.nseindia.com/content/RSS/Related_Party_Trans.xml"
URL_SHARE_TRANSFERS = "https://nsearchives.nseindia.com/content/RSS/Share_Transfers.xml"
URL_SHAREHOLDING_PATTERN = "https://nsearchives.nseindia.com/content/RSS/Shareholding_Pattern.xml"
URL_STATEMENT_OF_DEVIATION = "https://nsearchives.nseindia.com/content/RSS/Statement_Of_Deviation.xml"
URL_VOTING_RESULTS = "https://nsearchives.nseindia.com/content/RSS/Voting_Results.xml"
URL_CIRCULARS = "https://nsearchives.nseindia.com/content/RSS/Circulars.xml"
URL_UNIT_HOLDING_PATTERN = "https://nsearchives.nseindia.com/content/RSS/Unitholding_Patterns.xml"
URL_OFFER_DOCUMENTS = "https://nsearchives.nseindia.com/content/RSS/Offer_Documents.xml"

# --- Feed Processing Configuration ---
FEEDS_TO_PROCESS = [
    {
        "name": "Announcements",
        "url": URL_ANNOUNCEMENTS,
        "parser": parsers.parse_announcement_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_ANNOUNCEMENTS}
                   (guid, title, link, description, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Annual Reports",
        "url": URL_ANNUAL_REPORTS,
        "parser": parsers.parse_annual_report_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_ANNUAL_REPORTS}
                   (guid, title, link, report_date)
                   VALUES (%s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Board Meetings",
        "url": URL_BOARD_MEETINGS,
        "parser": parsers.parse_board_meeting_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_BOARD_MEETINGS}
                   (guid, title, link, meeting_date, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Business Responsibility and Sustainability Report",
        "url": URL_BRSR,
        "parser": parsers.parse_brsr_report_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_BRSR}
                   (guid, title, pdf_link, xml_link_name, submission_date)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Corporate Actions",
        "url": URL_CORPORATE_ACTIONS,
        "parser": parsers.parse_corporate_action_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_CORPORATE_ACTIONS}
                   (guid, title, link, description, published_at, ex_date,
                    series, purpose, face_value, record_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Insider Trading",
        "url": URL_INSIDER_TRADING,
        "parser": parsers.parse_insider_trading_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_INSIDER_TRADING}
                   (guid, title, link, security_type, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Investor Complaints",
        "url": URL_INVESTOR_COMPLAINTS,
        "parser": parsers.parse_investor_complaint_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_INVESTOR_COMPLAINTS}
                   (guid, title, link, quarter_ending_date, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Offer Documents",
        "url": URL_OFFER_DOCUMENTS,
        "parser": parsers.parse_offer_document_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_OFFER_DOCUMENTS}
                   (guid, title, link, description, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Related Party Transactions",
        "url": URL_RELATED_PARTY_TRANSACTIONS,
        "parser": parsers.parse_related_party_transaction_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_RELATED_PARTY_TRANSACTIONS}
                   (guid, title, link, period_end_date, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "SAST Regulation 29",
        "url": URL_REGULATION29,
        "parser": parsers.parse_regulation29_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_REGULATION29}
                   (guid, title, link, acquirer_name, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "SAST Regulation 31",
        "url": URL_REGULATION31,
        "parser": parsers.parse_regulation31_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_REGULATION31}
                   (guid, title, link, promoter_or_pacs_name, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Reason for Encumbrance",
        "url": URL_REASON_FOR_ENCUMBRANCE,
        "parser": parsers.parse_reason_for_encumbrance_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_REASON_FOR_ENCUMBRANCE}
                   (guid, title, link, promoter_name, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Secretarial Compliance",
        "url": URL_SECRETARIAL_COMPLIANCE,
        "parser": parsers.parse_secretarial_compliance_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_SECRETARIAL_COMPLIANCE}
                   (guid, title, pdf_link, xml_link, financial_year, submission_type, published_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Share Transfers",
        "url": URL_SHARE_TRANSFERS,
        "parser": parsers.parse_share_transfer_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_SHARE_TRANSFERS}
                   (guid, title, link, period_end_date, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Shareholding Pattern",
        "url": URL_SHAREHOLDING_PATTERN,
        "parser": parsers.parse_shareholding_pattern_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_SHAREHOLDING_PATTERN}
                   (guid, title, link, as_on_date, promoter_holding, public_holding,
                    employee_trust_holding, revised_status, submission_date, revision_date, published_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Statement of Deviation",
        "url": URL_STATEMENT_OF_DEVIATION,
        "parser": parsers.parse_statement_of_deviation_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_STATEMENT_OF_DEVIATION}
                   (guid, title, link, period_end_date, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Unit Holding Pattern",
        "url": URL_UNIT_HOLDING_PATTERN,
        "parser": parsers.parse_unit_holding_pattern_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_UNIT_HOLDING_PATTERN}
                   (guid, title, link, as_on_date, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Voting Results",
        "url": URL_VOTING_RESULTS,
        "parser": parsers.parse_voting_results_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_VOTING_RESULTS}
                   (guid, title, link, meeting_date, published_at)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
    {
        "name": "Circulars",
        "url": URL_CIRCULARS,
        "parser": parsers.parse_circular_entry,
        "sql": f"""INSERT INTO {TABLE_NSE_CIRCULARS}
                   (guid, title, link, published_at)
                   VALUES (%s, %s, %s, %s) ON CONFLICT (guid) DO NOTHING"""
    },
]