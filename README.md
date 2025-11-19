# Virtual CSR: Call Center Conflict Analysis

Automated pipeline for identifying and analyzing customer conflicts in call center transcripts using OpenAI GPT API for CSR training and quality assurance.

## 📊 Project Overview

This project analyzes real-world call center transcripts to identify customer conflicts, classify their types, and assess severity levels. The analysis uses a two-phase approach with GPT models to efficiently process large datasets at minimal cost.

### Key Features
- **Automated sentiment classification** using GPT-3.5-turbo
- **Deep conflict analysis** with GPT-4-turbo
- **Cost-efficient two-phase pipeline** ($1.87 for 1,500 transcripts)
- **Structured output** with full transcripts and metadata
- **Reproducible results** with configurable sampling

## 🎯 Results Summary

From 1,500 analyzed transcripts:
- **Conflicts identified**: 20 (1.3%)
- **Top conflict types**: Unmet expectations (85%), Miscommunication (50%), Service quality issues (40%)
- **Severity distribution**: 40% high (4), 55% medium (3), 5% low (2)

## 🛠️ Setup

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
git clone https://github.com/maitribg/virtual-csr-eda.git
cd virtual-csr-eda2. Install dependencies:
pip install -r requirements.txt3. Configure API key:
# Create .env file in project root
echo "OPENAI_API_KEY=your-api-key-here" > .env## 📁 Dataset

**Source**: [AIxBlock 92k Real-World Call Center Scripts](https://huggingface.co/datasets/AIxBlock/92k-real-world-call-center-scripts-english)

- **Domain**: Medicare/Healthcare inbound calls (dental, veterinary, allergy clinics)
- **Total available**: ~5,000 transcripts
- **Features**: Word-level timestamps, ASR confidence scores, PII-redacted

Place your data in `data/medicare_inbound/medicare_inbound/` (directory excluded from git).

## 🚀 Usage

### Phase 1: Sentiment Filtering

Analyzes all transcripts and identifies unsatisfied customers.

python phase1_sentiment_filter.py**Outputs**:
- `phase1_sentiment_results.csv` - All analyzed transcripts
- `phase1_unsatisfied_customers.csv` - Filtered unsatisfied customers
- Checkpoint files every 25 transcripts

**Cost**: ~$1.50 for 1,500 transcripts (GPT-3.5-turbo)

### Phase 2: Manual Review (Optional)

Interactive tool to browse unsatisfied customers.

python phase2_manual_review.py### Phase 3: Detailed Conflict Analysis

Deep analysis of conflicts with GPT-4.

python phase3_conflict_analysis.py**Outputs**:
- `phase3_conflict_analysis.csv` - Detailed conflict analysis with full transcripts

**Cost**: ~$0.30 for 20 transcripts (GPT-4-turbo)

## 📋 Output Schema

### Phase 1 Output Fields
- `transcript_id`: Unique identifier
- `sentiment`: SATISFIED | NEUTRAL | UNSATISFIED | ANGRY
- `frustration_level`: 1-5 scale
- `reason`: Brief explanation
- `audio_duration_seconds`: Call length
- `asr_confidence`: Transcription quality
- `full_text`: Complete transcript

### Phase 3 Output Fields
- All Phase 1 fields, plus:
- `has_conflict`: Boolean
- `conflict_types`: Classified categories
- `severity`: 1-5 scale (1=minor, 5=severe)
- `trigger_moment`: Quote showing conflict start
- `customer_tone`: calm | frustrated | angry
- `resolution_attempted`: Boolean
- `resolution_successful`: Boolean | null
- `key_phrases`: Notable customer quotes
- `summary`: One sentence description

## 🔧 Configuration

Edit `config.py` to customize:

PHASE1_SAMPLE_SIZE = 1500  # Number of transcripts to analyze
MAX_TRANSCRIPT_LENGTH = 4500  # Character limit for cost savings
PHASE1_MODEL = "gpt-3.5-turbo"  # Cheap model for filtering
PHASE3_MODEL = "gpt-4-turbo-preview"  # Better model for analysis## 📊 Methodology

### Conflict Classification

**Types**:
1. **Pricing Dispute** - Cost/billing disagreements
2. **Service Quality Issue** - Poor service, wait times, transfers
3. **Miscommunication** - Wrong information, confusion
4. **Unmet Expectations** - Service didn't match promise
5. **Other** - Any other frustration

**Severity Scale**:
- **1**: Minor irritation
- **2**: Mild frustration
- **3**: Moderate conflict
- **4**: Serious issue
- **5**: Severe/emotional conflict

### Prompt Engineering

- **Few-shot learning** with 5 examples (3 positive, 2 negative)
- **Structured JSON output** for consistent parsing
- **Low temperature** (0.2-0.3) for reliability
- **Input truncation** (3,500-4,500 chars) for cost efficiency

## 💰 Cost Breakdown

| Phase | Model | Transcripts | Cost |
|-------|-------|-------------|------|
| Phase 1 | GPT-3.5-turbo | 1,500 | $1.57 |
| Phase 3 | GPT-4-turbo | 20 | $0.30 |
| **Total** | | **1,520** | **$1.87** |

## 📈 Analysis Funnel
