#!/bin/bash
set -e  # Exit on error

echo "Installing NLTK..."
pip install --upgrade pip
pip install nltk==3.8.1

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt')"
python -c "import nltk; nltk.download('stopwords')"
python -c "import nltk; nltk.download('wordnet')"
python -c "import nltk; nltk.download('averaged_perceptron_tagger')"

echo "Setup completed successfully!"
