<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <img src="../logo.png" alt="WK Vidros Logo" class="sidebar-logo" />
      <div class="collapse-toggle" @click="toggleCollapse">
        <span class="icon">‹</span>
      </div>
    </div>
    
    <nav class="menu">
      <div class="menu-item" @click="navigate('board')" :class="{ active: currentSelection === 'board' }">
        <span class="icon">🗂️</span>
        <span>Ordens de Serviço</span>
      </div>

      <div class="menu-item has-submenu" @click="toggleCadastro" :class="{ active: currentSelection.includes('register') }">
        <div class="menu-label">
          <div class="label-content"><span class="icon">➕</span><span>Cadastros</span></div>
          <span class="arrow" :class="{ rotated: cadastroOpen }">▼</span>
        </div>
      </div>

      <transition name="slide">
        <div v-if="cadastroOpen" class="submenu">
          <div class="submenu-item" @click.stop="navigate('client-register')">Clientes</div>
          <div class="submenu-item" @click.stop="navigate('service-register')">Orçamentos</div>
          <div class="submenu-item" @click.stop="navigate('expense-register')">Despesas</div>
        </div>
      </transition>

      <div class="menu-item" @click="navigate('reports')" :class="{ active: currentSelection === 'reports' }">
        <span class="icon">📊</span>
        <span>Relatórios</span>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="menu-item footer-item" @click="emit('logout')">
        <span class="icon">🚪</span>
        <span>Sair do Sistema</span>
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
.sidebar { width: 100%; height: 100%; background-color: #ffffff; border-right: 1px solid #e0e6ed; color: #444; display: flex; flex-direction: column; overflow: hidden; }
.sidebar-header { position: relative; display: flex; flex-direction: column; align-items: center; padding: 30px 20px; border-bottom: 1px solid #f0f3f7; }
.sidebar-logo { width: 200px; height: auto; margin-bottom: 10px; object-fit: contain; transition: all 0.3s ease; }
.sidebar.collapsed .sidebar-logo { width: 40px; height: 40px; margin-bottom: 0; }
.brand-title { font-size: 1.2rem; font-weight: 800; letter-spacing: 2px; color: #56a6c1; }
.sidebar.collapsed .brand-title { display: none; }
.menu { padding: 20px 10px; flex: 1; }
.menu-item { padding: 15px 20px; cursor: pointer; transition: all 0.2s ease-in-out; display: flex; align-items: center; color: #7f8c8d; font-weight: 500; border-radius: 8px; margin-bottom: 5px; font-size: 0.9rem; }
.sidebar.collapsed .menu-item { justify-content: center; }
.sidebar.collapsed .menu-item span:not(.icon) { display: none; }
.menu-item:hover { background: #f8f9fa; color: #56a6c1; }
.menu-item.active { background: #56a6c1; color: #fff; font-weight: 700; box-shadow: 0 4px 12px rgba(86, 166, 193, 0.2); }
.icon { margin-right: 15px; font-size: 1.1rem; }
.sidebar.collapsed .icon { margin-right: 0; }
.menu-label { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.label-content { display: flex; align-items: center; }
.sidebar.collapsed .arrow { display: none; }
.submenu { background-color: #f8f9fa; border-radius: 8px; margin: 5px 0; overflow: hidden; }
.submenu-item { padding: 12px 20px 12px 55px; font-size: 0.85rem; color: #7f8c8d; cursor: pointer; transition: all 0.2s ease-in-out; }
.submenu-item:hover { background: #e9ecef; color: #56a6c1; }
.sidebar-footer { border-top: 1px solid #f0f3f7; padding: 15px; display: flex; align-items: center; }
.footer-item { flex: 1; margin: 0; }
.footer-item:hover { color: #c0392b; background: #fff5f5; }
.sidebar.collapsed .footer-item span:not(.icon) { display: none; }
.collapse-toggle { position: absolute; top: 25px; right: -15px; width: 30px; height: 30px; border-radius: 50%; background: #ffffff; border: 1px solid #e0e6ed; color: #56a6c1; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.collapse-toggle:hover { background: #56a6c1; color: #fff; border-color: #56a6c1; }
.collapse-toggle .icon { margin: 0; transition: transform 0.3s ease; }
.sidebar.collapsed .collapse-toggle .icon { transform: rotate(180deg); }
.slide-enter-active, .slide-leave-active { transition: all 0.3s ease-out; max-height: 200px; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; transform: translateY(-10px); }
.arrow { font-size: 0.7rem; transition: transform 0.3s; }
.rotated { transform: rotate(180deg); }
</style>