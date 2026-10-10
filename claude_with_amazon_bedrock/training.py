from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

model_id = "claude-haiku-4-5-20251001"


def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})


def chat(messages, tools=None, tool_choice=None):
    kwargs = {
        "model": model_id,
        "max_tokens": 1000,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
    if tool_choice:
        kwargs["tool_choice"] = {"type": "tool", "name": tool_choice}

    return client.messages.create(**kwargs)


article_details_schema = {
    "name": "article_details",
    "description": "Extracts key information from an article",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the article",
            },
            "author": {
                "type": "string",
                "description": "The author's name",
            },
            "topics": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of key topics mentioned",
            },
        },
        "required": ["title", "author", "topics"],
    },
}

article_text = """
The Rise of Quantum Computing
By Dr. Elena Vasquez

Quantum computing is moving from theory to practice faster than many
expected. This article covers recent breakthroughs in qubit stability,
the race between major tech companies, and what it all means for
cryptography and drug discovery in the next decade.
"""

messages = []
add_user_message(
    messages,
    f"""
Analyze the article below and extract key data. Then call the article_details tool.

<article_text>
{article_text}
</article_text>
""",
)

response = chat(messages, tools=[article_details_schema], tool_choice="article_details")

tool_use_block = next(block for block in response.content if block.type == "tool_use")
print(tool_use_block.input)
