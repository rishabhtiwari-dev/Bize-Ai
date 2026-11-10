import re
from typing import List, Set
from app.models import DocumentChunk
from app.parser import PDFDocument

STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

def clean_tokens(tokens: List[str]) -> List[str]:
    """Filter out English stop words while preserving domain technical tokens."""
    res = []
    for t in tokens:
        if t not in STOP_WORDS and len(t) > 1:
            res.append(t)
    return res

def tokenize(text: str, filter_stops: bool = True) -> List[str]:
    """Tokenize query and content preserving hyphenated codes like AL-104, QC-SOP-014, TX-200."""
    tokens = re.findall(r"[A-Za-z0-9]+(?:[-_/.][A-Za-z0-9]+)*", text.lower())
    expanded_tokens = list(tokens)
    for t in tokens:
        if "-" in t:
            for sub in t.split("-"):
                if len(sub) > 1:
                    expanded_tokens.append(sub)
    if filter_stops:
        return clean_tokens(expanded_tokens)
    return expanded_tokens

def chunk_document(doc: PDFDocument) -> List[DocumentChunk]:
    """Break a PDFDocument into high-granularity, section-aware chunks."""
    chunks: List[DocumentChunk] = []
    chunk_index = 1

    for page_info in doc.pages:
        page_num = page_info["page_num"]
        page_text = page_info["text"]
        
        # Split text into sections using section numbering pattern (e.g., '1. Purpose', '4. Preventive Maintenance')
        sections = re.split(r"\n(?=[0-9]+\.\s+[A-Za-z])", page_text)
        
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue

            first_line = sec.split("\n")[0].strip()
            sec_name_match = re.match(r"^([0-9]+\.\s+[A-Za-z0-9\s/_\-]+)", first_line)
            section_title = sec_name_match.group(1).strip() if sec_name_match else None

            # Handle Alarms section specially
            if "Common Alarms" in sec or "Alarm Meaning Operator action" in sec:
                alarm_entries = re.split(r"\n(?=AL-[0-9]{3})", sec)
                for entry in alarm_entries:
                    entry = entry.strip()
                    if not entry:
                        continue
                    chunk_text = f"Document: {doc.doc_number} (Rev {doc.revision})\nTitle: {doc.title}\nSection: {section_title or 'Common Alarms'}\nPage: {page_num}\n\n{entry}"
                    chunk = DocumentChunk(
                        chunk_id=f"{doc.doc_number}_R{doc.revision}_P{page_num}_C{chunk_index}",
                        doc_id=doc.filename,
                        doc_title=doc.title,
                        doc_number=doc.doc_number,
                        revision=doc.revision,
                        effective_date=doc.effective_date,
                        page=page_num,
                        section=section_title or "Common Alarms",
                        content=chunk_text,
                        tokens=tokenize(chunk_text),
                        is_superseded=doc.is_superseded,
                        superseded_by=doc.superseded_by or None
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                continue

            # Standard section chunking
            full_chunk_text = f"Document: {doc.doc_number} (Rev {doc.revision})\nTitle: {doc.title}\nSection: {section_title or 'General'}\nPage: {page_num}\n\n{sec}"
            chunks.append(DocumentChunk(
                chunk_id=f"{doc.doc_number}_R{doc.revision}_P{page_num}_C{chunk_index}",
                doc_id=doc.filename,
                doc_title=doc.title,
                doc_number=doc.doc_number,
                revision=doc.revision,
                effective_date=doc.effective_date,
                page=page_num,
                section=section_title or "General",
                content=full_chunk_text,
                tokens=tokenize(full_chunk_text),
                is_superseded=doc.is_superseded,
                superseded_by=doc.superseded_by or None
            ))
            chunk_index += 1

    return chunks
