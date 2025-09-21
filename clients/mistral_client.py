import json

from mistralai import Mistral
from pydantic import BaseModel, SecretStr
from typing import Optional

from models import Category

class LLMCategoryResponse(BaseModel):
	category_id: str
	confidence_level: int
	suggested_category_name: Optional[str]

model = "ministral-8b-latest"

class MistralClient:
	def __init__(self, access_token: SecretStr):
		self.client = Mistral(api_key=access_token)

	def categorize_transaction_by_products(self, product_names: list[str], categories: list[Category]) -> LLMCategoryResponse:
		chat_response = self.client.chat.parse(
			model=model,
			messages=[
				{
					"role": "system",
					"content": """
						A list of provided product names from an order and a list of categories (with a string and name). With this data, the goal
						should be to summarize the products into a single category. Also, provide a degree of confidence from 0 to 100 signifying how
						confident you are in your response (0 being low confidence and 100 being high confidence). If you cannot determine which category to summarize
						the product order as, you can suggest a category name that can be used.
						"""
				},
				{
					"role": "user",
					"content": f"Products:\n{json.dumps(product_names, indent=2)}\nCategories:\n{json.dumps([ob.__dict__ for ob in categories], indent=2)}"
				},
			],
			response_format=LLMCategoryResponse,
			max_tokens=256,
		)

		return chat_response.choices[0].message.parsed

	def categorize_transaction_by_payee(self, payee_name: str) -> LLMCategoryResponse:
		chat_response = self.client.chat.parse(
			model=model,
			messages=[
				{
					"role": "system",
					"content": "The payee (recepient of the payment) for a credit card transaction has been provided in addition to a list of payments"
				}
			],
			response_format=LLMCategoryResponse,
			max_tokens=256
		)

		return
	