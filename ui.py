import streamlit as st

def add_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
        }
        .main {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .content {
            flex: 1;
        }
        .footer {
            display: flex;
            justify-content: space-between;
            padding: 2rem 3rem;
            margin-top: auto;
            border-top: 1px solid #555;
            font-size: 0.9rem;
            color: #ccc;
            flex-wrap: wrap;
        }
        .footer-section {
            flex: 1;
            min-width: 300px;
            padding: 0 1rem;
        }
        .footer h3 {
            margin-top: 0;
            color: #fff;
        }
        .footer p {
            margin: 0.2rem 0;
        }
        .footer a {
            color: #4dd0e1;
            text-decoration: none;
        }
        </style>
    """, unsafe_allow_html=True)

def add_footer():
    st.markdown(
        """
        <style>
            .main {
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }
            .content {
                flex: 1;
            }
            .footer-container {
                display: flex;
                justify-content: space-between;
                padding: 3rem 2rem;
                margin-top: 50px;
                border-top: 1px solid #555;
                flex-wrap: wrap;
                color: white;
            }
            .footer-section {
                flex: 1;
                padding: 0 2rem;
                min-width: 300px;
            }
            .footer-section h3 {
                font-size: 1.4rem;
                margin-bottom: 0.5rem;
            }
            .footer-section p {
                margin: 0.2rem 0;
            }
            .footer-section a {
                color: #00bfa5;
                text-decoration: none;
            }
        </style>

        <div class="footer-container">
            <div class="footer-section">
                <h3>📬 Contact Us</h3>
                <p><b>Email:</b> <a href="mailto:internhunt@support.com">internhunt@support.com</a></p>
                <p><b>Phone:</b> +91-9876543210</p>
                <p><b>Location:</b> Greater Noida, India</p>
            </div>
            <div class="footer-section">
                <h3>🔐 Privacy Policy</h3>
                <p>We do not store your resume or any personal data.</p>
                <p>All processing is handled securely through trusted APIs.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

