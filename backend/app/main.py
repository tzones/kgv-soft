from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from .db import Base, engine, SessionLocal
from . import models, schemas, csv_import
from .auth import (
    get_db,
    get_current_user,
    get_current_member_user,
    create_access_token,
    hash_password,
    get_user_by_email,
)
from .email_utils import send_invite_email

import secrets

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kleingarten-Verwaltung")

origins = ["*"]  # für Entwicklung, später einschränken

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_initial_admin():
    db = SessionLocal()
    try:
        admin_exists = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).first()
        if not admin_exists:
            user = models.User(
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                role=models.UserRole.ADMIN,
                member_id=None,
            )
            db.add(user)
            db.commit()
            print("Initialer Admin erstellt: admin@example.com / admin123")
    finally:
        db.close()


create_initial_admin()


# Auth

@app.post("/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Nutzer existiert nicht")

    from .auth import verify_password
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Falsche Zugangsdaten")

    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


# Mitglieder (Admin nutzt /docs)

@app.post("/members", response_model=schemas.Member)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    m = models.Member(**member.dict())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@app.get("/members", response_model=list[schemas.Member])
def list_members(db: Session = Depends(get_db)):
    return db.query(models.Member).all()


# Parzellen & Verträge (einfach)

@app.post("/parcels", response_model=schemas.Parcel)
def create_parcel(parcel: schemas.ParcelCreate, db: Session = Depends(get_db)):
    p = models.Parcel(**parcel.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.get("/parcels", response_model=list[schemas.Parcel])
def list_parcels(db: Session = Depends(get_db)):
    return db.query(models.Parcel).all()


@app.post("/contracts", response_model=schemas.Contract)
def create_contract(contract: schemas.ContractCreate, db: Session = Depends(get_db)):
    c = models.Contract(**contract.dict())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@app.get("/contracts", response_model=list[schemas.Contract])
def list_contracts(db: Session = Depends(get_db)):
    return db.query(models.Contract).all()


# Rechnungen (einfacher Endpunkt)

@app.post("/invoices", response_model=schemas.Invoice)
def create_invoice(data: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    invoice = models.Invoice(
        member_id=data.member_id,
        contract_id=data.contract_id,
        year=data.year,
        invoice_date=data.invoice_date,
        due_date=data.due_date,
        total_amount=data.total_amount,
        status=data.status,
    )
    db.add(invoice)
    db.flush()

    for item in data.items:
        db_item = models.InvoiceItem(
            invoice_id=invoice.id,
            description=item.description,
            amount=item.amount,
        )
        db.add(db_item)

    db.commit()
    db.refresh(invoice)
    return invoice


@app.get("/invoices", response_model=list[schemas.Invoice])
def list_invoices(db: Session = Depends(get_db)):
    return db.query(models.Invoice).all()


# CSV-Import Bank

@app.post("/bank/import")
async def import_bank_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8", errors="ignore")
    created = csv_import.import_bank_csv(db, content, filename=file.filename)
    return {"imported": created}


@app.get("/bank/transactions", response_model=list[schemas.BankTransaction])
def list_bank_transactions(db: Session = Depends(get_db)):
    return db.query(models.BankTransaction).order_by(models.BankTransaction.booking_date.desc()).all()


# Kassenbuch

@app.post("/cashbook", response_model=schemas.CashbookEntry)
def create_cashbook_entry(entry: schemas.CashbookEntryCreate, db: Session = Depends(get_db)):
    e = models.CashbookEntry(**entry.dict())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@app.get("/cashbook", response_model=list[schemas.CashbookEntry])
def list_cashbook_entries(db: Session = Depends(get_db)):
    return db.query(models.CashbookEntry).order_by(models.CashbookEntry.date.desc()).all()


# Mitglieder einladen (Zugangsdaten mailen)

@app.post("/members/{member_id}/invite")
def invite_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Nur für Admins")

    member = db.query(models.Member).get(member_id)
    if not member or not member.email:
        raise HTTPException(status_code=404, detail="Mitglied oder E-Mail nicht gefunden")

    existing_user = db.query(models.User).filter(models.User.email == member.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Für dieses Mitglied existiert bereits ein Login")

    password = secrets.token_urlsafe(10)
    user = models.User(
        email=member.email,
        password_hash=hash_password(password),
        role=models.UserRole.MEMBER,
        member_id=member.id,
    )
    db.add(user)
    db.commit()

    send_invite_email(member.email, password)
    return {"status": "ok", "email_sent_to": member.email}


# Mitglieder-Portal: eigene Daten

@app.get("/me", response_model=schemas.Member)
def get_me(
    current_user: models.User = Depends(get_current_member_user),
    db: Session = Depends(get_db),
):
    member = db.query(models.Member).get(current_user.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")
    return member


@app.get("/me/parcels")
def get_my_parcels(
    current_user: models.User = Depends(get_current_member_user),
    db: Session = Depends(get_db),
):
    contracts = (
        db.query(models.Contract)
        .filter(models.Contract.member_id == current_user.member_id)
        .all()
    )
    result = []
    for c in contracts:
        result.append({
            "contract_id": c.id,
            "parcel_id": c.parcel.id,
            "parcel_number": c.parcel.number,
            "size_sqm": str(c.parcel.size_sqm) if c.parcel.size_sqm else None,
            "status": c.status.value,
            "start_date": c.start_date,
            "end_date": c.end_date,
            "yearly_rent": str(c.yearly_rent),
            "yearly_additional": str(c.yearly_additional),
        })
    return result


@app.get("/me/invoices", response_model=list[schemas.Invoice])
def get_my_invoices(
    current_user: models.User = Depends(get_current_member_user),
    db: Session = Depends(get_db),
):
    invoices = (
        db.query(models.Invoice)
        .filter(models.Invoice.member_id == current_user.member_id)
        .all()
    )
    return invoices


@app.get("/me/balance")
def get_my_balance(
    current_user: models.User = Depends(get_current_member_user),
    db: Session = Depends(get_db),
):
    member_id = current_user.member_id

    total_invoices = (
        db.query(func.coalesce(func.sum(models.Invoice.total_amount), 0))
        .filter(
            models.Invoice.member_id == member_id,
            models.Invoice.status != models.InvoiceStatus.CANCELLED
        )
        .scalar()
    )

    total_bank = (
        db.query(func.coalesce(func.sum(models.BankTransaction.amount), 0))
        .filter(models.BankTransaction.matched_member_id == member_id)
        .scalar()
    )

    balance = float(total_bank - total_invoices)
    return {"balance": balance, "total_invoices": float(total_invoices), "total_payments": float(total_bank)}


# Kalender

@app.post("/calendar/events", response_model=schemas.CalendarEvent)
def create_event(
    event: schemas.CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Nur für Admins")

    e = models.CalendarEvent(**event.dict())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@app.get("/calendar/events", response_model=list[schemas.CalendarEvent])
def list_events(db: Session = Depends(get_db)):
    return (
        db.query(models.CalendarEvent)
        .filter(models.CalendarEvent.is_public == True)
        .order_by(models.CalendarEvent.start.asc())
        .all()
    )
