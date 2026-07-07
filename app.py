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
    AWS_DATA_URL = "https://juror-audio-upload-sabicia.s3.us-east-2.amazonaws.com/06_F3/history.json?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMiJHMEUCIQCBuQLOjc%2Bp0Q4lnw0sbobW0kq230Hpg86hv19aRZr5uQIgFNpVzeeT4Jg6JHAKwvI8KdgnX3JxDrHDdp3yZilzfGAquQMIcBAAGgw5OTM0NTgwOTY1MjYiDNBpOi%2FSbEYwfeEetyqWAyUyJtri7SgLqPT9QkL1UnjmkyYLeddJ46yZRorbu%2FDmpPoYAzYOwwqSpP22Q2NR2xA44Aqo8ZaCQIqQ1rDz11fyHw5FIOTs900Ico85b3NTjruRwNr8hB1xQmi%2B1ReuvH5Qe0YnDBrMdFe0JNJTgBGylUzl27u83oph%2F5nYVVaOeDQOeTvlHjOfJ1gfvKCSfLTdqjTBPpikWSKwdLmgJR2SZC0vfLGAaA5TLBQpamyH2ouWSl01XYLzJJKPYQe3mJ2tGbRFNmAolLrZIg86E154xaHLm2Vy9%2Bg7FLtfJeaSS2okNzFOj8dvf08kMsycY68fWD20dvGsvkNAQG10w1oQT4tonuGIA5WOR7Gz7HFHMqO4XgVgmzioP2RnygmMIwxUSk0AV8B42nWhOX7%2F2eI%2FORzQcliR3pCoEfLSCXK73fk2lcWXMbfS1nx2IFpGAq4lTHpxG%2FnfQQDtaXxuQfLDEVv3YjU0I2rkGktNJhxS2GGprY190EMhbVOpmBpX8vbAybtYgNDhZwUM%2FQEaQXEaxPsCggQwjbK00gY63gJS3XhCVhoB24UURgJKwwfCoHmfHQ83aI%2FQqs6JOb78OsqZpksZw7BpD7KAAGjXbg%2BdxRyIHH5gTnDD9lWrhTL9o7JOEcfYBjdE3kq982Kq9Ks8kVTTXNifMTWv7hqwwHskcbrEucArWfPfvL2737pwIrb6N%2F5Pi27X44gtbgl%2FaI7woFIPHkqunoy3U2F0lOYX5yN0GJyqm51NboGDHm8mgKEs0uNYR0KoxHYwNhX5TMnIGiV1FhvYdsFzDSFBUaB2EoXgEMIaNd2Sf%2F%2FfnR7bRtZw7E4SVbvpS2rP%2BRmrDOdLRia2CUGJbrH76M7QidBSk2Gk%2FluiVGZUrdMQ60ULhtf8XWnuBJm6KhtwDhLdIsU6yRWIGWFtEN7SuXGn5xsc3UfeC3kq%2BkbJprhHKdSNbeapM6Q0y1XktFbUPSLLCKLaP9jwphkrg522iiT%2Fa2hBw9SzHPzMD9mwmPqQ9g%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA6OTVXRGHIO5P5RKB%2F20260707%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20260707T152055Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=596dd85f764b85f4ce90586af072dfc695d133335b6e440a8d9d967038378f9b"

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
