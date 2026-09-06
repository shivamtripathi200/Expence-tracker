from datetime import datetime,date
from decimal import Decimal
from psycopg import Connection
from pydantic import BaseModel
from fastapi import FastAPI,Depends, HTTPException ,status
from database import get_db
from typing import Literal


Expense_category = Literal['food','transport','rent']

class expense(BaseModel):
    title: str
    amount: Decimal
    category: Expense_category
    description: str | None= None
    expense_date: date

class expense_response(BaseModel):
    id: int
    title: str
    amount: Decimal
    category: Expense_category
    description: str | None= None
    expense_date: date
    created_at: datetime
    updated_at: datetime

class expense_update(BaseModel):
    title: str | None = None
    amount: Decimal | None = None
    category: Expense_category | None = None
    description: str | None = None
    expense_date: date | None = None