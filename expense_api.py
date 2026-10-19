

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json

app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://expense-tracker-sigma-two-50.vercel.app"
],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).with_name("web_expenses.json")


def load_expenses():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_expenses(expenses):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=4)


class Expense(BaseModel):
    title: str
    category: str
    amount: float
    expense_date: str

@app.get("/")
def home():
    return {
        "message": "Expense Tracker API is running!",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/expenses")
def get_expenses():
    return load_expenses()


@app.post("/expenses")
def add_expense(expense: Expense):
    expenses = load_expenses()

    new_expense = {
        "id": max(
            (item.get("id", 0) for item in expenses),
            default=0
        ) + 1,
        "title": expense.title,
        "category": expense.category,
        "amount": expense.amount,
        "expense_date": expense.expense_date,
    }

    expenses.append(new_expense)
    save_expenses(expenses)

    return {
        "message": "Expense added successfully",
        "expense": new_expense
    }

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    expenses = load_expenses()

    updated_expenses = [
        expense for expense in expenses
        if expense.get("id") != expense_id
    ]

    if len(updated_expenses) == len(expenses):
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    save_expenses(updated_expenses)

    return {
        "message": "Expense deleted successfully",
        "deleted_id": expense_id
    }

