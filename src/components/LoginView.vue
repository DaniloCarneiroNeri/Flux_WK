<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-wrapper">
        <img src="../logo.jpg" alt="WK Vidros" class="login-logo" />
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <input type="text" v-model="credentials.usuario" placeholder="USUÁRIO" class="modern-input" required />
        <input type="password" v-model="credentials.senha" placeholder="SENHA" class="modern-input" required />
        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? 'AUTENTICANDO...' : 'ACESSAR SISTEMA' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
const emit = defineEmits(['login-success']);
const credentials = reactive({ usuario: '', senha: '' });
const loading = ref(false);
const handleLogin = () => {
  loading.value = true;
  setTimeout(() => {
    emit('login-success', { id: 1, usuario: credentials.usuario, nome: 'Operador WK' });
    loading.value = false;
  }, 1000);
};
</script>

<style scoped>
.login-container { height: 100vh; width: 100vw; background: #000; display: flex; justify-content: center; align-items: center; }
.login-card { background: #000; padding: 60px 40px; border-radius: 8px; border: 1px solid #1a1a1a; width: 400px; max-width: 90%; text-align: center; }
.login-logo { width: 250px; margin-bottom: 20px; }
.brand { font-size: 1.8rem; font-weight: 900; letter-spacing: 3px; }
.wk { color: #40c4ff; }
.vidros { color: #fff; }
.tagline { color: #444; font-size: 0.7rem; letter-spacing: 4px; margin-top: 10px; font-weight: 700; }
.login-form { display: flex; flex-direction: column; gap: 20px; margin-top: 40px; }
.modern-input { background: #0a0a0a; border: 1px solid #222; color: #fff; padding: 18px; border-radius: 4px; font-size: 0.9rem; outline: none; }
.modern-input:focus { border-color: #40c4ff; }
.btn-login { background: #40c4ff; color: #000; padding: 18px; border: none; border-radius: 4px; font-weight: 900; cursor: pointer; }
</style>