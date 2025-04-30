from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel
from typing import List

from src.core.settings import settings
from src.models.email_models import ChaseExpenseResponse
from src.email.gmail import (
    get_gmail_client,
    search_emails,
    get_email_content,
    get_chase_expenses
)

class Email(BaseModel):
    """Model for email."""
    subject: str
    sender: str
    date: str
    body: str


def get_google_genai_client() -> ChatGoogleGenerativeAI:
    """Initialize the Google Generative AI client."""
    return ChatGoogleGenerativeAI(
        temperature=0,
        model=settings.GOOGLE_GEMINI_MODEL,
        max_output_tokens=512,
        top_k=40,
        top_p=0.95,
        api_key=settings.GOOGLE_GEMINI_TOKEN,
    )

@tool(description="Get the latest email from Gmail for the last 24 hours and not yet seen.",)
def get_latest_email() -> List[dict]:
    """Get the latest email from Gmail for the last 24 hours and not yet seen."""
    service = get_gmail_client()
    if not service:
        return []

    query = "newer_than:1d is:unread"
    messages = search_emails(service, query)
    if not messages:
        return []

    email_list = []
    for message in messages:
        message_id = message['id']
        email_content = get_email_content(service, message_id)
        if email_content:
            subject = message['payload']['headers'][0]['value']
            sender = message['payload']['headers'][1]['value']
            date = message['payload']['headers'][2]['value']
            email_list.append({
                "subject": subject,
                "sender": sender,
                "date": date,
                "body": email_content
            })
    return email_list

@tool(description="Get the chase expense from the email.")
def get_chase_expense() -> ChaseExpenseResponse:
    """Get the chase expense from the email."""
    return get_chase_expenses()
    

    
if __name__ == "__main__":
    # Step 1: Call your tool directly

    # Optional: Call your parsing logic too
    expenses = get_chase_expenses()
    if expenses.status == "failure":
        print("Failed to retrieve expenses.")
        exit(1)
    if not expenses.data:
        print("No expenses found.")
        exit(1)

    expense_data = [
        {
            "account": expense.account,
            "date": expense.date.strftime("%Y-%m-%d"),
            "merchant": expense.merchant,
            "amount": expense.amount
        }
        for expense in expenses.data
    ]
    # Step 2: Build context for the LLM manually
    context = "\n".join(
        [f"{expense['date']} - {expense['merchant']}: {expense['amount']}" for expense in expense_data]
    )

    # Step 3: Send to LLM for summarization or calculation
    llm = get_google_genai_client()
    query = f"""Based on the following email messages, how much did I spend? Can you summarize the total amount spent and provide a breakdown per month?\n\n 
    Only consider Chase credit card expense notifications. Format output as total + breakdown.\n\n{context}
    """

    response = llm.invoke([HumanMessage(content=query)])
    print(response.content)
