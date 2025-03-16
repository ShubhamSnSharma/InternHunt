import nltk
import spacy

# Test NLTK
nltk.download('punkt')
print("NLTK is working.")

# Test SpaCy
nlp = spacy.load("en_core_web_sm")
print("SpaCy is working.")
