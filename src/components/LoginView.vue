<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-wrapper">
        <img src="../logo.png" alt="WK Vidros" class="login-logo" />
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label>USUÁRIO</label>
          <input type="text" v-model="credentials.usuario" placeholder="Digite seu usuário" class="modern-input" required />
        </div>
        <div class="input-group">
          <label>SENHA</label>
          <input type="password" v-model="credentials.senha" placeholder="••••••••" class="modern-input" required />
        </div>
        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? 'AUTENTICANDO...' : 'ACESSAR SISTEMA' }}
        </button>
      </form>
      <p class="footer-text">Gestão Inteligente WK Vidros</p>
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
.login-container { height: 100vh; width: 100vw; background: #f4f7f6; display: flex; justify-content: center; align-items: center; }
.login-card { background: #ffffff; padding: 50px 40px; border-radius: 12px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); width: 420px; max-width: 90%; text-align: center; border-top: 5px solid #56a6c1; }
.login-logo { width: 220px; margin-bottom: 30px; }
.login-form { display: flex; flex-direction: column; gap: 20px; text-align: left; }
.input-group label { font-size: 0.7rem; font-weight: 800; color: #56a6c1; margin-bottom: 8px; display: block; letter-spacing: 1px; }
.modern-input { background: #f8f9fa; border: 1px solid #e0e6ed; color: #333; padding: 16px; border-radius: 8px; font-size: 0.95rem; outline: none; width: 100%; transition: all 0.2s; }
.modern-input:focus { border-color: #56a6c1; background: #fff; box-shadow: 0 0 0 4px rgba(86,166,193,0.1); }
.btn-login { background: #56a6c1; color: #fff; padding: 18px; border: none; border-radius: 8px; font-weight: 900; cursor: pointer; font-size: 1rem; margin-top: 10px; box-shadow: 0 6px 15px rgba(86,166,193,0.3); transition: transform 0.2s; }
.btn-login:hover { transform: translateY(-2px); background: #4a91a9; }
.btn-login:disabled { background: #a5cdd9; cursor: not-allowed; }
.footer-text { margin-top: 30px; font-size: 0.75rem; color: #95a5a6; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
</style>