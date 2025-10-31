from pydantic import BaseModel

class Transaction(BaseModel):
    id: str
    payee_id: str
    date: str
