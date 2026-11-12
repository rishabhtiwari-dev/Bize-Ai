# 🏭 BiztelAI — Shop-Floor Supervisor AI Copilot

[![Tests](https://img.shields.io/badge/pytest-12%20passed-brightgreen.svg)](tests/test_rag.py)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Mobile Ready](https://img.shields.io/badge/UI-Mobile%20Optimized-orange.svg)](#-local-network--mobile-deployment)

> An intelligent, grounded, and revision-aware AI assistant built for manufacturing shop-floor supervisors at **Kaveri Precision Components Pvt. Ltd. (Hosur Plant)**. Provides instant, verified answers from plant SOPs, manuals, and safety procedures directly to smartphones and tablets on the shop floor.

---

## 📑 Table of Contents
1. [Overview & Key Features](#-overview--key-features)
2. [Project Architecture](#-project-architecture)
3. [Setup & Quick Start](#-setup--quick-start)
4. [Local Network & Mobile Deployment](#-local-network--mobile-deployment)
5. [Testing & Evaluation](#-testing--evaluation)
   - [Sample Questions & App Answers](#1-sample-questions-answers)
   - [Our 5 Custom Questions & App Answers](#2-our-5-custom-questions-answers)
6. [Component File Structure](#-component-file-structure)
7. [Submission Deliverables](#-submission-deliverables)

---

## 🚀 Overview & Key Features

* **Zero-Hallucination Grounded QA**: Strictly answers from the indexed plant documentation (`MNT-MAN-CNC-02`, `QC-SOP-014`, `SAF-SOP-003`). If an answer is not in the documents, the copilot explicitly says so.
* **Revision-Aware Intelligence (The Core Improvement)**: Automatically detects when a procedure is superseded (e.g., `QC-SOP-014 Rev 03` is superseded by `Rev 04`), prioritizes the active standard, and alerts supervisors with warning banners if outdated procedures are searched.
* **Mobile-First Shop-Floor UX**: Designed for noisy, high-glare plant environments with high-contrast UI, thumb-friendly tap targets, one-tap quick lookup chips, and voice input (Speech-to-Text).
* **Multi-Provider LLM Chain**:
  * **Groq**: Ultra-fast inference with `llama-3.3-70b-versatile` or `llama-3.1-8b-instant`.
  * **OpenAI / Ollama**: Plug-and-play local or cloud OpenAI-compatible endpoints.
  * **Smart Local Extractor (Offline Fallback)**: Runs 100% out of the box without any external API keys or cloud dependencies.
* **Instant Phone Access via QR Code**: Auto-detects your LAN IP and prints an ASCII QR code in your terminal upon launch, plus a web modal with a camera-scannable QR code.

---

## 🏛 Project Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │    Plant Floor Supervisor (Phone / Tablet)    │
                  └───────────────────────┬──────────────────────┘
                                          │  HTTP / WebSockets
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND (main.py)                            │
│  ┌────────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   Static Web UI & JS   │  │   /api/query (POST) │  │   /api/qr & /info   │  │
│  └────────────────────────┘  └──────────┬──────────┘  └─────────────────────┘  │
└─────────────────────────────────────────┼──────────────────────────────────────┘
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                         RAG ENGINE (app/rag_engine.py)                         │
│  ┌────────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   Groq LLM Client      │  │  OpenAI / Ollama    │  │ Local Smart Extract │  │
│  └────────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────┼──────────────────────────────────────┘
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                     HYBRID RETRIEVER (app/retriever.py)                        │
│  • BM25 Okapi with domain code boosting (AL-104, BH-220, TX-200)               │
│  • Active Revision Prioritization (deprioritizes superseded Rev 03)             │
│  • Out-of-Scope Negative Detector (strict unanswerable refusal)                │
└─────────────────────────────────────────┼──────────────────────────────────────┘
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                  DOCUMENT PARSER & CHUNKER (app/parser.py)                     │
│  • PyPDF Metadata & Text Extraction                                            │
│  • Automatic Supersession Relationship Detection                               │
│  • Section-Aware & Table-Preserving Chunking (app/chunker.py)                  │
└─────────────────────────────────────────┬──────────────────────────────────────┘
                                          ▼
                        ┌───────────────────────────────────┐
                        │      docs/ (Plant SOP PDFs)       │
                        │ • MNT-MAN-CNC-02 Rev 02 (CNC PM)  │
                        │ • QC-SOP-014 Rev 03 (QC - Old)    │
                        │ • QC-SOP-014 Rev 04 (QC - Active) │
                        │ • SAF-SOP-003 Rev 05 (LOTO)       │
                        └───────────────────────────────────┘
```

---

## 🛠 Setup & Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/rishab-bizeai/shopfloor-copilot.git
cd shopfloor-copilot
```

### 2. Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure LLM API Keys
The app **works out of the box in offline local extractive mode** with zero configuration.  
To enable full generative LLM responses, copy `.env.example` to `.env` and add your API key:
```bash
cp .env.example .env
```
Inside `.env`:
```ini
# Option A: Groq (Recommended - Free & Fast)
GROQ_API_KEY=gsk_your_key_here
LLM_MODEL=llama-3.3-70b-versatile

# Option B: OpenAI
OPENAI_API_KEY=sk-your_key_here
LLM_MODEL=gpt-4o-mini

# Option C: Local Ollama
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.2
```

### 5. Start the Copilot
```bash
python main.py
```
Or with Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📱 Local Network & Mobile Deployment

When you launch `python main.py`, the application binds to `0.0.0.0:8000` and automatically detects your laptop's local Wi-Fi IP address.

1. **Terminal Output**:
   ```
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
2. **Open on Phone**:
   - Ensure your phone is connected to the same Wi-Fi network as your laptop.
   - Scan the ASCII QR code printed in the terminal or click the **"Phone Access"** button in the web UI header.
   - Or open your mobile browser and enter: `http://<YOUR_LOCAL_IP>:8000` (e.g. `http://192.168.1.10:8000`).

---

## 🧪 Testing & Evaluation

Run the automated test suite covering all 12 test assertions:
```bash
python -m pytest tests/test_rag.py -v
```
Output:
```
tests/test_rag.py::test_document_ingestion_and_supersession PASSED       [  8%]
tests/test_rag.py::test_sample_question_1_coolant PASSED                 [ 16%]
tests/test_rag.py::test_sample_question_2_alarm_al104 PASSED             [ 25%]
tests/test_rag.py::test_sample_question_3_loto_removal PASSED            [ 33%]
tests/test_rag.py::test_sample_question_4_bh220_tolerance PASSED         [ 41%]
tests/test_rag.py::test_sample_question_5_spindle_runout PASSED          [ 50%]
tests/test_rag.py::test_custom_question_1_missing_mtc PASSED             [ 58%]
tests/test_rag.py::test_custom_question_2_chuck_bolt_torque PASSED       [ 66%]
tests/test_rag.py::test_custom_question_3_sampling_plan PASSED           [ 75%]
tests/test_rag.py::test_custom_question_4_zero_energy PASSED             [ 83%]
tests/test_rag.py::test_custom_question_5_unanswerable PASSED            [ 91%]
tests/test_rag.py::test_superseded_warning_when_querying_old_standard PASSED [100%]
============================= 12 passed in 0.69s ==============================
```

---

### 1. Sample Questions & Answers

#### Q1: What is the recommended coolant concentration for the TX-200 CNC turning centre?
* **App Answer**:
  > The recommended coolant concentration for the TX-200 CNC turning centre is **6 - 8 %**.
  > • **Check Method**: Refractometer reading multiplied by a **1.0 factor**.  
  > • **Frequency**: Checked daily at the start of shift and weekly by the operator.
* **Source Citation**: `MNT-MAN-CNC-02 Rev 02, Page 1, Section: 3. Normal Operating Parameters`
* **Status**: ✅ Verified in SOP

#### Q2: The machine is showing alarm AL-104. What does it mean and what should the operator do?
* **App Answer**:
  > **Alarm AL-104 Meaning**: **Way lube oil level low**.  
  > **Required Operator Action**:  
  > 1. Top up with **ISO VG 68 oil** to the **MAX mark** on the sight glass.  
  > 2. Press the **RESET** button on the control panel.  
  > 3. The machine can continue its normal cycle after reset.
* **Source Citation**: `MNT-MAN-CNC-02 Rev 02, Page 2, Section: Common Alarms`
* **Status**: ✅ Verified in SOP

#### Q3: Who is allowed to remove a lockout lock from a machine?
* **App Answer**:
  > **Standard Policy (Section 5)**: **Each authorised person removes only their own personal lock**. Nobody may remove another person's lock.  
  > **Procedure When Lock Owner Is Absent (Section 6)**:  
  > 1. The **Shift Supervisor** must make every reasonable effort to contact the lock owner by phone.  
  > 2. If unreachable, **both the Production Manager and the Safety Officer** must authorise removal.  
  > 3. The machine must be physically inspected to confirm it is safe to re-energise.  
  > 4. Removal must be documented on form **SF-12 Lock Removal Record**, and the owner informed before their next shift.
* **Source Citation**: `SAF-SOP-003 Rev 05, Page 1-2, Sections 5 & 6`
* **Status**: ✅ Verified in SOP

#### Q4: What is the outer diameter tolerance for the BH-220 bearing housing?
* **App Answer**:
  > For the **BH-220 bearing housing**, the outer diameter specifications are:  
  > • **Nominal**: **90.000 mm**  
  > • **Tolerance**: **+/- 0.050 mm** (acceptable range: 89.950 mm to 90.050 mm)  
  > • **Measurement Method**: Calibrated **digital caliper**  
  > • **Defect Classification**: **Major** defect
* **Source Citation**: `QC-SOP-014 Rev 04, Page 2, Section: 6. Inspection Dimensions - BH-220 Bearing Housing`
* **Status**: ✅ Verified in SOP

#### Q5: How often should spindle runout be checked, and who does it?
* **App Answer**:
  > Spindle runout must be checked **Monthly** by a **Maintenance technician**.  
  > • **Check Method**: Dial indicator at the chuck face.  
  > • **Tolerance Limit**: Maximum allowable runout is **0.005 mm max**.
* **Source Citation**: `MNT-MAN-CNC-02 Rev 02, Page 1, Section 3 & Section 4`
* **Status**: ✅ Verified in SOP

---

### 2. Our 5 Custom Questions & Answers

#### Custom Q1 (QC Revision Change / Mandatory Document Check):
**Question**: *What should the inspector do if the supplier's Material Test Certificate (MTC) is missing during incoming material inspection?*
* **App Answer**:
  > Under **QC-SOP-014 Rev 04**, the supplier's **Material Test Certificate (MTC) is mandatory**.  
  > • **Required Action**: If the MTC is missing, the lot is put on **HOLD** and **must not be inspected or accepted** until the MTC is received.  
  > *(Note: In superseded Rev 03, MTC was only 'if available', but Rev 04 made it strictly mandatory).*
* **Source Citation**: `QC-SOP-014 Rev 04, Page 2, Section 5 (Procedure Step 2)`
* **Status**: ✅ Verified in SOP

#### Custom Q2 (Maintenance Torque Specification):
**Question**: *What is the required torque and sequence for tightening the chuck mounting bolts after maintenance on the TX-200 CNC?*
* **App Answer**:
  > When re-mounting the chuck after maintenance on the TX-200 CNC:  
  > • Tighten mounting bolts in a **criss-cross sequence**.  
  > • Tighten to **110 Nm** using a calibrated torque wrench.
* **Source Citation**: `MNT-MAN-CNC-02 Rev 02, Page 1, Section 5`
* **Status**: ✅ Verified in SOP

#### Custom Q3 (Lot-Size Sampling Plan Calculation):
**Question**: *For a received lot of 250 pieces of steel bar stock, how many samples must be inspected, and what defect rule applies?*
* **App Answer**:
  > Under **QC-SOP-014 Rev 04 (Section 4 Sampling Plan)**:  
  > • For a lot size between **91 - 500 pieces** (such as 250 pieces), inspect **13 samples** at random.  
  > • **Minor Defects**: Accept if 0, reject if 1 or more.  
  > • **Major Defects**: Complete lot is rejected (SQE may authorise 100% sorting at supplier's cost).  
  > • **Critical Defects**: Complete lot rejected and returned to supplier. Sorting is not allowed.
* **Source Citation**: `QC-SOP-014 Rev 04, Page 1, Section 4`
* **Status**: ✅ Verified in SOP

#### Custom Q4 (Safety Zero-Energy Verification Protocol):
**Question**: *How must an authorised person verify zero energy state before working on a machine under LOTO?*
* **App Answer**:
  > To verify zero energy under **SAF-SOP-003 Rev 05 (Section 4)**:  
  > 1. **Release Stored Energy**: Bleed hydraulic pressure and accumulators until gauge reads zero, vent compressed air to 0 bar, and block parts that can fall under gravity.  
  > 2. **Functional Verification**: Try to start the machine from the control panel and confirm it **does not start**.  
  > 3. **Gauge Confirmation**: Confirm all pressure gauges read zero.  
  > 4. **Controls**: Return controls to **OFF**.
* **Source Citation**: `SAF-SOP-003 Rev 05, Page 1, Section 4`
* **Status**: ✅ Verified in SOP

#### Custom Q5 (UNANSWERABLE / Out-of-Scope Question):
**Question**: *What is the maximum feed rate and spindle speed for cutting titanium alloy on CNC-04?*
* **App Answer**:
  > **This information is not found in the available plant SOPs and manuals.**  
  > None of the indexed documents (`MNT-MAN-CNC-02`, `QC-SOP-014`, `SAF-SOP-003`) contain details answering this query. Please verify with your Shift Supervisor, Maintenance Engineer, or Quality Lead.
* **Source Citation**: None (Zero hallucinations policy active)
* **Status**: ❌ Out of Document Scope (Handled with Strict Negative Assertion)

---

### 3. Real Shop-Floor Human Queries vs. Formal Queries

On an actual shop floor, supervisors and operators don't speak in formal academic prose. The copilot is specifically tested and optimized to handle messy, conversational human phrasing:

| Real Human Shop-Floor Query | Intent / Standard Topic | App Answer & Citation |
|---|---|---|
| *"AL-104 popped up on CNC-06. What oil do I top up and how to reset?"* | Machine Alarm Troubleshooting | Top up **ISO VG 68 oil** to MAX mark, press RESET (`MNT-MAN-CNC-02 Rev 02, Page 2`) |
| *"Refractometer check: what coolant percentage should we maintain on the TX-200?"* | Daily Operating Parameter | Recommended **6 - 8 %**, refractometer × 1.0 factor (`MNT-MAN-CNC-02 Rev 02, Page 1`) |
| *"Technician left his red LOTO lock on CNC-04 and went home. Can I take it off myself?"* | Safety Lockout Policy | **No.** Only owner can remove. Absent owner requires PM + Safety Officer authorization (`SAF-SOP-003 Rev 05, Page 1-2`) |
| *"Supplier delivered a batch of steel bars but forgot the MTC certificate. Can we proceed?"* | Incoming Inspection Rule | **No.** Put on **HOLD**. MTC is mandatory under Rev 04 (`QC-SOP-014 Rev 04, Page 2`) |
| *"Inspector is measuring BH-220 bearing housings with a digital caliper. What are the OD limits?"* | Dimensional Quality Check | Nominal **90.000 mm**, Tolerance **+/- 0.050 mm** (`QC-SOP-014 Rev 04, Page 2`) |
| *"Receiving just got 250 bought-out pins. How many pieces to sample, and defect rule?"* | Lot Sampling Plan | Inspect **13 samples**. Minor: 0 allowed. Major/Critical: Reject (`QC-SOP-014 Rev 04, Page 1`) |
| *"Technician just re-mounted the chuck on TX-200. What torque and pattern should he use?"* | Assembly & Maintenance | Tighten in **criss-cross sequence to 110 Nm** (`MNT-MAN-CNC-02 Rev 02, Page 1`) |
| *"Operator wants to know: what feed rate and spindle speed for cutting titanium on CNC-04?"* | **Unanswerable / Out of Scope** | **Strict Refusal**: *"This information is not found in the plant SOPs"* (Zero hallucinations) |

---

## 📂 Component File Structure

```
BizeAi/
├── app/
│   ├── __init__.py
│   ├── config.py             # Server settings, LAN IP auto-detection, LLM model configs
│   ├── models.py             # Pydantic schemas (QueryRequest, QueryResponse, Citations)
│   ├── parser.py             # PDF reader with automated QMS supersession detection
│   ├── chunker.py            # Section-aware chunking preserving tables & alarm entries
│   ├── retriever.py          # BM25 + keyword hybrid search with revision weighting
│   ├── rag_engine.py         # Multi-provider LLM chain + grounded prompt engineering
│   └── web/
│       ├── static/
│       │   ├── css/
│       │   │   └── style.css # High-contrast mobile shop-floor theme
│       │   └── js/
│       │       └── app.js    # Client logic: speech-to-text, quick chips, clipboard copy
│       └── templates/
│           └── index.html    # Clean, thumb-friendly responsive frontend
├── docs/                     # Plant SOP PDFs from Google Drive
│   ├── MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf
│   ├── QC-SOP-014_Rev03_Incoming_Material_Inspection.pdf
│   ├── QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf
│   ├── SAF-SOP-003_Lockout_Tagout_Procedure.pdf
│   └── Sample_Questions.pdf
├── tests/
│   ├── __init__.py
│   └── test_rag.py           # Automated test suite (12 assertions)
├── .env.example              # Template for API keys & model configuration
├── main.py                   # FastAPI server entry point + ASCII QR generation
├── requirements.txt          # Python dependencies
├── THINKING.md               # User analysis, user journey, AI challenge, reflection
└── README.md                 # Complete guide, sample test answers, and documentation
```

---

## 📦 Submission Deliverables

Per the BiztelAI assignment instructions:
1. **GitHub Repository**: Public repository containing all modular source code, tests, documentation, and sample questions.
2. **THINKING.md**: Contains the 5 required sections:
   - *Understand the user*
   - *User journey*
   - *AI challenge (conversation excerpts and reflection)*
   - *The improvement added, and why chosen*
   - *Final reflection (challenges faced, customer questions, next steps)*
3. **Screen Recording**: 2–3 minute video demonstration showcasing:
   - The copilot answering 2 sample questions with citations.
   - The copilot responding to an unanswerable question with strict negative assertion.
   - The application opened and used from a mobile phone on the same Wi-Fi network.
