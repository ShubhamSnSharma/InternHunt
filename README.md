**InternHunt
**
Built by students, for students – powered by smart logic and Python libraries, no AI, just pure efficiency!


Overview

InternHunt is a Python-based internship recommendation platform that uses Jooble and Adzuna APIs to fetch real-time internship listings based on the skills extracted from resumes. The project focuses on text parsing and data matching techniques, not AI or machine learning models. It also recommends upskilling resources using YouTube suggestions and basic logic.



Features


1. User Side
   
✨ Resume Upload: Simple drag-and-drop functionality to upload resumes in PDF format.

✨ Skill Extraction: Uses rule-based and NLP techniques to extract key skills from the uploaded resume.

✨ Internship Recommendations: Fetches internships using Jooble and Adzuna APIs based on the user’s skills.

✨ Career Field Prediction: Predicts the most suitable career domain (e.g., Software Development, Data Analytics) from the extracted skills.

✨ Skill Gap Analysis: Identifies missing or low-frequency skills to improve user profile strength.

✨ Course Suggestions: Recommends relevant courses to upskill and cover the identified gaps.

✨ Resume Scoring: Calculates a score based on resume structure, keyword coverage, and formatting.

✨ Resume Tips: Gives personalized tips to improve resume quality and content.

✨ User Level Classification: Categorizes users into Beginner, Intermediate, or Advanced based on overall resume strength.

✨ YouTube Video Recommendation: Shows a relevant video to help users improve resumes or prepare for interviews.


2. Admin Side (Under Development)

✨ Admin Dashboard: Will provide a dashboard for recruiters to manage and view candidate data.

✨ Candidate Filtering: Planned feature to filter and sort applicants by qualifications.

✨ Resume Insights: Will show statistics on common skills, gaps, and resume quality.

✨ Visual Applicant Tracking: Enables recruiters to track applicants with a visual interface.

✨ Manual Internship Uploads (Planned): Ability for admins to manually post internships.



🛠️ Tech Stack

🔹 Frontend

Streamlit: For building the interactive and responsive user interface.

HTML/CSS (via Streamlit components): Used indirectly for layout and styling.


🔹 Backend
Python: Core language used for processing resumes, logic implementation, and API integration.

pandas, re, docx2txt: For parsing and analyzing resume content.

Requests: To fetch internship data via APIs.


🔹 APIs & Data Sources

Jooble API: For fetching job and internship listings.

Adzuna API: Alternative source for real-time internship opportunities.

YouTube Data (manually embedded): For video recommendations.

(Note: No AI/ML models used in this version.)


🔹 Database (Planned for Admin Side)

MySQL or SQLite (Planned): To store user and resume data in the future.



⚡ Installation & Setup


1️⃣ Clone the Repository

git clone https://github.com/Psycho047/InternHunt.git

cd InternHunt


2️⃣ (Optional) Create a Virtual Environment

python -m venv venv

# Activate the environment

venv\Scripts\activate     # On Windows:

source venv/bin/activate  # On macOS/Linux:


3️⃣ Install the Required Packages

pip install -r requirements.txt


4️⃣ Set Up API Keys

Create a .env file or directly edit the configuration in your Python scripts (e.g., App.py, Courses.py) to include:

Jooble API Key

Adzuna App ID and App Key

Replace your crendentials here:

JOOBLE_API_KEY=your_jooble_key_here

ADZUNA_APP_ID=your_app_id

ADZUNA_APP_KEY=your_app_key


5️⃣ Database Configuration (If Using Admin Panel)

If you plan to connect this with a MySQL database:

Update your database connection credentials inside the file (e.g., db_connection.py or wherever DB is used):


Replace your crendentials here:

mysql.connector.connect(

    host="localhost",
    user="your_username",
    password="your_password",
    database="your_database"
    
)


6️⃣ Run the Application

streamlit run App.py


🚀 How It Works?

1️⃣ Upload Resume → The system extracts skills & key information
2️⃣ Analyze & Match → Matches user skills with relevant internships
3️⃣ Get Recommendations → View internship listings, skill gaps & suggested courses



📸 Screenshots


<img width="452" alt="image" src="https://github.com/user-attachments/assets/60358dbe-7700-4f3f-8dbd-3730544f78e1" />
<img width="452" alt="image" src="https://github.com/user-attachments/assets/2bce4fdb-f422-4d37-b5e5-563f52a6ac3b" />
<img width="452" alt="image" src="https://github.com/user-attachments/assets/9aa11702-2f59-4c9e-a698-1e36a7f8b12a" />
<img width="452" alt="image" src="https://github.com/user-attachments/assets/474508fb-49ad-4920-9788-70ab825fb76d" />
<img width="452" alt="image" src="https://github.com/user-attachments/assets/583c0770-a757-4b1b-af6c-1f6984dbdd9f" />



📈 Future Enhancements

🔹 The system needs improvement in its ranking algorithms to recommend more suitable opportunities to users.
🔹 Add LinkedIn integration for real-time internship fetching
🔹 Our systems need additional data sets for obtaining better skill-gap analytics.
🔹 Implement internship tracking system


📩 Contact

📧 Email: shubhamsharma99918@gmail.com
🌍 GitHub: https://github.com/Psycho047
🔗 LinkedIn: www.linkedin.com/in/shubham-sharma-163a962a9
