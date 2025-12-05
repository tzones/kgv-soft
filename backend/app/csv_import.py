import csv
from io import StringIO
from dateutil import parser
from sqlalchemy.orm import Session
from . import models


def import_bank_csv(db: Session, file_content: str, filename: str):
    f = StringIO(file_content)
    reader = csv.DictReader(f, delimiter=';')

    created = 0
    for row in reader:
        try:
            booking_date = parser.parse(row.get("Buchungstag") or row.get("Buchung"))
            value_date_raw = row.get("Wertstellung") or row.get("Valuta")
            value_date = parser.parse(value_date_raw) if value_date_raw else None

            amount_str = row.get("Betrag") or row.get("Umsatz")
            amount = amount_str.replace(".", "").replace(",", ".")

            balance_str = row.get("Saldo") or row.get("Kontostand") or None
            balance = None
            if balance_str:
                balance = balance_str.replace(".", "").replace(",", ".")

            tx = models.BankTransaction(
                booking_date=booking_date.date(),
                value_date=value_date.date() if value_date else None,
                amount=amount,
                balance=balance,
                purpose=row.get("Verwendungszweck") or "",
                counterparty_name=row.get("Name") or row.get("Beg\u00fcnstigter/Zahlungspflichtiger"),
                counterparty_iban=row.get("IBAN") or None,
                raw_data=row,
                import_filename=filename,
            )
            db.add(tx)
            created += 1
        except Exception:
            continue

    db.commit()
    return created
