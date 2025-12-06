# FM-ERP JUCS Submission Package - AI Coding Agent Instructions

## Project Overview
This is an **academic research submission package** for JUCS (Journal of Universal Computer Science). It contains documentation for **FM-ERP (Federated Modular Cloud ERP)** — a blockchain-enabled warehouse management system integrating federated learning, digital twins, and IoT for SMEs.

**Primary Purpose:** Preparing and submitting a research manuscript, NOT active software development.

## Package Structure

| File | Purpose |
|------|---------|
| `1. Cover Letter to JUCS Editor.md` | Formal submission letter to journal editor |
| `2. Author Statement and credit.md` | CRediT contributor roles & authorship declaration |
| `3. Manuscript.tex` | LaTeX source for the research paper |
| `4. readme and quick start guide.md` | Compilation & submission overview |
| `5. Submission Step-by-Step Instructions.md` | Detailed submission workflow checklist |
| `6. Post-Submission Action Plan.md` | Post-submission and peer review strategy |
| `7. FM_ERP_IMPLEMENTATION_PROMPT.md` | **Complete AI implementation spec** for FM-ERP prototype |
| `JUCS_COMPLETE_SUBMISSION_PACKAGE.md` | Package manifest and status |

## Key Technical Specifications (from `7. FM_ERP_IMPLEMENTATION_PROMPT.md`)

### FM-ERP Architecture
- **7-layer modular architecture** using ports-and-adapters pattern
- **Tech Stack:** Hyperledger Fabric 2.5+, Python 3.11+, Go 1.21+ (chaincode), TypeScript/React, FastAPI, PyTorch, Flower (federated learning)
- **Novel Components:**
  - **PoDQ (Proof-of-Data-Quality):** Custom consensus mechanism prioritizing data quality over computational work
  - **AQPSO-BV:** Adaptive Quantum-Inspired PSO with Blockchain Verification
  - **Federated Digital Twins:** Distributed warehouse simulation

### Reproducibility Requirements
- All experiments must run deterministically (fixed random seeds)
- Results must match manuscript claims (±5% variance)
- Complete in <2 hours on standard hardware
- Zero manual configuration via Docker Compose

## Working with This Package

### Document Conventions
- Markdown files numbered `1.` through `7.` indicate submission sequence
- LaTeX manuscript uses `jucs2e.cls` template (JUCS-specific)
- CRediT taxonomy used for author contributions

### When Editing Content
- **Cover letter/Author statement:** Placeholder text like `[Your Name]`, `[Institution]` needs replacement
- **LaTeX manuscript:** Author info on lines 14-17, figures require generation (see Step 2 in submission instructions)
- **Implementation prompt:** Contains complete code specifications—use for prototype development if needed

### AI Tool Disclosure Requirement
JUCS 2024+ requires disclosure of AI tools used in manuscript preparation. Document in `2. Author Statement and credit.md` under "AI TOOL DISCLOSURE" section.

## Commands & Workflows

### LaTeX Compilation (for `3. Manuscript.tex`)
```bash
pdflatex FM_ERP_JUCS_Manuscript.tex
bibtex FM_ERP_JUCS_Manuscript
pdflatex FM_ERP_JUCS_Manuscript.tex
pdflatex FM_ERP_JUCS_Manuscript.tex
```

### If Implementing FM-ERP Prototype
The `7. FM_ERP_IMPLEMENTATION_PROMPT.md` contains detailed specs including:
- Complete directory structure (`fm-erp/`)
- Hyperledger Fabric network configuration
- Go chaincode for inventory management
- Python SDK with async Fabric client
- PoDQ consensus Python implementation

## Critical Context

1. **This is documentation, not code.** The package prepares a journal submission—actual FM-ERP implementation would be separate.

2. **Target: JUCS Open Access journal.** No article processing charges, CC BY 4.0 license, authors retain copyright.

3. **Synthetic data only.** All experiments use generated datasets—no real warehouse or enterprise data.

4. **Key claims to preserve:** 42% inventory discrepancy reduction, 38% order fulfillment improvement, 2.3s PoDQ finality, 99.7% privacy preservation.
