from dataclasses import dataclass
import datetime

@dataclass
class Order:
	id: str
	date: datetime.date
	total_cost: float
	product_names: list[str]

@dataclass
class Category:
	id: str
	name: str
	category_group_name: str

@dataclass
class Transaction:
	order_id: str
	transaction_id: str
	date: datetime
