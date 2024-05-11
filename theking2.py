import anthropic
from openai import OpenAI
import os
from dotenv import load_dotenv
import re
import requests
import markdown
import webbrowser
import tempfile
from tqdm import tqdm
import time
from groq import Groq


load_dotenv()

# API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Clients
anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
ollama_client = OpenAI(base_url='http://localhost:11434/v1', api_key='llama3')
openai_client = OpenAI(api_key=openai_api_key)
groq_client = client = Groq(api_key=groq_api_key)

client = Groq()

# Colors (unused in HTML output, kept for possible console outputs or further expansions)
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Function to open a file and return its contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def groq_llama70B(messages):
    system_message3="You are a coder and problem solver expert"
    response = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message3},
            {"role": "user", "content": messages}
        ],
        model="llama3-70b-8192",
        temperature=0.3,
        max_tokens=1024,
    )
    message_content = response.choices[0].message.content.strip()
    return message_content

def ollamacpp(model, messages):
    system_message = {"role": "system", "content": "You are a coder and problem solver expert"}

    # Ensure messages is a list and each element is properly formatted
    if not isinstance(messages, list):
        messages = [{"role": "user", "content": messages}]
    else:
        messages = [{"role": "user", "content": msg} if not isinstance(msg, dict) else msg for msg in messages]
    messages.insert(0, system_message)

    response = ollama_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3
    )

    message_content = response.choices[0].message.content.strip()
    return message_content  


def claude3(messages):
    response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        messages=[{"role": "user", "content": messages}],
        max_tokens=700,
        system="You are a coder and problem solver expert",
        temperature=0.3,
    )

    message_content = response.content
    message_content = message_content[0].text.strip()
    return message_content

def openai(messages, system_message):
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": messages}
        ],
        temperature=0.3,
    )

    message_content = response.choices[0].message.content.strip()
    return message_content

def generate_html_response(full_response):
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interactive AI Response</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                margin: 40px;
                color: #333;
            }}
            .container {{
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            pre {{
                background-color: #282a36;
                color: #f8f8f2;
                border-radius: 5px;
                border: 1px solid #ccc;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', Courier, monospace;
                overflow: auto;
                white-space: pre-wrap;
            }}
            h1 {{
                color: #2c3e50;
            }}
            p, ol {{
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Response from AI Advisors</h1>
            <p>This section contains dynamically generated responses from various AI models processed by the <code>the_king</code> function.</p>
            <pre>{full_response}</pre>
        </div>
    </body>
    </html>
    '''

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as temp_file:
        temp_file.write(html_content)
        webbrowser.open('file://' + temp_file.name)

def the_king(user_message):
    system_message = """You are a wise and knowledgeable coder and problem solver king who provides thoughtful answers to questions.
    
    You have 10 advisors, who offer their insights to assist you.
    
    Consider their perspectives and advice, but ultimately provide your own well-reasoned response to the
    problem based on all context and advice. If you find their input helpful, feel free to acknowledge their
    contributions in your answer."""

    models = {
        "wizardlm2:7b": "Wizardlm2",
        "llama3": "Llama3 8B",
        "mistral": "Mistral 7B",
        "qwen:14b": "Qwen 14B",
        "phi3": "Phi3",
        "gemma:7b": "Gemma 7B",
        "codeqwen": "CodeQwen",
        "openchat": "OpenChat",
        "magicoder": "Magicoder"
    }
    answers = {}
    tasks = [f"Consulting {name}" for name in models.values()]
    progress_bar = tqdm(tasks, desc="Gathering insights", unit="task")

    for model, name in models.items():
        progress_bar.set_description(f"Consulting {name}")
        answers[name] = ollamacpp(model, user_message)
        progress_bar.update()

    # Adding Llama3 70B and Claude3 responses
    progress_bar.set_description("Consulting Llama3 70B Pessant")
    answers["Llama3 70B"] = groq_llama70B(user_message)
    progress_bar.update()

    progress_bar.set_description("Consulting Claude3 Pessant")
    answers["Claude3"] = claude3(user_message)
    progress_bar.update()

    # Construct the peasant_answers string
    peasant_answers = "\n\n".join(f"{name}'s advice: {advice}" for name, advice in answers.items())

    progress_bar.set_description("Compiling advice from Peasants")
    
    # Final processing and output
    king_prompt = f"Pessants Advice:{peasant_answers}\n\n{{Problem}}: {user_message}\n\nUse the insights from the advisors to create a step-by-step plan to solve the given {{problem}}, then solve the problem your way. Also, include footnotes to the best advisor contributions."
    progress_bar.set_description("The King is solving the problem")
    king_answer = openai(king_prompt, system_message)
    progress_bar.update()

    progress_bar.close()
    return king_answer

question = open_file("problem.txt")
html_response1 = the_king(question)  #First Run
#html_response2 = the_king(html_response1)  # Run it twice
generate_html_response(html_response1)
