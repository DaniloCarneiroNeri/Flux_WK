<template>
  <transition name="fade">
    <div v-if="showIntro" class="intro-overlay">
      <h1 class="typing-text">{{ displayedText }}<span class="cursor">|</span></h1>
    </div>
  </transition>

  <div v-if="!showIntro">
    <transition name="fade-view" mode="out-in">
      <LoginView v-if="!isAuthenticated" @login-success="handleLoginSuccess" />
      
      <div class="app-layout" :class="{ 'sidebar-mobile-open': isSidebarOpen, 'sidebar-collapsed': isSidebarCollapsed }" v-else>
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

const toggleSidebarCollapse = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
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
/* CSS Global / App.vue */
.app-layout { 
  display: flex; 
  height: 100vh; 
  width: 100vw; 
  overflow: hidden; 
}

.content-area { 
  flex: 1; /* Isso garante que o conteúdo ocupe todo o resto da tela */
  min-width: 0; 
  height: 100vh; 
  overflow-y: auto; 
  background-color: #f8fafc; 
}

/* No mobile, o sidebar flutua sobre o conteúdo */
@media (max-width: 768px) {
  .sidebar-wrapper {
    position: absolute;
    height: 100%;
    z-index: 1001;
  }
}
</style>