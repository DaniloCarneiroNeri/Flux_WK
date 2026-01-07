<template>
  <transition name="fade">
    <div v-if="showIntro" class="intro-overlay">
      <h1 class="typing-text">{{ displayedText }}<span class="cursor">|</span></h1>
    </div>
  </transition>

  <div v-if="!showIntro">
    <transition name="fade-view" mode="out-in">
      <LoginView v-if="!isAuthenticated" @login-success="handleLoginSuccess" />
      
      <div class="app-layout" :class="{ 'sidebar-mobile-open': isSidebarOpen }" v-else>
        <button class="mobile-toggle" @click="isSidebarOpen = !isSidebarOpen">
          <span v-if="!isSidebarOpen">☰</span>
          <span v-else>✕</span>
        </button>

        <div class="sidebar-wrapper">
          <Sidebar @navigate="handleNavigate" @logout="handleLogout" />
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

const currentView = ref('board');
const isAuthenticated = ref(false);
const isSidebarOpen = ref(false);

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

const activeComponent = computed(() => {
  switch (currentView.value) {
    case 'board': return ServiceBoard;
    case 'client-register': return ClientForm;
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
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
  -webkit-tap-highlight-color: transparent;
}

body {
  background-color: #000000;
  color: #ffffff;
  overflow: hidden;
  position: fixed;
  width: 100%;
  height: 100%;
}

.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: #000000;
}

.sidebar-wrapper {
  flex-shrink: 0;
  width: 260px;
  height: 100%;
  border-right: 1px solid #1a1a1a;
  z-index: 1000;
  transition: transform 0.3s ease;
  background: #000;
}

.content-area {
  flex: 1;
  min-width: 0;
  height: 100%;
  overflow-y: auto;
  background-color: #050505;
  position: relative;
  -webkit-overflow-scrolling: touch;
}

.mobile-toggle {
  display: none;
  position: fixed;
  top: 15px;
  right: 15px;
  width: 48px;
  height: 48px;
  background: #40c4ff;
  border: none;
  border-radius: 4px;
  color: #000;
  font-size: 1.5rem;
  z-index: 1100;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(64, 196, 255, 0.4);
}

@media (max-width: 768px) {
  .mobile-toggle { display: flex; align-items: center; justify-content: center; }
  
  .sidebar-wrapper {
    position: fixed;
    left: 0;
    top: 0;
    transform: translateX(-100%);
  }

  .sidebar-mobile-open .sidebar-wrapper {
    transform: translateX(0);
  }

  .sidebar-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.85);
    z-index: 999;
  }

  .sidebar-mobile-open .sidebar-overlay {
    display: block;
  }

  .content-area {
    padding-top: 60px;
  }

  .typing-text { font-size: 1.4rem !important; text-align: center; padding: 20px; }
}

.intro-overlay {
  position: fixed;
  inset: 0;
  background-color: #000000;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.typing-text {
  color: #40c4ff;
  font-family: 'Courier New', monospace;
  font-size: 2.2rem;
  letter-spacing: 2px;
  font-weight: bold;
}

.cursor { animation: blink 1s infinite; color: #ffffff; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
.fade-leave-active { transition: opacity 1s; }
.fade-leave-to { opacity: 0; }
.fade-view-enter-active, .fade-view-leave-active { transition: opacity 0.3s ease; }
.fade-view-enter-from, .fade-view-leave-to { opacity: 0; }
</style>