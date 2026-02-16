from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user
import requests
import json
from fintelligent.auth.models import Expense
from datetime import datetime

ai_coach = Blueprint('ai_coach', __name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

@ai_coach.route('/ai-coach')
@login_required
def coach_page():
    # Only premium users get the full coach experience
    if not current_user.is_premium:
         # Return a preview or teaser
         return render_template('ai_coach_teaser.html')
    return render_template('ai_coach.html')

@ai_coach.route('/api/ai/chat', methods=['POST'])
@login_required
def chat():
    if not current_user.is_premium:
        return jsonify({'error': 'Premium subscription required for AI Coach'}), 403

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    # Fetch User Context (Reduced to last 3 for speed)
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(3).all()
    expense_context = "\n".join([f"- {e.date.strftime('%Y-%m-%d')}: ₹{e.amount} at {e.merchant} ({e.category})" for e in expenses])

    system_prompt = f"""
    You are 'Fintelligent AI', a friendly and expert financial coach for Indian students.
    Recent transactions:
    {expense_context if expenses else "None."}
    
    Context: Indian economy, UPI, Savings.
    Tone: Witty, concise, practical.
    Goal: Financial literacy.
    Avoid long paragraphs. Be direct.
    """
    
    # Combined prompt
    full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"

    def generate():
        try:
            payload = {
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": True,
                "options": {
                    "num_ctx": 4096,
                    "seed": 42,
                    "temperature": 0.7
                }
            }
            
            # Using stream=True for requests
            with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=60) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            if 'response' in json_response:
                                content = json_response['response']
                                yield f"data: {json.dumps({'content': content})}\n\n"
                            if json_response.get('done', False):
                                yield "data: [DONE]\n\n"
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')
