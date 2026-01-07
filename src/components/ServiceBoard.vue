<template>
  <div class="board-container">
    <div class="board-header">
      <div class="header-left">
        <button class="btn-new" @click="openModal()"><span>+</span> NOVA OS</button>
        <h1>QUADRO WK</h1>
      </div>
      <div class="view-toggle">
        <button :class="{ active: viewMode === 'kanban' }" @click="viewMode = 'kanban'">⊞</button>
        <button :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">☰</button>
      </div>
    </div>

    <transition name="fade-view" mode="out-in">
      <div v-if="viewMode === 'kanban'" class="kanban-scroll-container">
        <div class="kanban-board">
          <div v-for="column in columns" :key="column.title" class="kanban-column">
            <div class="column-header" :style="{ borderTopColor: column.color }">
              <h3>{{ column.title.toUpperCase() }}</h3>
              <span class="task-count">{{ column.orders.length }}</span>
            </div>
            <transition-group name="card-list" tag="div" class="column-body">
              <div v-for="order in column.orders" :key="order.id" class="kanban-card" @click="openModal(order)">
                <div class="card-header">
                  <span class="id">#{{ order.id }}</span>
                  <span v-if="order.status === 'late'" class="badge-late">ATRASADO</span>
                </div>
                <h4>{{ order.clientes.nome }}</h4>
                <div class="card-footer">
                  <span class="price">{{ formatCurrency(order.valor_total) }}</span>
                </div>
              </div>
            </transition-group>
            <div v-if="column.orders.length === 0" class="empty-column">
              <p>Nenhuma O.S. aqui</p>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="table-view-container">
        <table class="service-table">
          <thead><tr><th>ID</th><th>CLIENTE</th><th>VALOR</th><th>STATUS</th></tr></thead>
          <tbody>
            <tr v-for="order in ordens" :key="order.id" @click="openModal(order)" class="clickable-row">
              <td>#{{ order.id }}</td><td>{{ order.clientes.nome }}</td><td class="cyan">{{ formatCurrency(order.valor_total) }}</td><td><span class="status-badge" :class="order.status">{{ order.status.toUpperCase() }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </transition>

    <transition name="modal">
      <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
        <div class="modal-content large-modal">
          
          <div class="modal-header">
            <div>
              <h2>
                {{ isEditing ? `Ordem de Serviço #${form.id}` : 'Nova Ordem de Serviço' }}
                <span v-if="isLocked" class="locked-badge">🔒 (Modo Leitura)</span>
              </h2>
              <p class="subtitle">{{ isEditing ? 'Gerencie os detalhes e emissão fiscal.' : 'Preencha os dados iniciais do serviço.' }}</p>
            </div>
            <button class="btn-close" @click="closeModal">×</button>
          </div>
          
          <div class="modal-body">
            <div class="modal-grid">
              
              <div class="grid-left">
                <div class="form-group">
                  <label>Cliente Solicitante <span class="required">*</span></label>
                  <select v-model="form.cliente_id" class="dark-input" :disabled="isLocked">
                    <option value="" disabled>Selecione um cliente...</option>
                    <option v-for="client in dbClients" :key="client.id" :value="client.id">
                      {{ client.nome }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Status Atual</label>
                  <select v-model="form.status" class="dark-input" :disabled="isLocked">
                    <option v-for="opt in statusOptions" :key="opt.key" :value="opt.key">{{ opt.label }}</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Observações / Laudo Técnico</label>
                  <textarea v-model="form.observacoes" rows="5" class="dark-input" placeholder="Detalhes técnicos do serviço..." :disabled="isLocked"></textarea>
                </div>
              </div>

              <div class="grid-right">
                <label class="section-label">Itens e Peças</label>
                
                <div class="items-card" :class="{ 'disabled-card': isLocked }">
                  <div class="add-item-row">
                      <button type="button" class="btn-new-item" @click="addItem" :disabled="isLocked">
                        + Adicionar Serviço / Peça
                      </button>
                  </div>

                  <div class="items-list-wrapper">
                    <div v-if="!form.items || form.items.length === 0" class="empty-items">Nenhum item adicionado</div>
                    <div v-else v-for="(item, index) in form.items" :key="index" class="item-row">
                      <div class="item-info">
                        <span class="item-qtd">{{ item.quantidade }}x</span>
                        <span class="item-name">{{ item.descricao_item }}</span>
                      </div>
                      <div class="item-actions">
                        <span class="item-price" :class="{'text-discount': item.valor_unitario < 0}">
                          {{ formatCurrency(item.valor_unitario * item.quantidade) }}
                        </span>
                        <button v-if="!isLocked" class="btn-remove-mini" @click="removeItem(index)">×</button>
                      </div>
                    </div>
                  </div>

                  <div class="total-display">
                    <span>Total Final</span>
                    <span class="total-value">{{ formatCurrency(form.valor_total) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <div class="footer-left">
            </div>

            <div class="footer-right">
              <button class="btn-cancel" @click="closeModal">{{ isLocked ? 'Fechar' : 'Cancelar' }}</button>
              <button v-if="!isLocked" class="btn-save" @click="saveOrder" :disabled="saving">
                {{ saving ? 'Salvando...' : 'Salvar Alterações' }}
              </button>
            </div>
          </div>

        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import demoData from '../data/demoData.json';

const viewMode = ref('kanban');
const ordens = ref(demoData.ordens);

const columns = computed(() => {
  const statusMap = {
    pending: 'Pendente',
    late: 'Pendente',
    production: 'Em Produção',
    completed: 'Concluído'
  };

  const grouped = ordens.value.reduce((acc, order) => {
    const status = statusMap[order.status] || 'Pendente';
    if (!acc[status]) {
      acc[status] = [];
    }
    acc[status].push(order);
    return acc;
  }, {});

  return [
    { title: 'Pendente', orders: grouped['Pendente'] || [], color: '#e67e22' },
    { title: 'Em Produção', orders: grouped['Em Produção'] || [], color: '#3498db' },
    { title: 'Concluído', orders: grouped['Concluído'] || [], color: '#2ecc71' }
  ];
});

const showModal = ref(false);
const isEditing = ref(false);
const saving = ref(false);
const form = ref(null);
const dbClients = ref(demoData.clientes);

const statusOptions = [
  { key: 'pending', label: 'Pendente' },
  { key: 'production', label: 'Em Produção' },
  { key: 'completed', label: 'Concluído' },
  { key: 'billed', label: 'Faturado' }
];

const isLocked = computed(() => isEditing.value && form.value?.status === 'billed');

watch(() => form.value?.items, (newItems) => {
  if (form.value && newItems) {
    form.value.valor_total = newItems.reduce((total, item) => total + (item.quantidade * item.valor_unitario), 0);
  }
}, { deep: true });

const openModal = (order = null) => {
  if (order) {
    isEditing.value = true;
    form.value = JSON.parse(JSON.stringify(order));
    form.value.items = form.value.itens_ordem || [];
  } else {
    isEditing.value = false;
    form.value = {
      id: null,
      cliente_id: "",
      status: 'pending',
      observacoes: '',
      items: [],
      valor_total: 0
    };
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  form.value = null;
};

const saveOrder = () => {
  saving.value = true;
  const client = dbClients.value.find(c => c.id === form.value.cliente_id);
  
  if (isEditing.value) {
    const index = ordens.value.findIndex(o => o.id === form.value.id);
    if (index !== -1) {
      const updatedOrder = { ...form.value, clientes: { nome: client?.nome || 'N/A' }, itens_ordem: form.value.items };
      delete updatedOrder.items;
      ordens.value[index] = updatedOrder;
    }
  } else {
    const newOrder = { ...form.value, id: Date.now(), clientes: { nome: client?.nome || 'N/A' }, itens_ordem: form.value.items };
    delete newOrder.items;
    ordens.value.unshift(newOrder);
  }
  
  setTimeout(() => {
    saving.value = false;
    closeModal();
  }, 500);
};

const addItem = () => {
  if (isLocked.value) return;
  form.value.items.push({ descricao_item: 'Novo Item', quantidade: 1, valor_unitario: 0 });
};

const removeItem = (index) => {
  if (isLocked.value) return;
  form.value.items.splice(index, 1);
};

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
};
</script>

<style scoped>
.board-container { padding: 20px; height: 100%; display: flex; flex-direction: column; background: #050505; }
.board-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.header-left { display: flex; align-items: center; gap: 15px; }
.header-left h1 { color: #fff; font-size: 1.1rem; letter-spacing: 2px; font-weight: 800; margin: 0; }
.btn-new { background: #40c4ff; color: #000; padding: 12px 20px; border-radius: 4px; font-weight: 900; border: none; cursor: pointer; font-size: 0.8rem; transition: background-color 0.3s; }
.btn-new:hover { background: #80dfff; }
.view-toggle { background: #111; padding: 4px; border-radius: 4px; display: flex; }
.view-toggle button { background: none; border: none; padding: 8px 12px; color: #444; cursor: pointer; }
.view-toggle button.active { color: #40c4ff; background: #000; border-radius: 2px; }
.kanban-scroll-container { flex: 1; overflow-x: auto; padding-bottom: 15px; }
.kanban-board { display: flex; gap: 15px; min-width: min-content; height: 100%; }
.kanban-column { width: 300px; background: #0a0a0a; border-radius: 4px; display: flex; flex-direction: column; flex-shrink: 0; }
.column-header { display: flex; justify-content: space-between; align-items: center; padding: 15px; border-top: 3px solid; }
.column-header h3 { font-size: 0.75rem; color: #888; font-weight: 800; letter-spacing: 1px; margin: 0; }
.task-count { background: #1a1a1a; color: #666; font-size: 0.7rem; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
.column-body { flex: 1; overflow-y: auto; padding: 0 12px 12px 12px; }
.kanban-card { background: #131313; padding: 15px; border-left: 3px solid #40c4ff; border-radius: 4px; cursor: pointer; margin-top: 12px; transition: transform 0.2s, background-color 0.2s; }
.kanban-card:hover { transform: translateY(-3px); background: #1a1a1a; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.id { font-size: 0.8rem; font-weight: bold; color: #666; }
.kanban-card h4 { color: #ddd; font-size: 0.9rem; margin: 0; font-weight: 600; }
.card-footer { margin-top: 15px; text-align: right; }
.price { color: #40c4ff; font-weight: 900; font-size: 1rem; }
.badge-late { background: #c0392b; color: #fff; padding: 3px 6px; font-size: 0.6rem; border-radius: 3px; font-weight: bold; }
.empty-column { padding: 20px; text-align: center; color: #444; font-size: 0.8rem; }
.table-view-container { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 4px; overflow-x: auto; }
.service-table { width: 100%; border-collapse: collapse; min-width: 600px; }
.service-table th { background: #111; color: #555; padding: 15px; text-align: left; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; }
.service-table td { padding: 18px 15px; border-bottom: 1px solid #111; font-size: 0.85rem; color: #ccc; }
.service-table tr:last-child td { border-bottom: none; }
.clickable-row { cursor: pointer; transition: background-color 0.2s; }
.clickable-row:hover { background-color: #0f0f0f; }
.cyan { color: #40c4ff; font-weight: 800; }
.status-badge { padding: 5px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; background: #333; color: #999; }
.status-badge.pending, .status-badge.late { background-color: rgba(230, 126, 34, 0.2); color: #e67e22; }
.status-badge.production { background-color: rgba(52, 152, 219, 0.2); color: #3498db; }
.status-badge.completed { background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; }
.status-badge.billed { background-color: rgba(155, 89, 182, 0.2); color: #9b59b6; }
.card-list-move, .card-list-enter-active, .card-list-leave-active { transition: all 0.5s ease; }
.card-list-enter-from, .card-list-leave-to { opacity: 0; transform: translateX(30px); }
.card-list-leave-active { position: absolute; }
.modal-backdrop { position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.85); z-index: 1000; display: flex; justify-content: center; align-items: center; }
.modal-content { background: #0a0a0a; border-top: 4px solid #40c4ff; border-radius: 8px; display: flex; flex-direction: column; width: 95%; max-height: 90vh; }
.large-modal { max-width: 900px; }
.modal-header { display: flex; justify-content: space-between; align-items: flex-start; padding: 20px 25px; border-bottom: 1px solid #1a1a1a; }
.modal-header h2 { font-size: 1.3rem; font-weight: 800; color: #fff; margin: 0; }
.subtitle { font-size: 0.9rem; color: #666; margin-top: 5px; }
.locked-badge { font-size: 0.8rem; color: #e67e22; }
.btn-close { background: none; border: none; color: #555; font-size: 1.8rem; cursor: pointer; line-height: 1; }
.modal-body { padding: 25px; overflow-y: auto; }
.modal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.form-group { display: flex; flex-direction: column; gap: 8px; margin-bottom: 15px; }
.form-group label { font-size: 0.7rem; color: #666; font-weight: 600; text-transform: uppercase; }
.required { color: #c0392b; }
.dark-input { background: #000; border: 1px solid #222; color: #fff; padding: 14px; border-radius: 4px; outline: none; width: 100%; font-size: 0.9rem; }
.dark-input:focus { border-color: #40c4ff; }
.dark-input:disabled { background: #111; color: #555; cursor: not-allowed; }
.section-label { font-size: 0.7rem; color: #666; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: block; }
.items-card { background: #000; border: 1px solid #1a1a1a; border-radius: 4px; }
.disabled-card { background: #050505; }
.add-item-row { padding: 15px; border-bottom: 1px solid #1a1a1a; }
.btn-new-item { width: 100%; background: #40c4ff; color: #000; border: none; padding: 12px; font-weight: 700; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
.items-list-wrapper { max-height: 250px; overflow-y: auto; padding: 5px; }
.empty-items { text-align: center; color: #444; font-size: 0.8rem; padding: 30px 0; }
.item-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; border-bottom: 1px solid #151515; }
.item-info { display: flex; align-items: center; gap: 10px; }
.item-qtd { font-size: 0.8rem; color: #666; }
.item-name { color: #ccc; font-weight: 500; }
.item-actions { display: flex; align-items: center; gap: 10px; }
.item-price { font-weight: 700; color: #40c4ff; }
.text-discount { color: #2ecc71; }
.btn-remove-mini { background: #1f1f1f; color: #c0392b; border: none; border-radius: 4px; width: 24px; height: 24px; cursor: pointer; font-weight: bold; }
.total-display { display: flex; justify-content: space-between; align-items: center; padding: 20px 15px; background: #111; border-top: 1px solid #1a1a1a; font-weight: bold; }
.total-value { font-size: 1.4rem; color: #40c4ff; }
.modal-footer { display: flex; justify-content: space-between; align-items: center; padding: 20px 25px; border-top: 1px solid #1a1a1a; background: #050505; }
.footer-right { display: flex; gap: 10px; }
.btn-cancel { background: #1a1a1a; color: #888; border: 1px solid #333; padding: 12px 24px; border-radius: 4px; font-weight: 700; cursor: pointer; }
.btn-save { background: #40c4ff; color: #000; border: none; padding: 12px 24px; font-weight: 900; border-radius: 4px; cursor: pointer; }
.btn-save:disabled { background: #888; cursor: not-allowed; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .modal-content, .modal-leave-active .modal-content { transition: transform 0.3s ease; }
.modal-enter-from .modal-content, .modal-leave-to .modal-content { transform: scale(0.95); }
@media (max-width: 768px) { .modal-grid { grid-template-columns: 1fr; } .kanban-column { width: 85vw; } .header-left h1 { display: none; } }
</style>