<template>
  <transition name="fade">
    <div v-if="showIntro" class="intro-overlay">
      <h1 class="typing-text">{{ displayedText }}<span class="cursor">|</span></h1>
    </div>
  </transition>

  <div v-if="!showIntro">
    <transition name="fade-view" mode="out-in">
      <LoginView v-if="!isAuthenticated" @login-success="handleLoginSuccess" />
      
      <div class="app-layout" :class="{ 'sidebar-collapsed': isSidebarCollapsed, 'sidebar-mobile-open': isSidebarOpen }" v-else>
        <button class="mobile-toggle" @click="isSidebarOpen = !isSidebarOpen">
          <span v-if="!isSidebarOpen">☰</span>
          <span v-else>✕</span>
        </button>

        <div class="sidebar-wrapper">
          <Sidebar @navigate="handleNavigate" @logout="handleLogout" @toggle-collapse="toggleSidebarCollapse" />
        </div>
        
        <div class="sidebar-overlay" @click="isSidebarOpen = false"></div>

        <main class="content-area">
          <transition name="fade-view" mode="out-in">
            <component :is="activeComponent" @cancel="changeView('board')" />
          </transition>
        </main>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { globalStore } from './store.js';
import LoginView from './components/LoginView.vue';
import Sidebar from './components/Sidebar.vue';
import ServiceBoard from './components/ServiceBoard.vue';
import ClientForm from './components/ClientForm.vue';
import ServiceForm from './components/ServiceForm.vue';
import ExpenseForm from './components/ExpenseForm.vue'; 
import ReportsView from './components/ReportsView.vue';
import ProdutoForm from './components/ProdutoForm.vue';

const currentView = ref('board');
const isAuthenticated = ref(false);
const isSidebarOpen = ref(false);
const isSidebarCollapsed = ref(false);

const fullText = "WK VIDROS: Forros e PVC.";
const displayedText = ref("");
const showIntro = ref(true);

const changeView = (viewName) => {
  currentView.value = viewName;
};

const handleNavigate = (dest) => {
  changeView(dest);
  isSidebarOpen.value = false;
};

const toggleSidebarCollapse = (val) => {
  isSidebarCollapsed.value = val;
};

const activeComponent = computed(() => {
  switch (currentView.value) {
    case 'board': return ServiceBoard;
    case 'client-register': return ClientForm;
    case 'product-register': return ProdutoForm;
    case 'service-register': return ServiceForm;
    case 'expense-register': return ExpenseForm;
    case 'reports': return ReportsView;
    default: return ServiceBoard;
  }
});

const handleLoginSuccess = (userData) => {
  isAuthenticated.value = true;
  sessionStorage.setItem('flux_user', JSON.stringify(userData));
  if (userData.usuario === 'demo') {
    globalStore.isDemo = true;
  }
};

const handleLogout = () => {
  isAuthenticated.value = false;
  sessionStorage.removeItem('flux_user');
  globalStore.isDemo = false;
  currentView.value = 'board';
};

onMounted(() => {
  const storedUser = sessionStorage.getItem('flux_user');
  if (storedUser) {
    const userData = JSON.parse(storedUser);
    isAuthenticated.value = true;
    if (userData.usuario === 'demo') {
      globalStore.isDemo = true;
    }
  }

  const hasVisited = sessionStorage.getItem('flux_visited');
  if (hasVisited) {
    showIntro.value = false;
  } else {
    let i = 0;
    const timer = setInterval(() => {
      if (i < fullText.length) {
        displayedText.value += fullText.charAt(i);
        i++;
      } else {
        clearInterval(timer);
        setTimeout(() => { showIntro.value = false; }, 1200);
        sessionStorage.setItem('flux_visited', 'true');
      }
    }, 50);
  }
});
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; -webkit-tap-highlight-color: transparent; }
body { background-color: #f8fafc; color: #1e293b; overflow: hidden; position: fixed; width: 100%; height: 100%; }

.app-layout { display: flex; height: 100vh; width: 100vw; overflow: hidden; }

.sidebar-wrapper { 
  flex-shrink: 0; 
  width: 260px; 
  height: 100%; 
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
  z-index: 1000;
}

.sidebar-collapsed .sidebar-wrapper { width: 80px; }

.content-area { 
  flex: 1; 
  min-width: 0; 
  height: 100%; 
  overflow-y: auto; 
  background-color: #f8fafc; 
  position: relative; 
  padding: 0;
}

.mobile-toggle { 
  display: none; 
  position: fixed; 
  top: 15px; 
  right: 15px; 
  width: 45px; 
  height: 45px; 
  background: #56a6c1; 
  border: none; 
  border-radius: 10px; 
  color: #fff; 
  font-size: 1.2rem; 
  z-index: 1100; 
  box-shadow: 0 4px 12px rgba(86, 166, 193, 0.3); 
}

@media (max-width: 768px) {
  .mobile-toggle { display: flex; align-items: center; justify-content: center; }
  .sidebar-wrapper { position: fixed; left: 0; top: 0; transform: translateX(-100%); width: 280px; }
  .sidebar-mobile-open .sidebar-wrapper { transform: translateX(0); }
  .sidebar-overlay { display: block; position: fixed; inset: 0; background: rgba(15, 23, 42, 0.5); z-index: 999; backdrop-filter: blur(4px); }
  .app-layout:not(.sidebar-mobile-open) .sidebar-overlay { display: none; }
}

.intro-overlay { position: fixed; inset: 0; background: #fff; z-index: 9999; display: flex; justify-content: center; align-items: center; }
.typing-text { color: #56a6c1; font-size: 2rem; font-weight: 900; }
.cursor { animation: blink 1s infinite; color: #56a6c1; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
.fade-leave-active { transition: opacity 0.8s; }
.fade-leave-to { opacity: 0; }
.fade-view-enter-active { transition: all 0.3s ease-out; }
.fade-view-leave-active { transition: all 0.2s ease-in; }
.fade-view-enter-from { opacity: 0; transform: translateY(10px); }
.fade-view-leave-to { opacity: 0; transform: translateY(-10px); }
</style>