from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel

from .models import ContractStatus, InvoiceStatus, CashbookType, UserRole


class MemberBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    street: Optional[str] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    member_since: Optional[date] = None
    is_active: bool = True


class MemberCreate(MemberBase):
    pass


class Member(MemberBase):
    id: int

    class Config:
        orm_mode = True


class ParcelBase(BaseModel):
    number: str
    size_sqm: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: bool = True


class ParcelCreate(ParcelBase):
    pass


class Parcel(ParcelBase):
    id: int

    class Config:
        orm_mode = True


class ContractBase(BaseModel):
    member_id: int
    parcel_id: int
    start_date: date
    end_date: Optional[date] = None
    status: ContractStatus = ContractStatus.ACTIVE
    yearly_rent: Decimal
    yearly_additional: Decimal = Decimal("0.00")


class ContractCreate(ContractBase):
    pass


class Contract(ContractBase):
    id: int

    class Config:
        orm_mode = True


class InvoiceItemBase(BaseModel):
    description: str
    amount: Decimal


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceBase(BaseModel):
    member_id: int
    contract_id: Optional[int] = None
    year: int
    invoice_date: date
    due_date: Optional[date] = None
    total_amount: Decimal
    status: InvoiceStatus = InvoiceStatus.OPEN


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]


class Invoice(InvoiceBase):
    id: int
    items: List[InvoiceItemBase] = []

    class Config:
        orm_mode = True


class BankTransactionBase(BaseModel):
    booking_date: date
    value_date: Optional[date] = None
    amount: Decimal
    balance: Optional[Decimal] = None
    purpose: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_iban: Optional[str] = None


class BankTransaction(BankTransactionBase):
    id: int

    class Config:
        orm_mode = True


class CashbookEntryBase(BaseModel):
    date: date
    type: CashbookType
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Decimal
    invoice_id: Optional[int] = None


class CashbookEntryCreate(CashbookEntryBase):
    pass


class CashbookEntry(CashbookEntryBase):
    id: int

    class Config:
        orm_mode = True


# Auth / User

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: str


class User(UserBase):
    id: int
    role: UserRole
    member_id: Optional[int]

    class Config:
        orm_mode = True


# Kalender

class CalendarEventBase(BaseModel):
    title: str
    start: datetime
    end: Optional[datetime] = None
    description: Optional[str] = None
    is_public: bool = True


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEvent(CalendarEventBase):
    id: int

    class Config:
        orm_mode = True
