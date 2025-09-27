# import streamlit as st

# def add_custom_css():
#     st.markdown("""
#         <style>
#         @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
#         html, body, [class*="css"] {
#             font-family: 'Montserrat', sans-serif;
#         }
#         .main {
#             display: flex;
#             flex-direction: column;
#             min-height: 100vh;
#         }
#         .content {
#             flex: 1;
#         }
#         .footer {
#             display: flex;
#             justify-content: space-between;
#             padding: 2rem 3rem;
#             margin-top: auto;
#             border-top: 1px solid #555;
#             font-size: 0.9rem;
#             color: #ccc;
#             flex-wrap: wrap;
#         }
#         .footer-section {
#             flex: 1;
#             min-width: 300px;
#             padding: 0 1rem;
#         }
#         .footer h3 {
#             margin-top: 0;
#             color: #fff;
#         }
#         .footer p {
#             margin: 0.2rem 0;
#         }
#         .footer a {
#             color: #4dd0e1;
#             text-decoration: none;
#         }
#         </style>
#     """, unsafe_allow_html=True)

# def add_footer():
#     st.markdown(
#         """
#         <style>
#             .main {
#                 display: flex;
#                 flex-direction: column;
#                 min-height: 100vh;
#             }
#             .content {
#                 flex: 1;
#             }
#             .footer-container {
#                 display: flex;
#                 justify-content: space-between;
#                 padding: 3rem 2rem;
#                 margin-top: 50px;
#                 border-top: 1px solid #555;
#                 flex-wrap: wrap;
#                 color: white;
#             }
#             .footer-section {
#                 flex: 1;
#                 padding: 0 2rem;
#                 min-width: 300px;
#             }
#             .footer-section h3 {
#                 font-size: 1.4rem;
#                 margin-bottom: 0.5rem;
#             }
#             .footer-section p {
#                 margin: 0.2rem 0;
#             }
#             .footer-section a {
#                 color: #00bfa5;
#                 text-decoration: none;
#             }
#         </style>

#         <div class="footer-container">
#             <div class="footer-section">
#                 <h3>📬 Contact Us</h3>
#                 <p><b>Email:</b> <a href="mailto:internhunt@support.com">internhunt@support.com</a></p>
#                 <p><b>Phone:</b> +91-9876543210</p>
#                 <p><b>Location:</b> Greater Noida, India</p>
#             </div>
#             <div class="footer-section">
#                 <h3>🔐 Privacy Policy</h3>
#                 <p>We do not store your resume or any personal data.</p>
#                 <p>All processing is handled securely through trusted APIs.</p>
#             </div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )








import streamlit as st

def add_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
        }
        
        /* Main Layout */
        .main {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            padding: 0;
        }
        
        .content {
            flex: 1;
            padding: 2rem 1rem;
        }
        
        /* Hero Section Styles */
        .hero-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 4rem 2rem;
            text-align: center;
            border-radius: 20px;
            margin: 2rem 0;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .hero-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.3;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 1;
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            font-weight: 400;
            opacity: 0.9;
            margin-bottom: 2rem;
            position: relative;
            z-index: 1;
        }
        
        /* Card Styles */
        .feature-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 2rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        .card-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }
        
        .card-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #ffffff;
        }
        
        .card-description {
            opacity: 0.8;
            line-height: 1.6;
        }
        
        /* Stats Section */
        .stats-container {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin: 3rem 0;
            gap: 2rem;
        }
        
        .stat-item {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            min-width: 200px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
        }
        
        .stat-item:hover {
            transform: scale(1.05);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            color: #ffffff;
            display: block;
        }
        
        .stat-label {
            font-size: 1rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        /* Button Styles */
        .custom-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
            text-decoration: none;
            display: inline-block;
            margin: 0.5rem;
        }
        
        .custom-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 25px rgba(102, 126, 234, 0.4);
        }
        
        /* Footer Styles */
        .footer-container {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-top: 3px solid #667eea;
            padding: 4rem 2rem 2rem;
            margin-top: 4rem;
            position: relative;
        }
        
        .footer-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, #667eea, transparent);
        }
        
        .footer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 3rem;
            margin-bottom: 2rem;
        }
        
        .footer-section {
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        .footer-section:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateY(-2px);
        }
        
        .footer-section h3 {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .footer-section p {
            margin: 1rem 0;
            line-height: 1.6;
            opacity: 0.9;
        }
        
        .footer-section a {
            color: #00bfa5;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .footer-section a:hover {
            color: #26a69a;
            text-shadow: 0 0 10px rgba(0, 191, 165, 0.3);
        }
        
        .footer-section a::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 0;
            height: 2px;
            background: linear-gradient(90deg, #00bfa5, #26a69a);
            transition: width 0.3s ease;
        }
        
        .footer-section a:hover::after {
            width: 100%;
        }
        
        .footer-bottom {
            text-align: center;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            opacity: 0.7;
            font-size: 0.9rem;
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* Mobile Responsiveness */
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }
            
            .hero-subtitle {
                font-size: 1.1rem;
            }
            
            .stats-container {
                flex-direction: column;
                align-items: center;
            }
            
            .footer-grid {
                grid-template-columns: 1fr;
                gap: 2rem;
            }
            
            .hero-container {
                padding: 3rem 1rem;
            }
        }
        
        /* Streamlit Specific Overrides */
        .stApp {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        }
        
        .main .block-container {
            padding: 1rem;
            max-width: 1200px;
        }
        
        /* Loading Animation */
        .loading-spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 2rem auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Success/Error Messages */
        .success-message {
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        
        .error-message {
            background: linear-gradient(135deg, #f44336, #d32f2f);
            color: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

def add_hero_section(title, subtitle):
    """Add an engaging hero section"""
    st.markdown(f"""
        <div class="hero-container fade-in">
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def add_feature_cards(features):
    """Add feature cards in a grid layout"""
    cols = st.columns(len(features))
    for i, feature in enumerate(features):
        with cols[i]:
            st.markdown(f"""
                <div class="feature-card fade-in">
                    <span class="card-icon">{feature['icon']}</span>
                    <h3 class="card-title">{feature['title']}</h3>
                    <p class="card-description">{feature['description']}</p>
                </div>
            """, unsafe_allow_html=True)

def add_stats_section(stats):
    """Add statistics section"""
    st.markdown("""
        <div class="stats-container">
    """, unsafe_allow_html=True)
    
    for stat in stats:
        st.markdown(f"""
            <div class="stat-item">
                <span class="stat-number">{stat['number']}</span>
                <span class="stat-label">{stat['label']}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_loading():
    """Show loading spinner"""
    st.markdown("""
        <div class="loading-spinner"></div>
    """, unsafe_allow_html=True)

def show_success_message(message):
    """Show success message"""
    st.markdown(f"""
        <div class="success-message">
            ✅ {message}
        </div>
    """, unsafe_allow_html=True)

def show_error_message(message):
    """Show error message"""
    st.markdown(f"""
        <div class="error-message">
            ❌ {message}
        </div>
    """, unsafe_allow_html=True)

def add_footer():
    st.markdown(
        """
        <div class="footer-container">
            <div class="footer-grid">
                <div class="footer-section">
                    <h3>📬 Contact Us</h3>
                    <p><b>Email:</b> <a href="mailto:internhunt@support.com">internhunt@support.com</a></p>
                    <p><b>Phone:</b> <a href="tel:+919876543210">+91-9876543210</a></p>
                    <p><b>Location:</b> Greater Noida, India 🇮🇳</p>
                    <p><b>Response Time:</b> Within 24 hours</p>
                </div>
                
                <div class="footer-section">
                    <h3>🔐 Privacy & Security</h3>
                    <p><b>Data Protection:</b> We do not store your resume or any personal data on our servers.</p>
                    <p><b>Processing:</b> All analysis is handled securely through trusted APIs with end-to-end encryption.</p>
                    <p><b>Compliance:</b> GDPR & CCPA compliant</p>
                </div>
                
                <div class="footer-section">
                    <h3>🚀 About InternHunt</h3>
                    <p><b>Mission:</b> Empowering students to land their dream internships through AI-powered resume optimization.</p>
                    <p><b>Features:</b> Smart analysis, skill recommendations, ATS optimization</p>
                    <p><b>Success Rate:</b> 85% of users report improved interview callbacks</p>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>© 2024 InternHunt. Made with ❤️ for aspiring professionals. All rights reserved.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def add_custom_button(text, url=None, onclick=None):
    """Add custom styled button"""
    if url:
        st.markdown(f"""
            <a href="{url}" class="custom-button" target="_blank">{text}</a>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <button class="custom-button" onclick="{onclick if onclick else ''}">{text}</button>
        """, unsafe_allow_html=True)
