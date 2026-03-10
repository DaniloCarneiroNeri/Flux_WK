<template>
  <aside class="modern-sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-brand">
      <img src="../logo.png" alt="Logo" class="brand-img" />
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
          <a @click="navigate('client-register')" class="sub-item">Clientes</a>
          <a @click="navigate('service-register')" class="sub-item">Orçamentos</a>
          <a @click="navigate('expense-register')" class="sub-item">Despesas</a>
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
        <span class="u-role">Administrador</span>
      </div>
      <button class="btn-logout" @click="emit('logout')">✕</button>
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
    toggleCollapse();
    cadastroOpen.value = true;
    return;
  }
  cadastroOpen.value = !cadastroOpen.value;
};
const navigate = (destination) => {
  currentSelection.value = destination;
  emit('navigate', destination);
  const isSubmenuDestination = ['client-register', 'service-register', 'expense-register'].includes(destination);
  
  if (isSubmenuDestination && !isCollapsed.value) {
      toggleCollapse();
  } else {
      cadastroOpen.value = false;
  }
};
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
  if (isCollapsed.value) {
    cadastroOpen.value = false;
  }
  emit('toggle-collapse');
};
</script>

<style scoped>
.modern-sidebar { width: 260px; height: 100vh; background: #fff; border-right: 1px solid #edf2f7; display: flex; flex-direction: column; transition: 0.3s; }
.sidebar-brand { padding: 32px 24px; text-align: center; }
.brand-img { width: 140px; transition: 0.3s; }
.nav-menu { flex: 1; padding: 0 16px; overflow-y: auto; }
.nav-section { font-size: 0.65rem; font-weight: 800; color: #94a3b8; padding: 24px 12px 12px; letter-spacing: 1px; }
.nav-item { display: flex; align-items: center; padding: 12px; border-radius: 12px; color: #475569; font-weight: 600; cursor: pointer; transition: 0.2s; margin-bottom: 4px; text-decoration: none; }
.nav-item:hover { background: #f1f5f9; color: #56a6c1; }
.nav-item.active { background: #56a6c1; color: #fff; }
.nav-icon { font-size: 1.2rem; margin-right: 12px; }
.nav-arrow { margin-left: auto; transition: 0.3s; }
.nav-group.open .nav-arrow { transform: rotate(90deg); }
.nav-sub { max-height: 0; overflow: hidden; transition: 0.3s; padding-left: 40px; }
.nav-group.open .nav-sub { max-height: 200px; padding-top: 8px; padding-bottom: 8px; }
.sub-item { display: block; padding: 8px 12px; color: #64748b; font-size: 0.9rem; border-radius: 8px; transition: 0.2s; cursor: pointer; }
.sub-item:hover { color: #56a6c1; background: #f8fafc; }

.sidebar-user { padding: 20px; border-top: 1px solid #edf2f7; display: flex; align-items: center; gap: 12px; }
.user-avatar { width: 40px; height: 40px; background: #e2e8f0; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #56a6c1; }
.user-meta { flex: 1; overflow: hidden; }
.u-name { display: block; font-size: 0.85rem; font-weight: 700; color: #1e293b; white-space: nowrap; text-overflow: ellipsis; }
.u-role { display: block; font-size: 0.7rem; color: #94a3b8; }
.btn-logout { background: transparent; border: none; color: #cbd5e1; cursor: pointer; font-size: 1.2rem; }
.btn-logout:hover { color: #ef4444; }

@media (max-width: 1024px) {
  .modern-sidebar { width: 80px; }
  .nav-text, .nav-section, .nav-arrow, .user-meta { display: none; }
  .brand-img { width: 40px; }
  .nav-sub { display: none; }
}
</style>