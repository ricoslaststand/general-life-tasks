from collections import Counter

class TransactionService:
    @staticmethod
    def get_transactions_by_payee_id(payee_id: str, transactions: tuple[str, str]) -> str | None:
        """
        Simple categorizer that determines that category of the transaction
        """

        category_count = Counter(map(lambda x: x[1], transactions))

        categories = []
        for c in category_count:
            if c:
                categories.append((category_count[c], c))

        categories.sort(reverse=True)
        
        return categories[0][1] if len(categories) else None
    