from flask import Flask, request, render_template_string, jsonify
from openai import OpenAI
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # CORS für alle Routen aktivieren

client = OpenAI()


# Load the entire content of the Markdown file once
def load_knowledge_base_from_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()  # Return the entire content of the Markdown file


# Ask OpenAI with knowledge-based answers only
def ask_openai(query, knowledge_base):
    messages = [
        {
            "role": "system",
            "content": "Sie sind ein hilfsbereiter Assistent, der nur die zur Verfügung gestellten Informationen zur Beantwortung von Fragen verwendet.",
        },
        {
            "role": "user",
            "content": f"Verwenden Sie zur Beantwortung der Frage nur die folgenden Kenntnisse: {knowledge_base}",
        },
        {"role": "user", "content": query},
    ]

    response = client.chat.completions.create(
        model="gpt-4o",  # Replace with your model name, e.g., gpt-4
        messages=messages,
        temperature=0,  # Ensures deterministic and knowledge-restricted answers
        max_tokens=1150,  # Limit response length if necessary
    )

    answer = response.choices[0].message.content

    if "I don't know" in answer or not answer:
        return "Leider hab ich dazu keine Info"
    else:
        return answer


# Lade die gesamte Markdown-Datei
knowledge_base = load_knowledge_base_from_markdown("k22.md")

# HTML-Template für die Startseite
html_template = """
<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8">
    <title>Terminal Bot</title>
  </head>
  <body>
    <h1>Stelle eine Frage an den Bot</h1>
    <form method="post" action="/ask">
      <label for="question">Frage:</label>
      <input type="text" id="question" name="question">
      <button type="submit">Senden</button>
    </form>
    {% if answer %}
    <h2>Antwort:</h2>
    <p>{{ answer }}</p>
    {% endif %}
  </body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(html_template)


@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.form["question"]
    answer = ask_openai(user_query, knowledge_base)
    return render_template_string(html_template, answer=answer)


@app.route("/api/qa_system", methods=["POST"])
def question_answer():
    data = request.get_json()
    user_input = data.get("input", "")
    answer = ask_openai(user_query, knowledge_base)
    response = {"input": user_input, "answer": answer}
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
