import streamlit as st
import json
import os
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Scott's Daily Journal & Advisor",
    page_icon="🧭",
    layout="wide"
)

# ---------------------------------------------------------
# 2. DATA INGESTION
# ---------------------------------------------------------
@st.cache_data
def load_historical_data(file_path="history.json"):
    """Loads and parses the JSON history file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        parsed_history = ""
        chunks = raw_data.get("chunkedPrompt", {}).get("chunks", [])
        
        for chunk in chunks:
            role = chunk.get("role", "UNKNOWN").upper()
            content = ""
            if "text" in chunk:
                content = chunk["text"]
            elif "parts" in chunk:
                parts_text = [p.get("text", "") for p in chunk["parts"] if "text" in p]
                content = " ".join(parts_text)
                
            if content.strip():
                parsed_history += f"--- {role} ---\n{content.strip()}\n\n"
                
        if not parsed_history:
            return "Error: Could not find conversation text in the JSON structure."
            
        return parsed_history

    except FileNotFoundError:
        return None
    except Exception as e:
        return f"Error loading file: {e}"

# ---------------------------------------------------------
# 3. MAIN APPLICATION LOOP
# ---------------------------------------------------------
def main():
    # --- HARDCODED API KEY FOR 24-HOUR F3 DEPLOYMENT ---
    # Scott: Replace the text inside the quotes below with your actual API key.
    api_key = "AIzaSyB2PFkN6c2W5aUWwQAQcuVsb1UG7446mq8"

    # --- UI HEADER & INTRO ---
    st.title("🧭 Scott's Daily Journal & Advisor")
    
    st.markdown("""
    This interface grants you direct access to the raw, unedited logs of Scott's personal and professional life in 2026. 
    Based upon regular journal entries and professional and personal interactions, this app allows his F3 advisors to pose in-depth inquiries into all aspects of Scott's life including his 7 guiding spokes of **Community, Family, Financial, Health, Home, Personal Development, and Spiritual.**
    
    👇 **To begin, type your query into the input box at the very bottom of this screen.**
    """)
    
    st.caption("🔒 **Privacy Guarantee:** Your queries are entirely ephemeral. Nothing you ask here is saved, logged, or monitored. You have the freedom to ask probing, unvarnished questions.")
    st.divider()

    # Load the asset
    with st.spinner("Ingesting historical data..."):
        history_context = load_historical_data("history.json") 

    if not history_context:
        st.error("Historical data file not found. Please ensure the file is in the directory.")
        return

    # ---------------------------------------------------------
    # 4. CHAT INTERFACE
    # ---------------------------------------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Welcome, F3 Advisor. The archive is online. I am prepared to answer your questions regarding Scott's historical data, business metrics, and personal operating system with radical transparency."
        })

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask the Advisor..."):
        
        if api_key == "PASTE_YOUR_API_KEY_HERE":
            st.error("🛑 System Error: API Key missing in source code.")
            return

        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Consulting the archive..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    system_prompt = f"""You are the AI custodian of Scott McWilliams' historical and strategic archive. 
The user speaking to you is NOT Scott. The user is an 'F3 Advisor'—either Steve, Joe, or Tony. They are Scott's trusted, deeply vulnerable peers from a 15-year Entrepreneur (EO) Forum. 
Your tone is Wise, Grounded, and Radically Transparent. You speak directly, without fluff. 
You address the user by name if they provide it, or simply as 'F3 Advisor'. 
You speak ABOUT Scott in the third person, providing them with the unvarnished truth, patterns, and context from his life based on the archive.

HISTORICAL TRANSCRIPT:
{history_context}
"""
                    response = client.models.generate_content(
                        model="gemini-3.1-pro-preview", 
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.3 
                        )
                    )
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()