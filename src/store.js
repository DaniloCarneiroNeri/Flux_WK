import { reactive } from 'vue';

export const globalStore = reactive({
  isDemo: false, 
  clients: [],
  services: [],
  orders: [],
  expenses: [],
  flags: {
    clientsLoaded: false,
    servicesLoaded: false,
    ordersLoaded: false,
    expensesLoaded: false
  }
});

export const invalidateCache = (type) => {
  if (type === 'all') {
    globalStore.flags.clientsLoaded = false;
    globalStore.flags.servicesLoaded = false;
    globalStore.flags.ordersLoaded = false;
    globalStore.flags.expensesLoaded = false;
  } else {
    const key = `${type}Loaded`;
    if (globalStore.flags.hasOwnProperty(key)) {
      globalStore.flags[key] = false;
    }
  }
};