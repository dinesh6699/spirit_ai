import ast
import datetime as dt
import operator
import os
import urllib.parse
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

APP_NAME = "SPIRIT"
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
MAX_MESSAGES = 20
MAX_MESSAGE_CHARS = 8000

SYSTEM_PROMPT = """
You are SPIRIT, a helpful personal AI assistant.
You can help with conversations, schoolwork, calculations, coding, writing,
general questions, and learning. Be friendly, accurate, and clear.
If you are uncertain, say so. Never claim you performed an action unless you did.
Answer in the language the user uses when practical.
"""

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

# Keep the API key on the server. Never place it in browser JavaScript.
api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=api_key) if api_key else None

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def calculate(expression: str):
    """Evaluate basic arithmetic without using Python eval()."""
    if len(expression) > 120:
        raise ValueError("Expression is too long.")
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent is too large.")
            result = OPS[type(node.op)](left, right)
            if isinstance(result, (int, float)) and abs(result) > 1e100:
                raise ValueError("Result is too large.")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](evaluate(node.operand))
        raise ValueError("Only basic arithmetic is supported.")

    return evaluate(tree.body)

def local_command(message: str):
    text = message.strip()
    lower = text.lower()

    if lower == "/time":
        return dt.datetime.now().astimezone().strftime("Current time: %I:%M %p")
    if lower == "/date":
        return dt.date.today().strftime("Today's date: %d-%m-%Y")
    if lower.startswith("/calc "):
        try:
            return f"Answer: {calculate(text[6:])}"
        except Exception:
            return "I couldn't calculate that. Try an expression such as /calc (25 + 5) * 3."
    if lower.startswith("/search "):
        query = text[8:].strip()
        if not query:
            return "Please add a search query after /search."
        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        return {"reply": f"Here is your web search: {url}", "link": url}
    if lower == "/help":
        return (
            "SPIRIT commands:\n"
            "/time — show the current time\n"
            "/date — show today's date\n"
            "/calc 12 * (5 + 2) — calculate\n"
            "/search your question — create a web search link\n"
            "/help — show this help"
        )
    return None

@app.get("/")
def home():
    return render_template("index.html", app_name=APP_NAME)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "ai_configured": bool(client)})

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    if not isinstance(messages, list) or not messages:
        return jsonify({"reply": "Please enter a message."}), 400

    # Accept only user/assistant text messages; limit history and payload size.
    clean_messages = []
    for item in messages[-MAX_MESSAGES:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            continue
        content = content.strip()
        if content:
            clean_messages.append({"role": role, "content": content[:MAX_MESSAGE_CHARS]})

    if not clean_messages or clean_messages[-1]["role"] != "user":
        return jsonify({"reply": "Please send a valid user message."}), 400

    command_result = local_command(clean_messages[-1]["content"])
    if command_result:
        if isinstance(command_result, dict):
            return jsonify(command_result)
        return jsonify({"reply": command_result})

    if client is None:
        return jsonify({
            "reply": "SPIRIT's AI connection is not configured yet. Add OPENAI_API_KEY to your environment and restart the app."
        }), 503

    try:
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=clean_messages,
            tools=[{"type": "web_search"}],
        )
        answer = response.output_text or "I couldn't create a response. Please try again."
        return jsonify({"reply": answer})
    except Exception as exc:
        app.logger.exception("SPIRIT API request failed: %s", exc)
        return jsonify({
            "reply": "SPIRIT couldn't connect to the AI service. Check your API key, model setting, internet connection, and API account."
        }), 502

if __name__ == "__main__":
    # For local development only. Use a production WSGI server when deploying.
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
