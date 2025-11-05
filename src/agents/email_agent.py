from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from collections import defaultdict
from datetime import datetime
from typing import List

from src.core.settings import settings
from src.models.email_models import ChaseExpense, ExpenseSummary


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


async def get_chase_expenses(_=None) -> List[ChaseExpense]:
    from src.email.gmail import get_chase_expenses as get_data
    print("🛠 Getting expenses...")
    data = await get_data(_)
    if not data:
        print("No expenses found.")
        return []
    print(f"💰 Expenses: {data}")
    return data


def summarize_expenses_by_month(expenses: List[ChaseExpense]) -> ExpenseSummary:
    """
    Summarize Chase expenses by month. Outputs total and monthly breakdown.
    """
    print("🛠 Summarizing expenses... ")
    print(f"💰 Expenses received: {len(expenses)}")
    if not expenses:
        raise ValueError("Expected a non-empty list of expense records.")
    
    # Initialize a dictionary to hold monthly totals
    monthly_totals = defaultdict(float)
    total = 0.0
    for expense in expenses:
        try:
            date_obj = datetime.strptime(expense.date.split(" at ")[0], "%b %d, %Y")
            month_str = date_obj.strftime("%B %Y")
            amt = expense.amount
            monthly_totals[month_str] += amt
            total += amt
        except Exception as e:
            print(f"Error processing expense: {expense}")
            continue  # skip malformed entries

    print(f"💰 Monthly Totals: {monthly_totals}"
          f"\n💰 Total: {total}")
    return ExpenseSummary(
        total=total,
        monthly_breakdown=monthly_totals
    )

    
async def perform_agent_work():
    runnable_get_expenses = RunnableLambda(func=lambda x: None, afunc=get_chase_expenses)
    runnable_summarize = RunnableLambda(summarize_expenses_by_month)
    chain = runnable_get_expenses | runnable_summarize

    try:
        summary = await chain.ainvoke({})
        print("\n✅ Raw Summary:")
        print(f"Total: ${summary.total}")
        for month, amount in summary.monthly_breakdown.items():
            print(f"{month}: ${amount}")

        # Use Gemini to summarize the totals
        gemini = get_google_genai_client()
        user_prompt = f"""
You are a helpful finance assistant. Given the following expense summary:
- Total spent: ${summary.total}
- Monthly breakdown: {summary.monthly_breakdown}

Write a brief summary of spending behavior.
"""
        result = await gemini.ainvoke([HumanMessage(content=user_prompt)])

        print("\n🧠 Gemini Summary:")
        print(result.content)

    except Exception as e:
        print("\n❌ Error during processing:")
        print(e)

if __name__ == "__main__":
    import asyncio
    asyncio.run(perform_agent_work())
