# # CSS styles module for InternHunt
# import streamlit as st

# class StyleManager:
#     """Manages all CSS styles for the application"""
    
#     @staticmethod
#     def apply_global_styles():
#         """Apply global CSS styles"""
#         st.markdown("""
#         <style>
#         /* Global styles */
#         html {
#             scroll-behavior: smooth;
#         }
        
#         .main .block-container {
#             padding-top: 2rem;
#             padding-bottom: 3rem;
#             max-width: 1200px;
#         }
        
#         /* Header styles */
#         .main-title {
#             font-size: 3.5rem;
#             font-weight: 700;
#             color: #2c2c2c;
#             text-align: center;
#             margin-top: 1rem;
#         }
        
#         .subtitle {
#             font-size: 1.5rem;
#             color: #666;
#             text-align: center;
#             margin-top: -0.5rem;
#         }
        
#         /* Navigation */
#         .topnav {
#             background-color: rgba(0, 0, 0, 0);
#             overflow: hidden;
#             padding: 10px 20px;
#             display: flex;
#             justify-content: flex-end;
#             align-items: center;
#             gap: 20px;
#             position: fixed;
#             top: 0;
#             width: 100%;
#             z-index: 1000;
#         }
        
#         .topnav a {
#             color: #f2f2f2;
#             text-decoration: none;
#             font-size: 16px;
#             padding: 8px 12px;
#             border-radius: 5px;
#             transition: background-color 0.3s ease;
#         }
        
#         .topnav a:hover {
#             background-color: #00796b;
#         }
#         </style>
#         """, unsafe_allow_html=True)
    
#     @staticmethod
#     def apply_theme_styles(theme_mode: str):
#         """Apply theme-specific styles"""
#         if theme_mode == "dark":
#             st.markdown("""
#             <style>
#             body {
#                 background-color: #0f172a;
#                 color: #ffffff;
#             }
#             .stApp {
#                 background-color: #0f172a;
#                 color: #ffffff;
#             }
#             .container {
#                 background: linear-gradient(135deg, #1a1a1a, #2e2e2e);
#                 color: white;
#             }
#             </style>
#             """, unsafe_allow_html=True)
#         else:
#             st.markdown("""
#             <style>
#             body {
#                 background-color: #f8fafc;
#                 color: #111827;
#             }
#             .stApp {
#                 background-color: #f8fafc;
#                 color: #111827;
#             }
#             .container {
#                 background: linear-gradient(135deg, #e0f2f1, #ffffff);
#                 color: black;
#             }
#             </style>
#             """, unsafe_allow_html=True)
    
#     @staticmethod
#     def get_skills_styles():
#         """Get CSS styles for skills display"""
#         return """
#         <style>
#         .skills-header {
#             display: flex;
#             align-items: center;
#             margin-top: 30px;
#             margin-bottom: 25px;
#             padding-bottom: 12px;
#             border-bottom: 2px solid rgba(110, 142, 251, 0.4);
#         }
        
#         .skills-header-icon {
#             font-size: 24px;
#             margin-right: 12px;
#             background: linear-gradient(135deg, #6e8efb 0%, #5a70e7 100%);
#             -webkit-background-clip: text;
#             -webkit-text-fill-color: transparent;
#             background-clip: text;
#         }
        
#         .skills-container {
#             margin-top: 15px;
#             padding: 10px 0;
#         }
        
#         .skill-category {
#             margin-top: 25px;
#             margin-bottom: 15px;
#             padding-bottom: 8px;
#             font-weight: 600;
#             color: #ffffff;
#             font-size: 20px;
#             display: flex;
#             align-items: center;
#             border-bottom: 1px solid rgba(255, 255, 255, 0.1);
#         }
        
#         .skills-grid {
#             display: flex;
#             flex-wrap: wrap;
#             gap: 10px;
#             margin-bottom: 20px;
#         }
        
#         .skill-tag {
#             display: inline-flex;
#             align-items: center;
#             padding: 8px 14px;
#             border-radius: 30px;
#             font-size: 14px;
#             transition: all 0.2s ease;
#             cursor: default;
#         }
        
#         .tech-skill {
#             background-color: rgba(84, 119, 153, 0.75);
#             color: white;
#             border: 1px solid rgba(84, 119, 153, 0.3);
#         }
        
#         .tech-skill:hover {
#             background-color: rgba(84, 119, 153, 0.9);
#             transform: translateY(-2px);
#             box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
#         }
        
#         .hardware-skill {
#             background-color: rgba(92, 131, 116, 0.75);
#             color: white;
#             border: 1px solid rgba(92, 131, 116, 0.3);
#         }
        
#         .hardware-skill:hover {
#             background-color: rgba(92, 131, 116, 0.9);
#             transform: translateY(-2px);
#             box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
#         }
#         </style>
#         """
    
#     @staticmethod
#     def get_job_listing_styles():
#         """Get CSS styles for job listings"""
#         return """
#         <style>
#         .job-listing {
#             padding: 15px 0;
#             margin-bottom: 10px;
#             border-left: 4px solid #8E44AD;
#             padding-left: 15px;
#         }
        
#         .job-title {
#             color: #FFFFFF;
#             font-size: 20px;
#             font-weight: bold;
#             margin-bottom: 15px;
#             letter-spacing: 0.3px;
#             display: flex;
#             align-items: center;
#         }
        
#         .job-info-container {
#             display: flex;
#             justify-content: space-between;
#             align-items: flex-start;
#             margin-bottom: 15px;
#         }
        
#         .job-info {
#             display: flex;
#             flex-direction: column;
#             gap: 10px;
#         }
        
#         .info-item {
#             display: flex;
#             align-items: center;
#             gap: 8px;
#             color: #CCCCCC;
#         }
        
#         .info-label {
#             font-weight: 600;
#             color: #9A9A9A;
#         }
        
#         .apply-button {
#             background-color: #4CAF50;
#             color: white;
#             padding: 8px 16px;
#             border: none;
#             border-radius: 20px;
#             cursor: pointer;
#             display: inline-block;
#             font-weight: bold;
#             transition: all 0.3s;
#             text-decoration: none;
#             text-align: center;
#             min-width: 100px;
#         }
        
#         .apply-button:hover {
#             background-color: #45a049;
#             box-shadow: 0 2px 5px rgba(76, 175, 80, 0.3);
#         }
        
#         .separator {
#             height: 1px;
#             background: linear-gradient(to right, rgba(142, 68, 173, 0), rgba(142, 68, 173, 0.5), rgba(142, 68, 173, 0));
#             margin: 20px 0;
#         }
#         </style>
#         """
    
#     @staticmethod
#     def get_animation_styles():
#         """Get CSS animation styles"""
#         return """
#         <style>
#         @keyframes fadeSlideIn {
#             from {
#                 opacity: 0;
#                 transform: translateY(20px);
#             }
#             to {
#                 opacity: 1;
#                 transform: translateY(0);
#             }
#         }
        
#         @keyframes shine {
#             0% {
#                 background-position: -100%;
#             }
#             100% {
#                 background-position: 200%;
#             }
#         }
        
#         .animated-header {
#             animation: fadeSlideIn 0.8s ease-out;
#             position: relative;
#             overflow: hidden;
#             transition: box-shadow 0.3s ease;
#         }
        
#         .animated-header:hover {
#             box-shadow: 0 0 12px #00ffe1;
#         }
        
#         .animated-header:hover::after {
#             content: '';
#             position: absolute;
#             top: 0;
#             left: -75%;
#             width: 50%;
#             height: 100%;
#             background: linear-gradient(120deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.05) 100%);
#             animation: shine 1s ease forwards;
#         }
#         </style>
#         """
    
#     @staticmethod
#     def get_chat_styles():
#         """Get CSS styles for enhanced chat interface"""
#         return """
#         <style>
#         /* Chat Container */
#         .chat-container {
#             background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
#             border-radius: 16px;
#             padding: 20px;
#             margin: 20px 0;
#             box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
#             border: 1px solid rgba(255, 255, 255, 0.1);
#         }
        
#         /* Chat Header */
#         .chat-header {
#             display: flex;
#             align-items: center;
#             justify-content: space-between;
#             margin-bottom: 20px;
#             padding-bottom: 15px;
#             border-bottom: 2px solid rgba(110, 142, 251, 0.3);
#         }
        
#         .chat-title {
#             display: flex;
#             align-items: center;
#             gap: 12px;
#             color: #ffffff;
#             font-size: 24px;
#             font-weight: 700;
#         }
        
#         .chat-avatar {
#             width: 40px;
#             height: 40px;
#             background: linear-gradient(135deg, #6e8efb 0%, #5a70e7 100%);
#             border-radius: 50%;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             font-size: 18px;
#             color: white;
#         }
        
#         /* Chat Status */
#         .chat-status {
#             display: flex;
#             align-items: center;
#             gap: 8px;
#             padding: 6px 12px;
#             background: rgba(76, 175, 80, 0.2);
#             border: 1px solid rgba(76, 175, 80, 0.3);
#             border-radius: 20px;
#             color: #4caf50;
#             font-size: 12px;
#             font-weight: 600;
#         }
        
#         .status-dot {
#             width: 8px;
#             height: 8px;
#             background: #4caf50;
#             border-radius: 50%;
#             animation: pulse 2s infinite;
#         }
        
#         @keyframes pulse {
#             0% { opacity: 1; }
#             50% { opacity: 0.5; }
#             100% { opacity: 1; }
#         }
        
#         /* Message Bubbles */
#         .message-container {
#             margin: 15px 0;
#             display: flex;
#             flex-direction: column;
#         }
        
#         .message-user {
#             align-self: flex-end;
#             max-width: 70%;
#         }
        
#         .message-assistant {
#             align-self: flex-start;
#             max-width: 85%;
#         }
        
#         .message-bubble {
#             padding: 12px 18px;
#             border-radius: 18px;
#             position: relative;
#             word-wrap: break-word;
#             line-height: 1.4;
#         }
        
#         .message-bubble.user {
#             background: linear-gradient(135deg, #6e8efb 0%, #5a70e7 100%);
#             color: white;
#             border-bottom-right-radius: 6px;
#         }
        
#         .message-bubble.assistant {
#             background: rgba(255, 255, 255, 0.1);
#             color: #ffffff;
#             border: 1px solid rgba(255, 255, 255, 0.2);
#             border-bottom-left-radius: 6px;
#         }
        
#         .message-time {
#             font-size: 10px;
#             opacity: 0.7;
#             margin-top: 4px;
#             text-align: right;
#         }
        
#         .message-assistant .message-time {
#             text-align: left;
#         }
        
#         /* Typing Indicator */
#         .typing-indicator {
#             display: flex;
#             align-items: center;
#             gap: 8px;
#             padding: 12px 18px;
#             background: rgba(255, 255, 255, 0.1);
#             border: 1px solid rgba(255, 255, 255, 0.2);
#             border-radius: 18px;
#             border-bottom-left-radius: 6px;
#             max-width: 85%;
#             margin: 15px 0;
#         }
        
#         .typing-dots {
#             display: flex;
#             gap: 4px;
#         }
        
#         .typing-dot {
#             width: 8px;
#             height: 8px;
#             background: #6e8efb;
#             border-radius: 50%;
#             animation: typing 1.4s infinite ease-in-out;
#         }
        
#         .typing-dot:nth-child(1) { animation-delay: -0.32s; }
#         .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        
#         @keyframes typing {
#             0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
#             40% { transform: scale(1); opacity: 1; }
#         }
        
#         /* Suggested Questions */
#         .suggested-questions {
#             margin: 20px 0;
#             padding: 15px;
#             background: rgba(255, 255, 255, 0.05);
#             border-radius: 12px;
#             border: 1px solid rgba(255, 255, 255, 0.1);
#         }
        
#         .suggested-questions h4 {
#             color: #ffffff;
#             margin-bottom: 12px;
#             font-size: 14px;
#             font-weight: 600;
#         }
        
#         .question-chips {
#             display: flex;
#             flex-wrap: wrap;
#             gap: 8px;
#         }
        
#         .question-chip {
#             padding: 8px 12px;
#             background: rgba(110, 142, 251, 0.2);
#             border: 1px solid rgba(110, 142, 251, 0.3);
#             border-radius: 20px;
#             color: #6e8efb;
#             font-size: 12px;
#             cursor: pointer;
#             transition: all 0.2s ease;
#         }
        
#         .question-chip:hover {
#             background: rgba(110, 142, 251, 0.3);
#             transform: translateY(-1px);
#         }
        
#         /* Chat Controls */
#         .chat-controls {
#             display: flex;
#             align-items: center;
#             gap: 12px;
#             margin: 15px 0;
#             padding: 12px;
#             background: rgba(255, 255, 255, 0.05);
#             border-radius: 12px;
#             border: 1px solid rgba(255, 255, 255, 0.1);
#         }
        
#         .control-group {
#             display: flex;
#             align-items: center;
#             gap: 8px;
#         }
        
#         .control-label {
#             color: #ffffff;
#             font-size: 12px;
#             font-weight: 600;
#         }
        
#         /* Chat Input Enhancement */
#         .stChatInput > div > div {
#             background: rgba(255, 255, 255, 0.1) !important;
#             border: 1px solid rgba(255, 255, 255, 0.2) !important;
#             border-radius: 25px !important;
#         }
        
#         .stChatInput input {
#             color: #ffffff !important;
#             background: transparent !important;
#         }
        
#         .stChatInput input::placeholder {
#             color: rgba(255, 255, 255, 0.6) !important;
#         }
        
#         /* Scrollbar Styling */
#         .chat-messages::-webkit-scrollbar {
#             width: 6px;
#         }
        
#         .chat-messages::-webkit-scrollbar-track {
#             background: rgba(255, 255, 255, 0.1);
#             border-radius: 3px;
#         }
        
#         .chat-messages::-webkit-scrollbar-thumb {
#             background: rgba(110, 142, 251, 0.5);
#             border-radius: 3px;
#         }
        
#         .chat-messages::-webkit-scrollbar-thumb:hover {
#             background: rgba(110, 142, 251, 0.7);
#         }
#         </style>
#         """






























# Add these modern styling improvements to your StyleManager class:

@staticmethod
def apply_modern_theme():
    """Apply modern, professional theme"""
    st.markdown("""
    <style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global variables for consistency */
    :root {
        --primary-color: #6366f1;
        --primary-gradient: linear-gradient(135deg, #6366f1, #8b5cf6);
        --secondary-color: #f3f4f6;
        --accent-color: #10b981;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --success-color: #059669;
        --warning-color: #d97706;
        --error-color: #dc2626;
        --border-radius: 12px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.15);
        --shadow-lg: 0 10px 24px rgba(0,0,0,0.2);
    }
    
    /* Enhanced main container */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1400px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Beautiful header with gradient */
    .hero-section {
        background: var(--primary-gradient);
        padding: 4rem 2rem;
        border-radius: var(--border-radius);
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        pointer-events: none;
    }
    
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        color: rgba(255,255,255,0.9);
        margin-top: 1rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }
    
    .feature-icon {
        width: 60px;
        height: 60px;
        background: var(--primary-gradient);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        font-size: 1.5rem;
        color: white;
    }
    
    /* Status indicators */
    .status-success {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #d97706, #f59e0b);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Enhanced metrics */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        text-align: center;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid var(--primary-color);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Enhanced file uploader */
    .stFileUploader > div {
        background: white !important;
        border: 2px dashed var(--primary-color) !important;
        border-radius: var(--border-radius) !important;
        padding: 2rem !important;
        text-align: center !important;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background: var(--primary-gradient) !important;
        border-radius: 10px !important;
    }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
