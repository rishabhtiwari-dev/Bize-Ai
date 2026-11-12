# BiztelAI — Shop-Floor Supervisor Copilot

A simple, fast, and grounded assistant built for manufacturing shop-floor supervisors at **Kaveri Precision Components Pvt. Ltd. (Hosur Plant)**. 

Supervisors on a noisy shift don't have time to walk back to an office and dig through three-ring binders. This tool lets them pull out their phone or tablet, ask a question about an alarm, inspection rule, or safety lockout, and get a direct, verified answer in 2 seconds with the exact document, revision, and page number cited.

---

## What's in Here

- **FastAPI backend** with a clean, mobile-first web interface.
- **RAG pipeline over the 4 provided PDFs**:
  - `MNT-MAN-CNC-02 Rev 02` — TX-200 CNC Preventive Maintenance Manual
  - `QC-SOP-014 Rev 03` — Incoming Material Inspection (Superseded)
  - `QC-SOP-014 Rev 04` — Incoming Material Inspection (Current Active Standard)
  - `SAF-SOP-003 Rev 05` — Lockout / Tagout (LOTO) Safety Procedure
- **Zero hallucinations**: If an answer isn't in the plant documents, the app says so straight up.
- **Revision-Aware Guardrail (My added improvement)**: The plant has both Rev 03 and Rev 04 of the QC SOP in circulation. In manufacturing, following an obsolete SOP causes major audit non-conformances and scrap parts. The app automatically detects superseded documents, defaults to the active standard, and flags an alert if an older rule is queried.
- **Works 100% offline out-of-the-box**: Comes with a built-in deterministic extractor and BM25 ranker, so you don't even need an external API key to run and test it. If you want full LLM generation, drop in a Groq or OpenAI key in `.env`.
- **Phone access on the same Wi-Fi**: Binds to `0.0.0.0` and prints an ASCII QR code in the terminal so you can scan and open it immediately on your phone.

---

## Quick Setup (Run in 60 Seconds)

### 1. Install dependencies
Make sure you have Python 3.10+ installed.

```bash
pip install -r requirements.txt
```

### 2. (Optional) Add an API key
The app works out of the box without any keys using its built-in local extractor. If you'd like to use a cloud LLM, copy `.env.example` to `.env`:

```bash
# Optional: for Groq (very fast, free tier)
GROQ_API_KEY=gsk_...
LLM_MODEL=llama-3.3-70b-versatile

# Or for OpenAI / Ollama:
# OPENAI_API_KEY=sk-...
# OPENAI_BASE_URL=http://localhost:11434/v1
```

### 3. Start the server
```bash
python main.py
```
*(On Windows, you can also just double-click `run.bat`)*

When the server starts, you will see a banner like this in your console:
```text
============================================================
🏭 INITIALIZING BIZTELAI PLANT COPILOT...
============================================================
 Loaded 4 SOP documents:
   • MNT-MAN-CNC-02 Rev 02: Preventive Maintenance Manual - TX-200 CNC Turning Centre [ACTIVE]
   • QC-SOP-014 Rev 03: Incoming Material Inspection - Standard Operating Procedure (SUPERSEDED by QC-SOP-014 Rev 04)
   • QC-SOP-014 Rev 04: Incoming Material Inspection - Standard Operating Procedure [ACTIVE]
   • SAF-SOP-003 Rev 05: Lockout / Tagout (LOTO) - Safety Procedure [ACTIVE]
 Created 48 section-aware chunks.
 RAG Engine ready using provider: Local Extractor (bm25-smart-extractive)

🚀 COPILOT IS LIVE & READY FOR SHOP-FLOOR USE!
💻 Local Access:   http://localhost:8000
📱 Phone/Tablet:   http://192.168.1.10:8000
📸 QR Code URL:    http://localhost:8000/api/qr
============================================================
```

---

## Opening on Your Phone (Local Network)

1. Make sure your phone is connected to the **same Wi-Fi network** as your laptop.
2. Open your mobile browser (Safari, Chrome) and type the network URL shown in your terminal (for example `http://192.168.1.10:8000`).
3. Alternatively, click the **"Phone Access"** button in the web header on your laptop, and scan the QR code with your phone camera.
4. The interface is responsive and designed for mobile screens with high-contrast text and thumb-friendly buttons.

---

## Testing the App

### The 5 Sample Questions from the Assignment

Here is how the app answers each of the 5 questions provided in the assignment brief:

#### 1. What is the recommended coolant concentration for the TX-200 CNC turning centre?
- **Answer**: The recommended coolant concentration is **6 - 8 %**, checked with a refractometer reading multiplied by a 1.0 factor. It is checked daily at the start of shift and weekly by the operator.
- **Source Citation**: `MNT-MAN-CNC-02 Rev 02, Page 1, Section: 3. Normal Operating Parameters`
- **Result**: Verified in document.

#### 2. The machine is showing alarm AL-104. What does it mean and what should the operator do?
- **Answer**: 
  - **Meaning**: Way lube oil level low.
  - **Operator action**: Top up with **ISO VG 68 oil** to the **MAX mark** on the sight glass, then press **RESET**. The machine can continue its cycle after reset.
- **Source Citation**: `MNT-MAN-CNC-02 Rev 02, Page 2, Section: Common Alarms`
- **Result**: Verified in document.

#### 3. Who is allowed to remove a lockout lock from a machine?
- **Answer**: 
  - **Standard rule (Section 5)**: Each authorised person removes **only their own personal lock**. Nobody is allowed to remove another person's lock.
  - **When lock owner is absent (Section 6)**: The Shift Supervisor must first make every reasonable effort to contact the owner by phone. If unreachable, **both the Production Manager and the Safety Officer** must authorise removal after physically inspecting the machine. The removal is recorded on form **SF-12 Lock Removal Record**, and the owner is notified before their next shift.
- **Source Citation**: `SAF-SOP-003 Rev 05, Page 1-2, Sections 5 & 6`
- **Result**: Verified in document.

#### 4. What is the outer diameter tolerance for the BH-220 bearing housing?
- **Answer**: For the BH-220 bearing housing, the outer diameter is **90.000 mm** with a tolerance of **+/- 0.050 mm** (acceptable range: 89.950 to 90.050 mm). It is measured using a calibrated digital caliper and is classified as a **Major** characteristic.
- **Source Citation**: `QC-SOP-014 Rev 04, Page 2, Section: 6. Inspection Dimensions - BH-220 Bearing Housing`
- **Result**: Verified in document.

#### 5. How often should spindle runout be checked, and who does it?
- **Answer**: Spindle runout must be checked **Monthly** by a **Maintenance technician** (tolerance is **0.005 mm max.** at the chuck face using a dial indicator).
- **Source Citation**: `MNT-MAN-CNC-02 Rev 02, Page 1, Section 3 & Section 4`
- **Result**: Verified in document.

---

### My 5 Custom Questions (Including One the Documents Cannot Answer)

To thoroughly test the copilot across quality, maintenance, safety, and edge-cases, I wrote these 5 additional questions:

#### Custom Q1 (QC Revision Change / Mandatory Document Rule):
> *"What should the inspector do if the supplier's Material Test Certificate (MTC) is missing during incoming inspection?"*
- **App Answer**: Under **QC-SOP-014 Rev 04**, the supplier's Material Test Certificate (MTC) is **mandatory**. If it is missing, the lot is placed on **HOLD** and must not be inspected or accepted until the MTC is received. *(Note: in older superseded Rev 03, MTC was only 'if available', but Rev 04 made it mandatory).*
- **Source Citation**: `QC-SOP-014 Rev 04, Page 2, Section 5`
- **Result**: Verified in document.

#### Custom Q2 (Maintenance Torque Specification):
> *"What is the required torque and sequence for tightening the chuck mounting bolts after maintenance on the TX-200 CNC?"*
- **App Answer**: Tighten the chuck mounting bolts in a **criss-cross sequence to 110 Nm** using a calibrated torque wrench.
- **Source Citation**: `MNT-MAN-CNC-02 Rev 02, Page 1, Section 5`
- **Result**: Verified in document.

#### Custom Q3 (Lot-Size Sampling Plan Calculation):
> *"For a received lot of 250 pieces of steel bar stock, how many samples must be inspected, and what defect rule applies?"*
- **App Answer**: For a lot size between 91 and 500 pieces (which includes 250 pieces), inspect **13 samples** at random.  
  - Minor defects allowed: 0 (reject if 1 or more).  
  - Major defects: Complete lot is rejected (SQE may decide 100% sorting at supplier cost).  
  - Critical defects: Complete lot rejected and returned to supplier. No sorting allowed.
- **Source Citation**: `QC-SOP-014 Rev 04, Page 1, Section 4`
- **Result**: Verified in document.

#### Custom Q4 (Safety Zero-Energy Verification Protocol):
> *"How must an authorised person verify zero energy state before working on a machine under LOTO?"*
- **App Answer**: First release stored energy: bleed hydraulic pressure and accumulators until the gauge reads zero, vent compressed air to 0 bar, and block gravity-fall parts. Then verify zero energy by attempting to start the machine from the control panel to confirm it does not start, confirm all pressure gauges read zero, and return controls to OFF.
- **Source Citation**: `SAF-SOP-003 Rev 05, Page 1, Section 4`
- **Result**: Verified in document.

#### Custom Q5 (UNANSWERABLE — Tests Zero Hallucination):
> *"What is the maximum feed rate and spindle speed for cutting titanium alloy on CNC-04?"*
- **App Answer**:
  > **This information is not found in the available plant SOPs and manuals.**  
  > None of the indexed documents (`MNT-MAN-CNC-02`, `QC-SOP-014`, `SAF-SOP-003`) contain details answering this query. Please verify with your Shift Supervisor, Maintenance Engineer, or Quality Lead.
- **Source Citation**: None. The app returns `is_found: false` and displays a blue out-of-scope notice.
- **Result**: Successfully refused without hallucinating.

---

### Real-World Shop-Floor Scenarios (Messy Human Phrasing)

Real supervisors rarely speak like an audit checklist. They speak quickly in conversational shorthand. The copilot includes quick-action chips for real shift questions:

- *"AL-104 on CNC-06, what oil and how to reset?"*
- *"Refractometer check: what coolant % on TX-200?"*
- *"Technician went home with lock on. Can I cut it?"*
- *"Batch arrived without MTC cert. Can we inspect?"*
- *"BH-220 bearing housing: OD caliper tolerance?"*
- *"Got 250 pins: how many to sample, defect rule?"*
- *"Re-mounted chuck: what torque and sequence?"*
- *"Who inspects spindle runout and how often?"*
- *"Can we cut titanium at 2500 RPM on CNC-04?"* (Unanswerable)

All of these can be tested with 1 click in the web UI.

---

## How It's Built (Architecture & Code Structure)

```
BizeAi/
├── app/
│   ├── config.py             # LAN IP detection, port binding, environment config
│   ├── models.py             # Clean Pydantic schemas (QueryRequest, QueryResponse, Citations)
│   ├── parser.py             # PyPDF text extraction & automated QMS supersession detection
│   ├── chunker.py            # Section-aware chunking (keeps table rows & alarms together)
│   ├── retriever.py          # BM25 + keyword hybrid search with active revision weighting
│   ├── rag_engine.py         # Multi-provider LLM chain + smart local extractive fallback
│   └── web/
│       ├── static/
│       │   ├── css/style.css # High-contrast mobile shop-floor theme
│       │   ├── js/app.js     # Speech-to-text, quick chips, clipboard copy
│       │   └── favicon.svg   # Custom industrial gear icon (no 404s)
│       └── templates/
│           └── index.html    # Clean, thumb-friendly mobile responsive UI
├── docs/                     # Downloaded official plant SOP PDFs
├── tests/
│   └── test_rag.py           # Automated test suite (13 tests passing in pytest)
├── main.py                   # FastAPI server entry point + ASCII QR generation
├── requirements.txt          # Python dependencies
├── THINKING.md               # User analysis, user journey, AI challenge, reflection
└── README.md                 # Complete documentation & test answers
```

### Why BM25 + Exact Code Match instead of a Heavy Vector DB?
For a plant SOP library of this size (tens to hundreds of pages), running a massive dense vector embedding model or spinning up Chroma/FAISS adds unnecessary cold-start latency, requires heavy GPU/torch dependencies (over 2 GB), and often drifts on exact machine codes (like confusing `AL-104` with `AL-101`). 

By combining **BM25 Okapi** with **exact code/symbol boosting** (for identifiers like `AL-104`, `BH-220`, `SAF-SOP-003`, `110 Nm`), retrieval is instantaneous (< 2ms), 100% deterministic, and runs on any low-power laptop or plant mini-PC with zero friction.

---

## Running the Automated Tests

The repo includes a full test suite covering document parsing, supersession detection, all 5 sample questions, custom questions, natural human phrasing, and out-of-scope negative assertion:

```bash
python -m pytest tests/test_rag.py -v
```

All **13 tests pass** in under 1 second:
```text
tests/test_rag.py::test_document_ingestion_and_supersession PASSED       [  7%]
tests/test_rag.py::test_sample_question_1_coolant PASSED                 [ 15%]
tests/test_rag.py::test_sample_question_2_alarm_al104 PASSED             [ 23%]
tests/test_rag.py::test_sample_question_3_loto_removal PASSED            [ 30%]
tests/test_rag.py::test_sample_question_4_bh220_tolerance PASSED         [ 38%]
tests/test_rag.py::test_sample_question_5_spindle_runout PASSED          [ 46%]
tests/test_rag.py::test_custom_question_1_missing_mtc PASSED             [ 53%]
tests/test_rag.py::test_custom_question_2_chuck_bolt_torque PASSED       [ 61%]
tests/test_rag.py::test_custom_question_3_sampling_plan PASSED           [ 69%]
tests/test_rag.py::test_custom_question_4_zero_energy PASSED             [ 76%]
tests/test_rag.py::test_custom_question_5_unanswerable PASSED            [ 84%]
tests/test_rag.py::test_superseded_warning_when_querying_old_standard PASSED [ 92%]
tests/test_rag.py::test_human_natural_queries PASSED                     [100%]

============================= 13 passed in 0.84s ==============================
```

---

## Submission Notes

- **THINKING.md**: Contains the full narrative covering:
  1. *Understand the user* (shop-floor supervisor profile, frustrations, assumptions)
  2. *User journey* (first draft before AI critique, failure modes)
  3. *AI challenge* (critique excerpts from a skeptical plant director & my reflection)
  4. *The improvement added* (Revision-aware intelligence & supersession guardrails)
  5. *Final reflection* (next steps, customer questions, challenges faced and handled)
- **Screen Recording (2–3 mins)**: Demonstrates:
  1. Answering 2 sample questions with verifiable citations.
  2. Handling the unanswerable question with a strict negative assertion.
  3. Live demonstration of the app opened and used from a mobile phone on the same Wi-Fi.
