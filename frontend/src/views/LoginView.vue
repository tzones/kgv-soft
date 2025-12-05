<template>
  <div>
    <h2>Mitglieder-Login</h2>
    <form @submit.prevent="login">
      <div>
        <input v-model="email" type="email" placeholder="E-Mail" required />
      </div>
      <div>
        <input v-model="password" type="password" placeholder="Passwort" required />
      </div>
      <button type="submit">Einloggen</button>
    </form>
    <p v-if="error" style="color:red">{{ error }}</p>
    <p style="margin-top:1rem; font-size:0.9rem;">
      Admin-Login (Standard): admin@example.com / admin123
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const email = ref('')
const password = ref('')
const error = ref('')

async function login() {
  error.value = ''
  try {
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    const res = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })

    localStorage.setItem('auth_token', res.data.access_token)
    window.location.href = '#/portal'
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Login fehlgeschlagen'
  }
}
</script>
