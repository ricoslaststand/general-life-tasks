from functools import reduce
from typing import Optional

import duckdb
import polars as pl
from dateutil import parser
from dotenv import load_dotenv
from loguru import logger
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from clients.mistral_client import MistralClient
from clients.ynab_client import YNABClient
from config import settings
from models import Category, Order
from services.order_categorizer import OrderCategorizer

load_dotenv()

JOB_NAME = "YNAB Transaction Categorization"

def main():
	mistral_client = MistralClient(access_token=settings.mistral_access_key)
	ynab_client = YNABClient(access_token=settings.ynab_access_key)

	con = duckdb.connect("order_database.db")
	print(con.sql("SHOW ALL TABLES"))

	con.execute("""CREATE OR REPLACE TABLE order_products (
					order_id VARCHAR,
					product_name VARCHAR
				)
	""")

	con.execute("""
					CREATE OR REPLACE TABLE orders (
						order_id VARCHAR,
						order_date DATE,
						total_amount DOUBLE
					)
				""")

	duckdb.read_csv("amazon_orders.csv", normalize_names=True)

	df = pl.read_csv("amazon_orders.csv")

	budget_id = "3c8bf77e-eb32-4252-9280-efcaa10d3c5e"

	automated_categorization_flag_color = "blue"

	amazon_payee_id = "ff703823-c86d-4ef9-b264-e18eb672e269"
	amazon_prime_payee_id = "d7e44915-375b-4551-a6ab-bc58e8d938f0"

	invalid_amazon_categories = [
		"Gas",
		"Transportation",
		"Alcohol",
		"Travel",
		"Credit card"
	]

	amazon_orders = df.filter(
		pl.col("Website") == "Amazon.com"
	).group_by("Order ID").all()

	category_groups = ynab_client.get_categories(budget_id=budget_id)

	formattedCategories = []

	for category_group in category_groups:
		for category in category_group.categories:
			formattedCategories.append(Category(category.id, category.name, category.category_group_name))

	categories_map: dict[str, Category] = {}

	for category in formattedCategories:
		categories_map[category.id] = category

	order_categorizer = OrderCategorizer(llm_client=mistral_client, categories=formattedCategories)

	total_order_price_idx = amazon_orders.get_column_index("Total Owed")
	order_date = amazon_orders.get_column_index("Order Date")
	product_name_idx = amazon_orders.get_column_index("Product Name")

	uncategorized_amazon_transactions = ynab_client.get_uncategorized_transactions(budget_id=budget_id, payee_id=amazon_prime_payee_id)

	uncategorized_amazon_transactions.transactions.sort(key=lambda x: x.var_date)

	def edit_transaction_memo(memo: str, old_category: Optional[Category], new_category: Category) -> str:
		if "updated from" in memo.lower():
			# TODO: in future, replace previously automated part of the memo with a new category
			return memo

		old_category_str = (old_category.id, old_category.name) if old_category else ("","uncategorized")
		new_category_str = (new_category.id, new_category.name)
		memo_addition = f"Updated from {old_category_str} to {new_category_str}"

		return memo + "\n\n" + memo_addition

	for row in amazon_orders.iter_rows():
		order_id = row[0]

		try:
			order_date = parser.isoparse(row[2][0])
		except Exception as e:
			print(e)
		total_order_price = reduce(lambda x, y: x + y, row[total_order_price_idx], 0)
		product_name = row[product_name_idx]
		
		order = Order(order_id, order_date, total_order_price, product_name)
		con.execute(
			"INSERT INTO orders (order_id, order_date, total_amount) VALUES (? , ?, ?)",
				(
					order_id,
					order_date.strftime("%Y-%m-%d"),
					total_order_price
				)
		)
		for product in product_name:
			con.execute("INSERT INTO order_products (order_id, product_name) VALUES (?, ?)", (order_id, product))

	for transaction in uncategorized_amazon_transactions.transactions[40:]:
		order_date, amount = transaction.var_date, -transaction.amount

		formatted_amount = amount / 1000

		result = con.execute("SELECT * FROM orders WHERE order_date = ? AND total_amount = ?",
			(
				order_date.strftime("%Y-%m-%d"),
				formatted_amount
			)
		)

		order = result.fetchone()
		if order:
			logger.debug("Found corresponding order for transaction {}", transaction.id)
			result = con.execute("SELECT product_name FROM order_products WHERE order_id = ?", [order[0]])
			product_names = [item[0] for item in result.fetchall()]
			print("Here are all the products:", product_names)
			response = order_categorizer.categorize_order_by_product_names(names=product_names)
			print("order_date =", order_date)

			new_category = categories_map[response.category_id]

			new_memo = edit_transaction_memo(
				transaction.memo,
				None,
				Category(id=new_category.id, name=new_category.name, category_group_name="")
			)

			existing_transaction = {
				"account_id": transaction.account_id,
				"var_date": transaction.var_date,
				"amount": transaction.amount,
				"payee_id": transaction.payee_id,
				"payee_name": transaction.payee_name,
				"category_id": response.category_id,
				"memo": new_memo,
				"approved": transaction.approved,
				"flag_color": automated_categorization_flag_color,
			}
			response = ynab_client.categorize_transaction(budget_id=budget_id, transaction_id=transaction.id, transaction_data=existing_transaction)
			logger.info("Categorizing transaction {} as '{}'", transaction.id, new_category.name)
			print(response)
			break
		else:
			print("Cannot find anything for order on", order_date, " and for $", formatted_amount)

		registry = CollectorRegistry()
		g = Gauge(JOB_NAME, 'Last time a batch job successfully finished', registry=registry)
		g.set_to_current_time()
		PROMETHEUS_PUSHGATEWAY = "http://pushgateway:9091"
		logger.debug(PROMETHEUS_PUSHGATEWAY)
		push_to_gateway(PROMETHEUS_PUSHGATEWAY, job='batchA', registry=registry)

if __name__ == "__main__":
	main()
