"""
Enhanced local chatbot service using Ollama with improved features.

Features:
- Streaming responses for better UX
- Model management and health checks
- Enhanced error handling
- Conversation context management
- Resume-aware responses

Env vars (optional):
- OLLAMA_HOST (default: http://localhost:11434)
- OLLAMA_MODEL (default: phi:latest)
"""
from __future__ import annotations

import os
import re
import requests
import json
import time
from typing import List, Dict, Any, Optional, Tuple, Generator
from dotenv import load_dotenv
import random

def _get_ollama_config() -> Tuple[str, str]:
    """Read Ollama host/model from env each call and sanitize host."""
    # Load .env each time so changes in UI take effect on rerun
    load_dotenv(override=False)
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()
    model = os.getenv("OLLAMA_MODEL", "phi:latest").strip()
    # Remove any trailing slash and accidental '/api' suffix
    if host.endswith("/api"):
        host = host[:-4]
    host = host.rstrip("/")
    return host, model

# Updated system prompt with stronger, more directive instructions
SYSTEM_PROMPT_BASE = """
You're a friendly career coach named CareerGPT, here to help users navigate their career journey. Your goal is to provide warm, personalized advice that feels like talking to a trusted mentor.

## Your Personality & Tone:
- Warm and approachable, like a helpful career advisor
- Professional but conversational - no corporate jargon
- Empathetic and encouraging
- Clear and concise in your explanations
- Proactive in offering helpful suggestions

## When Responding:
1. Start with a friendly acknowledgment of their question
2. Reference specific details from their resume naturally
3. Break down complex advice into simple, actionable steps
4. Use "you/your" to make it personal
5. End with an encouraging note or next step

## Response Format (be natural, not rigid):

� [Brief, friendly acknowledgment of their question]

🔍 **What I Notice**
• Specific, relevant observations from their resume
• Connections to their career goals
• Strengths that stand out

🎯 **My Recommendations**
• Practical, tailored suggestions
• Specific skills or areas to focus on
• Job titles or paths that could be a great fit

� **Your Action Plan**
1. Clear first step they can take now
2. Short-term goals (next few weeks)
3. Longer-term considerations

💡 **Quick Tip**
• A helpful resource, tool, or strategy
• A networking idea
• A portfolio project suggestion

## Example Interaction:
User: "What jobs should I apply for?"

� That's a great question! Based on your background, here are some roles that could be a fantastic fit:

🔍 **What I Notice**
• You have 2+ years of experience with Python and web development
• Your work at [Company] shows strong problem-solving skills
• You've successfully led [specific project] which demonstrates leadership

🎯 **My Recommendations**
• Python Developer roles at mid-sized tech companies
• Full-stack positions where you can leverage both frontend and backend skills
• Consider startups for faster growth opportunities

� **Your Action Plan**
1. Update your LinkedIn with keywords from job descriptions
2. Set up job alerts for "Python Developer" on LinkedIn and Indeed
3. Research 3-5 companies you'd love to work for

💡 **Quick Tip**
Check out [specific resource] to brush up on system design - it often comes up in interviews!

## Remember:
- Keep it conversational, like you're talking to a friend
- Be specific with your advice
- Highlight their strengths
- Make it easy to take the next step
"""

def _format_messages(user_messages: List[Dict[str, str]], system: Optional[str]) -> Dict[str, Any]:
    """Format messages for Ollama API with improved context handling"""
    prompt_parts = []
    
    # Add system prompt first
    if system:
        prompt_parts.append(f"System: {system}")
    
    # Format conversation history (last 6 messages for better context)
    for m in user_messages[-6:]:
        role = m.get("role", "user")
        content = m.get("content", "").strip()
        
        if role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
        else:
            # Add user's message with context
            prompt_parts.append(f"User: {content}")
    
    # Add instruction to be specific and actionable
    prompt_parts.append("\nAssistant:")
    
    prompt = "\n\n".join(p for p in prompt_parts if p)
    
    return {
        "model": _get_ollama_config()[1],
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # Lower for more focused responses
            "top_p": 0.9,
            "num_predict": 1000,  # Increased for more detailed responses
            "repeat_penalty": 1.2,  # Higher to reduce repetition
            "top_k": 50,
            "stop": ["\n\n\n", "User:", "Assistant:"]
        },
    }

def _format_structured_response(text: str) -> str:
    """Improved response formatter with better section detection"""
    try:
        # Clean up the text first
        text = text.strip()
        
        # Common section headers with emojis
        sections = [
            (r'(?i)(analysis|overview|summary)', '🔍'),
            (r'(?i)(recommendation|suggestion|advice)', '🎯'),
            (r'(?i)(next steps?|action items?)', '📈'),
            (r'(?i)(tip|pro tip|suggestion)', '💡'),
            (r'(?i)(example|sample)', '📋'),
            (r'(?i)(note|important|warning)', 'ℹ️'),
            (r'(?i)(resource|reference)', '📚'),
            (r'(?i)(question|clarification)', '❓')
        ]
        
        # Convert markdown headers to our format if needed
        for pattern, emoji in sections:
            text = re.sub(
                r'#{1,3}\s*' + pattern + r'[\s:]*\n',
                f'\n{emoji} **' + r'\1'.title() + '**\n\n',
                text,
                flags=re.IGNORECASE
            )
        
        # Ensure consistent bullet points
        text = re.sub(r'(?<=\n)([-•*]|\d+[.)])\s+', '• ', text)
        
        # Clean up spacing
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Ensure proper spacing after headers
        text = re.sub(r'(\n[🔍🎯📈💡📋ℹ️❓📚]\s+\*\*[^\n]+\*\*)(\S)', r'\1\n\2', text)
        
        return text.strip()
    except Exception as e:
        return f"Error formatting response: {str(e)}\n\n{text}"

def check_ollama_health() -> Dict[str, Any]:
    """Check if Ollama is running and get model info"""
    try:
        host, model = _get_ollama_config()
        response = requests.get(f"{host}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        
        model_exists = any(m.get("name", "").startswith(model) for m in models)
        
        return {
            "status": "healthy",
            "host": host,
            "model": model,
            "model_exists": model_exists,
            "available_models": [m.get("name", "") for m in models]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "host": _get_ollama_config()[0],
            "model": _get_ollama_config()[1]
        }

def _format_messages_streaming(user_messages: List[Dict[str, str]], system: Optional[str]) -> Dict[str, Any]:
    """Format messages for streaming Ollama API with friendly conversation style"""
    prompt_parts = []
    if system:
        prompt_parts.append(f"System: {system}")
    
    # Format conversation history
    for m in user_messages[-4:]:  # Keep last 4 messages for context
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "assistant":
            prompt_parts.append(f"Me: {content}")
        else:
            prompt_parts.append(f"You: {content}")
    
    prompt = "\n\n".join(prompt_parts)
    return {
        "model": _get_ollama_config()[1],
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 800,  # Increased from 300 to match non-streaming
            "repeat_penalty": 1.15,  # Slightly higher to reduce repetition
            "top_k": 40,  # Slightly more focused
            "stop": ["\n\n\n"]  # Stop on triple newline
        },
    }

def chat_ollama(messages: List[Dict[str, str]], resume_context: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
    """Send a chat to Ollama with a friendly, conversational tone"""
    # Start with the base system prompt
    sys = system_prompt or SYSTEM_PROMPT_BASE
    
    # Format the system prompt with resume context if available
    if resume_context:
        # Keep it concise but informative
        truncated_context = resume_context[:2000]
        sys = sys.format(
            resume_context=f"\n=== RESUME DETAILS ===\n{truncated_context}\n=== END RESUME ===\n"
        )
    else:
        sys = sys.format(
            resume_context="No resume details available. Please ask the user to upload their resume for personalized advice."
        )
    
    # Add conversation history with a friendly tone
    conversation = [
        {
            "role": "system",
            "content": sys
        },
        *messages[-5:],  # Keep last 5 messages for context
    ]
    
    # Prepare the payload with settings for natural responses
    payload = {
        "model": _get_ollama_config()[1],
        "messages": conversation,
        "options": {
            "temperature": 0.7,  # Slightly higher for more natural responses
            "top_p": 0.9,
            "num_predict": 800,
            "repeat_penalty": 1.1,  # Lower to allow some repetition for natural flow
            "top_k": 40,
        },
    }
    
    try:
        host, model = _get_ollama_config()
        if not host or not model:
            return "I'm having trouble connecting to the AI service. Please check your settings and try again."
        
        # Add a small delay to make it feel more natural
        time.sleep(0.5)
        
        response = requests.post(
            f"{host}/api/chat",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get('message', {}).get('content', '').strip()
        
        # Format the response to be more conversational
        return _format_conversational_response(response_text)
        
    except requests.exceptions.RequestException as e:
        return "I'm having trouble connecting right now. Could you try again in a moment?"
    except Exception as e:
        return "Hmm, something went wrong. Could you rephrase your question?"

def _format_conversational_response(text: str) -> str:
    """Format the response to be more conversational and friendly"""
    try:
        # Clean up any excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text.strip())
        
        # Ensure proper spacing after section headers
        text = re.sub(
            r'(🔍 |🎯 |📝 |💡 |💬 )', 
            '\n\1', 
            text
        )
        
        # Add a friendly sign-off if none exists
        if not any(phrase in text.lower() for phrase in ['good luck', 'best of luck', 'hope this helps']):
            sign_offs = [
                "\n\nHope this helps! Let me know if you have any other questions. 😊",
                "\n\nFeel free to ask if you need any clarification! 👍",
                "\n\nLet me know how else I can assist you! 🚀"
            ]
            text += random.choice(sign_offs)
            
        return text.strip()
    except:
        return text  # Return original if formatting fails

def chat_ollama_streaming(messages: List[Dict[str, str]], resume_context: Optional[str] = None, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
    """Send a streaming chat to Ollama and yield response chunks.
    messages: list of {role: 'user'|'assistant', content: str}
    resume_context: optional text to inject into system prompt
    """
    sys = system_prompt or SYSTEM_PROMPT_BASE
    if resume_context:
        sys = sys.format(resume_context=f"\n=== RESUME DETAILS ===\n{resume_context[:2500]}\n=== END RESUME ===\n")
    payload = _format_messages_streaming(messages, sys)
    
    try:
        host, _ = _get_ollama_config()
        resp = requests.post(f"{host}/api/generate", json=payload, stream=True, timeout=60)
        resp.raise_for_status()
        
        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if 'response' in data:
                        yield data['response']
                    if data.get('done', False):
                        break
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        host, model = _get_ollama_config()
        hint = ""
        if host.endswith("/api"):
            hint = " Hint: OLLAMA_HOST should be like 'http://localhost:11434' (no /api)."
        yield f"[Chat error: {e}. Using host={host}, model={model}.{hint}]"

def get_suggested_questions(resume_data: Dict[str, Any]) -> List[str]:
    """Generate more relevant suggested questions based on resume content"""
    if not resume_data:
        return [
            "What skills should I add to my resume?",
            "How can I improve my resume's impact?",
            "What are some good projects for my experience level?",
            "How can I highlight my achievements better?"
        ]
    
    skills = resume_data.get('skills', [])
    experience = resume_data.get('experience', [])
    
    questions = []
    
    # Add skill-specific questions
    if skills:
        skills_str = ', '.join(skills[:3])
        questions.extend([
            f"How can I highlight my {skills_str} experience better?",
            f"What are some advanced topics in {skills[0]} I should learn next?",
            f"How can I combine {skills_str} to build a portfolio project?"
        ])
    
    # Add experience-based questions
    if experience:
        latest_role = experience[0].get('title', 'your role') if experience else 'your experience'
        questions.extend([
            f"How can I better showcase my achievements as a {latest_role}?",
            "What metrics should I include to quantify my impact?",
            "How can I tailor my resume for senior roles?"
        ])
    
    # Add general career questions
    questions.extend([
        "What are the top skills in demand for my target roles?",
        "How can I improve my resume's ATS compatibility?",
        "What are some good open-source projects to contribute to?"
    ])
    
    return questions[:5]  # Return top 5 questions

def build_resume_context(resume_data: Dict[str, Any]) -> str:
    parts = []
    name = resume_data.get("name")
    email = resume_data.get("email")
    phone = resume_data.get("mobile_number")
    skills_list = resume_data.get("skills", [])
    tech_skills, other_skills = _categorize_skills(skills_list)
    parts.append(f"Name: {name or 'N/A'}")
    parts.append(f"Email: {email or 'N/A'} | Phone: {phone or 'N/A'}")
    parts.append("Skills (all): " + (", ".join(skills_list[:50]) if skills_list else "N/A"))
    if tech_skills:
        parts.append("Technical Skills: " + ", ".join(sorted(set(tech_skills))[:50]))
    if other_skills:
        parts.append("Other Skills: " + ", ".join(sorted(set(other_skills))[:50]))
    raw = resume_data.get("raw_text", "")
    if raw:
        parts.append("Summary:\n" + raw[:1200])
    return "\n".join(parts)

TECH_KEYWORDS = {
    # Core languages & frameworks
    "python","java","javascript","typescript","c","c++","c#","go","rust","php","ruby","kotlin","swift",
    "html","css","react","angular","vue","django","flask","spring","node","express","next","nestjs","fastapi",
    # Data, AI, tools
    "sql","mysql","postgres","mongodb","redis","elasticsearch","pandas","numpy","scikit","sklearn","pytorch","tensorflow","keras",
    "nlp","computer vision","opencv","langchain","huggingface","spark","hadoop","airflow","tableau","power bi","excel",
    # DevOps & cloud
    "docker","kubernetes","k8s","terraform","ansible","aws","azure","gcp","linux","git","github","gitlab","ci/cd",
    # Web, mobile, testing
    "rest","graphql","grpc","android","ios","xcode","android studio","jest","pytest","selenium"
}

def _categorize_skills(skills_list: Any) -> Tuple[list, list]:
    tech, other = [], []
    if not isinstance(skills_list, list):
        return tech, other
    for s in skills_list[:100]:
        if not isinstance(s, str):
            continue
        sl = s.strip()
        key = sl.lower()
        if key in TECH_KEYWORDS:
            tech.append(sl)
        else:
            # heuristic: if it contains known tech separators/terms
            if any(t in key for t in ["devops","engineer","framework","library","database","cloud","ml","ai","data "]):
                tech.append(sl)
            else:
                other.append(sl)
    return tech, other
