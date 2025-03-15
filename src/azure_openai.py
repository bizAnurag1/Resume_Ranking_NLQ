import json
from openai import AzureOpenAI
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_MODEL, PROMPT_TEMPLATE

class AzureOpenai:
    def __init__(self):
        self.openai_client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2024-02-01"
        )


    def convert_to_json(self, text):
        prompt_text = PROMPT_TEMPLATE + f"\nResume_text:\n{text}"

        response = self.openai_client.chat.completions.create(
            model=AZURE_OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=2000
        )

        extracted_data = response.choices[0].message.content.strip("```json")
        # print(extracted_data)
        return extracted_data
