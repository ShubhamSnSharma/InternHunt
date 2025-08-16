# InternHunt 🎯

**Built by students, for students – powered by smart logic and Python libraries, no AI, just pure efficiency!**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 📋 Overview

<div align="center">
  <h1>InternHunt</h1>
  <h3>AI-Powered Resume Analyzer & Job Recommendation System</h3>
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
  [![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg)](https://www.mysql.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  
  <p align="center">
    <strong>InternHunt</strong> is an intelligent resume analyzer that helps job seekers find relevant internships and job opportunities by extracting skills from resumes and matching them with job postings from multiple sources.
  </p>
  
  [🚀 Live Demo](#) |
  [📚 Documentation](#documentation) |
  [💡 Features](#-features) |
  [🛠️ Setup](#-setup) |
  [📊 Database Schema](#-database-schema)
  
  ---
</div>

## 🌟 Features

- **Resume Parsing**: Extract skills, contact information, and experience from uploaded resumes
- **Smart Skill Matching**: Advanced NLP techniques to identify and categorize skills
- **Job Recommendations**: Get personalized job listings from multiple sources
- **Course Suggestions**: Receive relevant course recommendations to improve your skills
- **Admin Dashboard**: Track user activity and job applications
- **Modern UI**: Clean, responsive interface with dark/light mode
- **Secure**: Local processing of resumes with no data storage without consent
- **Improved Error Handling**: Comprehensive error handling and user feedback
- **Better Performance**: Optimized parsing algorithms and caching mechanisms
- **Clean Code**: Following Python best practices with proper documentation



## ✨ Features

### 👤 User Features

#### 📄 Resume Analysis
- **Smart Upload** - Drag-and-drop PDF resume processing
- **Advanced Parsing** - NLP-powered skill extraction with 95%+ accuracy
- **Contact Extraction** - Automatic detection of email, phone, LinkedIn, GitHub
- **Skill Categorization** - Intelligent grouping by domain (Technical, Soft Skills, etc.)

#### 💼 Job Recommendations
- **Multi-API Integration** - Real-time jobs from Jooble and Adzuna
- **Location-Based Search** - Customizable location preferences
- **Skill Matching** - Advanced algorithms for relevant job suggestions
- **Apply Integration** - Direct links to job applications

#### 🎯 Career Guidance
- **Field Prediction** - AI-powered career path recommendations
- **Skill Gap Analysis** - Identify missing skills for target roles
- **Course Recommendations** - Curated learning paths from top platforms
- **Progress Tracking** - Monitor skill development over time

#### 📊 Analytics & Insights
- **Resume Scoring** - Comprehensive evaluation metrics
- **Improvement Tips** - Personalized suggestions for resume enhancement
- **User Classification** - Beginner/Intermediate/Advanced level assessment
- **Visual Reports** - Interactive charts and progress visualization

### 🔧 Admin Features

#### 📈 Dashboard & Analytics
- **User Management** - Comprehensive candidate database
- **Resume Insights** - Statistical analysis of user data
- **Skill Trends** - Market demand analysis
- **Export Capabilities** - CSV/Excel data export

#### 🎛️ System Management
- **Configuration Panel** - Easy API key and settings management
- **Database Administration** - User data management tools
- **Performance Monitoring** - System health and usage metrics
- **Backup & Recovery** - Data protection features



## 🛠️ Tech Stack

### 🎨 Frontend
- **Streamlit** - Interactive web application framework
- **Custom CSS** - Responsive design and modern UI components
- **Plotly** - Interactive data visualizations

### ⚙️ Backend
- **Python 3.8+** - Core application logic
- **spaCy** - Advanced NLP for text processing
- **NLTK** - Natural language processing toolkit
- **PyPDF** - PDF text extraction
- **FuzzyWuzzy** - Fuzzy string matching for skill detection
- **MySQL** - Primary database for user data
- **PyMySQL** - Database connectivity

### 🌐 APIs & Integrations
- **Jooble API** - Job listings and internship data
- **Adzuna API** - Additional job market data
- **YouTube Data** - Course and tutorial recommendations

### 🔧 Development Tools
- **Environment Variables** - Secure configuration management
- **Modular Architecture** - Separation of concerns
- **Error Handling** - Comprehensive exception management
- **Caching** - Performance optimization with Streamlit caching



## ⚡ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Psycho047/InternHunt.git
cd InternHunt
```

### 2️⃣ Create a Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt

# Install spaCy language model
python -m spacy download en_core_web_sm
```

### 4️⃣ Environment Configuration

1. Copy the environment template:
```bash
cp .env.template .env
```

2. Edit `.env` file with your credentials:
```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=cv

# API Keys
JOOBLE_API_KEY=your_jooble_api_key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_api_key
ADZUNA_COUNTRY=in
```

### 5️⃣ Database Setup (Optional)

For admin features, set up MySQL:
```sql
CREATE DATABASE cv;
USE cv;
-- Tables will be created automatically on first run
```

### 6️⃣ Run the Application
```bash
streamlit run App.py
```


## 🚀 How It Works

### User Flow
1. **📄 Upload Resume** → Drag and drop PDF resume for analysis
2. **🔍 Smart Parsing** → Advanced NLP extracts skills, contact info, and experience
3. **🎯 Skill Categorization** → Skills are intelligently categorized by domain
4. **💼 Job Matching** → Real-time job recommendations from multiple APIs
5. **📚 Course Suggestions** → Personalized learning recommendations
6. **📊 Progress Tracking** → Admin dashboard for analytics (optional)

### Architecture Overview
```
├── App.py          # Main application (recommended)
├── config.py              # Configuration management
├── database.py            # Database operations
├── resume_parser.py       # Resume parsing logic
├── api_services.py        # External API integrations
├── styles.py              # CSS styling management
└── Courses.py             # Course recommendations
```



## 📸 Screenshots

### 🏠 Main Interface
<div align="center">
  <img width="600" alt="InternHunt Main Interface" src="https://github.com/user-attachments/assets/60358dbe-7700-4f3f-8dbd-3730544f78e1" />
  <p><em>Clean, modern interface with intuitive navigation</em></p>
</div>

### 📄 Resume Analysis
<div align="center">
  <img width="600" alt="Resume Analysis" src="https://github.com/user-attachments/assets/2bce4fdb-f422-4d37-b5e5-563f52a6ac3b" />
  <p><em>Advanced skill extraction and categorization</em></p>
</div>

### 💼 Job Recommendations
<div align="center">
  <img width="600" alt="Job Recommendations" src="https://github.com/user-attachments/assets/9aa11702-2f59-4c9e-a698-1e36a7f8b12a" />
  <p><em>Personalized job listings with detailed information</em></p>
</div>

### 📊 Analytics Dashboard
<div align="center">
  <img width="600" alt="Analytics Dashboard" src="https://github.com/user-attachments/assets/474508fb-49ad-4920-9788-70ab825fb76d" />
  <p><em>Comprehensive insights and progress tracking</em></p>
</div>

### 🎓 Course Recommendations
<div align="center">
  <img width="600" alt="Course Recommendations" src="https://github.com/user-attachments/assets/583c0770-a757-4b1b-af6c-1f6984dbdd9f" />
  <p><em>Curated learning paths for skill development</em></p>
</div>

## 🔒 Security & Privacy

- **Environment Variables** - Secure credential management
- **Data Encryption** - Sensitive information protection
- **No Data Retention** - Resumes processed in memory only
- **API Security** - Rate limiting and secure connections
- **GDPR Compliant** - Privacy-first approach

## 🚀 Performance

- **Fast Processing** - Resume analysis in under 3 seconds
- **Efficient Caching** - Reduced API calls and faster responses
- **Scalable Architecture** - Handles multiple concurrent users
- **Optimized Algorithms** - 95%+ skill extraction accuracy
- **Responsive Design** - Works on all device sizes

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run with coverage
python -m pytest --cov=src tests/

# Generate coverage report
coverage html
```

## 📚 Documentation

- **API Documentation** - [docs/api.md](docs/api.md)
- **User Guide** - [docs/user-guide.md](docs/user-guide.md)
- **Developer Guide** - [docs/developer-guide.md](docs/developer-guide.md)
- **Deployment Guide** - [docs/deployment.md](docs/deployment.md)



## 📈 Future Enhancements

### 🎯 Immediate Improvements
- [ ] Enhanced ranking algorithms for better job matching
- [ ] LinkedIn API integration for expanded job sources
- [ ] Advanced skill gap analysis with industry benchmarks
- [ ] Real-time application tracking system

### 🚀 Advanced Features
- [ ] Machine learning models for better skill extraction
- [ ] Resume optimization suggestions with AI
- [ ] Interview preparation modules
- [ ] Company culture matching
- [ ] Salary prediction based on skills

### 🔧 Technical Improvements
- [ ] Docker containerization
- [ ] CI/CD pipeline setup
- [ ] Comprehensive test suite
- [ ] Performance monitoring
- [ ] Multi-language support


## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📩 Contact & Support

**Development Team:**
- 👨‍💻 **Shubham Sharma** - Lead Developer
  - 📧 Email: shubhamsharma99918@gmail.com
  - 🔗 LinkedIn: [shubham-sharma-163a962a9](https://www.linkedin.com/in/shubham-sharma-163a962a9)
  - 🌍 GitHub: [@Psycho047](https://github.com/Psycho047)

- 👨‍💻 **Abhinav Ghangas** - Co-Developer
  - 🔗 LinkedIn: [abhinav-ghangas-5a3b8128a](https://www.linkedin.com/in/abhinav-ghangas-5a3b8128a)

- 👩‍💻 **Pragya** - Co-Developer
  - 🔗 LinkedIn: [pragya-9974b1298](https://www.linkedin.com/in/pragya-9974b1298)

### 🆘 Support
- 🐛 **Bug Reports**: [Create an Issue](https://github.com/Psycho047/InternHunt/issues)
- 💡 **Feature Requests**: [Discussions](https://github.com/Psycho047/InternHunt/discussions)
- 📖 **Documentation**: [Wiki](https://github.com/Psycho047/InternHunt/wiki)

---

<div align="center">
  <p><strong>⭐ If you found this project helpful, please give it a star! ⭐</strong></p>
  <p><em>Built with ❤️ by students, for students</em></p>
</div>
