<template>
  <div class="app">
    <h1>Kleingarten Verwaltung</h1>

    <nav class="nav">
      <a href="#/login">Login</a>
      <a href="#/portal">Mein Garten</a>
      <a href="#/dashboard">Dashboard</a>
    </nav>

    <div class="content">
      <LoginView v-if="route === 'login'" />
      <MemberPortalView v-else-if="route === 'portal'" />
      <DashboardView v-else-if="route === 'dashboard'" />
      <LoginView v-else />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LoginView from './views/LoginView.vue'
import MemberPortalView from './views/MemberPortalView.vue'
import DashboardView from './views/DashboardView.vue'

const route = ref('login')

function updateRoute() {
  const hash = window.location.hash.replace('#/', '')
  route.value = hash || 'login'
}

onMounted(() => {
  window.addEventListener('hashchange', updateRoute)
  updateRoute()
})
</script>

<style>
.app {
  font-family: sans-serif;
  padding: 1rem;
  max-width: 1000px;
  margin: 0 auto;
}
.nav a {
  margin-right: 1rem;
}
.content {
  margin-top: 1rem;
}
table {
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ccc;
  padding: 0.25rem 0.5rem;
}
</style>
