from datetime import datetime,date
from decimal import Decimal
from psycopg import Connection
from fastapi import FastAPI,Depends, HTTPException ,status
from pydantic import BaseModel
from database import get_db
from typing import Literal
from Schema.expense import expense, expense_response, expense_update


app = FastAPI()

class income_create(BaseModel):
    title: str
    amount: Decimal
    category: Literal['salary','business','investment','other']
    description: str | None = None
    income_date: date

class income_response(BaseModel):
    id: int
    title: str
    amount: Decimal
    category: Literal['salary','business','investment','other']
    description: str | None = None
    income_date: date
    created_at: datetime
    updated_at: datetime

class income_update(BaseModel):
    title: str | None = None
    amount: Decimal | None = None
    category: Literal['salary','business','investment','other'] | None = None
    description: str | None = None
    income_date: date | None = None


@app.post("/income",
          response_model=income_response)
def create_income(income: income_create, db: Connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO income(
                title,
                amount,
                category,
                description,
                income_date
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING 
                id,
                title,
                amount,
                category,
                description,
                income_date,
                created_at,
                updated_at
            """,
            (
                income.title,
                income.amount,
                income.category,
                income.description,
                income.income_date
            )
        )
        row = cursor.fetchone()
    return income_response(
        id=row[0],
        title=row[1],
        amount=row[2],
        category=row[3],
        description=row[4],
        income_date=row[5],
        created_at=row[6],
        updated_at=row[7]
    )

@app.get("/")
def root():
    return{
        "message": "Expense tracker API is running"
    }


@app.get("/health")
def check_database(db: Connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    return {
        "status": "OK",
        "database":"connected",
        "test":result[0]
    }



#create expense endpoint

@app.post("/expences", response_model=expense_response,)
def create_expence(expense: expense, db:Connection = Depends(get_db),):
    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO expenses(
                title, 
                amount, 
                category, 
                description,
                expense_date )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, title, amount, category,description, expense_date,  created_at, updated_at
            """,
            (expense.title, expense.amount, expense.category,expense.description, expense.expense_date),
        )
    
        row = cursor.fetchone()

    return expense_response(
        id=row[0],
        title=row[1],
        amount=row[2],
        category=row[3],
        description=row[4],
        expense_date=row[5],
        created_at=row[6],
        updated_at=row[7]
    )

@app.get("/expenses",
          response_model=list[expense_response])

def get_expenses(db: Connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                title,
                amount,
                category,
                description,
                expense_date,
                created_at,
                updated_at
            FROM expenses
            ORDER BY id
            """
        )
        rows = cursor.fetchall()

    return [expense_response(
        id=row[0],
        title=row[1],
        amount=row[2],
        category=row[3],
        description=row[4],
        expense_date=row[5],
        created_at=row[6],
        updated_at=row[7]
    ) for row in rows]

@app.get("/expenses/{expense_id}", response_model=expense_response)
def get_expense(expense_id: int, db: Connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                title,
                amount,
                category,
                description,
                expense_date,
                created_at,
                updated_at
                FROM expenses
                WHERE id = %s
            """,
            (expense_id,)
        )
        row = cursor.fetchone()
        
    if not row:
        raise HTTPException(status_code=404, detail="Expense not found")

    return expense_response(
        id=row[0],
        title=row[1],
        amount=row[2],
        category=row[3],
        description=row[4],
        expense_date=row[5],
        created_at=row[6],
        updated_at=row[7]
    )

@app.put("/expenses/{expense_id}", response_model=expense_response)
def update_expense(expense_id: int,expense:expense_update, db:Connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            """
            UPDATE expenses
            SET
                title = %s,
                amount = %s,
                category = %s,
                description = %s
                expense_date = %s,
                updated_at = NOW()
            WHERE id = %s
            RETURNING
                id,
                title,
                amount,
                category,
                description,
                expense_date,
                created_at,
                updated_at
            """,
            (
                expense.title,
                expense.amount,
                expense.category,
                expense.description,
                expense.expense_date,
                expense_id
            )
        )

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Expense not found")

    return expense_response(
        id=row[0],
        title=row[1],
        amount=row[2],
        category=row[3],
        description=row[4],
        expense_date=row[5],
        created_at=row[6],
        updated_at=row[7]
    )

# delete expense endpoint

@app.delete(
    "/expenses/{expense_id}",
    status_code= status.HTTP_204_NO_CONTENT
)
def delete_expense(
    expense_id: int,
    db: Connection = Depends(get_db)
):
    with db.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM expenses
            where id = %s
            RETURNING ID
            """,
            (expense_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found")
