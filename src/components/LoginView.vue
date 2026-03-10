<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-wrapper">
        <img src="../logo.png" alt="WK Vidros" class="login-logo" />
        <h1>Bem-vindo</h1>
        <p>Acesse sua conta para gerenciar a fábrica</p>
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label>USUÁRIO</label>
          <input type="text" v-model="credentials.usuario" placeholder="Nome de usuário" class="modern-input" required />
        </div>
        <div class="input-group">
          <label>SENHA</label>
          <input type="password" v-model="credentials.senha" placeholder="••••••••" class="modern-input" required />
        </div>
        <button type="submit" class="btn-login" :disabled="loading">
          <span v-if="!loading">ACESSAR SISTEMA</span>
          <span v-else class="loader"></span>
        </button>
      </form>
      <p class="footer-text">WK Vidros &copy; 2026</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { api } from '../services/api';

const emit = defineEmits(['login-success']);
const credentials = reactive({ usuario: '', senha: '' });
const loading = ref(false);

const handleLogin = async () => {
  loading.value = true;
  try {
    const data = await api.post('/auth/login', credentials);
    emit('login-success', data);
  } catch (e) {
    alert('Usuário ou senha inválidos');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container { height: 100vh; width: 100vw; background: linear-gradient(135deg, #f4f7f6 0%, #e2e8e7 100%); display: flex; justify-content: center; align-items: center; padding: 20px; }
.login-card { background: #ffffff; padding: 40px; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.08); width: 100%; max-width: 400px; border: 1px solid rgba(255,255,255,0.8); }
.logo-wrapper { margin-bottom: 32px; text-align: center; }
.login-logo { width: 180px; margin-bottom: 16px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.05)); }
.logo-wrapper h1 { font-size: 1.5rem; color: #2d3436; margin-bottom: 8px; font-weight: 800; }
.logo-wrapper p { color: #95a5a6; font-size: 0.9rem; }
.login-form { display: flex; flex-direction: column; gap: 24px; }
.input-group label { font-size: 0.75rem; font-weight: 700; color: #56a6c1; margin-bottom: 8px; display: block; letter-spacing: 0.5px; }
.modern-input { background: #f8fafb; border: 2px solid #edf2f4; color: #2d3436; padding: 16px; border-radius: 12px; font-size: 1rem; outline: none; width: 100%; transition: all 0.3s; }
.modern-input:focus { border-color: #56a6c1; background: #fff; box-shadow: 0 0 0 4px rgba(86,166,193,0.1); }
.btn-login { background: #56a6c1; color: #fff; padding: 18px; border: none; border-radius: 12px; font-weight: 800; cursor: pointer; font-size: 1rem; margin-top: 8px; transition: all 0.3s; display: flex; justify-content: center; align-items: center; }
.btn-login:hover { background: #4592ab; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(86,166,193,0.3); }
.btn-login:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }
.footer-text { margin-top: 32px; font-size: 0.7rem; color: #bdc3c7; text-align: center; text-transform: uppercase; letter-spacing: 2px; }
.loader { width: 20px; height: 20px; border: 3px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: #fff; animation: spin 1s ease-in-out infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 480px) { .login-card { padding: 32px 24px; border-radius: 20px; } }
</style>