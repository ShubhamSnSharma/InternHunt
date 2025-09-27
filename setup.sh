#!/bin/bash
set -e  # Exit on error

# Ensure we're using the correct Python and pip
echo "Using Python: $(which python3)"
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"

# Install NLTK and its data
echo "Installing NLTK and dependencies..."
pip3 install --upgrade pip
pip3 install nltk==3.8.1

# Download NLTK data
echo "Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt', quiet=True)"
python3 -c "import nltk; nltk.download('stopwords', quiet=True)"
python3 -c "import nltk; nltk.download('wordnet', quiet=True)"
python3 -c "import nltk; nltk.download('averaged_perceptron_tagger', quiet=True)"

# Verify installation
echo "Verifying NLTK installation..."
python3 -c "import nltk; print('NLTK version:', nltk.__version__)"
python3 -c "import nltk; print('NLTK data path:', nltk.data.path)"

echo "✅ Setup completed successfully!"
