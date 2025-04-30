from datetime import datetime
from pydantic import BaseModel
from typing import List
from enum import Enum


# define the status of the response in terms of success or failure in an enum like fashion
class ResponseStatusEnum(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"

class ChaseExpense(BaseModel):
    account: str
    date: datetime
    merchant: str
    amount: str

class ChaseExpenseResponse(BaseModel):
    status: ResponseStatusEnum
    message: str
    data: List[ChaseExpense]

