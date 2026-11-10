import re
from pathlib import Path
from typing import List, Dict, Any
import pypdf

class PDFDocument:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.filename = file_path.name
        self.pages: List[Dict[str, Any]] = []
        self.doc_number: str = ""
        self.revision: str = ""
        self.effective_date: str = ""
        self.title: str = ""
        self.prepared_by: str = ""
        self.approved_by: str = ""
        self.is_superseded: bool = False
        self.superseded_by: str = ""
        self._parse()

    def _parse(self):
        reader = pypdf.PdfReader(str(self.file_path))
        full_first_page = ""
        
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if idx == 0:
                full_first_page = page_text
            self.pages.append({
                "page_num": idx + 1,
                "text": page_text
            })

        # Heuristic / regex extraction for QMS header fields
        doc_no_match = re.search(r"Document\s+No\.?\s*[:\n]?\s*([A-Z0-9\-_]+)", full_first_page, re.IGNORECASE)
        if not doc_no_match:
            doc_no_match = re.search(r"\b([A-Z]{2,4}-[A-Z0-9]+-[A-Z0-9\-]+)\b", full_first_page)
        if doc_no_match:
            self.doc_number = doc_no_match.group(1).strip()
        else:
            self.doc_number = self.filename.split("_")[0]

        rev_match = re.search(r"Revision\s*[:\n]?\s*([0-9A-Za-z]+)", full_first_page, re.IGNORECASE)
        if not rev_match:
            rev_match = re.search(r"Rev\s+([0-9]{2})", full_first_page, re.IGNORECASE)
        if rev_match:
            self.revision = rev_match.group(1).strip()

        date_match = re.search(r"Effective\s+Date\s*[:\n]?\s*([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})", full_first_page, re.IGNORECASE)
        if date_match:
            self.effective_date = date_match.group(1).strip()

        prep_match = re.search(r"Prepared\s+By\s*[:\n]?\s*([A-Za-z0-9\s,\.]+?)(?=Approved\s+By|$)", full_first_page, re.IGNORECASE)
        if prep_match:
            self.prepared_by = prep_match.group(1).strip().replace("\n", " ")

        appr_match = re.search(r"Approved\s+By\s*[:\n]?\s*([A-Za-z0-9\s,\.]+?)(?=\n[0-9]|\nPurpose|$)", full_first_page, re.IGNORECASE)
        if appr_match:
            self.approved_by = appr_match.group(1).strip().replace("\n", " ")

        # Title extraction
        lines = [line.strip() for line in full_first_page.split("\n") if line.strip()]
        for line in lines:
            if any(term in line for term in ["Manual", "Standard Operating Procedure", "Safety Procedure", "Procedure"]):
                self.title = line
                break
        if not self.title and len(lines) > 2:
            self.title = lines[2]


def load_all_documents(docs_dir: Path) -> List[PDFDocument]:
    """Load and parse all PDF documents in the docs directory, establishing supersession relations."""
    pdf_files = list(docs_dir.glob("*.pdf"))
    documents: List[PDFDocument] = []
    
    # Exclude non-SOP files like Sample_Questions.pdf from indexing
    for pdf_path in pdf_files:
        if "sample_question" in pdf_path.name.lower():
            continue
        doc = PDFDocument(pdf_path)
        documents.append(doc)

    # Detect supersession among documents with the same Document No
    docs_by_number: Dict[str, List[PDFDocument]] = {}
    for doc in documents:
        docs_by_number.setdefault(doc.doc_number, []).append(doc)

    for doc_no, doc_list in docs_by_number.items():
        if len(doc_list) > 1:
            # Sort by revision or effective date
            # Revisions are numbers like '03', '04'
            try:
                sorted_docs = sorted(doc_list, key=lambda d: int(d.revision))
            except ValueError:
                sorted_docs = sorted(doc_list, key=lambda d: d.revision)
            
            latest_doc = sorted_docs[-1]
            for older_doc in sorted_docs[:-1]:
                older_doc.is_superseded = True
                older_doc.superseded_by = f"{latest_doc.doc_number} Rev {latest_doc.revision}"

    return documents
