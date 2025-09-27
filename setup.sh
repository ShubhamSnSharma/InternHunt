#!/bin/bash
set -e  # Exit on error

# Print environment information
echo "=== Environment Information ==="
python --version
pip --version
which python

# Upgrade pip
echo "=== Upgrading pip ==="
python -m pip install --upgrade pip

# Install requirements
echo "=== Installing requirements ==="
pip install -r requirements.txt

# Download NLTK data
echo "=== Downloading NLTK data ==="
python -c "import nltk; nltk.download('punkt')"
python -c "import nltk; nltk.download('stopwords')"
python -c "import nltk; nltk.download('wordnet')"
python -c "import nltk; nltk.download('averaged_perceptron_tagger')"

# Install spaCy model
echo "=== Installing spaCy model ==="
python -m spacy download en_core_web_sm

# Verify installations
echo "=== Verifying installations ==="
python -c "import nltk; print(f'NLTK version: {nltk.__version__}')"
python -c "import spacy; print(f'spaCy version: {spacy.__version__}')"
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"

echo "✅ Setup completed successfully!"
