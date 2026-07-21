from flask import Blueprint, render_template, request, jsonify, Response, session
from flask_login import login_required, current_user
import os

from fintelligent.auth.models import Expense
from fintelligent.extensions import limiter
from fintelligent.utils.decorators import tier_required
from fintelligent.ai_coach.llm_service import stream_llm
from fintelligent.ai_coach.context import build_coach_context, get_data_sources

ai_coach = Blueprint('ai_coach', __name__)

_SSE_HEADERS = {
    'Cache-Control': 'no-cache',
    'X-Accel-Buffering': 'no',
    'Connection': 'keep-alive',
}


@ai_coach.route('/ai-coach')
@login_required
@tier_required(['STUDENT', 'PRO'])
def coach_page():
    provider = 'Groq Cloud' if os.environ.get('GROQ_API_KEY') else 'Ollama (Local)'
    data_sources = get_data_sources(current_user.id, session)
    return render_template(
        'ai_coach.html',
        ai_provider=provider,
        data_sources=data_sources,
    )


@ai_coach.route('/api/ai/chat', methods=['POST'])
@login_required
@tier_required(['STUDENT', 'PRO'])
@limiter.limit("20 per minute")
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    financial_context = build_coach_context(current_user.id, session)
    sources = get_data_sources(current_user.id, session)

    system_prompt = f"""You are Fintelligent AI, an elite financial advisor for Indian students.

CONNECTED DATA SOURCES: {', '.join(sources)}

USER FINANCIAL DATA:
{financial_context}

INSTRUCTIONS:
1. Use ALL available data — especially Analytics CSV synthesis (categories, clusters, insights) when the user asks about spending patterns, analytics, or uploads.
2. If Analytics CSV data is present, reference category totals, clusters, and health score in your answers.
3. Distinguish between receipt scans, CSV analytics, and bank statement data when relevant.
4. Give sharp, practical financial advice.
5. Keep answers concise (under 150 words unless asked for detail).
6. Use Indian context: UPI, ₹, 80C, SIP, etc.
7. Tone: witty and friendly, not robotic."""

    def generate():
        yield from stream_llm(
            system=system_prompt,
            user=user_message,
            temperature=0.7,
            max_tokens=400,
        )

    return Response(generate(), mimetype='text/event-stream', headers=_SSE_HEADERS)


@ai_coach.route('/api/ai/roast', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def roast():
    """Brutal, funny AI roast of user spending."""
    financial_context = build_coach_context(current_user.id, session)

    system_prompt = """You are FinTelligent Roast Bot — brutal, sarcastic, and funny.
Roast Gen Z students for bad money habits. Use 'bro', 'L', 'fr fr', 'Zomato victim'.
One or two sentences max. No preamble."""

    user_prompt = (
        f"Spending data (receipts + CSV analytics + statements):\n{financial_context}\n\n"
        "Roast this user's spending habits:"
    )

    def generate():
        yield from stream_llm(
            system=system_prompt,
            user=user_prompt,
            temperature=0.9,
            max_tokens=120,
        )

    return Response(generate(), mimetype='text/event-stream', headers=_SSE_HEADERS)
