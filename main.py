import streamlit as st
import requests
import pyperclip

# Streamlit page configuration with love theme
st.set_page_config(
    page_title="Love Quote Generator",
    page_icon="💖",
    layout="centered",
)

# Custom CSS for love-themed styling
st.markdown(
    """
    <style>
    body {
        background-color: #ffe6f0;
    }
    .stButton>button {
        background-color: #ff4d94;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #ff3385;
    }
    .quote-box {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(255, 77, 148, 0.2);
        font-style: italic;
        font-size: 20px;
        color: #ff4d94;
        text-align: center;
        margin: 20px 0;
    }
    .header {
        color: #ff3385;
        font-family: 'Georgia', serif;
        text-align: center;
        font-size: 36px;
    }
    .subheader {
        color: #ff66a3;
        font-family: 'Georgia', serif;
        text-align: center;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Hugging Face API setup (using your fine-tuned model)
API_KEY = "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"  
MODEL_URL = "https://api-inference.huggingface.co/models/rajan3208/uzmi-gpt"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Function to generate love quote
def generate_love_quote(theme):
    prompt = f"A romantic message about {theme}:\n"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 40,
            "temperature": 0.9,
            "top_p": 0.95,
            "do_sample": True,
            "return_full_text": False
        },
    }
    
    try:
        response = requests.post(MODEL_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            # Fixed response handling
            data = response.json()
            # The response format is typically a list with a single item containing generated_text
            if isinstance(data, list) and len(data) > 0:
                quote = data[0].get("generated_text", "").strip()
                if quote and ("love" in quote.lower() or "heart" in quote.lower() or theme.lower() in quote.lower()):
                    return quote
                else:
                    return "This quote doesn't feel romantic enough. Try again!"
            else:
                # Alternative format handling
                if isinstance(data, dict) and "generated_text" in data:
                    quote = data["generated_text"].strip()
                    return quote
                return "Couldn't parse the generated quote. Try again!"
        else:
            st.error(f"API Error: {response.status_code}")
            st.error(f"Response: {response.text}")
            return f"Error: Failed to generate quote (Status {response.status_code})."
    except Exception as e:
        st.error(f"Exception: {str(e)}")
        return f"Error: {str(e)}"

# Streamlit app layout
st.markdown("<h1 class='header'>💖 Love Quote Generator 💖</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Generate heartfelt love quotes to share with someone special!</p>", unsafe_allow_html=True)

# Sidebar for theme selection
st.sidebar.header("Choose a Theme")
theme = st.sidebar.selectbox(
    "Select a love quote theme:",
    ["romantic", "poetic", "sweet", "passionate", "eternal", "stars", "heart", "forever"]
)

# Generate button and quote display
if st.button("Generate Love Quote", key="generate"):
    with st.spinner("Crafting a romantic quote..."):
        quote = generate_love_quote(theme)
        st.session_state["quote"] = quote

# Display quote if available
if "quote" in st.session_state:
    st.markdown(f"<div class='quote-box'>{st.session_state['quote']}</div>", unsafe_allow_html=True)
    if st.button("Copy Quote", key="copy"):
        try:
            pyperclip.copy(st.session_state["quote"])
            st.success("Quote copied to clipboard!")
        except Exception as e:
            st.error(f"Could not copy to clipboard: {str(e)}")
            st.info("Note: pyperclip may not work in some Streamlit environments like Cloud deployments.")

# Footer
st.markdown(
    "<p style='text-align: center; color: #ff66a3;'>Made with 💕 using Streamlit & Hugging Face</p>",
    unsafe_allow_html=True
)
