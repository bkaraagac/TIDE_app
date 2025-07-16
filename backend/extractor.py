import openai
import os
from dotenv import load_dotenv
import json
import re
import tiktoken

# Constants
MODEL = "gpt-4o-mini"
MAX_TOKENS = 128000
RESERVED_TOKENS = 4000  # Tokens reserved for system message + prompt + output
MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_TOKENS

# Tokenizer for counting
encoding = tiktoken.encoding_for_model(MODEL)

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def truncate_to_token_limit(text: str, max_tokens: int) -> str:
    tokens = encoding.encode(text)
    return encoding.decode(tokens[:max_tokens])

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()


def clean_json_response(content):
    """Clean the response to extract only the JSON part"""
    # Remove markdown code blocks if present
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*$', '', content)

    # Find the JSON object (starts with { and ends with })
    start = content.find('{')
    end = content.rfind('}') + 1

    if start != -1 and end != -1:
        return content[start:end]
    return content

def extract_info(text):
    system_message = """You are a research assistant specialized in extracting structured data from academic theses and reports.
Extract only information that is explicitly stated in the provided text.
Do not make assumptions or generate information that is not present.
Your response must be ONLY a valid JSON object matching the specified schema - no explanatory text, no markdown formatting, no code blocks.
If a field is not mentioned in the text, return the value "not present" for that field.
Respond in English even when the input is in another language."""

    # ✅ Truncate the document text to avoid exceeding token limits
    truncated_text = truncate_to_token_limit(text, MAX_INPUT_TOKENS)

    prompt = f"""From the attached thesis or report, extract the following structured information as a JSON object:

{{
  "title": "the title of the thesis or report",
  "keywords": "the keywords of the thesis or report, such as the main variables or constructs studied",
  "research_goal": "objective or aim of the study or project",
  "research_question": "explicitly stated research question(s)",
  "hypotheses": "list of hypotheses if mentioned",
  "methodology": "briefly describe the methodology used in this study or project. Include relevant details such as whether it was empirical or theoretical, whether fieldwork was conducted, the type of analysis (e.g. qualitative, quantitative, mixed methods), and any specific methods mentioned (e.g. case study, experiment, survey, content analysis, etc.). Keep the description concise.",
  "findings_summary": "summarize whether findings matched expectations or the research/project aim was achieved",
  "future_research_suggestions": "suggestions made by the author for future research, typically found in the conclusion or discussion section",
  "author": "name of the thesis author",
  "supervisor": "name(s) of the thesis supervisor(s)",
  "study_programme": "name of the study programme or department",
  "submission_date": "date when the thesis was submitted",
  "organisation": "in the case of collaboration with external organisation(s), the name of the these organisation(s)"
}}

Document text:
{truncated_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw_content = response.choices[0].message.content

    try:
        # Clean the response to extract JSON
        cleaned_content = clean_json_response(raw_content)

        # Parse the JSON
        extracted_data = json.loads(cleaned_content)

        # Basic cleaning to prevent CSV issues
        for key, value in extracted_data.items():
            if isinstance(value, str):
                # Replace newlines and clean up quotes
                value = value.replace('\n', ' ').replace('\r', ' ')
                value = value.replace('"', "'")
                extracted_data[key] = value.strip()

        return extracted_data

    except Exception as e:
        return {"error": str(e), "raw_response": raw_content}