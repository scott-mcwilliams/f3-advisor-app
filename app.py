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
    AWS_DATA_URL = "https://juror-audio-upload-sabicia.s3.us-east-2.amazonaws.com/06_F3/history.json?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEJj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMiJHMEUCICuuFaWNHQiD6PyaouBqElZRUSv5ztAIk8gmdtjHOBwhAiEAiwZdw1IBns%2F9QGGvA9UnU%2BmjiZ1nSdZUm6NgJ2bZB%2FgquQMIYRAAGgw5OTM0NTgwOTY1MjYiDEuJE2VnfxRx73CLIyqWA8uCQny%2BNu5JmSrv6C%2FmiuNhRP90IgBqv0QI4ivGJKQ%2FrP0e9NWWNCfYmimYslq%2FLFPigZDP6iQfrxhAoMMy0eejV23Fygm8yaXz4SRYEQ0oUVQjO3qxTilac7SPe71%2F5Z8%2FU8ue%2FMs9kQ8gP3YaMzxABY50KxXJD%2BOWAKVyxKhuGYhcjU4N39k%2FXxocfc0%2F8rD0Pwsafl3AjP%2FVuhfqiycODlcReD4uFSBrxQ%2F2Cctto0MgOSwfLgLya6g9YcdP6MiKlrQd20wd8J%2BgZYRNTGR7c4er3rnjbqet%2FJ7i8c2uAUERV1irSObKrZxbj7kPH9I4WOF7AG%2BRNxf3pnpfVBqA6S2BtJrRrQQb18nbF8jijc6E77Qnoty1gMhvALhdElmMyimMmzyg4QwPt2ggaq%2BfMTttwpIWmx3aL2suUHmT8a%2Fp2UB6wkpLoDrvjTCcJxRuA3kBAn5JOkjlQDlIm3Uq0WiTfPs7pMXNp1BbP%2BLD%2BKkoghTjKCM%2Bm55%2Fq6giPNfdqkNo8sHN%2BPOa8a%2BJV1jtl%2FdNjTMwr8mw0gY63gIpGw99JJ3aYZLUewhW0tLPE8yAX6G1XTpmiPn9S26uGfaVUpXrBlrDkqsEm8xc3zQzeYKYHKYfdN4KZxERFjL6%2B30ceJ4TIYMrvEoYbwt70JHd%2FB6JDjmB%2BOGcTMYFqbz3kTK348CcFcjTFEk4XTKJ0N%2FwP67AhEeq1I5M67DQm8hqX6WoR%2F2nQBGmEPl3jtjxeBmouCKO93QCABNsLlFVtJu7cYbLnq7LifuVjqH0JrJpp9rymAJw9HfflUO1B8EibK%2Fv%2BhvLv2wropYu422KjfGz7Rv%2FIiESmlEqCwQ609nEpKXg0fMOsw9ugd4BYU6eOiV7d%2FaIhQHD%2BzvmOThSgPz9ubcUkPvujxkb0nIn5r%2F43I9VrVmiiWT0p%2BknbRSsIBID59ffZGd%2FG%2BvC7p3aCWO8n6fz9G0nGOT0dTX4Le1QuiSH9efF79MLdUO%2B86dOksA22Am0sOD%2BG3o%2FIA%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA6OTVXRGHGX5APHXX%2F20260706%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20260706T233732Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=941ee530aa6632e9e165c8764d0191b2c5e3336e0eddab03cb39c5d4df2b2cc8"

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

    if not history_context or "Error" in history_context:
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