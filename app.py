from flask import Flask, render_template, request, session, redirect, url_for
import requests
import uuid
import os
from dotenv import load_dotenv

# Load .env variables first
load_dotenv()

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())  # Session tracking

# Load OpenRouter API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not found in environment variables.")

def get_response(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",  # Change if hosted
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",  # ✅ Correct model ID
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"⚠️ API Error {response.status_code}: {response.text}"


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        selected_function = request.form['function']
        user_input = request.form.get('user_input', '').strip()

        if selected_function == 'question':
            prompt = f"Answer this question clearly: {user_input}"
        elif selected_function == 'summary':
            prompt = f"Summarize this text in 10-12 bullet points: {user_input}"
        elif selected_function == 'creative':
            prompt = f"Write a creative story or poem about: {user_input}"
        else:
            prompt = user_input

        ai_response = get_response(prompt)

        session['history'].append({
            "user": user_input,
            "ai": ai_response,
            "feedback": None
        })
        session.modified = True

        return redirect(url_for('index'))

    return render_template('index.html', history=session['history'])

@app.route('/feedback/<int:index>/<value>')
def feedback(index, value):
    if 'history' in session and 0 <= index < len(session['history']):
        session['history'][index]['feedback'] = value
        session.modified = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
