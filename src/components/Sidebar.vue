<template>
  <aside class="modern-sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-brand">
      <img src="../logo.png" alt="Logo" class="brand-img" />
      <button class="toggle-btn" @click="toggleCollapse">
        {{ isCollapsed ? '→' : '←' }}
      </button>
    </div>

    <nav class="nav-menu">
      <div class="nav-section">PRINCIPAL</div>
      <a @click="navigate('board')" :class="{ active: currentSelection === 'board' }" class="nav-item">
        <span class="nav-icon">🏠</span>
        <span class="nav-text">Quadro O.S.</span>
      </a>

      <div class="nav-section">GESTÃO</div>
      <div class="nav-group" :class="{ open: cadastroOpen }">
        <div class="nav-item group-trigger" @click="toggleCadastro">
          <span class="nav-icon">📦</span>
          <span class="nav-text">Cadastros</span>
          <span class="nav-arrow">›</span>
        </div>
        <div class="nav-sub">
          <a @click="navigate('client-register')" class="sub-item" :class="{ active: currentSelection === 'client-register' }">Clientes</a>
          <a @click="navigate('service-register')" class="sub-item" :class="{ active: currentSelection === 'service-register' }">Orçamentos</a>
          <a @click="navigate('expense-register')" class="sub-item" :class="{ active: currentSelection === 'expense-register' }">Despesas</a>
        </div>
      </div>

      <a @click="navigate('reports')" :class="{ active: currentSelection === 'reports' }" class="nav-item">
        <span class="nav-icon">📈</span>
        <span class="nav-text">Relatórios</span>
      </a>
    </nav>

    <div class="sidebar-user">
      <div class="user-avatar">D</div>
      <div class="user-meta">
        <span class="u-name">Danilo Neri</span>
        <button class="btn-logout-text" @click="emit('logout')">Sair do sistema</button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue';
const emit = defineEmits(['navigate', 'logout', 'toggle-collapse']);
const cadastroOpen = ref(false);
const currentSelection = ref('board');
const isCollapsed = ref(false);

const toggleCadastro = () => {
  if (isCollapsed.value) {
    isCollapsed.value = false;
    emit('toggle-collapse', false);
  }
  cadastroOpen.value = !cadastroOpen.value;
};

const navigate = (destination) => {
  currentSelection.value = destination;
  emit('navigate', destination);
};

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
  if (isCollapsed.value) cadastroOpen.value = false;
  emit('toggle-collapse', isCollapsed.value);
};
</script>

<style scoped>
.modern-sidebar { 
  width: 100%; 
  height: 100%; 
  background: #fff; 
  border-right: 1px solid #f1f5f9; 
  display: flex; 
  flex-direction: column; 
  transition: all 0.3s ease; 
  position: relative;
}

.sidebar-brand { padding: 30px 20px; display: flex; align-items: center; justify-content: space-between; height: 100px; }
.brand-img { width: 130px; transition: 0.2s; }
.collapsed .brand-img { width: 0; opacity: 0; visibility: hidden; }

.toggle-btn { background: #f8fafc; border: 1px solid #e2e8f0; width: 30px; height: 30px; border-radius: 8px; cursor: pointer; color: #56a6c1; display: flex; align-items: center; justify-content: center; font-weight: bold; }

.nav-menu { flex: 1; padding: 10px 16px; overflow-y: auto; overflow-x: hidden; }
.nav-section { font-size: 0.65rem; font-weight: 800; color: #94a3b8; padding: 25px 12px 10px; letter-spacing: 1px; }
.collapsed .nav-section { opacity: 0; }

.nav-item { display: flex; align-items: center; padding: 12px; border-radius: 12px; color: #64748b; font-weight: 600; cursor: pointer; transition: 0.2s; margin-bottom: 5px; text-decoration: none; white-space: nowrap; }
.nav-item:hover { background: #f1f5f9; color: #56a6c1; }
.nav-item.active { background: #56a6c1; color: #fff; box-shadow: 0 4px 12px rgba(86, 166, 193, 0.2); }

.nav-icon { font-size: 1.2rem; min-width: 32px; display: flex; justify-content: center; }
.nav-text { margin-left: 10px; transition: 0.2s; }
.collapsed .nav-text, .collapsed .nav-arrow { opacity: 0; width: 0; display: none; }

.nav-arrow { margin-left: auto; transition: 0.3s; }
.nav-group.open .nav-arrow { transform: rotate(90deg); }

.nav-sub { max-height: 0; overflow: hidden; transition: 0.3s; padding-left: 42px; }
.nav-group.open .nav-sub { max-height: 250px; padding-bottom: 10px; }
.sub-item { display: block; padding: 10px 0; color: #94a3b8; font-size: 0.85rem; transition: 0.2s; cursor: pointer; text-decoration: none; }
.sub-item:hover, .sub-item.active { color: #56a6c1; font-weight: 700; }

.sidebar-user { padding: 20px; border-top: 1px solid #f1f5f9; display: flex; align-items: center; gap: 12px; }
.user-avatar { width: 42px; height: 42px; background: #f1f5f9; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: #56a6c1; flex-shrink: 0; }
.user-meta { transition: 0.2s; white-space: nowrap; }
.collapsed .user-meta { opacity: 0; width: 0; display: none; }
.u-name { display: block; font-size: 0.85rem; font-weight: 700; color: #1e293b; }
.btn-logout-text { background: none; border: none; color: #ef4444; font-size: 0.75rem; padding: 0; cursor: pointer; font-weight: 600; }
</style>