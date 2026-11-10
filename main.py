import io
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import qrcode

from app import config
from app.parser import load_all_documents
from app.chunker import chunk_document
from app.retriever import DocumentRetriever
from app.rag_engine import RAGEngine
from app.models import QueryRequest, QueryResponse, SystemInfoResponse

# Global singletons
documents = []
all_chunks = []
retriever = None
rag_engine = None

def init_app_state():
    global documents, all_chunks, retriever, rag_engine
    if rag_engine is not None:
        return

    print("\n" + "=" * 60)
    print("🏭 INITIALIZING BIZTELAI PLANT COPILOT...")
    print("=" * 60)
    
    # 1. Load documents
    docs_path = config.DOCS_DIR
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=True)
    
    documents = load_all_documents(docs_path)
    print(f" Loaded {len(documents)} SOP documents:")
    for d in documents:
        status_tag = f"(SUPERSEDED by {d.superseded_by})" if d.is_superseded else "[ACTIVE]"
        print(f"   • {d.doc_number} Rev {d.revision}: {d.title} {status_tag}")

    # 2. Chunk documents
    all_chunks = []
    for d in documents:
        all_chunks.extend(chunk_document(d))
    print(f" Created {len(all_chunks)} section-aware chunks.")

    # 3. Build Retriever and RAG Engine
    retriever = DocumentRetriever(all_chunks)
    rag_engine = RAGEngine(retriever)
    print(f" RAG Engine ready using provider: {rag_engine.provider} ({rag_engine.model_name})")

    # 4. Print Network Access info
    local_url = f"http://localhost:{config.PORT}"
    network_url = f"http://{config.LOCAL_IP}:{config.PORT}"
    
    print("\n" + "🚀 COPILOT IS LIVE & READY FOR SHOP-FLOOR USE!")
    print(f"💻 Local Access:   {local_url}")
    print(f"📱 Phone/Tablet:   {network_url}")
    print(f"📸 QR Code URL:    {local_url}/api/qr")
    print("=" * 60 + "\n")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_app_state()
    yield

app = FastAPI(
    title="BiztelAI Plant Copilot",
    description="Shop-floor SOP, Maintenance & Safety AI Assistant for Supervisors",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")

@app.get("/", response_class=FileResponse)
async def serve_index():
    index_file = config.TEMPLATES_DIR / "index.html"
    return FileResponse(index_file)

@app.post("/api/query", response_model=QueryResponse)
async def handle_query(req: QueryRequest):
    global rag_engine
    if rag_engine is None:
        init_app_state()
    return rag_engine.answer_query(
        query=req.query,
        top_k=req.top_k,
        prefer_latest=req.prefer_latest
    )

@app.get("/api/info", response_model=SystemInfoResponse)
async def get_system_info():
    global documents, all_chunks, rag_engine
    if rag_engine is None:
        init_app_state()
        
    docs_summary = [
        {
            "doc_number": d.doc_number,
            "revision": d.revision,
            "title": d.title,
            "effective_date": d.effective_date,
            "is_superseded": d.is_superseded,
            "superseded_by": d.superseded_by
        }
        for d in documents
    ]
    return SystemInfoResponse(
        local_url=f"http://localhost:{config.PORT}",
        network_url=f"http://{config.LOCAL_IP}:{config.PORT}",
        local_ip=config.LOCAL_IP,
        port=config.PORT,
        total_docs=len(documents),
        total_chunks=len(all_chunks),
        active_provider=f"{rag_engine.provider} ({rag_engine.model_name})" if rag_engine else "Offline",
        docs_summary=docs_summary
    )

@app.get("/api/qr")
async def generate_qr():
    """Generates PNG QR code pointing directly to the mobile phone LAN URL."""
    network_url = f"http://{config.LOCAL_IP}:{config.PORT}"
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(network_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b0f19", back_color="#ffffff")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@app.get("/api/health")
async def health_check():
    global documents, all_chunks
    if rag_engine is None:
        init_app_state()
    return {"status": "ok", "docs_indexed": len(documents), "chunks_indexed": len(all_chunks)}

if __name__ == "__main__":
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=False)
