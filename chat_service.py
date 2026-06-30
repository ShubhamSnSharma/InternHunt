"""
Gemini AI Chatbot Service for Career Coaching

Features:
- Powered by Google's Gemini AI
- Cloud-based AI responses
- Enhanced error handling
- Conversation context management
- Resume-aware responses
- Streaming support

Environment Variables (required):
- GEMINI_API_KEY: Your Google Gemini API key
- GEMINI_MODEL: Model to use (default: gemini-1.5-flash)
"""
from __future__ import annotations

import os
import re
import json
import time
from typing import List, Dict, Any, Optional, Tuple, Generator
from dotenv import load_dotenv
import random
import google.generativeai as genai

def _get_gemini_config() -> Tuple[str, str]:
    """Read Gemini API key and model from env variables or Streamlit secrets."""
    try:
        # Load .env each time so changes in UI take effect on rerun
        load_dotenv(override=True)
        # Prefer environment, then Streamlit secrets (for Streamlit Cloud)
        try:
            import streamlit as st  # type: ignore
            st_secrets = getattr(st, 'secrets', None)
        except Exception:
            st_secrets = None
        api_key = (os.getenv("GEMINI_API_KEY") or
                   (st_secrets.get('GEMINI_API_KEY') if st_secrets else None) or
                   "").strip()
        model = (os.getenv("GEMINI_MODEL") or
                 (st_secrets.get('GEMINI_MODEL') if st_secrets else None) or
                 "gemini-1.5-flash").strip()

        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("Gemini API key not found in environment variables or Streamlit secrets")

        return api_key, model

    except Exception as e:
        print(f"Error in _get_gemini_config: {str(e)}")
        raise

# Enhanced system prompt with resume context integration
SYSTEM_PROMPT_BASE = """
You are a friendly career mentor helping someone with their job search. Be conversational, warm, and practical.

## Resume Context
{resume_context}

## Communication Style
- Write naturally like you're texting a friend who asked for career advice
- NO asterisks, NO bold markers (***), NO excessive formatting
- Use simple bullet points with dashes (-) or emojis when listing things
- Keep responses under 150 words unless asked for detail
- Be encouraging but honest
- Use "you/your" to make it personal

## Response Structure
1. Start with a friendly acknowledgment ("Great question!" / "I see where you're coming from")
2. Give 2-3 specific recommendations based on their skills
3. End with ONE actionable next step

## Example Good Response:
"Great question! Based on your background in embedded systems and VLSI, here are my top recommendations:

- Focus on RTOS like FreeRTOS - it's huge in embedded roles
- Learn Git if you haven't already - version control is essential
- Pick up basic data structures and algorithms

Start with an online RTOS tutorial this week. It'll make you way more competitive for firmware roles. Let me know if you need course recommendations! 🚀"
"""

def _format_conversational_response(text: str) -> str:
    """Format the response to be more conversational and friendly"""
    try:
        # Clean up any excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text.strip())
        
        # Replace formal phrases with more conversational ones
        replacements = {
            "I would like to": "I'd like to",
            "it is important": "it's important",
            "do not": "don't",
            "cannot": "can't",
            "I will": "I'll"
        }
        
        for formal, informal in replacements.items():
            text = text.replace(formal, informal)
        
        # Ensure proper spacing after section headers
        text = re.sub(
            r'(🔍 |🎯 |📝 |💡 |💬 )', 
            '\n\1', 
            text
        )
        
        # Add a friendly sign-off if none exists
        if not any(phrase in text.lower() for phrase in ['good luck', 'best of luck', 'hope this helps', 'let me know', 'feel free']):
            sign_offs = [
                "\n\nHope this helps! Let me know if you have any other questions. 😊",
                "\n\nFeel free to ask if you need any clarification! 👍",
                "\n\nLet me know how else I can assist you! 🚀"
            ]
            text += random.choice(sign_offs)
        
        # Add occasional emojis for friendliness
        emoji_map = [
            (r'\b(great|excellent|awesome|perfect)\b', '😊'),
            (r'\b(help|assist|support|guide)\b', '🤝'),
            (r'\b(thank|thanks|appreciate)\b', '🙏'),
            (r'\b(idea|suggestion|recommendation)\b', '💡')
        ]
        
        for pattern, emoji in emoji_map:
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, f"\\1 {emoji}", text, flags=re.IGNORECASE)
            
        return text.strip()
    except Exception as e:
        print(f"Error formatting response: {e}")
        return text  # Return original if formatting fails

def check_gemini_health() -> Dict[str, Any]:
    """Check if Gemini API is accessible and configured properly"""
    try:
        api_key, model = _get_gemini_config()
        
        if not api_key or api_key == "your_gemini_api_key_here":
            return {
                "status": "error",
                "error": "Gemini API key not configured. Please set GEMINI_API_KEY in your environment variables.",
                "model": model
            }
        
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Test the connection with a simple request
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content("Hello, this is a test.")
        
        return {
            "status": "healthy",
            "model": model,
            "api_key_configured": True,
            "test_response": "Connection successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "model": _get_gemini_config()[1]
        }

def chat_gemini(messages: List[Dict[str, str]], resume_context: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
    """
    Send a chat to Gemini and return a personalized response using resume context.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        resume_context: Context from the user's resume (skills, experience, etc.)
        system_prompt: Optional custom system prompt
        
    Returns:
        str: The generated response with personalized career advice
    """
    try:
        # Get API configuration
        api_key, model_name = _get_gemini_config()
        
        if not api_key or api_key == "your_gemini_api_key_here":
            return "I need a Gemini API key to work. Please configure GEMINI_API_KEY in your environment variables."
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Prepare the conversation for Gemini
        model = genai.GenerativeModel(model_name)
        
        # Prepare system prompt with resume context
        sys_prompt = system_prompt or SYSTEM_PROMPT_BASE
        
        # Format resume context if available
        formatted_context = "No resume information available. Ask the user to upload their resume for personalized advice."
        if resume_context and len(resume_context) > 10:  # Basic check for meaningful content
            # Truncate context if it's excessively long (approx 12k chars ~ 3k tokens)
            # Gemini 1.5 Flash has huge context, but we keep it reasonable for latency
            if len(resume_context) > 12000:
                formatted_context = resume_context[:12000] + "\n...[truncated]"
            else:
                formatted_context = resume_context
        
        # Inject resume context into the system prompt
        sys_prompt = sys_prompt.format(resume_context=formatted_context)
        
        # Build conversation history
        # Gemini 1.5 Flash has a large context window, so we can include more history
        history = []
        # Include last 10 messages (5 turns)
        for msg in messages[-10:]:
            role = msg.get("role", "user")
            content = (msg.get("content", "") or "").strip()
            if not content:
                continue
            prefix = "User" if role == "user" else "Assistant"
            history.append(f"{prefix}: {content}")
        history_text = "\n".join(history) if history else "User: Hello"
        
        # Single API call per question
        prompt = (
            f"{sys_prompt}\n\n"
            f"Candidate Profile Context (use this to personalize your answer):\n{formatted_context}\n\n"
            f"Conversation History:\n{history_text}\n\n"
            f"IMPORTANT: Answer the user's LATEST question from the history above. Do not just summarize the resume unless asked.\n"
            f"Assistant:"
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=4096,  # Significantly increased from 1024
            ),
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
            ]
        )
        
        # Check if response was blocked by safety filters
        if response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason'):
            return "⚠️ I couldn't process that request due to content safety filters. Please try rephrasing your question in a different way."
        
        # Check finish reason
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                # finish_reason: 1=STOP (normal), 2=MAX_TOKENS, 3=SAFETY, 4=RECITATION, 5=OTHER
                if candidate.finish_reason == 3:  # SAFETY
                    return "⚠️ The response was blocked by safety filters. Please rephrase your question."
                elif candidate.finish_reason == 2:  # MAX_TOKENS
                    # Instead of erroring, return what we have so far
                    partial_text = ""
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                         text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                         partial_text = ''.join(text_parts)
                    return _format_conversational_response(partial_text + "\n\n[Response truncated due to length]")
                elif candidate.finish_reason not in [1, 0]:  # Not STOP or UNSPECIFIED
                    return "⚠️ I encountered an issue generating the response. Please try again with a different question."
        
        # Format the response
        if response and hasattr(response, 'text'):
            try:
                return _format_conversational_response(response.text)
            except ValueError as e:
                # response.text failed - try accessing parts directly
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                        if text_parts:
                            return _format_conversational_response(''.join(text_parts))
                return "⚠️ I couldn't generate a proper response. Please try rephrasing your question."
        else:
            return "I'm having trouble generating a response right now. Could you try rephrasing your question?"
            
    except Exception as e:
        error_msg = str(e).lower()
        print(f"Gemini API Error: {str(e)}")  # Debug log
        
        # More detailed error handling
        if "api_key" in error_msg or "API key" in str(e):
            return "🔑 There's an issue with the API key configuration. Please check your Gemini API key in the .env file and ensure it's valid."
            
        if "quota" in error_msg or "limit" in error_msg:
            return "⚠️ I've reached my usage limit for now. Please try again later or check your API quota at https://ai.google.dev/"
            
        if "unavailable" in error_msg or "500" in str(e):
            return "🔌 The AI service is temporarily unavailable. Please try again in a few moments."
            
        if "timeout" in error_msg or "timed out" in error_msg:
            return "⏱️ The request timed out. Please check your internet connection and try again."
            
        # For other errors, provide more context
        print(f"Full error details: {str(e)}")
        return f"❌ I encountered an error: {str(e)[:200]}... Please try again or rephrase your question."

def chat_gemini_streaming(messages: List[Dict[str, str]], resume_context: Optional[str] = None, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
    """Send a streaming chat to Gemini and yield response chunks.
    
    This simulates streaming by breaking the complete response into chunks
    since Gemini's streaming API is different from traditional chat streaming.
    """
    try:
        # Get the complete response first
        full_response = chat_gemini(messages, resume_context, system_prompt)
        
        # Simulate streaming by yielding chunks
        chunk_size = 5  # Smaller chunks for more natural streaming
        for i in range(0, len(full_response), chunk_size):
            chunk = full_response[i:i+chunk_size]
            if chunk.strip():  # Skip empty chunks
                yield chunk
                time.sleep(0.02)  # Small delay for realistic streaming
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper():
            yield "Error: There's an issue with the API key configuration."
        elif "QUOTA" in error_msg.upper() or "LIMIT" in error_msg.upper():
            yield "Error: API quota exceeded. Please try again later."
        else:
            yield f"Error: {error_msg[:200]}"  # Truncate long error messages
        yield f"[Chat error: {e}]"

def get_suggested_questions(resume_data: Dict[str, Any]) -> List[str]:
    """Generate more relevant suggested questions based on resume content"""
    if not resume_data:
        return [
            "What skills should I focus on for my career?",
            "How can I improve my resume?",
            "What jobs should I apply for?",
            "Tell me about current industry trends",
            "How do I prepare for technical interviews?"
        ]
    
    base_questions = []
    
    # Get basic info
    name = resume_data.get('name', 'candidate')
    skills = resume_data.get('skills', [])
    experience = resume_data.get('total_experience', 0)
    
    # Experience-based questions
    if experience == 0:
        base_questions.extend([
            "What entry-level positions should I target?",
            "How can I gain experience as a fresh graduate?",
            "What projects should I build to stand out?"
        ])
    elif experience < 2:
        base_questions.extend([
            "How can I transition to a senior role?",
            "What skills gap should I address?",
            "Should I consider switching companies?"
        ])
    else:
        base_questions.extend([
            "How can I move into leadership roles?",
            "What's the best career progression path?",
            "Should I consider specializing or staying generalist?"
        ])
    
    # Skill-based questions
    if 'python' in [s.lower() for s in skills]:
        base_questions.append("What Python frameworks should I learn next?")
    if 'javascript' in [s.lower() for s in skills]:
        base_questions.append("Should I focus on frontend or backend JavaScript?")
    if 'data' in ' '.join(skills).lower():
        base_questions.append("What data science certifications are worth pursuing?")
    
    # Generic helpful questions
    base_questions.extend([
        "How competitive is my profile in the current market?",
        "What's missing from my skill set?",
        "How should I negotiate my next salary?",
        "What are the latest trends in my field?"
    ])
    
    # Return a random selection of 6-8 questions
    return random.sample(base_questions, min(6, len(base_questions)))

def build_resume_context(resume_data: Dict[str, Any]) -> str:
    """Build a comprehensive context from resume data for the AI"""
    if not resume_data:
        return "No resume data available."
    
    context_parts = []
    
    # Basic information
    if resume_data.get('name'):
        context_parts.append(f"Candidate: {resume_data['name']}")
    
    if resume_data.get('email'):
        context_parts.append(f"Email: {resume_data['email']}")
    
    # Experience summary
    total_exp = resume_data.get('total_experience', 0)
    if total_exp > 0:
        context_parts.append(f"Total Experience: {total_exp} years")
    else:
        context_parts.append("Experience: Fresh graduate/Entry level")
    
    # Skills
    skills = resume_data.get('skills', [])
    if skills:
        # Use ALL unique skills; sorted for consistency
        uniq_skills = sorted(list(dict.fromkeys([s.strip() for s in skills if s and isinstance(s, str)])), key=lambda x: x.lower())
        context_parts.append(f"Skills ({len(uniq_skills)}): {', '.join(uniq_skills)}")
    
    # Education
    education = resume_data.get('education', [])
    if education:
        edu_info = []
        for edu in education[:2]:  # Top 2 education entries
            if edu.get('degree') and edu.get('institution'):
                edu_info.append(f"{edu['degree']} from {edu['institution']}")
        if edu_info:
            context_parts.append(f"Education: {'; '.join(edu_info)}")
    
    # Work Experience
    experience = resume_data.get('work_experience', [])
    if experience:
        exp_info = []
        for exp in experience[:3]:  # Top 3 work experiences
            if exp.get('position') and exp.get('company'):
                duration = exp.get('duration', 'Duration not specified')
                exp_info.append(f"{exp['position']} at {exp['company']} ({duration})")
        if exp_info:
            context_parts.append(f"Work Experience: {'; '.join(exp_info)}")
    
    # Projects
    projects = resume_data.get('projects', [])
    if projects:
        proj_info = []
        for proj in projects[:2]:  # Top 2 projects
            if proj.get('name'):
                proj_info.append(proj['name'])
        if proj_info:
            context_parts.append(f"Key Projects: {', '.join(proj_info)}")
    
    return '\\n'.join(context_parts)

def parse_resume_via_gemini(pdf_bytes: bytes) -> str:
    """Use Gemini multimodal capability to perform OCR/text extraction on a PDF"""
    try:
        api_key, model_name = _get_gemini_config()
        if not api_key:
            return ""
        
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Both gemini-1.5-flash and gemini-2.5-flash are multimodal and support PDF
        model = genai.GenerativeModel(model_name)
        
        prompt = (
            "You are an expert resume parser OCR tool. Extract all textual content, sections, titles, dates, "
            "and candidate details from this document exactly as they appear. Do not summarize. Do not add metadata. "
            "Just return the raw text extracted from the document."
        )
        
        response = model.generate_content([
            {
                "mime_type": "application/pdf",
                "data": pdf_bytes
            },
            prompt
        ])
        
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        return ""
    except Exception as e:
        print(f"Error in parse_resume_via_gemini: {e}")
        return ""

def generate_personalized_suggestions(resume_data: Dict[str, Any]) -> List[str]:
    """Use Gemini to generate 3-5 highly personalized suggestions for the resume"""
    try:
        api_key, model_name = _get_gemini_config()
        if not api_key:
            return []
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        context = build_resume_context(resume_data)
        
        prompt = (
            "You are an elite recruiter and resume optimization expert.\n"
            f"Analyze the following candidate's resume context:\n{context}\n\n"
            "Generate 3 to 4 highly specific, realistic, and non-generic suggestions to improve their resume.\n"
            "Requirements:\n"
            "- Do NOT use generic advice like 'Add work experience' or 'Include contact info' or 'Add phone number'.\n"
            "- Make advice specific to their target domain and skills (e.g. if they know Python, suggest exact libraries/frameworks to add, or specific projects to build).\n"
            "- Tell them exactly WHAT to add or change (e.g. 'Integrate a database like PostgreSQL in your Python project to show full-stack capabilities').\n"
            "- Keep each suggestion concise (under 20 words).\n"
            "- Return response ONLY as a JSON list of strings, for example: [\"Suggestion 1\", \"Suggestion 2\", \"Suggestion 3\"]\n"
            "Return nothing but the JSON array."
        )
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=512,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                )
            )
        except Exception:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=512,
                )
            )
        
        if response and hasattr(response, 'text') and response.text:
            cleaned = response.text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
            
            try:
                suggs = json.loads(cleaned)
            except Exception:
                # Regex fallback to extract quoted strings if json is malformed
                suggs = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
                if not suggs:
                    suggs = re.findall(r"'([^'\\]*(?:\\.[^'\\]*)*)'", cleaned)
            
            if isinstance(suggs, list) and suggs:
                return [str(s).strip() for s in suggs if str(s).strip()]
    except Exception as e:
        print(f"Error in generate_personalized_suggestions: {e}")
    return []

def generate_personalized_templates(resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Use Gemini to generate custom, tailored ATS bullet points / templates for the candidate's skills"""
    try:
        api_key, model_name = _get_gemini_config()
        if not api_key:
            return []
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        context = build_resume_context(resume_data)
        
        prompt = (
            "You are an expert resume writer.\n"
            f"Analyze the following candidate's resume context:\n{context}\n\n"
            "Generate 2 distinct tailored templates/examples that they can add to their resume.\n"
            "One should be a 'Work Experience' or 'Project' bullet point block in STAR format.\n"
            "The other should be a tailored 'Professional Summary' block.\n"
            "Requirements:\n"
            "- Tailor it exactly to their specific skills and domain (e.g. use their actual tools/skills like Python, SQL, C++, React, etc.).\n"
            "- Make it sound extremely professional, realistic, and ready-to-use (with placeholder brackets like <metric> or <duration> for them to customize).\n"
            "- Return response ONLY as a JSON list of dictionaries containing 'title', 'tags' (list of strings), 'content' (the template text), and 'tip', for example:\n"
            "[\n"
            "  {\n"
            "    \"title\": \"Custom Work Experience Template\",\n"
            "    \"tags\": [\"Python\", \"FastAPI\", \"SQL\"],\n"
            "    \"content\": \"Developed a high-performance backend API using FastAPI and SQL to handle <metric> daily transactions, reducing average latency by <metric>.\",\n"
            "    \"tip\": \"Make sure to quantify the metrics based on your actual achievements.\"\n"
            "  }\n"
            "]\n"
            "Return nothing but the JSON array."
        )
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=1024,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "title": {"type": "STRING"},
                                "tags": {
                                    "type": "ARRAY",
                                    "items": {"type": "STRING"}
                                },
                                "content": {"type": "STRING"},
                                "tip": {"type": "STRING"}
                            },
                            "required": ["title", "tags", "content", "tip"]
                        }
                    }
                )
            )
        except Exception:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=1024,
                )
            )
        
        if response and hasattr(response, 'text') and response.text:
            cleaned = response.text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
            
            try:
                tpls = json.loads(cleaned)
                if isinstance(tpls, list) and tpls:
                    return tpls
            except Exception:
                pass
    except Exception as e:
        print(f"Error in generate_personalized_templates: {e}")
    return []

# Export public API
__all__ = [
    'check_gemini_health',
    'chat_gemini',
    'chat_gemini_streaming',
    'get_suggested_questions',
    'build_resume_context',
    'parse_resume_via_gemini',
    'generate_personalized_suggestions',
    'generate_personalized_templates'
]