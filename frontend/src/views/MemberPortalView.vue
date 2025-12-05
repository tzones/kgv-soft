<template>
  <div>
    <h2>Mein Garten</h2>
    <button @click="logout">Logout</button>

    <div v-if="member" style="margin-top:1rem;">
      <p><strong>{{ member.first_name }} {{ member.last_name }}</strong></p>
      <p>{{ member.street }}, {{ member.zip_code }} {{ member.city }}</p>
    </div>

    <h3>Kontostand</h3>
    <p v-if="balance">Aktueller Kontostand: {{ balance.balance.toFixed(2) }} €</p>

    <h3>Meine Parzellen</h3>
    <ul>
      <li v-for="p in parcels" :key="p.contract_id">
        Parzelle {{ p.parcel_number }} ({{ p.size_sqm }} m²), Vertrag: {{ p.status }}
      </li>
    </ul>

    <h3>Meine Rechnungen</h3>
    <table v-if="invoices.length">
      <thead>
        <tr>
          <th>Jahr</th>
          <th>Datum</th>
          <th>Betrag</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="inv in invoices" :key="inv.id">
          <td>{{ inv.year }}</td>
          <td>{{ inv.invoice_date }}</td>
          <td>{{ inv.total_amount }}</td>
          <td>{{ inv.status }}</td>
        </tr>
      </tbody>
    </table>

    <h3>Vereinstermine</h3>
    <ul>
      <li v-for="e in events" :key="e.id">
        {{ formatDate(e.start) }} – {{ e.title }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const member = ref(null)
const parcels = ref([])
const invoices = ref([])
const balance = ref(null)
const events = ref([])

function logout() {
  localStorage.removeItem('auth_token')
  window.location.href = '#/login'
}

function formatDate(d) {
  return new Date(d).toLocaleString('de-DE')
}

async function loadAll() {
  try {
    const [m, p, i, b, ev] = await Promise.all([
      api.get('/me'),
      api.get('/me/parcels'),
      api.get('/me/invoices'),
      api.get('/me/balance'),
      api.get('/calendar/events'),
    ])
    member.value = m.data
    parcels.value = p.data
    invoices.value = i.data
    balance.value = b.data
    events.value = ev.data
  } catch (e) {
    console.error(e)
    logout()
  }
}

onMounted(loadAll)
</script>
