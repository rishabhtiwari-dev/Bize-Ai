import pytest
from pathlib import Path
from app.parser import load_all_documents
from app.chunker import chunk_document
from app.retriever import DocumentRetriever
from app.rag_engine import RAGEngine
from app import config

@pytest.fixture(scope="module")
def rag_system():
    docs = load_all_documents(config.DOCS_DIR)
    chunks = []
    for d in docs:
        chunks.extend(chunk_document(d))
    retriever = DocumentRetriever(chunks)
    rag = RAGEngine(retriever)
    return {"docs": docs, "chunks": chunks, "retriever": retriever, "rag": rag}

def test_document_ingestion_and_supersession(rag_system):
    docs = rag_system["docs"]
    assert len(docs) >= 4, "Should have loaded at least 4 SOP documents"
    
    doc_numbers = {d.doc_number: d for d in docs}
    assert "MNT-MAN-CNC-02" in doc_numbers
    assert "QC-SOP-014" in doc_numbers
    assert "SAF-SOP-003" in doc_numbers

    # Test supersession detection
    rev3 = next(d for d in docs if d.doc_number == "QC-SOP-014" and d.revision == "03")
    rev4 = next(d for d in docs if d.doc_number == "QC-SOP-014" and d.revision == "04")
    
    assert rev3.is_superseded is True
    assert "Rev 04" in rev3.superseded_by
    assert rev4.is_superseded is False

def test_sample_question_1_coolant(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("What is the recommended coolant concentration for the TX-200 CNC turning centre?")
    assert resp.is_found is True
    assert "6 - 8" in resp.answer
    assert "MNT-MAN-CNC-02" in resp.sources[0].doc_number
    assert resp.sources[0].page == 1

def test_sample_question_2_alarm_al104(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("The machine is showing alarm AL-104. What does it mean and what should the operator do?")
    assert resp.is_found is True
    assert "Way lube oil level low" in resp.answer or "lube" in resp.answer.lower()
    assert "ISO VG 68" in resp.answer
    assert "RESET" in resp.answer
    assert "MNT-MAN-CNC-02" in resp.sources[0].doc_number
    assert resp.sources[0].page == 2

def test_sample_question_3_loto_removal(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("Who is allowed to remove a lockout lock from a machine?")
    assert resp.is_found is True
    assert "own personal lock" in resp.answer.lower() or "own lock" in resp.answer.lower()
    assert "Safety Officer" in resp.answer
    assert "Production Manager" in resp.answer
    assert "SAF-SOP-003" in resp.sources[0].doc_number

def test_sample_question_4_bh220_tolerance(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("What is the outer diameter tolerance for the BH-220 bearing housing?")
    assert resp.is_found is True
    assert "90.000" in resp.answer
    assert "+/- 0.050" in resp.answer or "0.050" in resp.answer
    assert "QC-SOP-014" in resp.sources[0].doc_number
    assert resp.sources[0].revision == "04"

def test_sample_question_5_spindle_runout(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("How often should spindle runout be checked, and who does it?")
    assert resp.is_found is True
    assert "Monthly" in resp.answer or "monthly" in resp.answer.lower()
    assert "Maintenance technician" in resp.answer
    assert "MNT-MAN-CNC-02" in resp.sources[0].doc_number

def test_custom_question_1_missing_mtc(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("What should the inspector do if the supplier's Material Test Certificate (MTC) is missing?")
    assert resp.is_found is True
    assert "HOLD" in resp.answer
    assert "mandatory" in resp.answer.lower()
    assert "QC-SOP-014" in resp.sources[0].doc_number
    assert resp.sources[0].revision == "04"

def test_custom_question_2_chuck_bolt_torque(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("What is the torque for TX-200 chuck mounting bolts after maintenance?")
    assert resp.is_found is True
    assert "110 Nm" in resp.answer
    assert "criss-cross" in resp.answer.lower()
    assert "MNT-MAN-CNC-02" in resp.sources[0].doc_number

def test_custom_question_3_sampling_plan(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("For a lot of 250 pieces, what is the sampling plan and defect acceptance rule?")
    assert resp.is_found is True
    assert "13" in resp.answer
    assert "QC-SOP-014" in resp.sources[0].doc_number
    assert resp.sources[0].revision == "04"

def test_custom_question_4_zero_energy(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("How do you verify zero energy under LOTO procedure?")
    assert resp.is_found is True
    assert "zero" in resp.answer.lower()
    assert "gauge" in resp.answer.lower()
    assert "SAF-SOP-003" in resp.sources[0].doc_number

def test_custom_question_5_unanswerable(rag_system):
    rag = rag_system["rag"]
    resp = rag.answer_query("What is the maximum feed rate and spindle speed for cutting titanium alloy on CNC-04?")
    assert resp.is_found is False
    assert "not found" in resp.answer.lower() or "cannot find" in resp.answer.lower()
    assert len(resp.sources) == 0 or not resp.is_found

def test_superseded_warning_when_querying_old_standard(rag_system):
    rag = rag_system["rag"]
    # Explicitly ask about Rev 03 sampling
    resp = rag.answer_query("What was the sample size under QC-SOP-014 Rev 03?", prefer_latest=False)
    assert resp.is_found is True
    # Should detect superseded warning
    assert resp.superseded_warning is not None
    assert "SUPERSEDED" in resp.superseded_warning

