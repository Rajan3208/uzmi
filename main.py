import streamlit as st
from transformers import pipeline
import time
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="Love Quote Generator",
    page_icon="💖",
    layout="centered",
)

# Custom CSS for love-themed styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #fff0f5;
    }
    div.stButton > button {
        background-color: #ff4d94;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #ff3385;
        border: none;
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
        border-left: 5px solid #ff4d94;
    }
    .header {
        color: #ff3385;
        font-family: 'Georgia', serif;
        text-align: center;
        font-size: 36px;
        margin-bottom: 10px;
    }
    .subheader {
        color: #ff66a3;
        font-family: 'Georgia', serif;
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }
    .stSpinner > div {
        border-color: #ff4d94 transparent transparent transparent;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #fff0f5;
        padding: 10px;
        text-align: center;
        color: #ff66a3;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App header
st.markdown("<h1 class='header'>💖 Love Quote Generator 💖</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Generate heartfelt love quotes to share with someone special!</p>", unsafe_allow_html=True)

# Session state initialization
if 'quotes_history' not in st.session_state:
    st.session_state.quotes_history = []
if 'current_quote' not in st.session_state:
    st.session_state.current_quote = ""
if 'loading' not in st.session_state:
    st.session_state.loading = False

# Sidebar for quote settings
with st.sidebar:
    st.header("Quote Settings")
    theme = st.selectbox(
        "Select a love quote theme:",
        ["romantic", "poetic", "sweet", "passionate", "eternal", "stars", "heart", "forever", "soul mates"]
    )
    max_length = st.slider("Quote Length", 30, 100, 50)
    temperature = st.slider("Creativity", 0.5, 1.0, 0.8)

# Function to generate love quote using DistilGPT2
@st.cache_resource
def load_generator():
    try:
        generator = pipeline('text-generation', model='distilgpt2')
        return generator
    except Exception as e:
        st.error(f"Error loading DistilGPT2: {str(e)}")
        return None

def generate_love_quote(theme, max_length=50, temperature=0.8):
    generator = load_generator()
    
    if generator is None:
        return "Failed to load DistilGPT2 model."
    
    try:
        prompt = f"A romantic love quote about {theme}:\n"
        output = generator(
            prompt,
            max_length=max_length,
            temperature=temperature,
            top_p=0.95,
            do_sample=True,
            truncation=True
        )
        generated_text = output[0]['generated_text'].strip()
        
        # Remove the prompt from the generated text
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return generated_text
    except Exception as e:
        return f"Error generating quote: {str(e)}"

# Function to copy text to clipboard (using JavaScript)
def get_clipboard_js(text):
    return f"""
        <script>
        function copyToClipboard() {{
            const text = `{text}`;
            navigator.clipboard.writeText(text).then(function() {{
                document.getElementById('copy-status').innerHTML = "Copied!";
                setTimeout(function() {{
                    document.getElementById('copy-status').innerHTML = "";
                }}, 2000);
            }});
        }}
        </script>
        <button onclick="copyToClipboard()" 
            style="background-color: #ff4d94; color: white; border: none; 
            border-radius: 5px; padding: 8px 15px; cursor: pointer;">
            Copy to Clipboard
        </button>
        <span id="copy-status" style="margin-left: 10px; color: #ff4d94;"></span>
    """

# Share buttons
def share_buttons(quote):
    encoded_quote = urllib.parse.quote(quote)
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_quote}"
    whatsapp_url = f"https://wa.me/?text={encoded_quote}"
    
    html = f"""
    <div style="display: flex; justify-content: center; gap: 15px; margin-top: 10px;">
        <a href="{twitter_url}" target="_blank" style="text-decoration: none;">
            <button style="background-color: #1DA1F2; color: white; border: none; border-radius: 5px; padding: 8px 15px; cursor: pointer;">
                Share on Twitter
            </button>
        </a>
        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
            <button style="background-color: #25D366; color: white; border: none; border-radius: 5px; padding: 8px 15px; cursor: pointer;">
                Share on WhatsApp
            </button>
        </a>
    </div>
    """
    return html

# Main app
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✨ Generate Love Quote ✨", key="generate"):
        st.session_state.loading = True
        
        with st.spinner("Crafting a romantic quote just for you..."):
            quote = generate_love_quote(theme, max_length, temperature)
            time.sleep(1)  # Optional delay for spinner
            st.session_state.current_quote = quote
            
            # Add to history if not an error
            if not quote.startswith("Error"):
                st.session_state.quotes_history.append((theme, quote))
        
        st.session_state.loading = False

# Display current quote
if st.session_state.current_quote:
    st.markdown(f"<div class='quote-box'>\"{st.session_state.current_quote}\"</div>", unsafe_allow_html=True)
    st.markdown(get_clipboard_js(st.session_state.current_quote), unsafe_allow_html=True)
    st.markdown(share_buttons(st.session_state.current_quote), unsafe_allow_html=True)

# Display quote history
if st.session_state.quotes_history:
    with st.expander("Quote History"):
        for i, (hist_theme, hist_quote) in enumerate(st.session_state.quotes_history):
            st.markdown(f"**Theme:** {hist_theme}")
            st.markdown(f"\"{hist_quote}\"")
            if i < len(st.session_state.quotes_history) - 1:
                st.markdown("---")

# Footer
st.markdown("""
<div class='footer'>Made with 💕 using Streamlit & Hugging Face</div>
""", unsafe_allow_html=True)
