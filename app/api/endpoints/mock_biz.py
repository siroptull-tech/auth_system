from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import check_permission, get_current_active_user
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/mock-business", tags=["mock-business"])


@router.get("/invoices")
async def get_invoices(
    current_user: User = Depends(check_permission("invoices", "read")),
    db: Session = Depends(get_db),
) -> dict:
    return {
        "user": current_user.username,
        "resource": "invoices",
        "action": "read",
        "invoices": [
            {"id": 1, "amount": 1000, "status": "paid"},
            {"id": 2, "amount": 2000, "status": "pending"},
        ],
    }


@router.post("/invoices")
async def create_invoice(
    current_user: User = Depends(check_permission("invoices", "create")),
    db: Session = Depends(get_db),
) -> dict:
    return {
        "user": current_user.username,
        "resource": "invoices",
        "action": "create",
        "message": "Invoice created successfully",
        "invoice_id": 3,
    }


@router.delete("/invoices/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(check_permission("invoices", "delete")),
    db: Session = Depends(get_db),
) -> dict:
    return {
        "user": current_user.username,
        "resource": "invoices",
        "action": "delete",
        "message": f"Invoice {invoice_id} deleted successfully",
    }


@router.get("/reports")
async def get_reports(
    current_user: User = Depends(check_permission("reports", "read")),
    db: Session = Depends(get_db),
) -> dict:
    return {
        "user": current_user.username,
        "resource": "reports",
        "action": "read",
        "reports": [
            {"id": 1, "name": "Monthly Report", "period": "2024-01"},
            {"id": 2, "name": "Quarterly Report", "period": "Q1"},
        ],
    }


@router.get("/documents")
async def get_documents(
    current_user: User = Depends(check_permission("documents", "read")),
    db: Session = Depends(get_db),
) -> dict:
    return {
        "user": current_user.username,
        "resource": "documents",
        "action": "read",
        "documents": [
            {"id": 1, "name": "Contract A", "type": "contract"},
            {"id": 2, "name": "Invoice X", "type": "invoice"},
        ],
    }
