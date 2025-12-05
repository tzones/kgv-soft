import enum
from sqlalchemy import (
    Column, Integer, String, Date, Boolean, ForeignKey,
    Numeric, Text, Enum, JSON, DateTime
)
from sqlalchemy.orm import relationship
from .db import Base


class ContractStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"
    PENDING = "PENDING"


class InvoiceStatus(str, enum.Enum):
    OPEN = "OPEN"
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"


class CashbookType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=True, unique=True)
    phone = Column(String(50), nullable=True)
    street = Column(String(200), nullable=True)
    zip_code = Column(String(10), nullable=True)
    city = Column(String(100), nullable=True)
    iban = Column(String(34), nullable=True)
    bic = Column(String(11), nullable=True)
    member_since = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    contracts = relationship("Contract", back_populates="member")
    invoices = relationship("Invoice", back_populates="member")
    user = relationship("User", back_populates="member", uselist=False)


class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), unique=True, nullable=False)
    size_sqm = Column(Numeric(10, 2), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    contracts = relationship("Contract", back_populates="parcel")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    parcel_id = Column(Integer, ForeignKey("parcels.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(Enum(ContractStatus), default=ContractStatus.ACTIVE)
    yearly_rent = Column(Numeric(10, 2), nullable=False, default=0)
    yearly_additional = Column(Numeric(10, 2), nullable=False, default=0)

    member = relationship("Member", back_populates="contracts")
    parcel = relationship("Parcel", back_populates="contracts")
    invoices = relationship("Invoice", back_populates="contract")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    year = Column(Integer, nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.OPEN)

    member = relationship("Member", back_populates="invoices")
    contract = relationship("Contract", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")
    bank_transactions = relationship("BankTransaction", back_populates="matched_invoice")
    cashbook_entries = relationship("CashbookEntry", back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    invoice = relationship("Invoice", back_populates="items")


class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id = Column(Integer, primary_key=True, index=True)
    booking_date = Column(Date, nullable=False)
    value_date = Column(Date, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    balance = Column(Numeric(10, 2), nullable=True)
    purpose = Column(Text, nullable=True)
    counterparty_name = Column(String(255), nullable=True)
    counterparty_iban = Column(String(34), nullable=True)
    raw_data = Column(JSON, nullable=True)
    import_filename = Column(String(255), nullable=True)

    matched_invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    matched_member_id = Column(Integer, ForeignKey("members.id"), nullable=True)

    matched_invoice = relationship("Invoice", back_populates="bank_transactions")


class CashbookEntry(Base):
    __tablename__ = "cashbook_entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    type = Column(Enum(CashbookType), nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)

    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    invoice = relationship("Invoice", back_populates="cashbook_entries")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)

    member = relationship("Member", back_populates="user")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)
