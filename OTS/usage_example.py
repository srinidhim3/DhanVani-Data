from ai_summarizer import AISummarizer

def main():
    """
    Example of how to use the AISummarizer class.
    """
    # Example PDF URL from a corporate announcement.
    # Replace with any public PDF or XML URL you want to test.
    pdf_url = "https://nsearchives.nseindia.com/corporate/xbrl/NOTICE_OF_SHAREHOLDERS_MEETINGS_1477439_04072025060838_WEB.xml"
    
    # Example of a large PDF that will trigger chunking
    # large_pdf_url = "https://arxiv.org/pdf/1706.03762" # "Attention Is All You Need" paper

    try:
        summarizer = AISummarizer()
        
        print(f"Summarizing URL: {pdf_url}")
        summary = summarizer.summarize(pdf_url)

        if summary:
            print("\n--- AI-Generated Summary ---")
            print(summary)
            print("----------------------------")
        else:
            print("\nCould not generate a summary for the given URL.")

    except Exception as e:
        print(f"An error occurred during the process: {e}")

if __name__ == "__main__":
    main()