// BiztelAI Plant Copilot - Mobile-First Shop-Floor Frontend Logic

document.addEventListener("DOMContentLoaded", () => {
    const queryForm = document.getElementById("query-form");
    const queryInput = document.getElementById("query-input");
    const submitBtn = document.getElementById("submit-btn");
    const voiceBtn = document.getElementById("voice-btn");
    const voiceStatus = document.getElementById("voice-status");
    const resultSection = document.getElementById("result-section");
    const loadingSpinner = document.getElementById("loading-spinner");
    
    const answerBody = document.getElementById("answer-body");
    const foundBadge = document.getElementById("found-badge");
    const providerBadge = document.getElementById("provider-badge");
    const timeBadge = document.getElementById("time-badge");
    const docBadge = document.getElementById("doc-badge");
    
    const supersededAlert = document.getElementById("superseded-alert");
    const supersededText = document.getElementById("superseded-text");
    const notFoundAlert = document.getElementById("not-found-alert");
    const sourcesContainer = document.getElementById("sources-container");
    const sourcesList = document.getElementById("sources-list");
    
    const copyBtn = document.getElementById("copy-btn");
    const qrBtn = document.getElementById("qr-btn");
    const qrModal = document.getElementById("qr-modal");
    const closeModalBtn = document.getElementById("close-modal-btn");
    const copyUrlBtn = document.getElementById("copy-url-btn");
    const ipValSpan = document.getElementById("ip-val");
    const lanUrlDisplay = document.getElementById("lan-url-display");

    let recognition = null;
    let isRecording = false;
    let currentRawAnswer = "";

    // 1. Fetch System Info (LAN IP, Docs summary)
    fetchSystemInfo();

    async function fetchSystemInfo() {
        try {
            const res = await fetch("/api/info");
            if (res.ok) {
                const data = await res.json();
                if (ipValSpan) ipValSpan.textContent = data.local_ip;
                if (lanUrlDisplay) lanUrlDisplay.textContent = `http://${data.local_ip}:${data.port}`;
            }
        } catch (e) {
            console.warn("Could not fetch system info", e);
        }
    }

    // 2. Query Submission
    queryForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (!query) return;

        await executeQuery(query);
    });

    async function executeQuery(query) {
        queryInput.value = query;
        resultSection.classList.add("hidden");
        loadingSpinner.classList.remove("hidden");
        submitBtn.disabled = true;

        try {
            const res = await fetch("/api/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, top_k: 4, prefer_latest: true })
            });

            if (!res.ok) {
                throw new Error(`Server returned error: ${res.status}`);
            }

            const data = await res.json();
            renderResponse(data);
        } catch (err) {
            console.error(err);
            alert("Error communicating with plant copilot server: " + err.message);
        } finally {
            loadingSpinner.classList.add("hidden");
            submitBtn.disabled = false;
        }
    }

    // 3. Render Query Response
    function renderResponse(data) {
        currentRawAnswer = data.answer;
        resultSection.classList.remove("hidden");

        // Format markdown to HTML
        answerBody.innerHTML = formatMarkdown(data.answer);

        // Found / Not Found Badge
        if (data.is_found) {
            foundBadge.textContent = "VERIFIED IN SOP";
            foundBadge.className = "badge-found";
            notFoundAlert.classList.add("hidden");
        } else {
            foundBadge.textContent = "OUT OF SCOPE / NOT IN SOPs";
            foundBadge.className = "badge-found not-found";
            notFoundAlert.classList.remove("hidden");
        }

        // Provider info
        providerBadge.textContent = `${data.provider} (${data.model})`;
        timeBadge.textContent = `⏱ ${data.processing_time_ms} ms`;
        docBadge.textContent = `📚 ${data.sources.length} sources retrieved`;

        // Superseded Warning
        if (data.superseded_warning) {
            supersededAlert.classList.remove("hidden");
            supersededText.textContent = data.superseded_warning;
        } else {
            supersededAlert.classList.add("hidden");
        }

        // Citations
        sourcesList.innerHTML = "";
        if (data.sources && data.sources.length > 0) {
            sourcesContainer.classList.remove("hidden");
            data.sources.forEach((src, idx) => {
                const card = document.createElement("div");
                card.className = `source-card ${src.is_superseded ? "superseded" : ""}`;
                
                const supersededTag = src.is_superseded 
                    ? `<span class="badge old">SUPERSEDED by ${src.superseded_by || 'Newer Rev'}</span>` 
                    : `<span class="badge active">ACTIVE</span>`;

                card.innerHTML = `
                    <div class="source-card-header">
                        <div>
                            <span class="source-meta">${src.doc_number}</span>
                            <span class="source-rev">Rev ${src.revision}</span>
                            ${supersededTag}
                        </div>
                        <span class="source-score">Relevance Score: ${src.score}</span>
                    </div>
                    <div class="source-section">
                        Page ${src.page} • ${src.section || 'General Procedure'}
                    </div>
                    <div class="source-snippet">${escapeHtml(src.snippet)}</div>
                `;
                sourcesList.appendChild(card);
            });
        } else {
            sourcesContainer.classList.add("hidden");
        }

        // Auto-scroll on mobile to results
        resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // 4. Quick Action Chips
    document.querySelectorAll(".chip").forEach((chip) => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-q");
            if (query) {
                executeQuery(query);
            }
        });
    });

    // 5. Speech-to-Text (Voice Input)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onstart = () => {
            isRecording = true;
            voiceBtn.classList.add("recording");
            voiceStatus.textContent = "Listening...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            queryInput.value = transcript;
            executeQuery(transcript);
        };

        recognition.onerror = (event) => {
            console.warn("Speech recognition error:", event.error);
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
        };

        voiceBtn.addEventListener("click", () => {
            if (!isRecording) {
                try {
                    recognition.start();
                } catch (e) {
                    console.error("Could not start recognition", e);
                }
            } else {
                recognition.stop();
                stopRecording();
            }
        });
    } else {
        voiceBtn.title = "Speech recognition not supported on this browser";
        voiceBtn.style.opacity = "0.5";
    }

    function stopRecording() {
        isRecording = false;
        voiceBtn.classList.remove("recording");
        voiceStatus.textContent = "Speak";
    }

    // 6. Copy Answer to Clipboard
    copyBtn.addEventListener("click", async () => {
        if (!currentRawAnswer) return;
        try {
            await navigator.clipboard.writeText(currentRawAnswer);
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = `<span>Copied! ✓</span>`;
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000);
        } catch (e) {
            console.error("Clipboard copy failed", e);
        }
    });

    // 7. QR Modal
    qrBtn.addEventListener("click", () => {
        qrModal.classList.remove("hidden");
    });

    closeModalBtn.addEventListener("click", () => {
        qrModal.classList.add("hidden");
    });

    qrModal.querySelector(".modal-backdrop").addEventListener("click", () => {
        qrModal.classList.add("hidden");
    });

    copyUrlBtn.addEventListener("click", async () => {
        const url = lanUrlDisplay.textContent;
        try {
            await navigator.clipboard.writeText(url);
            copyUrlBtn.textContent = "Copied!";
            setTimeout(() => { copyUrlBtn.textContent = "Copy URL"; }, 1500);
        } catch (e) {
            console.error("Copy failed", e);
        }
    });

    // 8. Markdown Formatter Helper
    function formatMarkdown(text) {
        if (!text) return "";
        let formatted = escapeHtml(text);

        // Bold: **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

        // Italics: *(text)* or *text*
        formatted = formatted.replace(/\*([^\*]+)\*/g, "<em>$1</em>");

        // Split paragraphs
        const paras = formatted.split(/\n\n+/);
        return paras.map(p => {
            p = p.trim();
            if (p.startsWith("• ") || p.startsWith("- ")) {
                const items = p.split(/\n[•\-]\s+/);
                return "<ul>" + items.map(it => `<li>${it.replace(/^[•\-]\s+/, "")}</li>`).join("") + "</ul>";
            }
            if (/^[0-9]+\.\s+/.test(p)) {
                const items = p.split(/\n(?=[0-9]+\.\s+)/);
                return "<ol>" + items.map(it => `<li>${it.replace(/^[0-9]+\.\s+/, "")}</li>`).join("") + "</ol>";
            }
            return `<p>${p.replace(/\n/g, "<br>")}</p>`;
        }).join("");
    }

    function escapeHtml(string) {
        return String(string)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
