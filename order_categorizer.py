from models import Category

from mistral_client import MistralClient

class OrderCategorizer:
    def __init__(self, llm_client: MistralClient, categories: list[Category]):
        self.llm_client = llm_client
        self.categories = categories
        self.confidence_threshold = 80

    def categorize_order_by_product_names(self, names: list[str]):
        print("Categorizing this order...")
        response = self.llm_client.categorize_transaction_by_products(names, self.categories)

        print(response)
        return response

        # if response.confidence_level >= self.confidence_threshold:
            