from setuptools import setup, find_packages

setup(
    name="internhunt",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'nltk>=3.8.1',
        'numpy>=1.26.0',
        'pandas>=2.2.0',
        'scikit-learn>=1.4.0',
        'scipy>=1.11.0',
        'torch>=2.3.0',
        'torchvision>=0.18.0',
        'torchaudio>=2.1.0',
        'sentence-transformers>=2.5.1',
        'transformers>=4.36.2',
        'spacy>=3.7.4',
        'streamlit>=1.32.0',
        'python-dotenv>=1.0.0',
        'PyPDF2>=3.0.1',
        'python-docx>=1.1.0',
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.2',
        'lxml>=5.1.0',
    ],
    python_requires='>=3.10.0',
)
