#!/bin/bash
set -e  # Exit on error

# Set NLTK data directory
export NLTK_DATA=/usr/local/share/nltk_data

# Create NLTK data directory if it doesn't exist
mkdir -p $NLTK_DATA

# Print environment information
echo "=== Environment Information ==="
python --version
pip --version
echo "NLTK_DATA: $NLTK_DATA"

# Install requirements
echo "=== Installing requirements ==="
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Install NLTK data
echo "=== Installing NLTK data ==="
python -m nltk.downloader -d $NLTK_DATA punkt
python -m nltk.downloader -d $NLTK_DATA stopwords
python -m nltk.downloader -d $NLTK_DATA wordnet
python -m nltk.downloader -d $NLTK_DATA averaged_perceptron_tagger

# Verify installations
echo "=== Verifying installations ==="
python -c "import nltk; print(f'NLTK version: {nltk.__version__}')"
python -c "import nltk; nltk.data.path.append('/usr/local/share/nltk_data/'); print(f'NLTK data paths: {nltk.data.path}')"
python -c "import spacy; print(f'spaCy version: {spacy.__version__}')"

# Create a test script to verify NLTK data
echo "=== Creating test script ==="
cat > test_nltk.py << 'EOL'
import nltk
nltk.data.path.append('/usr/local/share/nltk_data/')
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    print("✅ All NLTK data files found!")
except LookupError as e:
    print(f"❌ Missing NLTK data: {e}")
EOL

# Run the test script
python test_nltk.py

echo "✅ Setup completed successfully!"
