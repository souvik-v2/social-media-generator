import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)

# Initialize the Gemini Client
client = genai.Client(api_key=api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_post():
    data = request.json
    article_text = data.get('article', '')
    platform = data.get('platform', 'LinkedIn')
    tone = data.get('tone', 'Professional')
    include_hashtags = data.get('hashtags', True)

    if not article_text:
        return jsonify({'error': 'Article text is required.'}), 400

    # Build an optimized prompt for the AI based on user configurations
    prompt = f"""
    You are an expert social media manager. Convert the following article text into a highly engaging post optimized for {platform}.
    
    Tone of voice: {tone}
    Include Hashtags: {'Yes' if include_hashtags else 'No'}

    Platform Specific Constraints:
    - LinkedIn: Professional, educational, uses structural line breaks, hook at the beginning, relevant hashtags at the end.
    - X (Twitter): Punchy, concise, strictly under 280 characters, strong hook, maximum 2 hashtags.
    - Instagram: Engaging caption style, uses emojis for visual structure, separated block of hashtags at the very bottom.

    Article Content:
    {article_text}

    Provide only the final social media post content. Do not include introductory notes like "Here is your post:".
    """

    try:
        # Call the lightweight and fast Gemini 2.5 Flash model
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )
        return jsonify({'post': response.text})
    except Exception as e:
        return jsonify({'error': f"AI Generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
