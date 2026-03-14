from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user
import requests
import json
from fintelligent.auth.models import Expense
from datetime import datetime

ai_coach = Blueprint('ai_coach', __name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

from fintelligent.utils.decorators import tier_required

@ai_coach.route('/ai-coach')
@login_required
@tier_required(['STUDENT', 'PRO'])
def coach_page():
    return render_template('ai_coach.html')

@ai_coach.route('/api/ai/chat', methods=['POST'])
@login_required
@tier_required(['STUDENT', 'PRO'])
def chat():

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

@ai_coach.route('/api/ai/roast', methods=['POST'])
@login_required
def roast():
    """Brutal, funny AI roast of user spending."""
    # Fetch User Context
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(10).all()
    expense_context = "\n".join([f"- ₹{e.amount} at {e.merchant} ({e.category})" for e in expenses])

    system_prompt = f"""
    You are 'FinTelligent Roast Bot'. You are a brutal, sarcastic, and funny AI that roasts Gen Z students for their bad money habits.
    Your goal is to make them laugh at themselves but also feel a little guilt so they save more.
    Use terms like 'bro', 'L', 'fr fr', 'Zomato victim'.
    Be short. One or two sentences max.
    
    Recent user spending:
    {expense_context if expenses else "Wait, you haven't even logged anything? Too scared to see the truth?"}
    """
    
    full_prompt = f"{system_prompt}\n\nRoast this user's spending habits:"

    def generate():
        try:
            payload = {
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": True,
                "options": {"temperature": 0.9} # High temperature for more creative roasts
            }
            
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
