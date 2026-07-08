import streamlit as st
import json
import requests
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Scott's Daily Journal & Advisor", page_icon="🧭", layout="wide")

# ---------------------------------------------------------
# 2. DATA INGESTION (FROM SECURE EXTERNAL URL)
# ---------------------------------------------------------
@st.cache_data
def load_historical_data(file_url):
    """Downloads and parses the JSON history file directly from an AWS URL."""
    try:
        # Fetch the file from your unguessable AWS URL
        response = requests.get(file_url)
        response.raise_for_status() # Ensure the download was successful
        raw_data = response.json()
            
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

    except Exception as e:
        return f"Error loading external file: {e}"

# ---------------------------------------------------------
# 3. MAIN APPLICATION LOOP
# ---------------------------------------------------------
def main():
    # Pull the API Key securely from the Streamlit Secrets vault
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("🛑 System Error: API Key missing from Secrets vault.")
        return

    # --- ARCHITECT CONFIGURATION ---
    # Scott: Paste your unguessable AWS URL inside these quotes!
    AWS_DATA_URL = "https://juror-audio-upload-sabicia.s3.us-east-2.amazonaws.com/06_F3/history.json?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMiJHMEUCIQCiQrI1egh4u17Ob%2BHnhRu%2F1hXIWHVCb1be3GB2X4iw9QIgR5wmuBBApa%2B8p3Y9NvjFOovayeOdAxgHp1gC5r2sMdMquQMIfhAAGgw5OTM0NTgwOTY1MjYiDA5%2Bu2sW%2BGxQBWOEqSqWAw7bI1v7Jvpzwkzp0PN3evkbw58Uu86UmEC0VQkJmJXVsb8DA0IFwFcdlNvOrlZimEWaGo7Ro7sTNPOoB%2BUXk9OtO6soWldkvL%2BYnq8xyhUAQ%2FdSsqUbtB5Ipznw1Z5IkSeTSRMmhMTcgfEmP7JV2rjJx6RYws3TpbGhsa3dfbq2eolqhErUbXEBtTReNXpjkx5rQypWCe1vDnDZXhhDUJVwDWPR%2F%2BcrlDBuYtkVLvb2tton0JTX7IAw94OnF%2B9VQwclufp2zhywEcMorzlV1WnHaZoS35etkv%2B19PcWQaCa%2Bs3y4ciCTARPh5NkRyRp9WT9dG%2FbaBPz%2FS6%2Fq4UOqFUxZxsxTe6Pn9zjX6fFF3yfnSH870A6ID5x6%2BAfHOaXnqnaKSmeknfIyQ8W9wER23Z2kdNlp13bdX9egSOdJo5R%2BM225WG0JGnj%2F%2BK%2FYU62%2BugsgPqJ7GxMIF1F6CXdn8cG5O220idp7CwWLZWLgdW%2BDXw1KCPc8PxDVEuFyfeJloomaDM4v0%2F67aFeGDOQxgn8C5gCp7Ewyqy30gY63gK6%2BLdweSN7XY%2FD%2Bc0%2BxcYu9AXx45LacNnbLMUCy0kd3k4MWLb46p5ZWwOdT1DHemloJDX0nML1IclgLycWMPD8hzDHsAH8yLtn8OJOW%2F1AY9VPueWzsM1TpPl3CjN6k6JIUAXJQJ1XVwd%2Bq%2FfOZE7MvrBSsKSkxcSRzbdFCk5VNt52mR9EWVEOLbWC0ERpAsK2KqZ8PINJzfex%2FZ1uKYJM7TNc9tfNbnLBo9OzCaZwVUrQFp%2Fm3e6IzYi%2B6uL%2FIhqG6QDvzS4uk%2FzRRhDthD%2FaABamHWO6wfQsHAkEAac8qLNXr%2FV1z85LzXodtD3Hy%2Fr7u4FcN5DtJQ0OqDCfw%2FKfLPj25AFOQeo1bKTSP5vmywm1lydPBDFMIJJoPfPSgkGnceqeORvUm8yAl3MXZ2aUy7cPYBLdLjI5Oc6g9NpNZFWsQrxSmyJxwxw9i4iFnFW6JHSz0kwQYBHlFA5N%2Fg%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA6OTVXRGHFM6UX7N5%2F20260708%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20260708T044738Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=5e3d8bfef159da9a772baa0bd861c02568d9e69549369eeda33160a483b429d2"

    st.title("🧭 Scott's Daily Journal & Advisor")
    
    st.markdown("""
    This interface grants you direct access to the raw, unedited logs of Scott's personal and professional life in 2026. 
    Based upon regular journal entries and professional and personal interactions, this app allows his F3 advisors to pose in-depth inquiries into all aspects of Scott's life including his 7 guiding spokes of **Community, Family, Financial, Health, Home, Personal Development, and Spiritual.**
    
    👇 **To begin, type your query into the input box at the very bottom of this screen.**
    """)
    
    st.caption("🔒 **Privacy Guarantee:** Your queries are entirely ephemeral. Nothing you ask here is saved, logged, or monitored. You have the freedom to ask probing, unvarnished questions.")
    st.divider()

    with st.spinner("Establishing secure link to archive..."):
        history_context = load_historical_data(AWS_DATA_URL) 

    if not history_context or history_context.startswith("Error"):
        st.error(f"Failed to connect to secure archive. {history_context}")
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
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Consulting the archive..."):
                try:
                    client = genai.Client(api_key=api_key)
                    system_prompt = f"""You are the AI custodian of Scott McWilliams' historical and strategic archive. 
The user speaking to you is an 'F3 Advisor'—either Steve, Joe, or Tony. 
Your tone is Wise, Grounded, and Radically Transparent. You speak directly, without fluff. 
You speak ABOUT Scott in the third person.
HISTORICAL TRANSCRIPT:
{history_context}
"""
                    response = client.models.generate_content(
                        model="gemini-3.1-pro-preview", 
                        contents=prompt,
                        config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.3)
                    )
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
