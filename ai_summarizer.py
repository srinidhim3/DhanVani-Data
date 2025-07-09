import os
import logging
from typing import List, Optional

import requests
from openai import OpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF
from lxml import etree

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AISummarizer:
    """
    An AI-based summarizer that fetches content from a URL, extracts text,
    and uses the DeepSeek API to generate a summary.

    It handles large documents by splitting them into chunks, summarizing each
    chunk, and then summarizing the collective summaries (map-reduce approach).
    """

    # DeepSeek has a large context window, so we can use a much larger chunk size.
    # This reduces the number of API calls for large documents.
    MAX_CHUNK_SIZE = 100000

    def __init__(self):
        """
        Initializes the summarizer by setting up the DeepSeek API client.
        """
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.critical(
                "DEEPSEEK_API_KEY not found in .env file or environment variables."
            )
            raise ValueError("DEEPSEEK_API_KEY is not set.")

        try:
            logger.info("Initializing DeepSeek API client...")
            self.client = OpenAI(
                api_key=api_key, base_url="https://api.deepseek.com/v1"
            )
            logger.info("AISummarizer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize AISummarizer: {e}")
            raise

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extracts text from PDF content using PyMuPDF for better accuracy."""
        logger.info("Attempting to extract text from PDF using PyMuPDF (fitz)...")
        text = ""
        try:
            # PyMuPDF (fitz) is generally more robust for text extraction
            # and less prone to character encoding issues like '(cid:x)'.
            with fitz.open(stream=pdf_content, filetype="pdf") as doc:
                logger.info(f"PDF has {len(doc)} pages. Extracting text...")
                for i, page in enumerate(doc):
                    text += page.get_text()
                logger.info(f"PyMuPDF extracted {len(text)} characters from the PDF.")
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF using PyMuPDF: {e}")
            return ""

    def _extract_text_from_xml(self, xml_content: bytes) -> str:
        """Extracts text from XML content, focusing on human-readable text."""
        try:
            # Use a robust parser that can handle potentially broken XML
            parser = etree.XMLParser(recover=True, encoding="utf-8")
            root = etree.fromstring(xml_content, parser=parser)
            # Join all text nodes, separated by a space
            text_nodes = root.xpath("//text()")
            return " ".join(text.strip() for text in text_nodes if text.strip())
        except Exception as e:
            logger.error(f"Failed to extract text from XML: {e}")
            return ""

    def _get_text_from_url(self, url: str) -> Optional[str]:
        """Fetches content from a URL, determines file type, and extracts text."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            # Use a single request to get headers and content
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            content = response.content
            content_type = response.headers.get("content-type", "").lower()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching or reading URL {url}: {e}")
            return None

        # Determine file type by extension first, then by content-type
        url_lower = url.lower()
        if ".pdf" in url_lower or "application/pdf" in content_type:
            return self._extract_text_from_pdf(content)
        if (
            ".xml" in url_lower
            or "application/xml" in content_type
            or "text/xml" in content_type
        ):
            return self._extract_text_from_xml(content)

        logger.warning(
            f"Could not determine file type for URL: {url} (Content-Type: '{content_type}'). No text extracted."
        )
        return None

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Splits text into chunks of a maximum size."""
        if len(text) <= self.MAX_CHUNK_SIZE:
            return [text]

        chunks = [
            text[i : i + self.MAX_CHUNK_SIZE]
            for i in range(0, len(text), self.MAX_CHUNK_SIZE)
        ]
        logger.info(f"Split text into {len(chunks)} chunks.")
        return chunks

    def _summarize_text(self, text: str) -> Optional[str]:
        """Sends text to the DeepSeek API for summarization."""
        if not text:
            return None
        try:
            logger.info(
                f"Sending {len(text)} characters to DeepSeek API for summarization."
            )
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a highly experienced financial analyst. Your task is to generate a concise, professional summary of the following financial document. "
                            "Focus on extracting and clearly presenting the most important information relevant to investors, including: "
                            "financial results (revenues, profits, losses), corporate actions (dividends, mergers, buybacks), meeting outcomes (AGM/EGM resolutions), "
                            "and regulatory or compliance-related updates. "
                            "If no material information is found, state 'No significant investor-relevant information found.' "
                            "The summary should be objective, written in plain English, and formatted as short bullet points or a clear paragraph."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=4096,  # Adjust as needed
                temperature=0.2,  # Lower temperature for more factual summaries
            )
            summary = response.choices[0].message.content
            logger.info("Successfully received summary from DeepSeek API.")
            return summary.strip() if summary else None
        except Exception as e:
            logger.error(f"DeepSeek API summarization failed: {e}")
            return None

    def summarize(self, url: str) -> Optional[str]:
        """
        Public method to summarize content from a URL.
        Orchestrates fetching, parsing, chunking, and summarizing.
        """
        logger.info(f"Starting summarization for URL: {url}")
        full_text = self._get_text_from_url(url)

        if not full_text:
            logger.error(
                f"Could not retrieve or parse text from {url}. Aborting summarization."
            )
            return None

        chunks = self._split_text_into_chunks(full_text)

        if len(chunks) == 1:
            logger.info("Document is small. Generating direct summary.")
            return self._summarize_text(chunks[0])

        logger.info(
            f"Document is large. Summarizing {len(chunks)} chunks individually."
        )
        chunk_summaries = [self._summarize_text(chunk) for chunk in chunks]

        valid_summaries = [s for s in chunk_summaries if s]
        if not valid_summaries:
            logger.error("Failed to get summaries for any of the chunks.")
            return None

        logger.info("Combining and creating a final summary from chunk summaries.")
        combined_summaries = "\n\n".join(valid_summaries)
        return self._summarize_text(combined_summaries)
