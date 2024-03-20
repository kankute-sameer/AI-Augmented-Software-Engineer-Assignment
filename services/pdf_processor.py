from langchain_community.document_loaders import PyPDFLoader

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    return pages
