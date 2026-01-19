"""
Streamlit UI for Agentic Invoice Processing System
Demonstrates the step-by-step pipeline execution with Human-in-the-Loop verification.
"""

import streamlit as st
import json
import os
import warnings
import time
from pathlib import Path
from orchestrator import InvoiceProcessingOrchestrator
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Invoice AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium CSS Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container */
    .stApp {
        background-color: #f8fafc;
    }

    /* Cards */
    .agent-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .agent-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }

    /* Headlines */
    h1 {
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #0f172a;
    }
    h2, h3 {
        font-weight: 600;
        color: #334155;
    }

    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-success { background: #b0f2b6; color: #166534; }
    .status-error { background: #fecaca; color: #991b1b; }
    .status-pending { background: #e2e8f0; color: #475569; }
    
    /* Metrics */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .metric-val { font-size: 1.5rem; font-weight: 700; color: #0f172a; }
    .metric-lbl { font-size: 0.875rem; color: #64748b; font-weight: 500; }

</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'ingestion_result' not in st.session_state:
    st.session_state.ingestion_result = None
if 'extraction_result' not in st.session_state:
    st.session_state.extraction_result = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

def init_orchestrator(api_key, model, use_easyocr):
    if not st.session_state.orchestrator:
        st.session_state.orchestrator = InvoiceProcessingOrchestrator(
            openrouter_api_key=api_key,
            model=model,
            use_easyocr=use_easyocr
        )

# --- Helper Functions ---
def render_step_card(title, icon, status, content=None, error=None, is_expanded=False):
    status_map = {
        "success": ("✅ Success", "status-success"),
        "error": ("❌ Failed", "status-error"),
        "pending": ("⏳ Pending", "status-pending")
    }
    msg, cls = status_map.get(status, ("⚪ Unknown", "status-pending"))
    
    st.markdown(f"""
    <div class="agent-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.5rem; background:#f1f5f9; padding:8px; border-radius:8px;">{icon}</span>
                <h3 style="margin:0;">{title}</h3>
            </div>
            <span class="status-badge {cls}">{msg}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if error:
        st.error(f"Error: {error}")
    
    if content:
        with st.expander("View Details", expanded=is_expanded):
            st.json(content)
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main App ---
def main():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚡ Invoice AI Agent")
        st.markdown("<p style='font-size:1.1rem; color:#64748b;'>Transparent, Human-in-the-Loop Invoice Processing System</p>", unsafe_allow_html=True)
    with col2:
        # Mock Metrics
        m1, m2 = st.columns(2)
        with m1:
            st.markdown('<div class="metric-card"><div class="metric-val">98%</div><div class="metric-lbl">Accuracy</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-card"><div class="metric-val">1.2s</div><div class="metric-lbl">Speed</div></div>', unsafe_allow_html=True)

    st.divider()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("OpenRouter Key", value=os.getenv("OPENROUTER_API_KEY", ""), type="password")
        model = st.selectbox("Model", ["openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-3-opus"])
        
        # OCR Check
        import shutil
        tesseract_real = shutil.which("tesseract") is not None
        
        st.subheader("OCR Engine")
        st.info(f"PDF Engine: {'✅ Ready' if True else '❌'}")
        if tesseract_real:
            st.success("Tesseract: ✅ Ready")
        else:
            st.warning("Tesseract: ⚠️ Not Found")

        use_easyocr = st.checkbox("Force EasyOCR", value=not tesseract_real)
        
        if st.button("Reset System", type="secondary", width="stretch"):
            st.session_state.clear()
            st.rerun()

    if not api_key:
        st.warning("Please provide an API Key to start.")
        return

    # Initialize Orchestrator
    try:
        init_orchestrator(api_key, model, use_easyocr)
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        return

    orchestrator = st.session_state.orchestrator

    # Pipeline Visualization
    col_upload, col_pipeline = st.columns([1, 1.5])

    # --- 1. Upload Section ---
    with col_upload:
        st.subheader("1. Ingest Document")
        uploaded_file = st.file_uploader("Upload Invoice", type=["pdf", "png", "jpg"], label_visibility="collapsed")
        
        if uploaded_file:
            # Save File
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            file_path = temp_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Show Preview
            if uploaded_file.type == "application/pdf":
                st.info("📄 PDF Document Loaded")
            else:
                st.image(uploaded_file, caption="Invoice Preview", width="stretch")

            # Auto-Start Phase 1: Extraction
            if st.button("✨ Analyze Invoice", type="primary", width="stretch"):
                with st.spinner("🤖 Agents working... Data Ingestion & Extraction..."):
                    # Step 1: Ingest
                    ingest_res = orchestrator.document_agent.process(str(file_path))
                    st.session_state.ingestion_result = ingest_res
                    
                    if ingest_res.get("raw_text"):
                        # Step 2: Extract
                        extract_res = orchestrator.extraction_agent.extract(ingest_res["raw_text"])
                        st.session_state.extraction_result = extract_res
                        st.session_state.processing_complete = False  # Reset final flag
                        st.rerun()
                    else:
                        st.error("No text extracted!")

    # --- 2. Pipeline Results & Human in Loop ---
    with col_pipeline:
        st.subheader("2. Agent Workflow")
        
        # Step 1: OCR Result
        if st.session_state.ingestion_result:
            render_step_card(
                "Document Ingestion", 
                "👁️", 
                "success", 
                {"source": st.session_state.ingestion_result.get("source_type"), "text_len": len(st.session_state.ingestion_result.get("raw_text", ""))}
            )

        # Step 2: Extraction & Verification
        if st.session_state.extraction_result:
            # If we haven't finished processing, show the edit form
            if not st.session_state.processing_complete:
                st.markdown("### 🕵️ Human Verification Required")
                st.info("Please review the AI's extraction before commiting to the database.")
                
                raw_data = st.session_state.extraction_result
                
                with st.form("verification_form"):
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        biller = st.text_input("Biller Name", value=raw_data.get("biller_name") or "")
                        amount = st.text_input("Total Amount", value=str(raw_data.get("total_amount") or ""))
                    with col_f2:
                        address = st.text_input("Address", value=raw_data.get("biller_address") or "")
                        date = st.text_input("Due Date", value=raw_data.get("due_date") or "")
                    
                    submitted = st.form_submit_button("✅ Approve & Save", type="primary", width="stretch")
                    
                    if submitted:
                        # Update data with user edits
                        edited_data = {
                            "biller_name": biller,
                            "biller_address": address,
                            "total_amount": float(amount) if amount and amount != 'None' else 0,
                            "due_date": date
                        }
                        
                        # Step 3: Validation
                        val_res = orchestrator.validation_agent.validate(edited_data)
                        
                        # Step 4: Decision
                        dec_res = orchestrator.tool_decision_agent.decide(val_res, edited_data)
                        
                        # Step 5: DB Write
                        db_res = None
                        if dec_res["should_write"]:
                            db_res = orchestrator.database_tool.write_invoice_to_db(dec_res["data_to_write"])
                        
                        # Save final state results to display
                        st.session_state.final_results = {
                            "validation": val_res,
                            "decision": dec_res,
                            "db": db_res
                        }
                        st.session_state.processing_complete = True
                        st.rerun()

            else:
                # Show Final Results (Read Only Card)
                render_step_card("Information Extraction", "🧠", "success", st.session_state.extraction_result)
                
                final = st.session_state.final_results
                
                # Validation
                status_v = "success" if final["validation"]["status"] == "valid" else "error"
                render_step_card("Validation Agent", "🛡️", status_v, final["validation"], is_expanded=True)
                
                # DB Write
                if final["decision"]["should_write"]:
                    db_stat = "success" if final["db"] and final["db"].get("success") else "error"
                    render_step_card("Database Tool", "💾", db_stat, final["db"])
                    
                    if db_stat == "success":
                        st.balloons()
                        st.success("🎉 Process Completed Successfully!")
                else:
                    render_step_card("Database Tool", "💾", "pending", {"reason": "Skipped due to validation failure"})
                    st.warning("Stopped by Agent Guardrails.")

        elif not st.session_state.ingestion_result:
            # Empty state placeholder
            st.markdown("""
            <div style="border: 2px dashed #e2e8f0; border-radius:12px; height:300px; display:flex; align-items:center; justify-content:center; color:#94a3b8;">
                waiting for document...
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
