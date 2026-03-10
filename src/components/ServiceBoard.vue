<template>
  <div class="board-container">
    <header class="board-header">
      <div class="header-info">
        <h1>QUADRO DE SERVIÇOS</h1>
        <p>Gestão de produção e fluxo de trabalho</p>
      </div>
      <div class="header-controls">
        <div class="view-switch">
          <button :class="{ active: viewMode === 'kanban' }" @click="viewMode = 'kanban'">Grade</button>
          <button :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">Lista</button>
        </div>
        <button class="btn-primary-action" @click="openModal()">+ NOVA O.S.</button>
      </div>
    </header>

    <div class="content-area">
      <transition name="fade" mode="out-in">
        <div v-if="viewMode === 'kanban'" class="kanban-container">
          <div 
            v-for="column in columns" 
            :key="column.title" 
            class="kanban-column"
            @dragover.prevent
            @drop="onDrop(column.title)"
          >
            <div class="column-title" :style="{ borderTopColor: column.color }">
              <span class="status-dot" :style="{ backgroundColor: column.color }"></span>
              <h3>{{ column.title }}</h3>
              <span class="badge-count">{{ column.orders.length }}</span>
            </div>
            
            <div class="column-cards">
              <div 
                v-for="order in column.orders" 
                :key="order.id" 
                class="service-card" 
                @click="openModal(order)"
                draggable="true"
                @dragstart="onDragStart(order)"
              >
                <div class="card-top">
                  <span class="os-number">#{{ order.id }}</span>
                  <span v-if="order.status === 'late'" class="tag-late">ATRASADO</span>
                </div>
                <h4 class="client-name">{{ order.clientes.nome }}</h4>
                <div class="card-bottom">
                  <span class="total-price">{{ formatCurrency(order.valor_total) }}</span>
                  <span class="icon-drag">⋮⋮</span>
                </div>
              </div>
              <div v-if="column.orders.length === 0" class="empty-state">Sem ordens</div>
            </div>
          </div>
        </div>

        <div v-else class="table-view-wrapper">
          <div class="responsive-table">
            <table class="modern-grid">
              <thead>
                <tr>
                  <th>O.S.</th>
                  <th>CLIENTE</th>
                  <th>VALOR TOTAL</th>
                  <th>STATUS</th>
                  <th class="text-right">AÇÕES</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in ordens" :key="order.id" class="row-hover">
                  <td><strong>#{{ order.id }}</strong></td>
                  <td>{{ order.clientes.nome }}</td>
                  <td class="price-col">{{ formatCurrency(order.valor_total) }}</td>
                  <td><span class="status-tag" :class="order.status">{{ getStatusLabel(order.status) }}</span></td>
                  <td class="text-right">
                    <button class="btn-edit-small" @click="openModal(order)">ABRIR DETALHES</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </transition>
    </div>

    <transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card os-details">
          <div class="modal-header">
            <div class="header-title">
              <span class="os-id-badge">O.S. #{{ form.id || 'NOVA' }}</span>
              <h3>{{ isEditing ? 'Detalhes do Serviço' : 'Nova Ordem de Serviço' }}</h3>
            </div>
            <button class="close-x" @click="closeModal">×</button>
          </div>
          
          <div class="modal-body scrollable">
            <div class="form-grid">
              <div class="field-group">
                <label>CLIENTE</label>
                <select v-model="form.cliente_id" class="custom-input" :disabled="isLocked">
                  <option v-for="client in dbClients" :key="client.id" :value="client.id">{{ client.nome }}</option>
                </select>
              </div>
              <div class="field-group">
                <label>STATUS DA PRODUÇÃO</label>
                <select v-model="form.status" class="custom-input" :disabled="isLocked">
                  <option value="pending">Pendente</option>
                  <option value="production">Em Produção</option>
                  <option value="completed">Concluído</option>
                  <option value="billed">NFe Emitida</option>
                </select>
              </div>

              <div class="items-summary-section full-width">
                <div class="section-title">ITENS E MEDIÇÕES</div>
                <div class="items-list-box">
                  <div v-if="form.items.length === 0" class="empty-items">Nenhum item registrado nesta O.S.</div>
                  <div v-for="(item, idx) in form.items" :key="idx" class="os-item-row">
                    <div class="item-desc">
                      <span class="qty">{{ item.quantidade }}x</span>
                      <span class="name">{{ item.descricao_item }}</span>
                    </div>
                    <div class="item-val">{{ formatCurrency(item.valor_unitario * item.quantidade) }}</div>
                  </div>
                </div>
              </div>

              <div class="field-group full-width">
                <label>OBSERVAÇÕES DE FÁBRICA</label>
                <textarea v-model="form.observacoes" class="custom-input" rows="3" :disabled="isLocked"></textarea>
              </div>
            </div>

            <div class="os-financial-footer">
              <div class="fin-block">
                <span>SUBTOTAL</span>
                <strong>{{ formatCurrency(subtotalItems) }}</strong>
              </div>
              <div class="fin-block">
                <span>DESCONTO</span>
                <input type="number" v-model.number="form.desconto" class="mini-input" :disabled="isLocked" />
              </div>
              <div class="fin-block total">
                <span>TOTAL FINAL</span>
                <strong>{{ formatCurrency(form.valor_total) }}</strong>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-sec" @click="closeModal">FECHAR</button>
            <button class="btn-pri" @click="saveOrder" :disabled="saving || isLocked">
              {{ saving ? 'SALVANDO...' : 'ATUALIZAR O.S.' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="notify.show" class="custom-alert-overlay" @click="notify.show = false">
        <div class="alert-box" :class="notify.type">
          <div class="alert-icon">{{ notify.type === 'error' ? '✕' : '✓' }}</div>
          <div class="alert-content">
            <h4>{{ notify.title }}</h4>
            <p>{{ notify.message }}</p>
          </div>
          <button class="btn-close-alert" @click="notify.show = false">OK</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, reactive } from 'vue';
import { api } from '../services/api';

const viewMode = ref('kanban');
const ordens = ref([]);
const draggedOrder = ref(null);
const showModal = ref(false);
const isEditing = ref(false);
const saving = ref(false);
const form = ref(null);
const dbClients = ref([]);

const notify = reactive({
  show: false,
  title: '',
  message: '',
  type: 'success'
});

const triggerNotify = (title, message, type = 'success') => {
  notify.title = title;
  notify.message = message;
  notify.type = type;
  notify.show = true;
};

const loadData = async () => {
  try {
    const [resOrdens, resClientes] = await Promise.all([
      api.get('/ordens'),
      api.get('/clientes')
    ]);
    ordens.value = resOrdens;
    dbClients.value = resClientes;
  } catch (e) {
    triggerNotify('Erro de Conexão', 'Não foi possível carregar os dados.', 'error');
  }
};

onMounted(loadData);

const columns = computed(() => {
  const statusMap = {
    pending: 'Pendente',
    late: 'Pendente',
    production: 'Em Produção',
    completed: 'Concluído',
    billed: 'NFe Emitida'
  };

  const grouped = ordens.value.reduce((acc, order) => {
    const status = statusMap[order.status] || 'Pendente';
    if (!acc[status]) acc[status] = [];
    acc[status].push(order);
    return acc;
  }, {});

  return [
    { title: 'Pendente', orders: grouped['Pendente'] || [], color: '#f39c12' },
    { title: 'Em Produção', orders: grouped['Em Produção'] || [], color: '#56a6c1' },
    { title: 'NFe Emitida', orders: grouped['NFe Emitida'] || [], color: '#9b59b6' },
    { title: 'Concluído', orders: grouped['Concluído'] || [], color: '#2ecc71' }
  ];
});

const getStatusLabel = (status) => {
  const labels = { pending: 'Pendente', production: 'Produção', completed: 'Concluído', billed: 'NFe Emitida', late: 'Atrasado' };
  return labels[status] || status;
};

const subtotalItems = computed(() => {
  if (!form.value || !form.value.items) return 0;
  return form.value.items.reduce((total, item) => total + (item.quantidade * item.valor_unitario), 0);
});

const isLocked = computed(() => isEditing.value && form.value?.status === 'billed');

watch(() => [form.value?.items, form.value?.desconto], () => {
  if (form.value && form.value.items) {
    form.value.valor_total = subtotalItems.value - (form.value.desconto || 0);
  }
}, { deep: true });

const openModal = (order = null) => {
  if (order) {
    isEditing.value = true;
    form.value = JSON.parse(JSON.stringify(order));
    form.value.items = form.value.itens_ordem || form.value.items || [];
    form.value.desconto = form.value.desconto || 0;
  } else {
    isEditing.value = false;
    form.value = { id: null, cliente_id: "", status: 'pending', observacoes: '', items: [], desconto: 0, valor_total: 0 };
  }
  showModal.value = true;
};

const closeModal = () => { showModal.value = false; form.value = null; };

const saveOrder = async () => {
  saving.value = true;
  try {
    const payload = { ...form.value };
    if (isEditing.value) {
      await api.put(`/ordens/${form.value.id}`, payload);
    } else {
      await api.post('/ordens', payload);
    }
    await loadData();
    closeModal();
    triggerNotify('Sucesso', 'Ordem de serviço salva com sucesso.', 'success');
  } catch (e) {
    triggerNotify('Erro ao Salvar', e.message, 'error');
  } finally {
    saving.value = false;
  }
};

const onDragStart = (order) => { draggedOrder.value = order; };

const onDrop = async (targetColumnTitle) => {
  if (!draggedOrder.value) return;
  const titleToStatus = { 'Pendente': 'pending', 'Em Produção': 'production', 'Concluído': 'completed', 'NFe Emitida': 'billed' };
  const newStatus = titleToStatus[targetColumnTitle];
  const oldStatus = draggedOrder.value.status;

  if (oldStatus === newStatus) return;

  const orderIndex = ordens.value.findIndex(o => o.id === draggedOrder.value.id);
  if (orderIndex !== -1) {
    ordens.value[orderIndex].status = newStatus;
  }

  try {
    await api.patch(`/ordens/${draggedOrder.value.id}/status`, { status: newStatus });
  } catch (e) {
    if (orderIndex !== -1) {
      ordens.value[orderIndex].status = oldStatus;
    }
    triggerNotify('Erro ao Mover', 'Não foi possível atualizar o status no servidor.', 'error');
  }
  draggedOrder.value = null;
};

const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
</script>

<style scoped>
.board-container { padding: 24px; background: #f8fafc; min-height: 100vh; }
.board-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; gap: 20px; flex-wrap: wrap; }
.header-info h1 { font-size: 1.5rem; font-weight: 900; color: #1e293b; margin: 0; }
.header-info p { color: #64748b; font-size: 0.9rem; margin-top: 4px; }
.header-controls { display: flex; gap: 16px; align-items: center; }
.view-switch { background: #e2e8f0; padding: 4px; border-radius: 12px; display: flex; }
.view-switch button { border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; font-weight: 600; background: transparent; color: #64748b; transition: 0.3s; }
.view-switch button.active { background: #fff; color: #56a6c1; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
.btn-primary-action { background: #56a6c1; color: #fff; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; box-shadow: 0 10px 15px -3px rgba(86,166,193,0.3); }

.kanban-container { display: flex; gap: 20px; overflow-x: auto; padding-bottom: 20px; }
.kanban-column { min-width: 300px; flex: 1; background: #f1f5f9; border-radius: 16px; display: flex; flex-direction: column; max-height: 80vh; }
.column-title { padding: 16px; display: flex; align-items: center; gap: 10px; border-top: 4px solid; background: rgba(255,255,255,0.5); border-radius: 16px 16px 0 0; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.column-title h3 { font-size: 0.8rem; font-weight: 800; color: #475569; margin: 0; text-transform: uppercase; }
.badge-count { margin-left: auto; background: #fff; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; color: #94a3b8; }
.column-cards { padding: 12px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 12px; }
.service-card { background: #fff; padding: 16px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); cursor: pointer; border: 1px solid transparent; transition: 0.2s; }
.service-card:hover { transform: translateY(-2px); border-color: #56a6c1; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
.card-top { display: flex; justify-content: space-between; margin-bottom: 12px; }
.os-number { font-size: 0.75rem; font-weight: 800; color: #cbd5e1; }
.tag-late { background: #fee2e2; color: #ef4444; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: 800; }
.client-name { font-size: 0.95rem; color: #1e293b; margin: 0 0 16px 0; font-weight: 700; }
.card-bottom { display: flex; justify-content: space-between; align-items: center; }
.total-price { color: #56a6c1; font-weight: 900; font-size: 1.1rem; }
.icon-drag { color: #e2e8f0; font-size: 1.2rem; }

.table-view-wrapper { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #edf2f7; }
.modern-grid { width: 100%; border-collapse: collapse; }
.modern-grid th { text-align: left; padding: 16px; color: #94a3b8; font-size: 0.75rem; border-bottom: 1px solid #f1f5f9; text-transform: uppercase; font-weight: 800; }
.modern-grid td { padding: 16px; border-bottom: 1px solid #f8fafc; font-size: 0.9rem; color: #1e293b; }
.row-hover:hover { background-color: #f8fafc; }
.status-tag { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; }
.status-tag.pending { background: #fef3c7; color: #d97706; }
.status-tag.production { background: #e0f2fe; color: #0284c7; }
.status-tag.completed { background: #dcfce7; color: #16a34a; }
.status-tag.billed { background: #f3e8ff; color: #9333ea; }
.btn-edit-small { background: #56a6c1; border: none; padding: 8px 16px; border-radius: 8px; color: #fff; font-weight: 800; cursor: pointer; font-size: 0.7rem; }
.text-right { text-align: right; }

.modal-card.os-details { max-width: 650px; }
.header-title { display: flex; align-items: center; gap: 12px; }
.os-id-badge { background: #f1f5f9; color: #56a6c1; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 900; }
.items-summary-section { margin: 20px 0; background: #f8fafc; padding: 20px; border-radius: 16px; border: 1px solid #e2e8f0; }
.section-title { font-size: 0.7rem; font-weight: 900; color: #94a3b8; margin-bottom: 15px; letter-spacing: 1px; }
.os-item-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
.item-desc { display: flex; gap: 10px; font-size: 0.9rem; }
.qty { color: #56a6c1; font-weight: 900; }
.name { color: #1e293b; font-weight: 600; }
.item-val { font-weight: 800; color: #64748b; font-size: 0.9rem; }
.os-financial-footer { display: grid; grid-template-columns: 1fr 1fr 1.5fr; gap: 20px; margin-top: 30px; padding-top: 20px; border-top: 2px solid #f1f5f9; }
.fin-block { display: flex; flex-direction: column; gap: 5px; }
.fin-block span { font-size: 0.65rem; font-weight: 800; color: #94a3b8; }
.fin-block strong { font-size: 1.1rem; color: #1e293b; }
.fin-block.total strong { color: #56a6c1; font-size: 1.4rem; font-weight: 950; }
.mini-input { background: #fff; border: 1px solid #cbd5e1; padding: 8px; border-radius: 8px; font-weight: 800; color: #ef4444; width: 100px; }

@media (max-width: 768px) {
  .os-financial-footer { grid-template-columns: 1fr; gap: 15px; }
  .modern-grid th:nth-child(3), .modern-grid td:nth-child(3) { display: none; }
}
</style>