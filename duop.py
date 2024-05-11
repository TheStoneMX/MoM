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


def claude3(messages, system_message):
    response = anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": messages}],
        max_tokens=700,
        system=system_message,
        temperature=0.3,
        stream=False
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
        temperature=0.3
    )

    message_content = response.choices[0].message.content.strip()
    return message_content

def duopoly(user_message):
    system_message_oi = (f"You are a wise and knowledgeable openai coder and problem solver expert who provides thoughtful answers to questions. Discuss and push back at Claude3 Oracle, challenge his suggestions and evaluate the best solutions based on the context from other advisors answers to solve the problem {user_message}")
    system_message_c3 = (f"You are a wise and knowledgeable claude3 coder and problem solver expert who provides thoughtful answers to questions. Discuss and push back at OpenAI Oracle, challenge his suggestions and evaluate the best solutions based on the context from other advisors answers to solve the problem {user_message}")
    system_message5 = ("You are an expert at looking at a conversation between two smart oracles and extracting the best answer to a problem from the conversation.")
    
    conversation_history = []  # This will store the conversation history
    
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
        
    peasant_answers = "\n\n".join(f"{name}'s advice: {advice}" for name, advice in answers.items())
    
    oracle_prompt = (f"{{ADVISORS' INSIGHTS}}:{peasant_answers}\n\nHello Oracle OpenAI, this is Oracle Claude3. Let's discuss and find a solution to the {{PROBLEM}} while challenging and taking the {{ADVISORS' INSIGHTS}} into consideration. Solve the {{PROBLEM}}: {user_message}")

    conversation_history.append(oracle_prompt)  # Start the conversation

    for i in range(6):  # Six turns of discussion
        current_context = "\n".join(conversation_history)
        if i % 2 == 0:  # OpenAI's turn to speak
            claude_message = claude3(current_context, system_message_c3)
            openai_message = f"Oracle Claude3 said: {claude_message}\n"
            print(YELLOW + openai_message + RESET_COLOR)
            conversation_history.append(openai_message)
        else:  # Claude3's turn to speak
            openai_message = openai(current_context, system_message_oi)
            claude_message = f"Oracle OpenAI responded: {openai_message}\n"
            print(CYAN + claude_message + RESET_COLOR)
            conversation_history.append(claude_message)

        time.sleep(1)  # Simulate processing time

    # Combine the conversation history for final response
    full_conversation = "\n".join(conversation_history)
    final_response = openai(f"Summarize the conversation and conclude with a final answer to the {user_message}:\n{full_conversation}", system_message5)
    progress_bar.update()

    progress_bar.close()  # Close the progress bar
    return final_response


# The HTML generator function remains the same
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
            <h1>Response from AI Oracles</h1>
            <p>This section contains dynamically generated responses from a discussion between Oracle AI models, processed and finalized for the user.</p>
            <pre>{full_response}</pre>
        </div>
    </body>
    </html>
    '''

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as temp_file:
        temp_file.write(html_content)
        webbrowser.open('file://' + temp_file.name)

# Example usage
question = open_file("problem.txt")
final_response = duopoly(question)
generate_html_response(final_response)
