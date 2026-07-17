<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="welcome">
    <div class="hero card">
      <div class="logo">🤝</div>
      <h1>Bondly</h1>
      <p class="tagline">
        Stay close to the people who matter. Remember the details, never miss a
        birthday, and always know who to reach out to next.
      </p>
      <div class="actions">
        <RouterLink :to="{ name: 'login' }" class="btn">Get started</RouterLink>
        <RouterLink :to="{ name: 'login' }" class="btn secondary">I already have an account</RouterLink>
      </div>
    </div>
    <ul class="features">
      <li><span>🧠</span> Remember what matters about everyone</li>
      <li><span>🔔</span> Gentle reminders to reconnect</li>
      <li><span>📈</span> See the health of your relationships</li>
    </ul>
  </div>
</template>

<style scoped>
.welcome {
  max-width: 560px;
  margin: 6vh auto 0;
  text-align: center;
}
.hero {
  padding: 40px 32px;
}
.logo {
  font-size: 56px;
}
h1 {
  font-size: 40px;
  margin: 8px 0;
}
.tagline {
  color: var(--muted);
  font-size: 16px;
  line-height: 1.6;
  margin: 0 auto 28px;
  max-width: 420px;
}
.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}
.actions .btn {
  width: 260px;
  justify-content: center;
}
.features {
  list-style: none;
  padding: 0;
  margin: 28px auto 0;
  display: grid;
  gap: 10px;
  max-width: 360px;
  text-align: left;
}
.features li {
  display: flex;
  gap: 12px;
  align-items: center;
  color: var(--muted);
  font-weight: 500;
}
.features span {
  font-size: 20px;
}
</style>
