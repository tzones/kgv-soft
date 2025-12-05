\# Kleingarten-Verwaltung



Docker-basierte Webanwendung für einen Kleingartenverein.



\## Bestandteile



\- Backend: FastAPI (Python) + PostgreSQL

\- Frontend: Vue 3 (Vite)

\- Auth: Login für Mitglieder (JWT)

\- Funktionen:

&nbsp; - Mitgliederverwaltung (API)

&nbsp; - Parzellen, Verträge, Rechnungen (API-Grundlage)

&nbsp; - CSV-Import von Kontoauszügen

&nbsp; - Kassenbuch (API-Grundlage)

&nbsp; - Mitgliederportal: Login, eigene Daten, Rechnungen, Kontostand, Termine



\## Start (lokal)



Voraussetzung: Docker \& Docker Compose installiert.



```bash

docker compose build

docker compose up -d



