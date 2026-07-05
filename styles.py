# CSS styles module for InternHunt - Professional UI Design System
import streamlit as st

class StyleManager:
    """Manages all CSS styles for the application with a modern, professional design system"""
    
    # Professional Color Palette - Enhanced Purple & Dark Theme
    COLORS = {
        # Primary Colors - Modern Purple-Indigo Gradient
        'primary': '#6366F1',          # Indigo-500
        'primary_light': '#818CF8',     # Indigo-400
        'primary_dark': '#4F46E5',      # Indigo-600
        'primary_gradient': 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
        
        # Secondary Purple Tones
        'purple_600': '#7C3AED',        # Purple-600
        'purple_500': '#A78BFA',        # Purple-400
        'purple_dark': '#5B21B6',       # Purple-800
        
        # Accent Colors - Vibrant Green
        'accent': '#10B981',            # Emerald-500
        'accent_light': '#34D399',      # Emerald-400
        'accent_dark': '#059669',       # Emerald-600
        
        # Neutral Colors - Sophisticated Grays
        'gray_50': '#F9FAFB',
        'gray_100': '#F3F4F6',
        'gray_200': '#E5E7EB',
        'gray_300': '#D1D5DB',
        'gray_400': '#9CA3AF',
        'gray_500': '#6B7280',
        'gray_600': '#4B5563',
        'gray_700': '#374151',
        'gray_800': '#1F2937',
        'gray_900': '#111827',
        
        # Dark Theme Colors - Deep Purple-Tinted
        'dark_bg': '#0D1429',           # Very Dark Blue-Purple
        'dark_surface': '#1A1F3A',      # Dark Blue-Purple Surface
        'dark_card': '#242F5C',         # Card Background with Purple tint
        'dark_border': '#3A4570',       # Border Purple-tint
        
        # Light Theme Colors
        'light_bg': '#FFFFFF',
        'light_surface': '#F8FAFC',     # Slate-50
        'light_card': '#FFFFFF',
        'light_border': '#E2E8F0',      # Slate-200
        
        # Status Colors
        'success': '#10B981',           # Emerald-500
        'warning': '#F59E0B',           # Amber-500
        'error': '#EF4444',             # Red-500
        'info': '#3B82F6',              # Blue-500
    }
    
    @classmethod
    def apply_global_styles(cls):
        """Apply modern global CSS styles with professional design system"""
        st.markdown(f"""
        <style>
        /* Base Styles */
        :root {{
            --primary: {cls.COLORS['primary']};
            --primary-light: {cls.COLORS['primary_light']};
            --primary-dark: {cls.COLORS['primary_dark']};
            --accent: {cls.COLORS['accent']};
            --dark-bg: {cls.COLORS['dark_bg']};
            --dark-surface: {cls.COLORS['dark_surface']};
            --dark-card: {cls.COLORS['dark_card']};
            --dark-border: {cls.COLORS['dark_border']};
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-primary) !important;
            background-color: var(--dark-bg) !important;
            margin: 0;
            padding: 0;
        }}
        
        /* Force dark theme on all Streamlit elements */
        .stApp, .stApp > div, .main, .block-container, .stApp > div > div > div > div > section > div > div > div > div,
        .stApp > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div,
        .stApp > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div {{
            background-color: var(--dark-bg) !important;
            color: var(--text-primary) !important;
        }}
        
        /* Ensure all text is visible */
        .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, 
        .stMarkdown h5, .stMarkdown h6, .stMarkdown li, .stMarkdown ol, .stMarkdown ul, .stMarkdown table,
        .stAlert, .stAlert p, .stAlert h1, .stAlert h2, .stAlert h3, .stAlert h4,
        .stAlert h5, .stAlert h6, .stAlert li, .stAlert ol, .stAlert ul, .stAlert table {{
            color: var(--text-primary) !important;
        }}
        
        /* ── Hide Native Streamlit Label and Default Icon ── */
        [data-testid="stFileUploader"] > label {{ display: none !important; }}
        [data-testid="stFileUploader"] section svg {{ display: none !important; }}
        
        /* Hide native file limits helper elements */
        [data-testid="stFileUploaderLimit"],
        [data-testid="stFileUploader"] [data-testid="stFileUploaderLimit"],
        [data-testid="stFileUploader"] small,
        .stFileUploader small {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            overflow: hidden !important;
        }}
        
        /* Modern Drag & Drop File Uploader Override */
        [data-testid="stFileUploader"] {{
            margin-top: 1.5rem;
            margin-bottom: 2rem;
            width: 100% !important;
        }}
        [data-testid="stFileUploader"] > label {{ display: none !important; }}
        
        [data-testid="stFileUploader"] section {{
            background: linear-gradient(160deg, rgba(20, 26, 53, 0.7) 0%, rgba(13, 17, 30, 0.75) 100%) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(99, 102, 241, 0.18) !important;
            border-radius: 24px !important;
            padding: 3.5rem 2.5rem 3rem !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 380px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25) !important;
            position: relative !important;
            cursor: pointer !important;
        }}
        [data-testid="stFileUploader"] section:hover {{
            background: linear-gradient(160deg, rgba(25, 32, 64, 0.75) 0%, rgba(17, 22, 40, 0.8) 100%) !important;
            border-color: rgba(99, 102, 241, 0.38) !important;
            box-shadow: 0 0 30px rgba(99, 102, 241, 0.12), 0 12px 40px 0 rgba(0, 0, 0, 0.35) !important;
        }}
        
        /* Hide native Streamlit drag/drop icons */
        [data-testid="stFileUploader"] section svg {{
            display: none !important;
        }}
        
        /* ── Empty State Styles ── */
        [data-testid="stFileUploader"] section::before {{
            content: "" !important;
            display: block !important;
            width: 64px !important;
            height: 64px !important;
            margin-bottom: 24px !important;
            background-color: rgba(139, 92, 246, 0.08) !important;
            border: 1px solid rgba(139, 92, 246, 0.2) !important;
            border-radius: 16px !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 24 24' fill='none' stroke='%238B5CF6' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/%3E%3Cpolyline points='17 8 12 3 7 8'/%3E%3Cline x1='12' y1='3' x2='12' y2='15'/%3E%3C/svg%3E") !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            box-shadow: 0 0 20px rgba(139, 92, 241, 0.15) !important;
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease !important;
        }}
        [data-testid="stFileUploader"] section:hover::before {{
            transform: translateY(-6px) !important;
            box-shadow: 0 0 25px rgba(139, 92, 241, 0.3) !important;
        }}

        [data-testid="stFileUploaderDropzoneInstructions"] {{
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            font-family: inherit !important;
            width: 100% !important;
        }}

        /* Title Line */
        [data-testid="stFileUploaderDropzoneInstructions"]::before {{
            content: "Ready to Discover Better Internships?" !important;
            font-size: 24px !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #A78BFA 0%, #60A5FA 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            display: block !important;
            text-align: center !important;
            letter-spacing: -0.5px !important;
            margin-top: 4px !important;
            margin-bottom: 12px !important;
        }}

        /* Description Line (First native child of instructions) */
        [data-testid="stFileUploaderDropzoneInstructions"] > div:first-child,
        [data-testid="stFileUploaderDropzoneInstructions"] > span:first-child,
        [data-testid="stFileUploaderDropzoneInstructions"] > div:first-of-type,
        [data-testid="stFileUploaderDropzoneInstructions"] > span:first-of-type {{
            font-size: 0 !important;
            color: transparent !important;
            margin-bottom: 24px !important;
            max-width: 500px !important;
            display: block !important;
        }}
        [data-testid="stFileUploaderDropzoneInstructions"] > div:first-child::after,
        [data-testid="stFileUploaderDropzoneInstructions"] > span:first-child::after,
        [data-testid="stFileUploaderDropzoneInstructions"] > div:first-of-type::after,
        [data-testid="stFileUploaderDropzoneInstructions"] > span:first-of-type::after {{
            content: "Upload your resume and let InternHunt analyze your experience, identify your strengths, and recommend internships tailored to your profile." !important;
            font-size: 15px !important;
            font-weight: 400 !important;
            color: #94A3B8 !important;
            line-height: 1.65 !important;
            display: block !important;
            text-align: center !important;
        }}

        /* Hide the native second child ("50MB per file • PDF") */
        [data-testid="stFileUploaderDropzoneInstructions"] > div:nth-child(2),
        [data-testid="stFileUploaderDropzoneInstructions"] > span:nth-child(2),
        [data-testid="stFileUploaderDropzoneInstructions"] > div:nth-of-type(2),
        [data-testid="stFileUploaderDropzoneInstructions"] > span:nth-of-type(2),
        [data-testid="stFileUploaderDropzoneInstructions"] > div:last-child,
        [data-testid="stFileUploaderDropzoneInstructions"] > span:last-child {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            overflow: hidden !important;
        }}

        /* Divider Line */
        [data-testid="stFileUploaderDropzoneInstructions"]::after {{
            content: "────────────  or  ────────────" !important;
            font-size: 13px !important;
            color: rgba(255, 255, 255, 0.08) !important;
            font-weight: 500 !important;
            margin-bottom: 24px !important;
            letter-spacing: 1px !important;
            display: block !important;
            text-align: center !important;
        }}

        /* Style the Streamlit button element as the CTA block */
        [data-testid="stFileUploader"] button,
        [data-testid="stFileUploader"] button * {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            width: auto !important;
            height: auto !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            font-size: 0 !important;
            color: transparent !important;
            line-height: 0 !important;
            font-family: inherit !important;
        }}
        [data-testid="stFileUploader"] button:hover {{
            background: transparent !important;
            box-shadow: none !important;
            transform: none !important;
        }}
        
        [data-testid="stFileUploader"] button::before {{
            content: "Drop your resume here" !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
            display: block !important;
            margin-bottom: 8px !important;
            font-family: inherit !important;
            line-height: 1.4 !important;
        }}
        
        [data-testid="stFileUploader"] button::after {{
            content: "Browse from your device" !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            color: #818CF8 !important;
            display: block !important;
            line-height: 1.4 !important;
            transition: color 0.2s ease !important;
        }}
        
        [data-testid="stFileUploader"] button:hover::after {{
            color: #A78BFA !important;
            text-decoration: underline !important;
            text-underline-offset: 4px !important;
        }}

        /* Trust Row */
        [data-testid="stFileUploader"] section::after {{
            content: "🔒 Secure upload    •    ✨ AI-powered analysis    •    🛡 Private by design" !important;
            display: block !important;
            font-size: 12px !important;
            color: #475569 !important;
            font-weight: 500;
            margin-top: 32px !important;
            text-align: center !important;
            letter-spacing: 0.2px !important;
        }}

        /* ── Uploaded State Transition ── */
        [data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section::before {{
            content: "" !important;
            width: 48px !important;
            height: 48px !important;
            border-radius: 50% !important;
            background-color: rgba(16, 185, 129, 0.1) !important;
            border: 1.5px solid rgba(16, 185, 129, 0.25) !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2310B981' stroke-width='2.5' stroke-linecap='round'%3E%3Cpolyline points='20 6 9 17 4 12'/%3E%3C/svg%3E") !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            box-shadow: none !important;
            margin-bottom: 20px !important;
            transform: none !important;
        }}
        [data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section:hover::before {{
            transform: none !important;
            box-shadow: none !important;
        }}

        [data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) [data-testid="stFileUploaderDropzoneInstructions"] > div,
        [data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) [data-testid="stFileUploaderDropzoneInstructions"] > span {{
            display: none !important;
        }}

        [data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) [data-testid="stFileUploaderDropzoneInstructions"]::before {{
            content: "Resume Uploaded Successfully" !important;
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #10B981 !important;
            margin-bottom: 8px !important;
            display: block !important;
        }}
        [data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) [data-testid="stFileUploaderDropzoneInstructions"]::after {{
            content: "Preparing AI analysis..." !important;
            font-size: 14px !important;
            color: #94A3B8 !important;
            display: block !important;
            margin-bottom: 24px !important;
        }}

        [data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) button {{
            display: none !important;
        }}
        [data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section::after {{
            display: none !important;
        }}

        [data-testid="stFileUploader"] [data-testid="stUploadedFile"] {{
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: auto !important;
        }}
        [data-testid="stFileUploader"] [data-testid="stUploadedFile"] div {{
            color: #F1F5F9 !important;
            font-size: 14px !important;
            font-weight: 600 !important;
        }}
        
        /* Modern Glass Card Styling */
        .glass-card {{
            background: rgba(20, 26, 53, 0.45) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            margin: 16px 0 !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            position: relative;
            overflow: hidden;
        }}
        .glass-card:hover {{
            transform: translateY(-4px) !important;
            border-color: rgba(99, 102, 241, 0.3) !important;
            box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15), 0 8px 32px 0 rgba(0, 0, 0, 0.45) !important;
        }}
        
        /* Streamlit Container Adjustments */
        .main .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1100px;
            padding-left: 1.25rem;
            padding-right: 1.25rem;
        }}
        
        /* Hide Streamlit Elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {StyleManager.COLORS['gray_100']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {StyleManager.COLORS['gray_300']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {StyleManager.COLORS['gray_400']};
        }}
        
        /* Professional Typography Scale */
        .typography-h1 {{
    font-size: 4rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
}}
        
        .typography-h2 {{
            font-size: 2.25rem;
            font-weight: 700;
            line-height: 1.2;
            letter-spacing: -0.01em;
        }}
        
        .typography-h3 {{
            font-size: 1.875rem;
            font-weight: 600;
            line-height: 1.3;
        }}
        
        .typography-body-large {{
            font-size: 1.125rem;
            line-height: 1.6;
            font-weight: 400;
        }}
        
        .typography-body {{
            font-size: 1rem;
            line-height: 1.6;
            font-weight: 400;
        }}
        
        .typography-caption {{
            font-size: 0.875rem;
            line-height: 1.4;
            font-weight: 500;
        }}
        
        /* Professional Card System */
        .pro-card {{
            background: {StyleManager.COLORS['light_card']};
            border: 1px solid {StyleManager.COLORS['light_border']};
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            transition: all 0.2s ease-in-out;
        }}
        
        .pro-card:hover {{
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transform: translateY(-2px);
        }}
        
        .pro-card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 16px;
            border-bottom: 1px solid {StyleManager.COLORS['gray_200']};
        }}
        
        .pro-card-icon {{
            width: 40px;
            height: 40px;
            background: {StyleManager.COLORS['primary_gradient']};
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-size: 18px;
        }}
        
        .pro-card-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: {StyleManager.COLORS['gray_900']};
            margin: 0;
        }}
        
        /* Professional Button System */
        .pro-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 12px 24px;
            font-size: 0.875rem;
            font-weight: 600;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s ease-in-out;
            gap: 8px;
        }}
        
        .pro-btn-primary {{
            background: {StyleManager.COLORS['primary_gradient']};
            color: white;
            box-shadow: 0 1px 2px 0 rgba(79, 70, 229, 0.05);
        }}
        
        .pro-btn-primary:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px 0 rgba(79, 70, 229, 0.15);
        }}
        
        .pro-btn-secondary {{
            background: {StyleManager.COLORS['gray_100']};
            color: {StyleManager.COLORS['gray_700']};
            border: 1px solid {StyleManager.COLORS['gray_300']};
        }}
        
        .pro-btn-secondary:hover {{
            background: {StyleManager.COLORS['gray_200']};
            border-color: {StyleManager.COLORS['gray_400']};
        }}
        
        .pro-btn-success {{
            background: {StyleManager.COLORS['success']};
            color: white;
        }}
        
        .pro-btn-success:hover {{
            background: {StyleManager.COLORS['accent_dark']};
            transform: translateY(-1px);
        }}
        
        /* Professional Badge System */
        .pro-badge {{
            display: inline-flex;
            align-items: center;
            padding: 6px 12px;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .pro-badge-primary {{
            background: rgba(79, 70, 229, 0.1);
            color: {StyleManager.COLORS['primary_dark']};
        }}
        
        .pro-badge-success {{
            background: rgba(16, 185, 129, 0.1);
            color: {StyleManager.COLORS['accent_dark']};
        }}
        
        .pro-badge-warning {{
            background: rgba(245, 158, 11, 0.1);
            color: #D97706;
        }}
        
        /* Professional Alert System */
        .pro-alert {{
            padding: 16px;
            border-radius: 12px;
            margin: 16px 0;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }}
        
        .pro-alert-info {{
            background: rgba(59, 130, 246, 0.05);
            border: 1px solid rgba(59, 130, 246, 0.2);
            color: #1E40AF;
        }}
        
        .pro-alert-success {{
            background: rgba(16, 185, 129, 0.05);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #047857;
        }}
        
        .pro-alert-warning {{
            background: rgba(245, 158, 11, 0.05);
            border: 1px solid rgba(245, 158, 11, 0.2);
            color: #92400E;
        }}
        
        .pro-alert-error {{
            background: rgba(239, 68, 68, 0.05);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #DC2626;
        }}
        
        /* Layout Improvements */
        .pro-container {{
            max-width: 100%;
            margin: 0 auto;
            padding: 0 16px;
        }}
        
        .pro-grid {{
            display: grid;
            gap: 24px;
        }}
        
        .pro-grid-2 {{
            grid-template-columns: repeat(2, 1fr);
        }}
        
        .pro-grid-3 {{
            grid-template-columns: repeat(3, 1fr);
        }}
        
        @media (max-width: 768px) {{
            .pro-grid-2, .pro-grid-3 {{
                grid-template-columns: 1fr;
            }}
            
            .main .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    @classmethod
    def apply_theme_styles(cls, theme_mode: str):
        """Apply professional theme-specific styles"""
        if theme_mode == "dark":
            st.markdown(f"""
            <style>
            /* Dark Theme - Professional */
            .stApp {{
                background-color: {StyleManager.COLORS['dark_bg']};
                color: #F1F5F9;
            }}
            
            /* Dark Theme Cards */
            .pro-card {{
                background: {StyleManager.COLORS['dark_surface']};
                border-color: {StyleManager.COLORS['dark_border']};
                color: #F1F5F9;
            }}
            
            .pro-card:hover {{
                background: #293548;
                box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }}
            
            .pro-card-header {{
                border-bottom-color: {StyleManager.COLORS['dark_border']};
            }}
            
            .pro-card-title {{
                color: #F1F5F9;
            }}
            
            /* Dark Theme Typography */
            .typography-h1, .typography-h2, .typography-h3 {{
                color: #F8FAFC;
            }}
            
            /* Dark Theme Buttons */
            .pro-btn-secondary {{
                background: {StyleManager.COLORS['dark_card']};
                color: #F1F5F9;
                border-color: {StyleManager.COLORS['dark_border']};
            }}
            
            .pro-btn-secondary:hover {{
                background: {StyleManager.COLORS['dark_border']};
                border-color: #64748B;
            }}
            
            /* Dark Theme Form Elements */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stSelectbox > div > div > select {{
                background-color: {StyleManager.COLORS['dark_surface']};
                border: 1px solid {StyleManager.COLORS['dark_border']};
                color: #F1F5F9;
            }}
            
            /* Dark Theme Sidebar */
            .css-1d391kg {{
                background-color: {StyleManager.COLORS['dark_surface']};
            }}
            
            /* Dark Theme Scrollbar */
            ::-webkit-scrollbar-track {{
                background: {StyleManager.COLORS['dark_surface']};
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {StyleManager.COLORS['dark_border']};
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: #64748B;
            }}
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <style>
            /* Light Theme - Professional */
            .stApp {{
                background: linear-gradient(135deg, {StyleManager.COLORS['light_bg']} 0%, {StyleManager.COLORS['light_surface']} 100%);
                color: {StyleManager.COLORS['gray_900']};
            }}
            
            /* Light Theme Cards */
            .pro-card {{
                background: {StyleManager.COLORS['light_card']};
                border-color: {StyleManager.COLORS['light_border']};
                color: {StyleManager.COLORS['gray_900']};
            }}
            
            .pro-card:hover {{
                background: #FFFFFF;
                box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }}
            
            /* Light Theme Typography */
            .typography-h1, .typography-h2, .typography-h3 {{
                color: {StyleManager.COLORS['gray_900']};
            }}
            
            /* Light Theme Form Elements */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stSelectbox > div > div > select {{
                background-color: {StyleManager.COLORS['light_card']};
                border: 1px solid {StyleManager.COLORS['light_border']};
                color: {StyleManager.COLORS['gray_900']};
            }}
            
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {{
                border-color: {StyleManager.COLORS['primary']};
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
            }}
            
            /* Light Theme Sidebar */
            .css-1d391kg {{
                background-color: {StyleManager.COLORS['light_surface']};
            }}
            </style>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def get_skills_styles():
        """Get professional CSS styles for skills display"""
        return f"""
        <style>
        /* Professional Skills Display */
        .skills-header {{
            display: flex;
            align-items: center;
            margin: 32px 0 24px 0;
            padding: 0 0 16px 0;
            border-bottom: 2px solid {StyleManager.COLORS['primary']};
            position: relative;
        }}
        
        .skills-header::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 60px;
            height: 2px;
            background: {StyleManager.COLORS['primary_gradient']};
        }}
        
        .skills-header-icon {{
            width: 48px;
            height: 48px;
            background: {StyleManager.COLORS['primary_gradient']};
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;
            font-size: 20px;
            color: white;
        }}
        
        .skills-header-text {{
            font-size: 1.5rem;
            font-weight: 700;
            color: inherit;
            margin: 0;
            letter-spacing: -0.01em;
        }}
        
        .skills-container {{
            margin-top: 24px;
            padding: 0;
        }}
        
        .skill-section {{
            margin-bottom: 32px;
        }}
        
        .skill-category {{
            display: flex;
            align-items: center;
            margin: 0 0 16px 0;
            padding: 0 0 12px 0;
            font-weight: 600;
            font-size: 1.125rem;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }}
        
        .category-icon {{
            font-size: 18px;
            margin-right: 12px;
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, {StyleManager.COLORS['gray_100']} 0%, {StyleManager.COLORS['gray_200']} 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .skills-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 24px;
        }}
        
        .skill-tag {{
            display: inline-flex;
            align-items: center;
            padding: 8px 14px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: default;
            position: relative;
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #E2E8F0 !important;
            overflow: hidden;
        }}
        
        .skill-tag::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
            transition: left 0.5s;
        }}
        
        .skill-tag:hover::before {{
            left: 100%;
        }}
        
        /* Glass tag hover states with brand colors */
        .tech-skill:hover {{
            background: rgba(99, 102, 241, 0.15) !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            color: #818CF8 !important;
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.25);
        }}
        
        .hardware-skill:hover {{
            background: rgba(45, 212, 191, 0.12) !important;
            border-color: rgba(45, 212, 191, 0.4) !important;
            color: #2DD4BF !important;
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 0 15px rgba(45, 212, 191, 0.25);
        }}
        
        .soft-skill:hover {{
            background: rgba(139, 92, 246, 0.15) !important;
            border-color: rgba(139, 92, 246, 0.4) !important;
            color: #A78BFA !important;
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.25);
        }}
        
        .data-skill:hover {{
            background: rgba(56, 189, 248, 0.12) !important;
            border-color: rgba(56, 189, 248, 0.4) !important;
            color: #38BDF8 !important;
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
        }}
        
        .design-skill:hover {{
            background: rgba(236, 72, 153, 0.12) !important;
            border-color: rgba(236, 72, 153, 0.4) !important;
            color: #F472B6 !important;
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 0 15px rgba(236, 72, 153, 0.25);
        }}
        
        .business-skill:hover {{
            background: rgba(99, 102, 241, 0.15) !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            color: #818CF8 !important;
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.25);
        }}
        
        .other-skill:hover {{
            background: rgba(148, 163, 184, 0.12) !important;
            border-color: rgba(148, 163, 184, 0.3) !important;
            color: #E2E8F0 !important;
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 0 15px rgba(148, 163, 184, 0.25);
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .skills-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }}
            
            .skills-header-icon {{
                margin-right: 0;
            }}
            
            .skill-tag {{
                font-size: 0.8rem;
                padding: 8px 12px;
            }}
        }}
        </style>
        """
    
    @staticmethod
    def get_job_listing_styles():
        """Get professional CSS styles for job listings"""
        return f"""
        <style>
        /* Professional Job Listing Cards */
        .job-listing {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .job-listing::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: {StyleManager.COLORS['primary_gradient']};
        }}
        
        .job-listing:hover {{
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(79, 70, 229, 0.3);
            transform: translateY(-4px);
            box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.25);
        }}
        
        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }}
        
        .job-title {{
            font-size: 1.375rem;
            font-weight: 700;
            color: #F8FAFC;
            margin: 0 0 8px 0;
            line-height: 1.3;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .job-title-icon {{
            width: 40px;
            height: 40px;
            background: {StyleManager.COLORS['primary_gradient']};
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: white;
        }}
        
        .job-company {{
            font-size: 1rem;
            color: {StyleManager.COLORS['gray_400']};
            font-weight: 500;
            margin-bottom: 4px;
        }}
        
        .job-location {{
            font-size: 0.875rem;
            color: {StyleManager.COLORS['gray_500']};
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .job-info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 20px 0;
        }}
        
        .job-info-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .job-info-icon {{
            width: 32px;
            height: 32px;
            background: {StyleManager.COLORS['primary_gradient']};
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            color: white;
        }}
        
        .job-info-content {{
            flex: 1;
        }}
        
        .job-info-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: {StyleManager.COLORS['gray_400']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 2px;
        }}
        
        .job-info-value {{
            font-size: 0.875rem;
            color: #F1F5F9;
            font-weight: 500;
        }}
        
        .job-description {{
            color: {StyleManager.COLORS['gray_300']};
            line-height: 1.6;
            margin: 20px 0;
            font-size: 0.875rem;
        }}
        
        .job-skills {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 20px 0;
        }}
        
        .job-skill-tag {{
            background: rgba(79, 70, 229, 0.2);
            color: {StyleManager.COLORS['primary_light']};
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(79, 70, 229, 0.3);
        }}
        
        .job-actions {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .job-salary {{
            font-size: 1.125rem;
            font-weight: 700;
            color: {StyleManager.COLORS['success']};
        }}
        
        .apply-button {{
            background: {StyleManager.COLORS['primary_gradient']};
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .apply-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4);
        }}
        
        .apply-button:active {{
            transform: translateY(0);
        }}
        
        .job-match-score {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: {StyleManager.COLORS['success']};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .separator {{
            height: 1px;
            background: linear-gradient(
                to right, 
                transparent, 
                rgba(79, 70, 229, 0.3) 20%, 
                rgba(79, 70, 229, 0.6) 50%, 
                rgba(79, 70, 229, 0.3) 80%, 
                transparent
            );
            margin: 32px 0;
        }}
        
        /* Light theme adjustments */
        [data-theme="light"] .job-listing {{
            background: white;
            border-color: {StyleManager.COLORS['light_border']};
        }}
        
        [data-theme="light"] .job-listing:hover {{
            background: {StyleManager.COLORS['light_surface']};
            box-shadow: 0 20px 40px -12px rgba(79, 70, 229, 0.15);
        }}
        
        [data-theme="light"] .job-title {{
            color: {StyleManager.COLORS['gray_900']};
        }}
        
        [data-theme="light"] .job-info-item {{
            background: {StyleManager.COLORS['light_surface']};
            border-color: {StyleManager.COLORS['light_border']};
        }}
        
        [data-theme="light"] .job-info-value {{
            color: {StyleManager.COLORS['gray_700']};
        }}
        
        [data-theme="light"] .job-description {{
            color: {StyleManager.COLORS['gray_600']};
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .job-info-grid {{
                grid-template-columns: 1fr;
            }}
            
            .job-header {{
                flex-direction: column;
                gap: 12px;
            }}
            
            .job-actions {{
                flex-direction: column;
                gap: 12px;
                align-items: stretch;
            }}
            
            .apply-button {{
                justify-content: center;
            }}
        }}
        </style>
        """
    
    @staticmethod
    def get_animation_styles():
        """Get professional CSS animation styles"""
        return f"""
        <style>
        /* Professional Animations */
        @keyframes fadeSlideIn {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes fadeSlideInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        @keyframes fadeSlideInRight {{
            from {{
                opacity: 0;
                transform: translateX(30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        @keyframes gentleGlow {{
            0%, 100% {{
                box-shadow: 0 0 20px rgba(79, 70, 229, 0.1);
            }}
            50% {{
                box-shadow: 0 0 30px rgba(79, 70, 229, 0.2);
            }}
        }}
        
        @keyframes shimmer {{
            0% {{
                background-position: -1000px 0;
            }}
            100% {{
                background-position: 1000px 0;
            }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.6;
            }}
        }}
        
        @keyframes bounce {{
            0%, 20%, 53%, 80%, 100% {{
                transform: translate3d(0, 0, 0);
            }}
            40%, 43% {{
                transform: translate3d(0, -8px, 0);
            }}
            70% {{
                transform: translate3d(0, -4px, 0);
            }}
            90% {{
                transform: translate3d(0, -2px, 0);
            }}
        }}
        
        /* Animation Classes */
        .animate-fade-in {{
            animation: fadeSlideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .animate-fade-in-left {{
            animation: fadeSlideInLeft 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .animate-fade-in-right {{
            animation: fadeSlideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .animate-delay-100 {{
            animation-delay: 0.1s;
        }}
        
        .animate-delay-200 {{
            animation-delay: 0.2s;
        }}
        
        .animate-delay-300 {{
            animation-delay: 0.3s;
        }}
        
        .animate-delay-400 {{
            animation-delay: 0.4s;
        }}
        
        /* Header Animations */
        .animated-header {{
            animation: fadeSlideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .animated-header:hover {{
            animation: gentleGlow 2s infinite;
        }}
        
        /* Shimmer Effect */
        .shimmer-effect {{
            position: relative;
            overflow: hidden;
        }}
        
        .shimmer-effect::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.1),
                transparent
            );
            animation: shimmer 2s infinite;
        }}
        
        /* Loading Animation */
        .loading-dots {{
            display: inline-flex;
            gap: 4px;
        }}
        
        .loading-dot {{
            width: 8px;
            height: 8px;
            background: {StyleManager.COLORS['primary']};
            border-radius: 50%;
            animation: pulse 1.4s ease-in-out infinite both;
        }}
        
        .loading-dot:nth-child(1) {{
            animation-delay: -0.32s;
        }}
        
        .loading-dot:nth-child(2) {{
            animation-delay: -0.16s;
        }}
        
        /* Hover Animations */
        .hover-lift {{
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .hover-lift:hover {{
            transform: translateY(-2px);
        }}
        
        .hover-scale {{
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .hover-scale:hover {{
            transform: scale(1.02);
        }}
        
        /* Smooth Scrolling */
        .smooth-scroll {{
            scroll-behavior: smooth;
        }}
        
        /* Reduced Motion */
        @media (prefers-reduced-motion: reduce) {{
            *,
            *::before,
            *::after {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}
        </style>
        """
    
    @staticmethod
    def get_scroll_indicator_styles():
        """Get scroll indicator (mouse) animation styles"""
        return """
        <style>
        /* ---------------- SCROLL INDICATOR ---------------- */
        .hero-cta {
            text-align: center;
            margin-top: 40px;
        }

        .scroll-indicator {
            display: inline-block;
            position: relative;
            width: 26px;
            height: 42px;
            border: 2px solid rgba(255, 255, 255, 0.6);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .scroll-indicator::before {
            content: '';
            position: absolute;
            top: 6px;
            left: 50%;
            transform: translateX(-50%);
            width: 4px;
            height: 8px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 2px;
            animation: mouse-scroll 2s infinite;
            -webkit-animation: mouse-scroll 2s infinite;
        }

        .scroll-indicator:hover {
            border-color: #fff;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
        }

        @keyframes mouse-scroll {
            0% { opacity: 1; transform: translateX(-50%) translateY(0); }
            100% { opacity: 0; transform: translateX(-50%) translateY(20px); }
        }

        @-webkit-keyframes mouse-scroll {
            0% { opacity: 1; transform: translateX(-50%) translateY(0); }
            100% { opacity: 0; transform: translateX(-50%) translateY(20px); }
        }
        </style>
        """
    
    @staticmethod
    def get_hero_section(font_b64=""):
        """Get complete hero section with CSS and HTML markup
        
        Args:
            font_b64: Base64 encoded font data for Nevera font
            
        Returns:
            str: Complete HTML/CSS for hero section
        """
        return f"""
        <style>
        /* ---------------- CUSTOM FONT ---------------- */
        @font-face {{
            font-family: 'Nevera';
            src: url('data:application/x-font-opentype;base64,{font_b64}') format('opentype'),
                 url('data:font/otf;base64,{font_b64}') format('opentype');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }}
        
        /* ---------------- HERO SECTION ---------------- */
        .hero-section {{
            position: relative;
            background: radial-gradient(120% 160% at 50% 10%, #0e132a 20%, #0b1028 100%);
            padding: 40px 20px 80px;
            text-align: center;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 8px 40px rgba(0,0,0,0.25);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .hero-section:hover {{
            transform: scale(1.005);
            box-shadow: 0 12px 45px rgba(0,0,0,0.3);
        }}

        /* Subtle background animation with moving gradient */
        .hero-section::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg, rgba(124,58,237,0.1), rgba(45,212,191,0.1), rgba(124,58,237,0.1), rgba(45,212,191,0.1));
            background-size: 200% 200%;
            animation: moveGradient 10s ease-in-out infinite alternate;
            z-index: 0;
        }}

        @keyframes moveGradient {{
            0% {{ background-position: 0% 50%; }}
            100% {{ background-position: 100% 50%; }}
        }}

        /* Glow halo */
        .hero-section::after {{
            content: "";
            position: absolute;
            top: -150px;
            left: 50%;
            transform: translateX(-50%);
            width: 1000px;
            height: 1000px;
            background: radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.1), rgba(99, 102, 241, 0.05) 70%, transparent 100%);
            filter: blur(120px);
            z-index: 0;
            animation: pulseGlow 8s ease-in-out infinite alternate;
        }}

        @keyframes pulseGlow {{
            0% {{ opacity: 0.8; transform: translateX(-50%) scale(1); }}
            100% {{ opacity: 1; transform: translateX(-50%) scale(1.08); }}
        }}

        /* ============ UNIFIED ANIMATIONS ============ */
        /* Smooth fade-up animation with cubic-bezier easing */
        @keyframes fadeUp {{
            0% {{ opacity: 0; transform: translateY(40px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}

        /* ---------------- TEXT STYLING ---------------- */
        .hero-badge {{
            display: inline-block;
            background: rgba(99,102,241,0.15);
            border: 1px solid rgba(99,102,241,0.3);
            box-shadow: inset 0 0 10px rgba(255,255,255,0.05);
            backdrop-filter: blur(15px);
            color: #a5b4fc;
            padding: 8px 20px;
            border-radius: 50px;
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 28px;
            letter-spacing: 0.5px;
            text-shadow: 0 0 10px rgba(165,180,252,0.3);
            animation: fadeUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            z-index: 2;
        }}
        
        .hero-branding {{
            font-family: 'Nevera', 'Helvetica Neue', Arial, sans-serif !important;
            font-size: 5.5rem;
            font-weight: 400;
            color: #fff;
            margin-bottom: 25px;
            margin-top: 20px;
            letter-spacing: 0.18em;
            animation: fadeUp 1s cubic-bezier(0.4, 0, 0.2, 1), gradientFlow 6s ease-in-out infinite alternate;
            position: relative;
            z-index: 2;
            text-transform: uppercase;
            font-feature-settings: 'kern' 1;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            background: linear-gradient(100deg, #8b5cf6, #2dd4bf, #38bdf8, #8b5cf6);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        @keyframes gradientFlow {{
            0% {{ background-position: 0% 50%; }}
            100% {{ background-position: 100% 50%; }}
        }}

        .hero-title {{
            font-family: 'Inter', sans-serif;
            font-size: 2.8rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 20px;
            line-height: 1.2;
            letter-spacing: -0.02em;
            animation: fadeUp 1.1s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            z-index: 2;
        }}

        .hero-title span {{
            color: #2cb67d;
            background: linear-gradient(135deg, #7f5af0, #2cb67d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .hero-desc {{
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            font-weight: 400;
            color: #94a3b8;
            max-width: 700px;
            margin: 0 auto 30px;
            line-height: 1.7;
            letter-spacing: 0.01em;
            padding: 0 10px;
            text-align: center;
            position: relative;
            z-index: 2;
        }}

        /* Scroll target for upload section */
        #upload-section {{
            scroll-margin-top: 20px;
        }}

        /* ---------------- RESPONSIVE DESIGN ---------------- */
        @media (max-width: 1024px) {{
            .hero-section {{ padding: 40px 20px 80px; }}
            .hero-branding {{ font-size: 4rem; }}
            .hero-title {{ font-size: 2.1rem; line-height: 1.2; }}
            .hero-desc {{ font-size: 1rem; max-width: 600px; line-height: 1.6; }}
            .hero-badge {{ font-size: 0.85rem; }}
            .cta-button {{ font-size: 1rem; padding: 12px 32px; }}
        }}

        @media (max-width: 768px) {{
            .hero-section {{ padding: 35px 16px 65px; }}
            .hero-branding {{ font-size: 3rem; letter-spacing: 0.12em; }}
            .hero-title {{ font-size: 1.7rem; line-height: 1.25; }}
            .hero-desc {{ font-size: 0.95rem; max-width: 100%; padding: 0 10px; line-height: 1.6; }}
            .hero-badge {{ font-size: 0.8rem; padding: 6px 16px; }}
            .cta-button {{ font-size: 0.95rem; padding: 12px 28px; margin-top: 24px; }}
        }}

        @media (max-width: 480px) {{
            .hero-section {{ padding: 30px 12px 55px; }}
            .hero-branding {{ font-size: 2.2rem; }}
            .hero-title {{ font-size: 1.6rem; line-height: 1.3; }}
            .hero-desc {{ font-size: 0.95rem; line-height: 1.6; }}
            .hero-badge {{ font-size: 0.75rem; padding: 5px 14px; }}
        }}
        </style>

        <!-- HERO SECTION -->
        <div class="hero-section">
            <div class="hero-badge">⚡ Intelligent Internship Matching Using ML, APIs & Web Data</div>
            <div class="hero-branding">INTERNHUNT</div>
            <h1 class="hero-title">Find Internships That <span>Fit You</span></h1>
            <div class="hero-cta">
                <a href="#upload-section" class="scroll-indicator" title="Scroll down to upload"></a>
            </div>
        </div>
        """
    
    @staticmethod
    def get_streamlit_component_overrides():
        """Get CSS overrides for Streamlit components with dark theme styling
        
        Returns:
            str: CSS for overriding default Streamlit component styles
        """
        return """
        <style>
            :root {
                --primary: #6366F1;
                --primary-light: #818CF8;
                --primary-dark: #4F46E5;
                --secondary: #8B5CF6;
                --accent: #10B981;
                --dark-bg: #0A0E27;
                --dark-surface: #141A35;
                --dark-card: #1A1F3A;
                --dark-border: #2D3748;
                --text-primary: #F8FAFC;
                --text-secondary: #9CA3AF;
                --gradient-primary: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
                --gradient-secondary: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
                --glow-primary: 0 0 20px rgba(99, 102, 241, 0.3);
                --glow-secondary: 0 0 30px rgba(139, 92, 246, 0.4);
            }
            
            /* Hide empty style-only element containers to prevent flex layout gap spacing */
            .element-container:has(style):not(:has(p, span, h1, h2, h3, h4, h5, h6, img, button, a)),
            .element-container:has(div[data-testid="stMarkdownContainer"] > style:only-child) {
                display: none !important;
            }
            
            /* Reduce top padding of main container */
            div.stMainBlockContainer.block-container {
                padding-top: 6rem !important;
                padding-bottom: 2rem !important;
            }

            /* Base styles with animations */
            .stApp {
                background: linear-gradient(135deg, #0A0E27 0%, #0F1532 50%, #141A35 100%);
                color: var(--text-primary);
                background-attachment: fixed;
            }
            
            /* Sidebar */
            .css-1d391kg, .e1fqkh3o3 {
                background: linear-gradient(180deg, #141A35 0%, #1A1F3A 100%) !important;
                border-right: 1px solid rgba(99, 102, 241, 0.1) !important;
            }
            
            /* File uploader */
            .stFileUploader > div > div > div > button {
                background: var(--primary);
                color: white !important;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                transition: all 0.2s ease;
            }
            
            .stFileUploader > div > div > div > button:hover {
                background: var(--primary-light);
                transform: translateY(-1px);
            }
            
            /* File uploader text */
            .stFileUploader > div > div > div > div > div > div {
                color: #E2E8F0 !important;  /* Lighter text color for better visibility */
                background-color: #1E293B;   /* Dark background for the text area */
                padding: 8px 12px;          /* Add some padding around the text */
                border-radius: 4px;          /* Rounded corners */
                border: 1px solid #475569;   /* Subtle border */
                margin-top: 4px;            /* Add some space above the text */
            }
            
            .stFileUploader > div > div > div > div > div > div::before {
                color: #E2E8F0 !important;  /* Lighter color for the icon */
                margin-right: 8px;          /* Add space between icon and text */
            }
            
            .stFileUploader > div > div > div > div > div > div::after {
                color: #E2E8F0 !important;  /* Lighter color for any after content */
            }
            
            /* Make the file name more visible */
            .stFileUploader > div > div > div > div > div > div > span {
                color: #E2E8F0 !important;
                font-weight: 500;           /* Slightly bolder text */
            }
            
            /* Buttons - Professional Styling */
            .stButton > button {
                background: var(--gradient-primary);
                color: white;
                border: 2px solid transparent;
                border-radius: 10px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                font-weight: 600;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
                position: relative;
                overflow: hidden;
            }
            
            .stButton > button::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.1);
                transform: translate(-50%, -50%);
                transition: width 0.6s, height 0.6s;
            }
            
            .stButton > button:hover {
                background: var(--gradient-secondary);
                box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4), var(--glow-secondary);
                transform: translateY(-2px);
            }
            
            .stButton > button:hover::before {
                width: 300px;
                height: 300px;
            }
            
            .stButton > button:active {
                transform: translateY(0);
                box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
            }
            
            /* Input fields - Enhanced */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea {
                background-color: rgba(26, 31, 58, 0.8);
                color: var(--text-primary);
                border: 2px solid rgba(99, 102, 241, 0.2);
                border-radius: 10px;
                transition: all 0.3s ease;
                padding: 12px 16px !important;
                font-size: 14px;
            }
            
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {
                border-color: #6366F1;
                box-shadow: 0 0 20px rgba(99, 102, 241, 0.3), inset 0 0 10px rgba(99, 102, 241, 0.1);
                background-color: rgba(26, 31, 58, 1);
            }
            
            /* Select boxes - Enhanced */
            .stSelectbox > div > div > div {
                background-color: rgba(26, 31, 58, 0.8);
                color: var(--text-primary);
                border: 2px solid rgba(99, 102, 241, 0.2);
                border-radius: 10px;
                transition: all 0.3s ease;
            }
            
            .stSelectbox > div > div > div:hover {
                border-color: #6366F1;
                background-color: rgba(26, 31, 58, 1);
                box-shadow: 0 0 15px rgba(99, 102, 241, 0.2);
            }
            
            /* Hide empty Streamlit style-only containers to remove layout gaps */
            div[data-testid="stElementContainer"]:has(style:only-child) {
                display: none !important;
            }
        </style>
        """
    
    @staticmethod
    def get_sidebar_chat_styles():
        """Get CSS styles for sidebar chat interface
        
        Returns:
            str: CSS for sidebar chat components (messages, chips, scrollbar)
        """
        return f"""
        <style>
        /* Professional Sidebar Styles */
        .sb-chat-title {{
            font-weight: 700; 
            font-size: 1.125rem; 
            margin-bottom: 12px;
            color: inherit;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .sb-chip {{
            display: inline-block; 
            padding: 8px 12px; 
            border-radius: 20px; 
            font-size: 0.75rem; 
            font-weight: 600;
            margin-right: 8px; 
            margin-bottom: 6px;
            background: {StyleManager.COLORS['primary_gradient']};
            color: white;
            border: none;
            transition: all 0.2s ease;
        }}
        
        .sb-chip:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(79, 70, 229, 0.3);
        }}
        
        .msg-wrap {{
            max-height: 60vh; 
            overflow-y: auto; 
            padding-right: 6px;
            margin: 16px 0;
        }}
        
        .msg {{
            margin: 10px 0; 
            padding: 12px 16px; 
            border-radius: 16px; 
            line-height: 1.4;
            font-size: 0.875rem;
            transition: all 0.2s ease;
        }}
        
        .msg:hover {{
            transform: translateY(-1px);
        }}
        
        .msg-user {{
            background: {StyleManager.COLORS['primary_gradient']}; 
            color: white;
            border: none;
            margin-left: 20px;
            border-bottom-right-radius: 6px;
        }}
        
        .msg-assist {{
            background: rgba(255, 255, 255, 0.08); 
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: inherit;
            margin-right: 20px;
            border-bottom-left-radius: 6px;
            backdrop-filter: blur(8px);
        }}
        
        .msg-role {{
            font-size: 0.625rem; 
            opacity: 0.7; 
            margin-bottom: 4px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Sidebar scrollbar */
        .msg-wrap::-webkit-scrollbar {{
            width: 6px;
        }}
        
        .msg-wrap::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 3px;
        }}
        
        .msg-wrap::-webkit-scrollbar-thumb {{
            background: {StyleManager.COLORS['primary_gradient']};
            border-radius: 3px;
        }}
        
        .msg-wrap::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, {StyleManager.COLORS['primary_light']} 0%, {StyleManager.COLORS['primary_dark']} 100%);
        }}

        /* Sidebar Navigation Menu */
        .sidebar-nav {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-top: 15px;
            margin-bottom: 25px;
            font-family: 'Inter', sans-serif;
            width: 100%;
        }}
        
        .sidebar-nav .nav-title {{
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
            padding-left: 8px;
        }}
        
        .sidebar-nav .nav-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-radius: 10px;
            color: #94a3b8 !important;
            text-decoration: none !important;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.25s ease;
            border: 1px solid transparent;
            cursor: pointer;
        }}
        
        .sidebar-nav .nav-item:hover {{
            color: #f8fafc !important;
            background: rgba(255, 255, 255, 0.04);
            border-color: rgba(255, 255, 255, 0.06);
            text-decoration: none !important;
        }}
        
        .sidebar-nav .nav-item.active {{
            color: #fff !important;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2)) !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
        }}
        </style>
        """
    
    @staticmethod
    def get_course_card_styles():
        """Get CSS styles for course catalog cards
        
        Returns:
            str: CSS for course cards, buttons, badges, and animations
        """
        return """
        <style>
        @keyframes fadeInUp {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        .course-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.25);
            animation: fadeInUp 0.5s ease-out;
            transition: all 0.3s ease;
        }
        
        .course-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        .course-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }
        
        .course-header h3 {
            font-size: 1.1rem;
            margin-bottom: 6px;
            color: #e0e7ff;
        }
        
        .course-title {
            color: #E6EAF3;
            font-size: 18px;
            font-weight: 800;
            margin: 0;
        }
        
        .provider {
            font-size: 0.9rem;
            color: rgba(255,255,255,0.6);
            margin-bottom: 10px;
        }
        
        .summary {
            font-size: 0.9rem;
            color: rgba(255,255,255,0.7);
            margin-bottom: 15px;
            line-height: 1.55;
        }
        
        .course-btn {
            display: inline-block;
            padding: 6px 12px;
            font-size: 0.85rem;
            color: #a78bfa;
            border: 1px solid rgba(167,139,250,0.3);
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.3s ease;
            font-weight: 700;
        }
        
        .course-btn:hover {
            background: linear-gradient(90deg, #7c3aed, #2dd4bf);
            color: white;
            border-color: transparent;
            box-shadow: 0 8px 18px rgba(99,102,241,0.2);
        }
        
        .badge {
            background: linear-gradient(90deg, #7c3aed, #2dd4bf);
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            margin-right: 8px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-weight: 800;
        }
        </style>
        """
    
    @staticmethod
    def get_chat_styles():
        """Get professional CSS styles for enhanced chat interface"""
        return f"""
        <style>
        /* Professional Chat Container */
        .chat-container {{
            background: linear-gradient(135deg, {StyleManager.COLORS['dark_surface']} 0%, {StyleManager.COLORS['dark_bg']} 100%);
            border-radius: 20px;
            padding: 28px;
            margin: 24px 0;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(16px);
            animation: fadeSlideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        /* Professional Chat Header */
        .chat-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            padding-bottom: 20px;
            border-bottom: 2px solid {StyleManager.COLORS['primary']};
            position: relative;
        }}
        
        .chat-header::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 80px;
            height: 2px;
            background: {StyleManager.COLORS['primary_gradient']};
        }}
        
        .chat-title {{
            display: flex;
            align-items: center;
            gap: 16px;
            color: #F8FAFC;
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }}
        
        .chat-avatar {{
            width: 48px;
            height: 48px;
            background: {StyleManager.COLORS['primary_gradient']};
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: white;
            box-shadow: 0 8px 16px -4px rgba(79, 70, 229, 0.4);
        }}
        
        /* Professional Chat Status */
        .chat-status {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 16px;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.28);
            border-radius: 24px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .chat-status .status-online {{ color: #22c55e; text-shadow: 0 0 6px rgba(34, 197, 94, 0.35); }}
        .chat-status span {{ color: #22c55e; }}
        .status-online {{ color: #22c55e; animation: statusPulse 1.2s ease-in-out infinite; }}
        
        .status-dot {{
            width: 10px;
            height: 10px;
            background: {StyleManager.COLORS['success']};
            border-radius: 50%;
            animation: statusPulse 2s infinite;
        }}
        
        @keyframes statusPulse {{
            0%, 100% {{ 
                opacity: 1; 
                transform: scale(1);
            }}
            50% {{ 
                opacity: 0.6; 
                transform: scale(1.1);
            }}
        }}
        
        /* Professional Message Bubbles */
        .message-container {{
            margin: 20px 0;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        
        .message-user {{
            align-self: flex-end;
            max-width: 75%;
        }}
        
        .message-assistant {{
            align-self: flex-start;
            max-width: 85%;
        }}
        
        .message-bubble {{
            padding: 16px 20px;
            border-radius: 20px;
            position: relative;
            word-wrap: break-word;
            line-height: 1.5;
            font-size: 0.875rem;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .message-bubble.user {{
            background: {StyleManager.COLORS['primary_gradient']};
            color: white;
            border-bottom-right-radius: 8px;
            box-shadow: 0 4px 12px -2px rgba(79, 70, 229, 0.25);
        }}
        
        .message-bubble.assistant {{
            background: rgba(255, 255, 255, 0.08);
            color: #F1F5F9;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-bottom-left-radius: 8px;
            backdrop-filter: blur(8px);
        }}
        
        .message-bubble:hover {{
            transform: translateY(-1px);
        }}
        
        .message-time {{
            font-size: 0.625rem;
            opacity: 0.6;
            margin-top: 6px;
            text-align: right;
            font-weight: 500;
        }}
        
        .message-assistant .message-time {{
            text-align: left;
        }}
        
        /* Professional Typing Indicator */
        .typing-indicator {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            border-bottom-left-radius: 8px;
            max-width: 85%;
            margin: 20px 0;
            backdrop-filter: blur(8px);
        }}
        
        .typing-text {{
            color: {StyleManager.COLORS['gray_300']};
            font-size: 0.875rem;
            font-weight: 500;
        }}
        
        .typing-dots {{
            display: flex;
            gap: 6px;
        }}
        
        .typing-dot {{
            width: 10px;
            height: 10px;
            background: {StyleManager.COLORS['primary']};
            border-radius: 50%;
            animation: typingAnimation 1.4s ease-in-out infinite;
        }}
        
        .typing-dot:nth-child(1) {{ animation-delay: -0.32s; }}
        .typing-dot:nth-child(2) {{ animation-delay: -0.16s; }}
        .typing-dot:nth-child(3) {{ animation-delay: 0s; }}
        
        @keyframes typingAnimation {{
            0%, 60%, 100% {{ 
                transform: translateY(0) scale(0.8); 
                opacity: 0.5; 
            }}
            30% {{ 
                transform: translateY(-8px) scale(1); 
                opacity: 1; 
            }}
        }}
        
        /* Professional Suggested Questions */
        .suggested-questions {{
            margin: 24px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.04);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(8px);
        }}
        
        .suggested-questions h4 {{
            color: #F8FAFC;
            margin-bottom: 16px;
            font-size: 0.875rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .suggested-questions h4::before {{
            content: '💡';
            font-size: 1rem;
        }}
        
        .question-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .question-chip {{
            padding: 10px 16px;
            background: rgba(79, 70, 229, 0.15);
            border: 1px solid rgba(79, 70, 229, 0.3);
            border-radius: 24px;
            color: {StyleManager.COLORS['primary_light']};
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .question-chip:hover {{
            background: rgba(79, 70, 229, 0.25);
            border-color: rgba(79, 70, 229, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px -2px rgba(79, 70, 229, 0.3);
        }}
        
        /* Professional Chat Controls */
        .chat-controls {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin: 20px 0;
            padding: 16px 20px;
            background: rgba(255, 255, 255, 0.04);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(8px);
        }}
        
        .control-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .control-label {{
            color: #F1F5F9;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Enhanced Chat Input */
        .stChatInput > div > div {{
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 16px !important;
            backdrop-filter: blur(8px);
        }}
        
        .stChatInput > div > div:focus-within {{
            border-color: {StyleManager.COLORS['primary']} !important;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
        }}
        
        .stChatInput input {{
            color: #F1F5F9 !important;
            background: transparent !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
        }}
        
        .stChatInput input::placeholder {{
            color: rgba(241, 245, 249, 0.5) !important;
        }}
        
        /* Professional Scrollbar */
        .chat-messages {{
            max-height: 60vh;
            overflow-y: auto;
            padding-right: 8px;
        }}
        
        .chat-messages::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .chat-messages::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }}
        
        .chat-messages::-webkit-scrollbar-thumb {{
            background: {StyleManager.COLORS['primary_gradient']};
            border-radius: 8px;
        }}
        
        .chat-messages::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, {StyleManager.COLORS['primary_light']} 0%, {StyleManager.COLORS['primary_dark']} 100%);
        }}
        
        /* Section dividers */
        .section-divider, .section-divider-lg {{
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            margin: 40px 0;
        }}
        .section-divider-lg {{ height: 2px; opacity: 0.9; }}
        
        /* Sticky chat input */
        .chat-input {{
            position: sticky;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            padding: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            z-index: 10;
        }}
        
        /* Light Theme Adjustments */
        [data-theme="light"] .chat-container {{
            background: linear-gradient(135deg, {StyleManager.COLORS['light_card']} 0%, {StyleManager.COLORS['light_surface']} 100%);
            border-color: {StyleManager.COLORS['light_border']};
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
        }}
        
        [data-theme="light"] .chat-title {{
            color: {StyleManager.COLORS['gray_900']};
        }}
        
        [data-theme="light"] .message-bubble.assistant {{
            background: {StyleManager.COLORS['light_surface']};
            color: {StyleManager.COLORS['gray_700']};
            border-color: {StyleManager.COLORS['light_border']};
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .chat-container {{
                padding: 20px 16px;
                margin: 16px 0;
            }}
            
            .chat-header {{
                flex-direction: column;
                gap: 12px;
                align-items: flex-start;
            }}
            
            .message-user, .message-assistant {{
                max-width: 90%;
            }}
            
            .chat-controls {{
                flex-direction: column;
                gap: 12px;
            }}
        }}
        </style>
        """
