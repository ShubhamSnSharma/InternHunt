# """
# Landing Page Module for InternHunt
# Professional landing page with features, benefits, and CTA
# """
# import streamlit as st
# from styles import StyleManager

# def render_landing_page():
#     """Render the professional landing page"""
    
#     # Hero Section
#     st.markdown(f"""
#         <div style="
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             padding: 80px 40px;
#             border-radius: 20px;
#             margin-bottom: 60px;
#             text-align: center;
#             box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
#         ">
#             <div style="
#                 font-size: 4rem;
#                 margin-bottom: 24px;
#                 animation: bounce 2s infinite;
#             ">🎯</div>
#             <h1 style="
#                 font-size: 3.5rem;
#                 font-weight: 800;
#                 color: white;
#                 margin-bottom: 24px;
#                 text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
#             ">Welcome to InternHunt</h1>
#             <p style="
#                 font-size: 1.5rem;
#                 color: rgba(255, 255, 255, 0.95);
#                 max-width: 800px;
#                 margin: 0 auto 40px;
#                 line-height: 1.6;
#             ">
#                 Your AI-Powered Career Companion for Resume Analysis, 
#                 Job Matching, and Career Growth
#             </p>
#             <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
#                 <a href="#get-started" style="
#                     background: white;
#                     color: #667eea;
#                     padding: 16px 40px;
#                     border-radius: 50px;
#                     text-decoration: none;
#                     font-weight: 700;
#                     font-size: 1.1rem;
#                     box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
#                     transition: transform 0.2s;
#                 " onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
#                     Get Started Free →
#                 </a>
#                 <a href="#how-it-works" style="
#                     background: rgba(255, 255, 255, 0.2);
#                     color: white;
#                     padding: 16px 40px;
#                     border-radius: 50px;
#                     text-decoration: none;
#                     font-weight: 700;
#                     font-size: 1.1rem;
#                     border: 2px solid white;
#                     transition: background 0.2s;
#                 " onmouseover="this.style.background='rgba(255, 255, 255, 0.3)'" onmouseout="this.style.background='rgba(255, 255, 255, 0.2)'">
#                     Learn More
#                 </a>
#             </div>
#         </div>
        
#         <style>
#         @keyframes bounce {{
#             0%, 20%, 50%, 80%, 100% {{
#                 transform: translateY(0);
#             }}
#             40% {{
#                 transform: translateY(-20px);
#             }}
#             60% {{
#                 transform: translateY(-10px);
#             }}
#         }}
#         </style>
#     """, unsafe_allow_html=True)
    
#     # Stats Section
#     st.markdown("""
#         <div style="
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
#             gap: 30px;
#             margin: 60px 0;
#         ">
#             <div style="
#                 text-align: center;
#                 padding: 30px;
#                 background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
#                 border-radius: 16px;
#                 box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
#             ">
#                 <div style="font-size: 3rem; font-weight: 800; color: white;">10K+</div>
#                 <div style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.9); font-weight: 600;">Resumes Analyzed</div>
#             </div>
#             <div style="
#                 text-align: center;
#                 padding: 30px;
#                 background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
#                 border-radius: 16px;
#                 box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
#             ">
#                 <div style="font-size: 3rem; font-weight: 800; color: white;">95%</div>
#                 <div style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.9); font-weight: 600;">Accuracy Rate</div>
#             </div>
#             <div style="
#                 text-align: center;
#                 padding: 30px;
#                 background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
#                 border-radius: 16px;
#                 box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
#             ">
#                 <div style="font-size: 3rem; font-weight: 800; color: white;">5K+</div>
#                 <div style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.9); font-weight: 600;">Jobs Posted Daily</div>
#             </div>
#             <div style="
#                 text-align: center;
#                 padding: 30px;
#                 background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
#                 border-radius: 16px;
#                 box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
#             ">
#                 <div style="font-size: 3rem; font-weight: 800; color: white;">24/7</div>
#                 <div style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.9); font-weight: 600;">AI Assistant</div>
#             </div>
#         </div>
#     """, unsafe_allow_html=True)
    
#     # Features Section
#     st.markdown("""
#         <div id="how-it-works" style="margin: 80px 0 60px;">
#             <h2 style="
#                 text-align: center;
#                 font-size: 2.5rem;
#                 font-weight: 800;
#                 margin-bottom: 20px;
#                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#                 -webkit-background-clip: text;
#                 -webkit-text-fill-color: transparent;
#             ">✨ Powerful Features</h2>
#             <p style="
#                 text-align: center;
#                 font-size: 1.2rem;
#                 color: #666;
#                 max-width: 600px;
#                 margin: 0 auto 60px;
#             ">Everything you need to accelerate your career journey</p>
#         </div>
#     """, unsafe_allow_html=True)
    
#     # Feature Cards
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown("""
#             <div style="
#                 background: white;
#                 padding: 40px 30px;
#                 border-radius: 20px;
#                 box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
#                 text-align: center;
#                 transition: transform 0.3s;
#                 height: 100%;
#             " onmouseover="this.style.transform='translateY(-10px)'" onmouseout="this.style.transform='translateY(0)'">
#                 <div style="
#                     width: 80px;
#                     height: 80px;
#                     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#                     border-radius: 50%;
#                     display: flex;
#                     align-items: center;
#                     justify-content: center;
#                     margin: 0 auto 24px;
#                     font-size: 2.5rem;
#                 ">📊</div>
#                 <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 16px; color: #333;">Smart Resume Analysis</h3>
#                 <p style="color: #666; line-height: 1.6; font-size: 1rem;">
#                     Advanced AI algorithms analyze your resume, extract skills, 
#                     and provide detailed scoring with actionable improvements.
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown("""
#             <div style="
#                 background: white;
#                 padding: 40px 30px;
#                 border-radius: 20px;
#                 box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
#                 text-align: center;
#                 transition: transform 0.3s;
#                 height: 100%;
#             " onmouseover="this.style.transform='translateY(-10px)'" onmouseout="this.style.transform='translateY(0)'">
#                 <div style="
#                     width: 80px;
#                     height: 80px;
#                     background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
#                     border-radius: 50%;
#                     display: flex;
#                     align-items: center;
#                     justify-content: center;
#                     margin: 0 auto 24px;
#                     font-size: 2.5rem;
#                 ">🎯</div>
#                 <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 16px; color: #333;">Personalized Job Matching</h3>
#                 <p style="color: #666; line-height: 1.6; font-size: 1rem;">
#                     Get real-time job recommendations from multiple sources 
#                     perfectly matched to your skills and experience level.
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown("""
#             <div style="
#                 background: white;
#                 padding: 40px 30px;
#                 border-radius: 20px;
#                 box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
#                 text-align: center;
#                 transition: transform 0.3s;
#                 height: 100%;
#             " onmouseover="this.style.transform='translateY(-10px)'" onmouseout="this.style.transform='translateY(0)'">
#                 <div style="
#                     width: 80px;
#                     height: 80px;
#                     background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
#                     border-radius: 50%;
#                     display: flex;
#                     align-items: center;
#                     justify-content: center;
#                     margin: 0 auto 24px;
#                     font-size: 2.5rem;
#                 ">💬</div>
#                 <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 16px; color: #333;">AI Career Assistant</h3>
#                 <p style="color: #666; line-height: 1.6; font-size: 1rem;">
#                     Chat with our intelligent assistant for personalized career 
#                     advice, resume tips, and interview preparation guidance.
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     # Additional Features
#     st.markdown("<br><br>", unsafe_allow_html=True)
#     col4, col5, col6 = st.columns(3)
    
#     with col4:
#         st.markdown("""
#             <div style="
#                 background: white;
#                 padding: 40px 30px;
#                 border-radius: 20px;
#                 box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
#                 text-align: center;
#                 transition: transform 0.3s;
#                 height: 100%;
#             " onmouseover="this.style.transform='translateY(-10px)'" onmouseout="this.style.transform='translateY(0)'">
#                 <div style="
#                     width: 80px;
#                     height: 80px;
#                     background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
#                     border-radius: 50%;
#                     display: flex;
#                     align-items: center;
#                     justify-content: center;
#                     margin: 0 auto 24px;
#                     font-size: 2.5rem;
#                 ">🛠️</div>
#                 <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 16px; color: #333;">Skills Enhancement</h3>
#                 <p style="color: #666; line-height: 1.6; font-size: 1rem;">
#                     Discover skill gaps and get curated course recommendations 
#                     to boost your profile and career prospects.
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     with col5:
#         st.markdown("""
#             <div style="
#                 background: white;
#                 padding: 40px 30px;
#                 border-radius: 20px;
#                 box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
#                 text-align: center;
#                 transition: transform 0.3s;
#                 height: 100%;
#             " onmouseover="this.style.transform='translateY(-10px)'" onmouseout="this.style.transform='translateY(0)'">
#                 <div style="
#                     width: 80px;
#                     height: 80px;
#                     background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
#                     border-radius: 50%;
#                     display: flex;
#                     align-items: center;
#                     justify-content: center;
#                     margin: 0 auto 24px;
#                     font-size: 2.5rem;
#                 ">📈</div>
#                 <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 16px; color: #333;">Progress Tracking</h3>
#                 <p style="color: #666; line-height: 1.6; font-size: 1rem;">
#                     Monitor your resume improvement journey with detailed 
#                     analytics and comprehensive score breakdowns.
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     with col6:
#         st.markdown("""
#             <div style="
#                 background: white;
#                 padding: 40px 30px;
#                 border-radius: 20px;
#                 box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
#                 text-align: center;
#                 transition: transform 0.3s;
#                 height: 100%;
#             " onmouseover="this.style.transform='translateY(-10px)'" onmouseout="this.style.transform='translateY(0)'">
#                 <div style="
#                     width: 80px;
#                     height: 80px;
#                     background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
#                     border-radius: 50%;
#                     display: flex;
#                     align-items: center;
#                     justify-content: center;
#                     margin: 0 auto 24px;
#                     font-size: 2.5rem;
#                 ">🔒</div>
#                 <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 16px; color: #333;">Privacy First</h3>
#                 <p style="color: #666; line-height: 1.6; font-size: 1rem;">
#                     Your data security is our priority. We don't store your 
#                     resume permanently - full privacy guaranteed.
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     # How It Works Section
#     st.markdown("""
#         <div style="margin: 100px 0 60px;">
#             <h2 style="
#                 text-align: center;
#                 font-size: 2.5rem;
#                 font-weight: 800;
#                 margin-bottom: 20px;
#                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#                 -webkit-background-clip: text;
#                 -webkit-text-fill-color: transparent;
#             ">🚀 How It Works</h2>
#             <p style="
#                 text-align: center;
#                 font-size: 1.2rem;
#                 color: #666;
#                 max-width: 600px;
#                 margin: 0 auto 60px;
#             ">Get started in three simple steps</p>
#         </div>
#     """, unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown("""
#             <div style="text-align: center; padding: 20px;">
#                 <div style="
#                     width: 100px;
#                     height: 100px;
#                     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#                     border-radius: 50%;
#                     display: flex;
#                     align-items: center;
#                     justify-content: center;
#                     margin: 0 auto 24px;
#                     font-size: 3rem;
#                     color: white;
#                     font-weight: 800;
#                 ">1</div>
#                 <h3 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 12px;">Upload Your Resume</h3>
#                 <p style="color: #666; line-height: 1.6;">
#                     Simply upload your PDF resume to get started with the analysis
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown("""
#             <div style="text-align: center; padding: 20px;">
#                 <div style="
#                     width: 100px;
#                     height: 100px;
#                     background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
#                     border-radius: 50%;
#                     display: flex;
#                     align-items: center;
#                     justify-content: center;
#                     margin: 0 auto 24px;
#                     font-size: 3rem;
#                     color: white;
#                     font-weight: 800;
#                 ">2</div>
#                 <h3 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 12px;">Get Instant Analysis</h3>
#                 <p style="color: #666; line-height: 1.6;">
#                     Our AI analyzes your skills, experience, and provides detailed feedback
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown("""
#             <div style="text-align: center; padding: 20px;">
#                 <div style="
#                     width: 100px;
#                     height: 100px;
#                     background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
#                     border-radius: 50%;
#                     display: flex;
#                     align-items: center;
#                     justify-content: center;
#                     margin: 0 auto 24px;
#                     font-size: 3rem;
#                     color: white;
#                     font-weight: 800;
#                 ">3</div>
#                 <h3 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 12px;">Find Perfect Jobs</h3>
#                 <p style="color: #666; line-height: 1.6;">
#                     Browse personalized job recommendations and apply with confidence
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     # CTA Section
#     st.markdown("""
#         <div id="get-started" style="
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             padding: 80px 40px;
#             border-radius: 20px;
#             text-align: center;
#             margin: 100px 0 60px;
#             box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
#         ">
#             <h2 style="
#                 font-size: 3rem;
#                 font-weight: 800;
#                 color: white;
#                 margin-bottom: 24px;
#             ">Ready to Transform Your Career?</h2>
#             <p style="
#                 font-size: 1.3rem;
#                 color: rgba(255, 255, 255, 0.95);
#                 max-width: 700px;
#                 margin: 0 auto 40px;
#                 line-height: 1.6;
#             ">
#                 Join thousands of job seekers who have successfully improved their 
#                 resumes and landed their dream jobs with InternHunt
#             </p>
#         </div>
#     """, unsafe_allow_html=True)
    
#     # Large CTA Button
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         if st.button("🚀 Analyze My Resume Now", key="cta_button", use_container_width=True):
#             st.session_state.page = "analyzer"
#             st.rerun()
    
#     st.markdown("""
#         <style>
#         .stButton > button {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             font-size: 1.3rem;
#             font-weight: 700;
#             padding: 20px 50px;
#             border-radius: 50px;
#             border: none;
#             box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
#             transition: all 0.3s;
#         }
#         .stButton > button:hover {
#             transform: translateY(-5px);
#             box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
#         }
#         </style>
#     """, unsafe_allow_html=True)
    
#     # Testimonials Section
#     st.markdown("""
#         <div style="margin: 80px 0 40px;">
#             <h2 style="
#                 text-align: center;
#                 font-size: 2.5rem;
#                 font-weight: 800;
#                 margin-bottom: 20px;
#                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#                 -webkit-background-clip: text;
#                 -webkit-text-fill-color: transparent;
#             ">💬 What Our Users Say</h2>
#         </div>
#     """, unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown("""
#             <div style="
#                 background: white;
#                 padding: 30px;
#                 border-radius: 16px;
#                 box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
#             ">
#                 <div style="color: #FFD700; font-size: 1.5rem; margin-bottom: 16px;">⭐⭐⭐⭐⭐</div>
#                 <p style="color: #666; line-height: 1.6; margin-bottom: 20px; font-style: italic;">
#                     "InternHunt helped me identify gaps in my resume and provided 
#                     actionable feedback. Got my dream job within 2 weeks!"
#                 </p>
#                 <div style="font-weight: 700; color: #333;">- Sarah K.</div>
#                 <div style="color: #999; font-size: 0.9rem;">Software Engineer</div>
#             </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown("""
#             <div style="
#                 background: white;
#                 padding: 30px;
#                 border-radius: 16px;
#                 box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
#             ">
#                 <div style="color: #FFD700; font-size: 1.5rem; margin-bottom: 16px;">⭐⭐⭐⭐⭐</div>
#                 <p style="color: #666; line-height: 1.6; margin-bottom: 20px; font-style: italic;">
#                     "The AI assistant is incredibly helpful! It answered all my career 
#                     questions and gave me great interview tips."
#                 </p>
#                 <div style="font-weight: 700; color: #333;">- Michael R.</div>
#                 <div style="color: #999; font-size: 0.9rem;">Data Analyst</div>
#             </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown("""
#             <div style="
#                 background: white;
#                 padding: 30px;
#                 border-radius: 16px;
#                 box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
#             ">
#                 <div style="color: #FFD700; font-size: 1.5rem; margin-bottom: 16px;">⭐⭐⭐⭐⭐</div>
#                 <p style="color: #666; line-height: 1.6; margin-bottom: 20px; font-style: italic;">
#                     "The job matching feature is amazing! Found opportunities I never 
#                     would have discovered on my own."
#                 </p>
#                 <div style="font-weight: 700; color: #333;">- Priya S.</div>
#                 <div style="color: #999; font-size: 0.9rem;">Product Manager</div>
#             </div>
#         """, unsafe_allow_html=True)
    
#     # Footer
#     st.markdown("""
#         <div style="
#             margin-top: 100px;
#             padding: 40px 20px 20px;
#             border-top: 2px solid #eee;
#             text-align: center;
#         ">
#             <p style="color: #999; font-size: 0.9rem; margin-bottom: 16px;">
#                 © 2025 InternHunt. Developed by 
#                 <a href='https://www.linkedin.com/in/shubham-sharma-163a962a9' target='_blank' style='color: #667eea;'>Shubham</a>, 
#                 <a href='https://www.linkedin.com/in/abhinav-ghangas-5a3b8128a' target='_blank' style='color: #667eea;'>Abhinav</a>, 
#                 <a href='https://www.linkedin.com/in/pragya-9974b1298' target='_blank' style='color: #667eea;'>Pragya</a>
#             </p>
#             <p style="color: #999; font-size: 0.85rem;">
#                 📧 internhunt@support.com | 📍 Greater Noida, India
#             </p>
#             <p style="color: #999; font-size: 0.8rem; margin-top: 12px;">
#                 🔒 We respect your privacy. Your resume data is processed securely and not stored permanently.
#             </p>
#         </div>
#     """, unsafe_allow_html=True)


"""
Landing Page Module for InternHunt
Professional landing page with features, benefits, and CTA
"""
import streamlit as st

def render_landing_page():
    """Render the professional landing page"""
    
    # Hero Section
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #50207A 0%, #838CE5 100%);
            padding: 100px 40px;
            border-radius: 24px;
            margin-bottom: 80px;
            text-align: center;
            box-shadow: 0 25px 70px rgba(80, 32, 122, 0.3);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50%;
                right: -10%;
                width: 500px;
                height: 500px;
                background: radial-gradient(circle, rgba(214, 185, 252, 0.2) 0%, transparent 70%);
                border-radius: 50%;
            "></div>
            <div style="
                position: absolute;
                bottom: -30%;
                left: -5%;
                width: 400px;
                height: 400px;
                background: radial-gradient(circle, rgba(131, 140, 229, 0.2) 0%, transparent 70%);
                border-radius: 50%;
            "></div>
            <div style="
                font-size: 5rem;
                margin-bottom: 30px;
                animation: float 3s ease-in-out infinite;
                position: relative;
                z-index: 1;
            ">🎯</div>
            <h1 style="
                font-size: 4rem;
                font-weight: 900;
                color: white;
                margin-bottom: 28px;
                text-shadow: 2px 4px 8px rgba(0,0,0,0.2);
                letter-spacing: -1px;
                position: relative;
                z-index: 1;
            ">Welcome to InternHunt</h1>
            <p style="
                font-size: 1.6rem;
                color: rgba(255, 255, 255, 0.95);
                max-width: 850px;
                margin: 0 auto 50px;
                line-height: 1.7;
                font-weight: 300;
                position: relative;
                z-index: 1;
            ">
                Your AI-Powered Career Companion for Resume Analysis, 
                Job Matching, and Professional Growth
            </p>
            <div style="display: flex; gap: 24px; justify-content: center; flex-wrap: wrap; position: relative; z-index: 1;">
                <a href="#get-started" style="
                    background: white;
                    color: #50207A;
                    padding: 18px 48px;
                    border-radius: 50px;
                    text-decoration: none;
                    font-weight: 700;
                    font-size: 1.15rem;
                    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25);
                    transition: all 0.3s ease;
                    display: inline-block;
                " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 16px 45px rgba(0, 0, 0, 0.3)'" 
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 12px 35px rgba(0, 0, 0, 0.25)'">
                    Get Started Free →
                </a>
                <a href="#how-it-works" style="
                    background: rgba(255, 255, 255, 0.15);
                    color: white;
                    padding: 18px 48px;
                    border-radius: 50px;
                    text-decoration: none;
                    font-weight: 700;
                    font-size: 1.15rem;
                    border: 2px solid rgba(255, 255, 255, 0.4);
                    backdrop-filter: blur(10px);
                    transition: all 0.3s ease;
                    display: inline-block;
                " onmouseover="this.style.background='rgba(255, 255, 255, 0.25)'" 
                   onmouseout="this.style.background='rgba(255, 255, 255, 0.15)'">
                    Learn More
                </a>
            </div>
        </div>
        
        <style>
        @keyframes float {{
            0%, 100% {{
                transform: translateY(0px);
            }}
            50% {{
                transform: translateY(-20px);
            }}
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown("""
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 32px;
            margin: 80px 0;
        ">
            <div style="
                text-align: center;
                padding: 40px 30px;
                background: linear-gradient(135deg, #50207A 0%, #6B2FA3 100%);
                border-radius: 20px;
                box-shadow: 0 12px 35px rgba(80, 32, 122, 0.25);
                transition: transform 0.3s ease;
            " onmouseover="this.style.transform='translateY(-8px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="font-size: 3.5rem; font-weight: 900; color: white; margin-bottom: 8px;">10K+</div>
                <div style="font-size: 1.15rem; color: #D6B9FC; font-weight: 600;">Resumes Analyzed</div>
            </div>
            <div style="
                text-align: center;
                padding: 40px 30px;
                background: linear-gradient(135deg, #838CE5 0%, #9BA3E8 100%);
                border-radius: 20px;
                box-shadow: 0 12px 35px rgba(131, 140, 229, 0.25);
                transition: transform 0.3s ease;
            " onmouseover="this.style.transform='translateY(-8px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="font-size: 3.5rem; font-weight: 900; color: white; margin-bottom: 8px;">95%</div>
                <div style="font-size: 1.15rem; color: white; font-weight: 600; opacity: 0.95;">Accuracy Rate</div>
            </div>
            <div style="
                text-align: center;
                padding: 40px 30px;
                background: linear-gradient(135deg, #D6B9FC 0%, #E5D9FF 100%);
                border-radius: 20px;
                box-shadow: 0 12px 35px rgba(214, 185, 252, 0.25);
                transition: transform 0.3s ease;
            " onmouseover="this.style.transform='translateY(-8px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="font-size: 3.5rem; font-weight: 900; color: #50207A; margin-bottom: 8px;">5K+</div>
                <div style="font-size: 1.15rem; color: #50207A; font-weight: 600;">Jobs Posted Daily</div>
            </div>
            <div style="
                text-align: center;
                padding: 40px 30px;
                background: linear-gradient(135deg, #50207A 0%, #838CE5 100%);
                border-radius: 20px;
                box-shadow: 0 12px 35px rgba(80, 32, 122, 0.25);
                transition: transform 0.3s ease;
            " onmouseover="this.style.transform='translateY(-8px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="font-size: 3.5rem; font-weight: 900; color: white; margin-bottom: 8px;">24/7</div>
                <div style="font-size: 1.15rem; color: #D6B9FC; font-weight: 600;">AI Assistant</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("""
        <div id="how-it-works" style="margin: 100px 0 60px;">
            <h2 style="
                text-align: center;
                font-size: 3rem;
                font-weight: 900;
                margin-bottom: 24px;
                color: #50207A;
                letter-spacing: -1px;
            ">✨ Powerful Features</h2>
            <p style="
                text-align: center;
                font-size: 1.3rem;
                color: #666;
                max-width: 650px;
                margin: 0 auto 70px;
                line-height: 1.6;
            ">Everything you need to accelerate your career journey</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="
                background: white;
                padding: 45px 35px;
                border-radius: 24px;
                box-shadow: 0 12px 45px rgba(80, 32, 122, 0.12);
                text-align: center;
                transition: all 0.4s ease;
                height: 100%;
                border: 2px solid transparent;
            " onmouseover="this.style.transform='translateY(-12px)'; this.style.borderColor='#D6B9FC'; this.style.boxShadow='0 20px 60px rgba(80, 32, 122, 0.2)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='transparent'; this.style.boxShadow='0 12px 45px rgba(80, 32, 122, 0.12)'">
                <div style="
                    width: 90px;
                    height: 90px;
                    background: linear-gradient(135deg, #50207A 0%, #838CE5 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 28px;
                    font-size: 2.8rem;
                    box-shadow: 0 8px 25px rgba(80, 32, 122, 0.3);
                ">📊</div>
                <h3 style="font-size: 1.6rem; font-weight: 800; margin-bottom: 18px; color: #50207A;">Smart Resume Analysis</h3>
                <p style="color: #666; line-height: 1.7; font-size: 1.05rem;">
                    Advanced AI algorithms analyze your resume, extract skills, 
                    and provide detailed scoring with actionable improvements.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="
                background: white;
                padding: 45px 35px;
                border-radius: 24px;
                box-shadow: 0 12px 45px rgba(80, 32, 122, 0.12);
                text-align: center;
                transition: all 0.4s ease;
                height: 100%;
                border: 2px solid transparent;
            " onmouseover="this.style.transform='translateY(-12px)'; this.style.borderColor='#D6B9FC'; this.style.boxShadow='0 20px 60px rgba(80, 32, 122, 0.2)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='transparent'; this.style.boxShadow='0 12px 45px rgba(80, 32, 122, 0.12)'">
                <div style="
                    width: 90px;
                    height: 90px;
                    background: linear-gradient(135deg, #838CE5 0%, #D6B9FC 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 28px;
                    font-size: 2.8rem;
                    box-shadow: 0 8px 25px rgba(131, 140, 229, 0.3);
                ">🎯</div>
                <h3 style="font-size: 1.6rem; font-weight: 800; margin-bottom: 18px; color: #50207A;">Personalized Job Matching</h3>
                <p style="color: #666; line-height: 1.7; font-size: 1.05rem;">
                    Get real-time job recommendations from multiple sources 
                    perfectly matched to your skills and experience level.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="
                background: white;
                padding: 45px 35px;
                border-radius: 24px;
                box-shadow: 0 12px 45px rgba(80, 32, 122, 0.12);
                text-align: center;
                transition: all 0.4s ease;
                height: 100%;
                border: 2px solid transparent;
            " onmouseover="this.style.transform='translateY(-12px)'; this.style.borderColor='#D6B9FC'; this.style.boxShadow='0 20px 60px rgba(80, 32, 122, 0.2)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='transparent'; this.style.boxShadow='0 12px 45px rgba(80, 32, 122, 0.12)'">
                <div style="
                    width: 90px;
                    height: 90px;
                    background: linear-gradient(135deg, #D6B9FC 0%, #50207A 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 28px;
                    font-size: 2.8rem;
                    box-shadow: 0 8px 25px rgba(214, 185, 252, 0.3);
                ">💬</div>
                <h3 style="font-size: 1.6rem; font-weight: 800; margin-bottom: 18px; color: #50207A;">AI Career Assistant</h3>
                <p style="color: #666; line-height: 1.7; font-size: 1.05rem;">
                    Chat with our intelligent assistant for personalized career 
                    advice, resume tips, and interview preparation guidance.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Additional Features
    st.markdown("<br><br>", unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
            <div style="
                background: white;
                padding: 45px 35px;
                border-radius: 24px;
                box-shadow: 0 12px 45px rgba(80, 32, 122, 0.12);
                text-align: center;
                transition: all 0.4s ease;
                height: 100%;
                border: 2px solid transparent;
            " onmouseover="this.style.transform='translateY(-12px)'; this.style.borderColor='#838CE5'; this.style.boxShadow='0 20px 60px rgba(80, 32, 122, 0.2)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='transparent'; this.style.boxShadow='0 12px 45px rgba(80, 32, 122, 0.12)'">
                <div style="
                    width: 90px;
                    height: 90px;
                    background: linear-gradient(135deg, #50207A 0%, #D6B9FC 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 28px;
                    font-size: 2.8rem;
                    box-shadow: 0 8px 25px rgba(80, 32, 122, 0.3);
                ">🛠️</div>
                <h3 style="font-size: 1.6rem; font-weight: 800; margin-bottom: 18px; color: #50207A;">Skills Enhancement</h3>
                <p style="color: #666; line-height: 1.7; font-size: 1.05rem;">
                    Discover skill gaps and get curated course recommendations 
                    to boost your profile and career prospects.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
            <div style="
                background: white;
                padding: 45px 35px;
                border-radius: 24px;
                box-shadow: 0 12px 45px rgba(80, 32, 122, 0.12);
                text-align: center;
                transition: all 0.4s ease;
                height: 100%;
                border: 2px solid transparent;
            " onmouseover="this.style.transform='translateY(-12px)'; this.style.borderColor='#838CE5'; this.style.boxShadow='0 20px 60px rgba(80, 32, 122, 0.2)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='transparent'; this.style.boxShadow='0 12px 45px rgba(80, 32, 122, 0.12)'">
                <div style="
                    width: 90px;
                    height: 90px;
                    background: linear-gradient(135deg, #838CE5 0%, #50207A 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 28px;
                    font-size: 2.8rem;
                    box-shadow: 0 8px 25px rgba(131, 140, 229, 0.3);
                ">📈</div>
                <h3 style="font-size: 1.6rem; font-weight: 800; margin-bottom: 18px; color: #50207A;">Progress Tracking</h3>
                <p style="color: #666; line-height: 1.7; font-size: 1.05rem;">
                    Monitor your resume improvement journey with detailed 
                    analytics and comprehensive score breakdowns.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
            <div style="
                background: white;
                padding: 45px 35px;
                border-radius: 24px;
                box-shadow: 0 12px 45px rgba(80, 32, 122, 0.12);
                text-align: center;
                transition: all 0.4s ease;
                height: 100%;
                border: 2px solid transparent;
            " onmouseover="this.style.transform='translateY(-12px)'; this.style.borderColor='#838CE5'; this.style.boxShadow='0 20px 60px rgba(80, 32, 122, 0.2)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='transparent'; this.style.boxShadow='0 12px 45px rgba(80, 32, 122, 0.12)'">
                <div style="
                    width: 90px;
                    height: 90px;
                    background: linear-gradient(135deg, #D6B9FC 0%, #838CE5 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 28px;
                    font-size: 2.8rem;
                    box-shadow: 0 8px 25px rgba(214, 185, 252, 0.3);
                ">🔒</div>
                <h3 style="font-size: 1.6rem; font-weight: 800; margin-bottom: 18px; color: #50207A;">Privacy First</h3>
                <p style="color: #666; line-height: 1.7; font-size: 1.05rem;">
                    Your data security is our priority. We don't store your 
                    resume permanently - full privacy guaranteed.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("""
        <div style="margin: 120px 0 60px;">
            <h2 style="
                text-align: center;
                font-size: 3rem;
                font-weight: 900;
                margin-bottom: 24px;
                color: #50207A;
                letter-spacing: -1px;
            ">🚀 How It Works</h2>
            <p style="
                text-align: center;
                font-size: 1.3rem;
                color: #666;
                max-width: 650px;
                margin: 0 auto 70px;
                line-height: 1.6;
            ">Get started in three simple steps</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="text-align: center; padding: 30px 20px;">
                <div style="
                    width: 110px;
                    height: 110px;
                    background: linear-gradient(135deg, #50207A 0%, #838CE5 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 28px;
                    font-size: 3.5rem;
                    color: white;
                    font-weight: 900;
                    box-shadow: 0 10px 30px rgba(80, 32, 122, 0.3);
                ">1</div>
                <h3 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 14px; color: #50207A;">Upload Your Resume</h3>
                <p style="color: #666; line-height: 1.7; font-size: 1.05rem;">
                    Simply upload your PDF resume to get started with the analysis
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 30px 20px;">
                <div style="
                    width: 110px;
                    height: 110px;
                    background: linear-gradient(135deg, #838CE5 0%, #D6B9FC 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 28px;
                    font-size: 3.5rem;
                    color: white;
                    font-weight: 900;
                    box-shadow: 0 10px 30px rgba(131, 140, 229, 0.3);
                ">2</div>
                <h3 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 14px; color: #50207A;">Get Instant Analysis</h3>
                <p style="color: #666; line-height: 1.7; font-size: 1.05rem;">
                    Our AI analyzes your skills, experience, and provides detailed feedback
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="text-align: center; padding: 30px 20px;">
                <div style="
                    width: 110px;
                    height: 110px;
                    background: linear-gradient(135deg, #D6B9FC 0%, #50207A 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 28px;
                    font-size: 3.5rem;
                    color: white;
                    font-weight: 900;
                    box-shadow: 0 10px 30px rgba(214, 185, 252, 0.3);
                ">3</div>
                <h3 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 14px; color: #50207A;">Find Perfect Jobs</h3>
                <p style="color: #666; line-height: 1.7; font-size: 1.05rem;">
                    Browse personalized job recommendations and apply with confidence
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("""
        <div id="get-started" style="
            background: linear-gradient(135deg, #50207A 0%, #838CE5 100%);
            padding: 90px 50px;
            border-radius: 28px;
            text-align: center;
            margin: 120px 0 80px;
            box-shadow: 0 25px 70px rgba(80, 32, 122, 0.35);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -20%;
                right: -5%;
                width: 400px;
                height: 400px;
                background: radial-gradient(circle, rgba(214, 185, 252, 0.2) 0%, transparent 70%);
                border-radius: 50%;
            "></div>
            <h2 style="
                font-size: 3.5rem;
                font-weight: 900;
                color: white;
                margin-bottom: 28px;
                letter-spacing: -1px;
                position: relative;
                z-index: 1;
            ">Ready to Transform Your Career?</h2>
            <p style="
                font-size: 1.4rem;
                color: rgba(255, 255, 255, 0.95);
                max-width: 750px;
                margin: 0 auto 50px;
                line-height: 1.7;
                position: relative;
                z-index: 1;
            ">
                Join thousands of job seekers who have successfully improved their 
                resumes and landed their dream jobs with InternHunt
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Large CTA Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze My Resume Now", key="cta_button", use_container_width=True):
            st.session_state.page = "analyzer"
            st.rerun()
    
    st.markdown("""
        <style>
        .stButton > button {
            background: linear-gradient(135deg, #50207A 0%, #838CE5 100%);
            color: white;
            font-size: 1.4rem;
            font-weight: 800;
            padding: 24px 60px;
            border-radius: 50px;
            border: none;
            box-shadow: 0 15px 40px rgba(80, 32, 122, 0.4);
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-6px);
            box-shadow: 0 20px 50px rgba(80, 32, 122, 0.6);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Testimonials Section
    st.markdown("""
        <div style="margin: 100px 0 50px;">
            <h2 style="
                text-align: center;
                font-size: 3rem;
                font-weight: 900;
                margin-bottom: 24px;
                color: #50207A;
                letter-spacing: -1px;
            ">💬 What Our Users Say</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="
                background: white;
                padding: 40px 35px;
                border-radius: 24px;
                box-shadow: 0 12px 40px rgba(80, 32, 122, 0.12);
                border-left: 5px solid #50207A;
            ">
                <div style="color: #FFD700; font-size: 1.8rem; margin-bottom: 20px;">⭐⭐⭐⭐⭐</div>
                <p style="color: #666; line-height: 1.7; margin-bottom: 24px; font-style: italic; font-size: 1.05rem;">
                    "InternHunt helped me identify gaps in my resume and provided 
                    actionable feedback. Got my dream job within 2 weeks!"
                </p>
                <div style="font-weight: 800; color: #50207A; font-size: 1.1rem;">- Sarah K.</div>
                <div style="color: #838CE5; font-size: 0.95rem; margin-top: 4px;">Software Engineer</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="
                background: white;
                padding: 40px 35px;
                border-radius: 24px;
                box-shadow: 0 12px 40px rgba(80, 32, 122, 0.12);
                border-left: 5px solid #838CE5;
            ">
                <div style="color: #FFD700; font-size: 1.8rem; margin-bottom: 20px;">⭐⭐⭐⭐⭐</div>
                <p style="color: #666; line-height: 1.7; margin-bottom: 24px; font-style: italic; font-size: 1.05rem;">
                    "The AI assistant is incredibly helpful! It answered all my career 
                    questions and gave me great interview tips."
                </p>
                <div style="font-weight: 800; color: #50207A; font-size: 1.1rem;">- Michael R.</div>
                <div style="color: #838CE5; font-size: 0.95rem; margin-top: 4px;">Data Analyst</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="
                background: white;
                padding: 40px 35px;
                border-radius: 24px;
                box-shadow: 0 12px 40px rgba(80, 32, 122, 0.12);
                border-left: 5px solid #D6B9FC;
            ">
                <div style="color: #FFD700; font-size: 1.8rem; margin-bottom: 20px;">⭐⭐⭐⭐⭐</div>
                <p style="color: #666; line-height: 1.7; margin-bottom: 24px; font-style: italic; font-size: 1.05rem;">
                    "The job matching feature is amazing! Found opportunities I never 
                    would have discovered on my own."
                </p>
                <div style="font-weight: 800; color: #50207A; font-size: 1.1rem;">- Priya S.</div>
                <div style="color: #838CE5; font-size: 0.95rem; margin-top: 4px;">Product Manager</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div style="
            margin-top: 120px;
            padding: 50px 30px 30px;
            border-top: 3px solid #D6B9FC;
            text-align: center;
            background: linear-gradient(180deg, transparent 0%, rgba(214, 185, 252, 0.1) 100%);
        ">
            <p style="color: #666; font-size: 1rem; margin-bottom: 20px; font-weight: 500;">
                © 2025 InternHunt. Developed by 
                <a href='https://www.linkedin.com/in/shubham-sharma-163a962a9' target='_blank' style='color: #50207A; font-weight: 700; text-decoration: none;'>Shubham</a>, 
                <a href='https://www.linkedin.com/in/abhinav-ghangas-5a3b8128a' target='_blank' style='color: #50207A; font-weight: 700; text-decoration: none;'>Abhinav</a>, 
                <a href='https://www.linkedin.com/in/pragya-9974b1298' target='_blank' style='color: #50207A; font-weight: 700; text-decoration: none;'>Pragya</a>
            </p>
            <p style="color: #666; font-size: 0.95rem; margin-bottom: 16px;">
                📧 internhunt@support.com | 📍 Greater Noida, India
            </p>
            <p style="color: #838CE5; font-size: 0.9rem; margin-top: 16px; font-weight: 500;">
                🔒 We respect your privacy. Your resume data is processed securely and not stored permanently.
            </p>
        </div>
    """, unsafe_allow_html=True)
