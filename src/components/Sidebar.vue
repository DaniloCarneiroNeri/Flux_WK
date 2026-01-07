<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <img src="../logo.png" alt="Flux Logo" class="sidebar-logo" />
      <h2>Flux</h2>
    </div>
    
    <nav class="menu">
      <div class="menu-item" @click="navigate('board')" :class="{ active: currentSelection === 'board' }">
        <span class="icon">📋</span> Ordem de Serviços
      </div>

      <div class="menu-item has-submenu" @click="toggleCadastro" :class="{ active: currentSelection.includes('register') }">
        <div class="menu-label">
          <span><span class="icon">📝</span> Cadastro</span>
          <span class="arrow" :class="{ rotated: cadastroOpen }">▼</span>
        </div>
      </div>

      <transition name="slide">
        <div v-if="cadastroOpen" class="submenu">
          <div class="submenu-item" @click="navigate('client-register')">
            ➔ Cliente
          </div>
          <div class="submenu-item" @click="navigate('service-register')">
            ➔ Orçamentos
          </div>
          <div class="submenu-item" @click="navigate('expense-register')">
            ➔ Despesas
          </div>
        </div>
      </transition>

      <div class="menu-item" @click="navigate('reports')" :class="{ active: currentSelection === 'reports' }">
        <span class="icon">📊</span> Relatórios
      </div>
    </nav>

    <div class="sidebar-bottom">
      <div class="sidebar-footer" @click="showAboutModal = true">
        <span class="icon">ℹ️</span> Sobre o Sistema
      </div>
      <div class="sidebar-footer logout" @click="showLogoutModal = true">
        <span class="icon">⏻</span> Sair
      </div>
    </div>

    <transition name="fade">
      <div v-if="showAboutModal" class="modal-backdrop" @click.self="showAboutModal = false">
        <div class="about-card">
          <button class="btn-close" @click="showAboutModal = false">×</button>
          
          <img src="../logo.png" alt="Flux Logo" class="about-logo" />
          
          <h3>Flux Manager</h3>
          <p class="tagline">Excelência em Gestão de Serviços Prestados</p>
          
          <div class="divider"></div>
          
          <div class="developer-info">
            <p class="dev-label">Desenvolvido por</p>
            <p class="dev-name">Danilo Carneiro Neri</p>
            <p class="dev-role">Engenharia de Software & Soluções Tecnológicas</p>
          </div>

          <div class="version-badge">
            Versão 1.0.0
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="showLogoutModal" class="modal-backdrop" @click.self="showLogoutModal = false">
        <div class="logout-card">
          <h3>Desconectar</h3>
          <p>Deseja realmente sair do sistema?</p>
          
          <div class="modal-actions">
            <button class="btn-cancel" @click="showLogoutModal = false">Cancelar</button>
            <button class="btn-confirm-logout" @click="confirmLogout">Sair</button>
          </div>
        </div>
      </div>
    </transition>

  </aside>
</template>

<script setup>
import { ref } from 'vue';

const emit = defineEmits(['navigate', 'logout']);

const cadastroOpen = ref(false);
const currentSelection = ref('board');
const showAboutModal = ref(false);
const showLogoutModal = ref(false);

const toggleCadastro = () => {
  cadastroOpen.value = !cadastroOpen.value;
};

const navigate = (destination) => {
  currentSelection.value = destination;
  emit('navigate', destination);
};

const confirmLogout = () => {
  showLogoutModal.value = false;
  emit('logout');
};
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  background-color: #02152e;
  border-right: 1px solid #2ecc71;
  color: #ecf0f1;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0,0,0,0.3);
}

.sidebar-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
  background: linear-gradient(180deg, #02152e 0%, #02152e 100%);
  border-bottom: 1px solid #1a3c52;
}

.sidebar-logo {
  width: 130px;
  height: auto;
  margin-bottom: 10px;
  object-fit: contain;
}

.sidebar-header h2 {
  color: #d4a74e;
  font-family: 'Arial', sans-serif;
  letter-spacing: 3px;
  font-size: 1.5rem;
  text-transform: uppercase;
  margin: 0;
}

.menu {
  margin-top: 20px;
  flex: 1;
  overflow-y: auto;
}

.menu-item {
  padding: 16px 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  color: #bdc3c7;
  font-weight: 500;
  border-left: 4px solid transparent;
  user-select: none;
}

.menu-item:hover, .menu-item.active {
  background-color: rgba(46, 204, 113, 0.08);
  color: #2ecc71;
  border-left: 4px solid #2ecc71;
}

.icon {
  margin-right: 12px;
  font-size: 1.1em;
  display: inline-block;
  width: 25px;
  text-align: center;
}

.submenu {
  background-color: #000d14;
  overflow: hidden;
}

.submenu-item {
  padding: 12px 20px 12px 60px;
  font-size: 0.9em;
  color: #7f8c8d;
  cursor: pointer;
  transition: color 0.2s;
}

.submenu-item:hover {
  color: #f1c40f;
  background-color: rgba(255, 255, 255, 0.02);
}

.has-submenu .menu-label {
  display: flex;
  justify-content: space-between;
  width: 100%;
  align-items: center;
}

.arrow {
  font-size: 0.7em;
  transition: transform 0.3s;
}

.arrow.rotated {
  transform: rotate(180deg);
}

.slide-enter-active, .slide-leave-active {
  transition: max-height 0.3s ease-in-out, opacity 0.3s;
  max-height: 200px;
  opacity: 1;
}

.slide-enter-from, .slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.sidebar-bottom {
  border-top: 1px solid #1a3c52;
  background-color: #021226;
}

.sidebar-footer {
  padding: 15px 25px;
  color: #7f8c8d;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.sidebar-footer:hover {
  color: #f1c40f;
  background-color: #031a36;
}

.sidebar-footer.logout:hover {
  color: #e74c3c;
  background-color: #031a36;
}

/* Modal Backdrop */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.about-card {
  background: white;
  width: 380px;
  padding: 40px 30px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
  position: relative;
  color: #2c3e50;
  border-top: 5px solid #2ecc71;
}

.logout-card {
  background: white;
  width: 320px;
  padding: 30px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
  position: relative;
  color: #2c3e50;
  border-top: 5px solid #e74c3c;
}

.logout-card h3 {
  margin: 0 0 10px;
  font-size: 1.4rem;
  color: #02152e;
}

.logout-card p {
  color: #7f8c8d;
  margin-bottom: 25px;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn-cancel {
  background: #f1f2f6;
  color: #7f8c8d;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-cancel:hover {
  background: #e1e2e6;
  color: #2c3e50;
}

.btn-confirm-logout {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-confirm-logout:hover {
  background: #c0392b;
}

.btn-close {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #bdc3c7;
  cursor: pointer;
}
.btn-close:hover { color: #e74c3c; }

.about-logo {
  width: 80px;
  margin-bottom: 15px;
}

.about-card h3 {
  margin: 0;
  font-size: 1.4rem;
  color: #02152e;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.tagline {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-top: 5px;
  font-weight: 500;
}

.divider {
  height: 1px;
  background: #eee;
  margin: 20px 0;
  width: 100%;
}

.developer-info {
  margin-bottom: 20px;
}

.dev-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #95a5a6;
  margin-bottom: 5px;
  letter-spacing: 0.5px;
}

.dev-name {
  font-size: 1.1rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.dev-role {
  font-size: 0.8rem;
  color: #3498db;
  margin-top: 2px;
}

.version-badge {
  display: inline-block;
  background: #f8f9fa;
  border: 1px solid #e1e4e8;
  color: #7f8c8d;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-family: monospace;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>