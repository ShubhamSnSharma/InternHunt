import streamlit as st
import pandas as pd
import base64,random
import time,datetime
#libraries to parse the resume pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import yt_dlp as youtube_dl #for uploading youtube videos
import plotly.express as px #to create visualisations at the admin session
import nltk
nltk.download('stopwords')
import requests
import json
import time
import datetime

import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Download necessary NLTK resources if not already present
nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
if not os.path.exists(os.path.join(nltk_data_path, "corpora/stopwords")):
    nltk.download("stopwords", download_dir=nltk_data_path)

# Set NLTK data path (helps Streamlit Cloud locate it)
nltk.data.path.append(nltk_data_path)

def fetch_yt_video(link):
    try:
        with youtube_dl.YoutubeDL({}) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get('title', 'Unknown Title')
    except Exception as e:
        return f"Error fetching video: {e}"


def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

import io
from pdfminer.high_level import extract_text
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    if isinstance(file, str):  # ✅ Handling file paths
        with open(file, "rb") as fh:
            for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                page_interpreter.process_page(page)
    else:  # ✅ Handling Streamlit file objects
        with io.BytesIO(file.getbuffer()) as fh:
            for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                page_interpreter.process_page(page)

    text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")

import random
import streamlit as st

def course_recommender(course_list):
    """
    Recommends courses based on the given list.

    Parameters:
    - course_list (list of tuples): Each tuple contains (Course Name, Course Link).

    Returns:
    - List of recommended course names.
    """
    st.subheader("📚 **Courses & Certificates Recommendations** 🎓")

    # Choose the number of recommendations
    no_of_reco = st.slider("Choose Number of Course Recommendations:", 1, 10, 5)

    # Select random courses without modifying the original list
    recommended_courses = random.sample(course_list, min(no_of_reco, len(course_list)))

    # Display courses
    for idx, (c_name, c_link) in enumerate(recommended_courses, start=1):
        st.markdown(f"✅ ({idx}) [{c_name}]({c_link})")
        st.write("---")  # Adds a separator for better readability

    return [c_name for c_name, _ in recommended_courses]  # Returns the list of recommended course names


# Jooble API credentials
# import requests
# import json

# Jooble API Key
# JOOBLE_API_KEY = "4d4c75a1-1761-49c7-a003-71ed93beaf52"

# def fetch_jobs_from_jooble(skills, location=""):
#     """
#     Fetches real-time job listings from Jooble API based on ALL skills.

#     Parameters:
#     - skills (list): List of extracted skills from resume.
#     - location (str): Location for job search (default: Remote jobs).

#     Returns:
#     - List of job postings (max 5) or an error message.
#     """
#     url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    
#     # Combine all skills into a single search query (e.g., "Python, Data Science, AI")
#     keywords = ", ".join(skills)  # ✅ Using all skills together in one search

#     payload = {
#         "keywords": keywords,
#         "location": location,  # Allows users to specify job location
#         "page": 1
#     }

#     headers = {"Content-Type": "application/json"}

#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(payload))

#         if response.status_code == 200:
#             jobs = response.json().get("jobs", [])[:5]  # Get top 5 jobs
#             return jobs if jobs else None
#         else:
#             return None  # No jobs found
    
#     except Exception as e:
#         return None  # Handle API errors

# import requests
# import streamlit as st

# Adzuna API Credentials
ADZUNA_APP_ID = "Your App ID"
ADZUNA_API_KEY = "Your Unique Api Key"
ADZUNA_COUNTRY = "in"  # Change this based on the country you want

# Function to fetch job listings
def get_jobs_from_adzuna(skill, location="India", results=10):
    url = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "results_per_page": results,
        "what": skill,  # Search based on skill
        "where": location,  # User-inputted location
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        jobs = response.json()
        return jobs.get("results", [])  # Return list of job results
    else:
        st.error("⚠️ Failed to fetch jobs. Please check the location format.")
        return []


#CONNECT TO DATABASE

connection = pymysql.connect(host='localhost',user='root',password='Your Sql Password',db='cv')
cursor = connection.cursor()

def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    if not connection.open:
        return

    insert_sql = """
    INSERT INTO user_data (Name, Email_ID, resume_score, Timestamp, Page_no, Predicted_Field, 
                           User_level, Actual_skills, Recommended_skills, Recommended_courses)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """  # ✅ Explicit column names

    rec_values = (name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills, courses)

    try:
        cursor.execute(insert_sql, rec_values)
        connection.commit()
    except pymysql.MySQLError as e:
        st.error(f"Database Insert Error: {e}")


st.set_page_config(
   page_title="InternHunt - Your Internship Finder",
   page_icon='/Users/shubham/Desktop/Project/Logo/InternHunt_logo.png',
)
def run():
    img = Image.open('/Users/shubham/Desktop/Project/Logo/InternHunt_logo.png')
    # img = img.resize((250,250))
    st.image(img)
    st.title("AI Resume Analyser")
    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    st.sidebar.markdown(
    """
    <p style='text-align: center; font-size: 12px;'>
        © Developed by 
        <a href='https://www.linkedin.com/in/shubham-sharma-163a962a9' target='_blank'>Shubham</a>, 
        <a href='https://www.linkedin.com/in/abhinav-ghangas-5a3b8128a' target='_blank'>Abhinav</a>, 
        <a href='https://www.linkedin.com/in/pragya-9974b1298' target='_blank'>Pragya</a>
    </p>
    """,
    unsafe_allow_html=True
)

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(500) NOT NULL,
                     Email_ID VARCHAR(500) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field BLOB NOT NULL,
                     User_level BLOB NOT NULL,
                     Actual_skills BLOB NOT NULL,
                     Recommended_skills BLOB NOT NULL,
                     Recommended_courses BLOB NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if choice == 'User':
        st.markdown('''<h5 style='text-align: left; color: #008000;'> Upload your resume, and get smart recommendations</h5>''',
                    unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(4)
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                resume_text = pdf_reader(save_image_path)
                st.header("📄 **Resume Analysis**")
                st.success("Hello " + resume_data['name'])

                st.subheader("📌 **Your Basic Info**")
            try:
                st.text(f"👤 Name: {resume_data['name']}")
                st.text(f"📧 Email: {resume_data['email']}")
                st.text(f"📞 Contact: {resume_data['mobile_number']}")
                st.text(f"📑 Resume Pages: {resume_data['no_of_pages']}")
            except:
                pass
            
            cand_level = ''
            if resume_data['no_of_pages'] == 1:
                cand_level = "Fresher"
                st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
            elif resume_data['no_of_pages'] == 2:
                cand_level = "Intermediate"
                st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
            elif resume_data['no_of_pages'] >=3:
                cand_level = "Experienced"
                st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''',unsafe_allow_html=True)

            from streamlit_tags import st_tags

            # Extracted skills from resume
            extracted_skills = resume_data.get('skills', [])

            # Show extracted skills in the same tag format as recommended skills
            st.subheader("🛠 **Extracted Skills**")

            # Display extracted skills as red tags
            st_tags(label='### Extracted Skills:',
                    text='Skills extracted from your resume',
                    value=extracted_skills, key='extracted_skills_display')
            
            # Let user enter job location (default: Remote)
            # location = st.text_input("🌍 Enter Job Location (Leave blank for remote jobs)", "")

            # 🔹 Fetch jobs using all skills together
            # st.header("🔍 **Job Recommendations Based on Your Skills**")

            # jobs = fetch_jobs_from_jooble(extracted_skills, location)

            # if jobs:
            #     for job in jobs:
            #         st.markdown(f"✅ **{job['title']}** at **{job['company']}**")
            #         st.text(f"📍 Location: {job['location']}")
            #         st.markdown(f"[🔗 Apply Here]({job['link']})")
            #         st.write("---")  # Separator for readability
            # else:
            #     st.warning(f"⚠ No jobs found for `{', '.join(extracted_skills)}` in `{location or 'Remote'}`.")
            
            # Get user input
            location_input = st.text_input("🌍 Enter Job Location (Leave blank for remote jobs)", "")

            # Get the most relevant skill
            top_skill = resume_data.get('skills', ["Developer"])[0]

            # Fetch jobs using the specified location
            jobs = get_jobs_from_adzuna(top_skill, location=location_input if location_input else "India", results=5)

            # Display job recommendations
            st.subheader("🎯 Job Recommendations for You")
            if jobs:
                for job in jobs:
                    job_title = job.get("title", "No Title")
                    company_name = job.get("company", {}).get("display_name", "Unknown Company")  # Get company name
                    job_location = job.get("location", {}).get("display_name", "Location Not Available")
                    salary_min = job.get("salary_min", "N/A")
                    salary_max = job.get("salary_max", "N/A")
                    job_link = job.get("redirect_url", "#")

                    # Display job details
                    st.markdown(f"**🔹 {job_title}**")
                    st.write(f"🏢 Company: {company_name}")  # Display company name
                    st.write(f"📍 Location: {job_location}")
                    st.write(f"💰 Salary: {salary_min} - {salary_max}")
                    st.write(f"🔗 [View Job]({job_link})")
                    st.write("---")
            else:
                st.info("No jobs found for the specified location. Try a different city or country!")


            from streamlit_tags import st_tags
            
            # Extracted skills from resume
            extracted_skills = resume_data.get('skills', [])

            # Initialize recommended skills and career field
            reco_field = "General"  # Default fallback value
            recommended_skills = []

            # Define skill categories
            ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit']
            web_keyword = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                        'javascript', 'angular js', 'c#', 'flask']
            android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
            ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
            uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                            'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                            'illustrator', 'adobe after effects', 'after effects', 'adobe premiere pro',
                            'premiere pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                            'user research', 'user experience']

            # Convert to lowercase for easier matching
            extracted_skills = [skill.lower() for skill in extracted_skills]

            # Matching
            if any(skill in ds_keyword for skill in extracted_skills):
                reco_field = "Data Science"
                recommended_skills = ['Flask', 'Numpy', 'Pandas', 'Deep Learning', 'AWS', 'Azure', 'Streamlit']
            elif any(skill in web_keyword for skill in extracted_skills):
                reco_field = "Web Development"
                recommended_skills = ['React', 'Django', 'HTML', 'CSS', 'Javascript', 'Node.js']
            elif any(skill in android_keyword for skill in extracted_skills):
                reco_field = "Android Development"
                recommended_skills = ['Kotlin', 'Java', 'Flutter', 'XML']
            elif any(skill in ios_keyword for skill in extracted_skills):
                reco_field = "iOS Development"
                recommended_skills = ['Swift', 'Xcode', 'Cocoa']
            elif any(skill in uiux_keyword for skill in extracted_skills):
                reco_field = "UI/UX Design"
                recommended_skills = ['Figma', 'Adobe XD', 'User Research', 'Prototyping']


            # Initialize recommended fields and skills
            recommended_skills = []
            recommended_fields = set()
            rec_course = None

            
            # Skill category mapping
            skill_matches = []
            for skill in resume_data['skills']:
                skill_lower = skill.lower()

                # Data Science Recommendation
                if skill_lower in ds_keyword:
                    skill_matches.append(f"{skill_lower} (Data Science)")
                    recommended_fields.add('Data Science')
                    recommended_skills.extend(['Data Visualization', 'Predictive Analysis', 'Statistical Modeling', 'Data Mining',
                                            'Clustering & Classification', 'Data Analytics', 'Quantitative Analysis', 'Web Scraping',
                                            'ML Algorithms', 'Keras', 'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                            'Streamlit'])

                # Web Development Recommendation
                elif skill_lower in web_keyword:
                    skill_matches.append(f"{skill_lower} (Web Development)")
                    recommended_fields.add('Web Development')
                    recommended_skills.extend(['React', 'Django', 'Node JS', 'React JS', 'PHP', 'Laravel', 'Magento', 'WordPress',
                                            'JavaScript', 'Angular JS', 'C#', 'Flask', 'SDK'])

                # Android Development
                elif skill_lower in android_keyword:
                    skill_matches.append(f"{skill_lower} (Android Development)")
                    recommended_fields.add('Android Development')
                    recommended_skills.extend(['Android', 'Android Development', 'Flutter', 'Kotlin', 'XML', 'Java', 'Kivy', 'GIT',
                                            'SDK', 'SQLite'])

                # iOS Development
                elif skill_lower in ios_keyword:
                    skill_matches.append(f"{skill_lower} (iOS Development)")
                    recommended_fields.add('iOS Development')
                    recommended_skills.extend(['iOS', 'iOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode', 'Objective-C',
                                            'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation', 'Auto-Layout'])

                # UI/UX Recommendation
                elif skill_lower in uiux_keyword:
                    skill_matches.append(f"{skill_lower} (UI-UX)")
                    recommended_fields.add('UI/UX Design')
                    recommended_skills.extend(['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq', 'Prototyping',
                                            'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing', 'Illustrator', 'After Effects',
                                            'Premiere Pro', 'InDesign', 'Wireframe', 'Solid', 'Grasp', 'User Research'])

            # If no specific field is matched
            if not recommended_fields:
                recommended_fields.add('General')
                st.info("We couldn't determine your specific field based on your skills. Here are some general recommendations.")
                has_programming = any('programming' in skill.lower() or 'html' in skill.lower() or 'c++' in skill.lower()
                                    for skill in resume_data['skills'])
                if has_programming:
                    recommended_fields.add('Web Development')
                    recommended_skills.extend(['JavaScript', 'React', 'Node.js', 'Python', 'Django', 'Database Management',
                                            'API Development', 'Git', 'DevOps', 'Testing'])
                else:
                    # General skills that benefit any role
                    recommended_skills.extend(['Communication', 'Problem Solving', 'Critical Thinking', 'Time Management',
                                            'Project Management', 'Microsoft Office', 'Data Analysis', 'Leadership',
                                            'Teamwork', 'Attention to Detail'])

            # Display Recommended Fields
            st.subheader("Possible Career Fields Based on Your Skills")
            st.write(", ".join(recommended_fields))

            # Display Recommended Skills
            recommended_keywords = st_tags(label='### Recommended skills for you.',
                                        text='Recommended skills generated from System',
                                        value=list(set(recommended_skills)), key='skills_reco')


            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 the chances of getting a Job</h4>''',
                        unsafe_allow_html=True)


                
                ## Insert into table
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = str(cur_date+'_'+cur_time)

                ### Resume writing recommendation
            st.subheader("**Resume Tips & Ideas💡**")
            resume_score = 0
            if 'Objective' in resume_text:
                resume_score = resume_score+20
                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',unsafe_allow_html=True)
            else:
                st.markdown('''<h5 style='text-align: left; color: #FF0000;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

            if 'Declaration'  in resume_text:
                resume_score = resume_score + 20
                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Declaration</h5>''', unsafe_allow_html=True)
            else:
                st.markdown('''<h5 style='text-align: left; color: #FF0000;'>[-] Please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',unsafe_allow_html=True)

            if 'Hobbies' or 'Interests'in resume_text:
                resume_score = resume_score + 20
                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
            else:
                st.markdown('''<h5 style='text-align: left; color: #FF0000;'>[-] Please add Hobbies. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

            if 'Achievements' in resume_text:
                resume_score = resume_score + 20
                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
            else:
                st.markdown('''<h5 style='text-align: left; color: #FF0000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

            if 'Projects' in resume_text:
                resume_score = resume_score + 20
                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
            else:
                st.markdown('''<h5 style='text-align: left; color: #FF0000;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

            st.subheader("**Resume Score📝**")
            st.markdown(
                """
                <style>
                .stProgress > div > div > div > div {
                    background-color: #d73b5c;
                    }
                    </style>""",
                    unsafe_allow_html=True,
                    )
            my_bar = st.progress(0)
            score = 0
            for percent_complete in range(resume_score):
                score +=1
                time.sleep(0.1)
                my_bar.progress(percent_complete + 1)
            st.success('** Your Resume Writing Score: ' + str(score)+'**')
            st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")
            st.balloons()

            insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                        str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                        str(recommended_skills), str(rec_course))


            ## Resume writing video
            st.header("**Bonus Video for Resume Writing Tips💡**")
            resume_vid = random.choice(resume_videos)
            res_vid_title = fetch_yt_video(resume_vid)
            st.subheader("✅ **"+res_vid_title+"**")
            st.video(resume_vid)



            ## Interview Preparation Video
            st.header("**Bonus Video for Interview Tips💡**")
            interview_vid = random.choice(interview_videos)
            int_vid_title = fetch_yt_video(interview_vid)
            st.subheader("✅ **" + int_vid_title + "**")
            st.video(interview_vid)

            connection.commit()
        else:
            st.error('Welcome!!!')
    else:
        import pandas as pd
        import plotly.express as px

        # Utility function to generate a download link
        def get_table_download_link(df, filename, link_text):
            import base64
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'

        # --- Admin Side ---
        st.success('Welcome to Admin Side')

        # Multiple admin credentials stored in a dictionary
        admins = {
            'admin1': 'password1',
            'admin2': 'password2',
            'admin3': 'password3'
        }

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            if ad_user in admins and ad_password == admins[ad_user]:
                st.success(f"Welcome Mr./Ms. {ad_user}")

                # ✅ Display Data from DB
                cursor.execute('''SELECT * FROM user_data''')
                data = cursor.fetchall()

                df = pd.DataFrame(data, columns=[
                    'ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                    'Predicted_Field', 'User_level', 'Actual Skills', 'Recommended Skills',
                    'Recommended Course'
                ])
                st.header("**User's Data**")
                st.dataframe(df)

                # ✅ Download CSV Report
                st.markdown(get_table_download_link(df, 'User_Data.csv', '📥 Download Report'), unsafe_allow_html=True)

                # ✅ Read data again for charts
                query = 'SELECT * FROM user_data;'
                plot_data = pd.read_sql(query, connection)

                # Decode bytes to string if needed
                for col in ['Predicted_Field', 'User_level']:
                    if plot_data[col].dtype == object:
                        plot_data[col] = plot_data[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)

                # ✅ Pie Chart: Predicted Field
                st.subheader("📊 Pie-Chart for Predicted Field Recommendation")
                field_counts = plot_data['Predicted_Field'].value_counts().reset_index()
                field_counts.columns = ['Predicted_Field', 'Count']
                fig1 = px.pie(
                    field_counts,
                    values='Count',
                    names='Predicted_Field',
                    title='Predicted Field according to the Skills'
                )
                st.plotly_chart(fig1)

                # ✅ Pie Chart: User Experience Level
                st.subheader("📊 Pie-Chart for User's Experienced Level")
                level_counts = plot_data['User_level'].value_counts().reset_index()
                level_counts.columns = ['User_level', 'Count']
                fig2 = px.pie(
                    level_counts,
                    values='Count',
                    names='User_level',
                    title="User's👨‍💻 Experienced Level"
                )
                st.plotly_chart(fig2)

            else:
                st.error("❌ Wrong ID & Password Provided")
run()
