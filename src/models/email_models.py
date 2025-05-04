from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict
from enum import Enum


# define the status of the response in terms of success or failure in an enum like fashion
class ResponseStatusEnum(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"

class ChaseExpense(BaseModel):
    account: str
    date: str
    merchant: str
    amount: float

class ChaseExpenseResponse(BaseModel):
    status: ResponseStatusEnum
    message: str
    data: List[ChaseExpense]

class ExpenseSummary(BaseModel):
    total: float
    monthly_breakdown: Dict[str, float]