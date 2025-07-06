import os
import logging
import io
from typing import List, Optional
import functools

import google.generativeai as genai
from dotenv import load_dotenv
import requests
import fitz  # PyMuPDF
from lxml import etree

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AISummarizer:
    """
    An AI-based summarizer that fetches content from a URL (PDF or XML),
    extracts text, and uses the Gemini API to generate a summary.

    It handles large documents by splitting them into chunks, summarizing each
    chunk, and then summarizing the collective summaries (map-reduce approach).
    """
    # Using a model with a larger context window is beneficial for summarization.
    # gemini-1.5-flash is a good balance of speed, cost, and context size.
    MODEL_NAME = "gemini-1.5-flash"
    # A safe character limit per chunk to stay well within API token limits.
    # This can be adjusted based on the model's specific token limits.
    # Average token-to-char ratio is ~1:4. 10000 chars is ~2500 tokens.
    MAX_CHUNK_SIZE = 10000

    def __init__(self):
        """
        Initializes the summarizer and configures the Gemini API.
        """
        try:
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.MODEL_NAME)
            self.generation_config = {
                "temperature": 0.2,
            }
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
            parser = etree.XMLParser(recover=True, encoding='utf-8')
            root = etree.fromstring(xml_content, parser=parser)
            # Join all text nodes, separated by a space
            text_nodes = root.xpath('//text()')
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
            content_type = response.headers.get('content-type', '').lower()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching or reading URL {url}: {e}")
            return None

        # Determine file type by extension first, then by content-type
        url_lower = url.lower()
        if ".pdf" in url_lower or "application/pdf" in content_type:
            return self._extract_text_from_pdf(content)
        if ".xml" in url_lower or "application/xml" in content_type or "text/xml" in content_type:
            return self._extract_text_from_xml(content)

        logger.warning(f"Could not determine file type for URL: {url} (Content-Type: '{content_type}'). No text extracted.")
        return None

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Splits text into chunks of a maximum size."""
        if len(text) <= self.MAX_CHUNK_SIZE:
            return [text]
        
        chunks = [text[i:i + self.MAX_CHUNK_SIZE] for i in range(0, len(text), self.MAX_CHUNK_SIZE)]
        logger.info(f"Split text into {len(chunks)} chunks.")
        return chunks

    def _summarize_text(self, text: str, prompt: str) -> Optional[str]:
        """Sends text to Gemini API for summarization."""
        if not text:
            return None
        try:
            full_prompt = f"{prompt}\n\n---\n\n{text}"
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return None

    @functools.lru_cache(maxsize=512)
    def summarize(self, url: str) -> Optional[str]:
        """
        Public method to summarize content from a URL.
        Orchestrates fetching, parsing, chunking, and summarizing.
        This method is cached to avoid re-processing the same URL.
        """
        logger.info(f"Starting summarization for URL: {url}")
        full_text = self._get_text_from_url(url)

        if not full_text:
            logger.error(f"Could not retrieve or parse text from {url}. Aborting summarization.")
            return None

        chunks = self._split_text_into_chunks(full_text)
        
        if len(chunks) == 1:
            logger.info("Document is small. Generating a direct summary.")
            prompt = "Strictly using only the information from the text below, provide a very short, concise summary in a single paragraph. Do not add any information that is not present in the text."
            return self._summarize_text(chunks[0], prompt)
        
        logger.info(f"Document is large. Summarizing {len(chunks)} chunks individually.")
        chunk_summaries = [self._summarize_text(chunk, "Strictly using only the information from the text chunk below, summarize its key points in 2-3 bullet points. Do not add external information.") for chunk in chunks]
        
        valid_summaries = [s for s in chunk_summaries if s]
        if not valid_summaries:
            logger.error("Failed to get summaries for any of the chunks.")
            return None

        logger.info("Combining and creating a final summary from chunk summaries.")
        combined_summaries = "\n\n".join(valid_summaries)
        final_prompt = "The following are summaries from different parts of a large document. Synthesize them into a single, cohesive, and very short final summary of the entire document. Ensure the final summary is based *only* on the information provided in the text chunks below and does not introduce any external information."
        return self._summarize_text(combined_summaries, final_prompt)