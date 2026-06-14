#!/bin/bash
# Quick start script for EDA Pipeline

echo "🚀 EDA Pipeline - Quick Start"
echo "=============================="
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi

echo "✅ Python found: $(python --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Setup environment
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please add your GROQ_API_KEY to .env file"
    echo ""
else
    echo "✅ .env file exists"
    echo ""
fi

# Run test
echo "🧪 Running test script..."
python test_pipeline.py

echo ""
echo "=============================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Add your GROQ_API_KEY to .env file"
echo "  2. Run: streamlit run src/ui/app.py"
echo "  3. Upload a CSV and start analyzing!"
echo ""
echo "📚 Documentation:"
echo "  - README.md: Overview"
echo "  - SETUP.md: Detailed setup"
echo "  - ARCHITECTURE.md: Technical details"
echo "=============================="
