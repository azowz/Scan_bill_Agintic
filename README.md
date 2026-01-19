# Agentic Invoice Processing Workflow

A production-grade agentic AI system for processing invoices with transparent, step-by-step pipeline execution.

**🌍 Optimized for Arabic invoices** - Handles RTL layouts, Arabic digits, and mixed Arabic/English content.

## 🎯 Overview

This system demonstrates a **multi-agent workflow** for invoice processing where:
- **Responsibilities are strictly separated** across specialized agents
- **Each agent has a single, well-defined purpose**
- **Tool usage is controlled and transparent**
- **The UI exposes the entire reasoning pipeline** for debuggability
- **Arabic-optimized** with GPT-4o, Tesseract (ara+eng), and PyMuPDF

## 🏗️ Architecture

### Agents

1. **Document Ingestion Agent** (`agents/document_ingestion_agent.py`)
   - Converts PDF/image invoices → raw text
   - Uses OCR (Tesseract with Arabic+English) and PDF parsing (PyMuPDF for RTL)
   - **Does NOT extract meaning** - only text extraction
   - **Arabic-optimized**: Handles Arabic digits (٠١٢٣٤٥٦٧٨٩) and RTL layouts

2. **Information Extraction Agent** (`agents/extraction_agent.py`)
   - Extracts structured fields from raw text using LLM (GPT-4o recommended for Arabic)
   - Fields: `biller_name`, `biller_address`, `total_amount`, `due_date`
   - Uses semantic understanding (not position-based)
   - **Arabic-aware**: Understands Arabic invoice terms (فاتورة, المبلغ الإجمالي, etc.)

3. **Validation Agent** (`agents/validation_agent.py`)
   - Validates extracted fields
   - Checks required fields, data types, formats
   - Returns validation status and errors

4. **Tool Decision Agent** (`agents/tool_decision_agent.py`)
   - Decides whether to call database write tool
   - Only triggers DB write if validation passes

5. **Database Tool** (`tools/database_tool.py`)
   - Mock database implementation
   - Stores validated invoices (JSON file for demo)

### Orchestrator

The `orchestrator.py` coordinates all agents and maintains the pipeline state.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Tesseract OCR with **Arabic language pack** installed ([Installation guide](ARABIC_SETUP.md))
- **OpenRouter API key** (Get free key from https://openrouter.ai - provides access to GPT-4o, Claude, etc.)

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR:**
   - **Windows:** Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS:** `brew install tesseract`
   - **Linux:** `sudo apt-get install tesseract-ocr`

4. **Set up environment variables:**

   **Option 1: Use setup script (Easiest)**
   ```bash
   python setup_env.py
   ```

   **Option 2: Create manually**
   Create a `.env` file in the project root:
   ```bash
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=openai/gpt-4o  # Recommended for Arabic invoices
   ```
   
   **💡 Get your free API key from: https://openrouter.ai**

   See [CREATE_ENV.md](CREATE_ENV.md) for detailed instructions.

5. **Run the Streamlit UI:**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## 📋 Usage

1. **Upload an invoice** (PDF or image)
2. **Enter your OpenAI API key** in the sidebar
3. **Click "Process Invoice"**
4. **View step-by-step results** for each agent:
   - Document Ingestion (raw text)
   - Information Extraction (structured JSON)
   - Validation (status and errors)
   - Tool Decision (write/not write)
   - Database Write (execution result)

## 🎨 UI Features

The UI displays:

- ✅ **Invoice Preview** - File information
- ✅ **OCR Text Panel** - Raw extracted text
- ✅ **Extracted JSON Panel** - Structured invoice data
- ✅ **Validation Result** - Green (valid) / Red (incomplete)
- ✅ **DB Write Triggered** - Badge showing execution status

Each agent step shows:
- Agent name
- Status (success/failed/error/skipped)
- Input data
- Output data
- Errors (if any)

## 📁 Project Structure

```
.
├── agents/
│   ├── document_ingestion_agent.py
│   ├── extraction_agent.py
│   ├── validation_agent.py
│   └── tool_decision_agent.py
├── tools/
│   └── database_tool.py
├── prompts.py              # All agent prompts
├── orchestrator.py         # Master orchestrator
├── app.py                  # Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

## 🔑 Key Design Principles

1. **Separation of Concerns**: Each agent has a single responsibility
2. **No Direct DB Writes**: Agents return structured outputs, orchestrator decides on tool usage
3. **Transparency**: All steps are visible in the UI
4. **Semantic Understanding**: No hard-coded positions or templates
5. **Safe Tool Usage**: Tools only called after validation

## 🧪 Testing

Test with sample invoices:
- PDF invoices
- Image invoices (PNG, JPG)
- Various layouts and languages

The system handles:
- ✅ Different invoice formats
- ✅ Missing fields (returns null)
- ✅ Invalid data (validation catches errors)
- ✅ OCR failures (graceful error handling)

## 📝 Prompts

All prompts are defined in `prompts.py`:
- System prompt (global)
- Agent 1: Document Ingestion
- Agent 2: Information Extraction
- Agent 3: Validation
- Agent 4: Tool Decision
- Master Orchestration prompt

## 🎓 Educational Value

This implementation demonstrates:
- **Agentic AI architecture** with specialized agents
- **Prompt engineering** for structured outputs
- **Tool calling patterns** with safety checks
- **UI transparency** for debugging AI systems
- **Production-grade patterns** (error handling, validation, logging)

## 🔧 Configuration

- **LLM Provider**: **OpenRouter API** (provides access to multiple models)
- **Recommended Model**: `openai/gpt-4o` (best for Arabic) or `openai/gpt-4o-mini` (cost-effective)
- **Alternative Models**: `anthropic/claude-3-opus`, `anthropic/claude-3-sonnet` (via OpenRouter)
- **Database**: Mock JSON file (`invoices_db.json`)
- **OCR Engine**: Tesseract with Arabic+English (`ara+eng`)
- **PDF Engine**: PyMuPDF (best for Arabic/RTL PDFs)
- **EasyOCR**: Optional fallback for low-quality images

**💡 Get your free OpenRouter API key from: https://openrouter.ai**

See [ARABIC_SETUP.md](ARABIC_SETUP.md) for Arabic-specific setup instructions.

## 📄 License

This is an educational project for demonstrating agentic AI workflows.

## 🤝 Contributing

Feel free to extend this with:
- Real database integration
- Additional validation rules
- Multi-language support
- Batch processing
- API endpoints

---

**Built for demonstrating production-grade agentic AI systems** 🚀
