import streamlit as st
import requests
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import base64

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

# Sidebar for model selection and theme
with st.sidebar:
    st.header("Settings")
    
    generation_method = st.radio(
        "Generation Method:",
        ["Hugging Face API", "Local Model"]
    )
    
    if generation_method == "Hugging Face API":
        model_id = st.text_input("Model ID", "rajan3208/uzmi-gpt")
        api_key = st.text_input("API Key", "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", type="password")
    else:
        model_id = st.text_input("Model ID", "rajan3208/uzmi-gpt")
        st.warning("Loading models locally may use significant memory and take longer to load.")

    st.header("Quote Settings")
    theme = st.selectbox(
        "Select a love quote theme:",
        ["romantic", "poetic", "sweet", "passionate", "eternal", "stars", "heart", "forever", "soul mates"]
    )
    
    max_length = st.slider("Quote Length", 30, 100, 50)
    temperature = st.slider("Creativity", 0.5, 1.0, 0.8)

# Function to generate love quote using Hugging Face API
def generate_love_quote_api(theme, model_id, api_key, max_length=50, temperature=0.8):
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    prompt = f"A romantic love quote about {theme}:\n"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_length,
            "temperature": temperature,
            "top_p": 0.95,
            "do_sample": True,
            "return_full_text": False
        },
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                quote = data[0].get("generated_text", "").strip()
                return quote
            elif isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"].strip()
            else:
                return f"Unexpected response format: {data}"
        else:
            error_details = response.text
            return f"Error {response.status_code}: {error_details}"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate love quote using local model
@st.cache_resource
def load_model_and_tokenizer(model_id):
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)
        
        # Move model to GPU if available
        if torch.cuda.is_available():
            model = model.to("cuda")
            
        return model, tokenizer
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

def generate_love_quote_local(theme, model_id, max_length=50, temperature=0.8):
    model, tokenizer = load_model_and_tokenizer(model_id)
    
    if model is None or tokenizer is None:
        return "Failed to load the model. Please check the model ID and try again."
    
    try:
        prompt = f"A romantic love quote about {theme}:\n"
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # Move inputs to the same device as the model
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_length=max_length,
                do_sample=True,
                temperature=temperature,
                top_p=0.95,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id
            )
            
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
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
    encoded_quote = base64.b64encode(quote.encode('utf-8')).decode('utf-8')
    
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
            if generation_method == "Hugging Face API":
                quote = generate_love_quote_api(theme, model_id, api_key, max_length, temperature)
            else:
                quote = generate_love_quote_local(theme, model_id, max_length, temperature)
            
            # Add some delay to show the spinner (optional)
            time.sleep(1)
            
            st.session_state.current_quote = quote
            
            # Add to history if it's not an error message
            if not quote.startswith("Error"):
                st.session_state.quotes_history.append((theme, quote))
        
        st.session_state.loading = False

# Display current quote
if st.session_state.current_quote:
    st.markdown(f"<div class='quote-box'>"{st.session_state.current_quote}"</div>", unsafe_allow_html=True)
    
    # Copy to clipboard button using JavaScript
    st.markdown(get_clipboard_js(st.session_state.current_quote), unsafe_allow_html=True)
    
    # Share buttons
    st.markdown(share_buttons(st.session_state.current_quote), unsafe_allow_html=True)

# Display quote history
if st.session_state.quotes_history:
    with st.expander("Quote History"):
        for i, (hist_theme, hist_quote) in enumerate(st.session_state.quotes_history):
            st.markdown(f"**Theme:** {hist_theme}")
            st.markdown(f""{hist_quote}"")
            if i < len(st.session_state.quotes_history) - 1:
                st.markdown("---")

# Footer
st.markdown("""
<div class='footer'>Made with 💕 using Streamlit & Hugging Face</div>
""", unsafe_allow_html=True)
