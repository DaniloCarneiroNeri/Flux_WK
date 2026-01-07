<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-wrapper">
        <img src="../logo.png" alt="WK Vidros Logo" class="login-logo" />
        <h1>WK VIDROS</h1>
        <p class="tagline">VIDROS, FORROS & PVC</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <span class="input-icon">👤</span>
          <input 
            type="text" 
            v-model="credentials.usuario" 
            placeholder="Usuário" 
            class="modern-input" 
            required 
            autofocus
          />
        </div>

        <div class="input-group">
          <span class="input-icon">🔒</span>
          <input 
            type="password" 
            v-model="credentials.senha" 
            placeholder="Senha" 
            class="modern-input" 
            required 
          />
        </div>

        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? 'AUTENTICANDO...' : 'ACESSAR PAINEL' }}
          <span v-if="!loading">➔</span>
        </button>
      </form>
    </div>

    <transition name="pop">
      <div v-if="showErrorModal" class="error-backdrop" @click.self="closeError">
        <div class="error-card">
          <div class="error-icon">❌</div>
          <h3>Acesso Negado</h3>
          <p>Credenciais não conferem.</p>
          <button class="btn-error-close" @click="closeError">Tentar Novamente</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { globalStore } from '../store.js';

const emit = defineEmits(['login-success']);

const API_URL = import.meta.env.DEV ? 'http://localhost:8000' : '';

const credentials = reactive({
  usuario: '',
  senha: ''
});

const loading = ref(false);
const showErrorModal = ref(false);

const handleLogin = async () => {
  if (!credentials.usuario || !credentials.senha) return;
  
  loading.value = true;

  if (credentials.usuario === 'demo' && credentials.senha === '123') {
    setTimeout(() => {
      globalStore.isDemo = true;
      const demoUser = {
        id: 0,
        usuario: 'demo',
        nome: 'Usuário Demonstração',
        token: 'demo-token'
      };
      emit('login-success', demoUser);
      loading.value = false;
    }, 800);
    return;
  }

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });

    if (response.ok) {
      const data = await response.json();
      globalStore.isDemo = false;
      emit('login-success', data);
    } else {
      showErrorModal.value = true;
    }
  } catch (error) {
    console.error("Erro de conexão", error);
    showErrorModal.value = true;
  } finally {
    if (!globalStore.isDemo) loading.value = false;
  }
};

const closeError = () => {
  showErrorModal.value = false;
  credentials.senha = ''; 
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  background: #000000;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  position: relative;
}

.login-container::before {
  content: "";
  position: absolute;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(64, 196, 255, 0.15) 0%, transparent 70%);
  top: -100px;
  right: -100px;
}

.login-card {
  background: #0a0a0a;
  padding: 50px 40px;
  border-radius: 4px;
  border: 1px solid #1a1a1a;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 30px 60px rgba(0,0,0,0.5);
  text-align: center;
  animation: slideUp 0.6s ease-out;
}

.logo-wrapper {
  margin-bottom: 40px;
}

.login-logo {
  width: 120px;
  margin-bottom: 20px;
}

.logo-wrapper h1 {
  color: #ffffff;
  font-size: 2.2rem;
  margin: 0;
  letter-spacing: 4px;
  font-weight: 800;
}

.tagline {
  color: #40c4ff;
  font-size: 0.8rem;
  letter-spacing: 3px;
  font-weight: 600;
  margin-top: 5px;
  text-transform: uppercase;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.input-group {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.1rem;
  color: #444;
}

.modern-input {
  width: 100%;
  padding: 16px 16px 16px 50px;
  background: #111;
  border: 1px solid #222;
  border-radius: 4px;
  color: #fff;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
}

.modern-input:focus {
  border-color: #40c4ff;
  background: #000;
}

.btn-login {
  background: #40c4ff;
  color: #000;
  padding: 16px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  letter-spacing: 1px;
}

.btn-login:hover {
  background: #ffffff;
  transform: translateY(-2px);
}

.btn-login:disabled {
  background: #333;
  color: #666;
  cursor: not-allowed;
}

.error-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.error-card {
  background: #111;
  padding: 40px;
  border-radius: 4px;
  text-align: center;
  width: 350px;
  border: 1px solid #c0392b;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.error-card h3 {
  color: #fff;
  margin: 0 0 10px 0;
}

.error-card p {
  color: #888;
  margin-bottom: 25px;
}

.btn-error-close {
  background: #c0392b;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.pop-enter-active, .pop-leave-active { transition: opacity 0.3s; }
.pop-enter-from, .pop-leave-to { opacity: 0; }
</style>