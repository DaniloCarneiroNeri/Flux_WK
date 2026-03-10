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

        <div v-else class="table-container">
          <div class="responsive-table">
            <table class="modern-grid">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>CLIENTE</th>
                  <th>VALOR</th>
                  <th>STATUS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in ordens" :key="order.id" @click="openModal(order)" class="row-hover">
                  <td><strong>#{{ order.id }}</strong></td>
                  <td>{{ order.clientes.nome }}</td>
                  <td class="price-col">{{ formatCurrency(order.valor_total) }}</td>
                  <td><span class="status-tag" :class="order.status">{{ order.status }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </transition>
    </div>

    <transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header">
            <h3>{{ isEditing ? `Editar O.S. #${form.id}` : 'Nova Ordem de Serviço' }}</h3>
            <button class="close-x" @click="closeModal">×</button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="field-group">
                <label>CLIENTE</label>
                <select v-model="form.cliente_id" class="custom-input" :disabled="isLocked">
                  <option v-for="client in dbClients" :key="client.id" :value="client.id">{{ client.nome }}</option>
                </select>
              </div>
              <div class="field-group">
                <label>STATUS</label>
                <select v-model="form.status" class="custom-input" :disabled="isLocked">
                  <option value="pending">Pendente</option>
                  <option value="production">Em Produção</option>
                  <option value="completed">Concluído</option>
                  <option value="billed">NFe Emitida</option>
                </select>
              </div>
              <div class="field-group full-width">
                <label>OBSERVAÇÕES</label>
                <textarea v-model="form.observacoes" class="custom-input" rows="3" :disabled="isLocked"></textarea>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-sec" @click="closeModal">CANCELAR</button>
            <button class="btn-pri" @click="saveOrder" :disabled="saving">{{ saving ? 'SALVANDO...' : 'SALVAR' }}</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { api } from '../services/api';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import logoImg from '../logo.png';

const viewMode = ref('kanban');
const ordens = ref([]);
const draggedOrder = ref(null);
const showModal = ref(false);
const isEditing = ref(false);
const saving = ref(false);
const form = ref(null);
const dbClients = ref([]);

const loadData = async () => {
  const [resOrdens, resClientes] = await Promise.all([
    api.get('/ordens'),
    api.get('/clientes')
  ]);
  ordens.value = resOrdens;
  dbClients.value = resClientes;
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
    form.value.items = form.value.itens_ordem || [];
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
  } catch (e) {
    alert(e.message);
  } finally {
    saving.value = false;
  }
};

const onDragStart = (order) => { draggedOrder.value = order; };

const onDrop = async (targetColumnTitle) => {
  if (!draggedOrder.value) return;
  const titleToStatus = { 'Pendente': 'pending', 'Em Produção': 'production', 'Concluído': 'completed', 'NFe Emitida': 'billed' };
  const newStatus = titleToStatus[targetColumnTitle];
  try {
    await api.patch(`/ordens/${draggedOrder.value.id}/status`, { status: newStatus });
    await loadData();
  } catch (e) {
    alert(e.message);
  }
  draggedOrder.value = null;
};

const addItem = () => { if (!isLocked.value) form.value.items.push({ descricao_item: '', quantidade: 1, valor_unitario: 0 }); };
const removeItem = (index) => { if (!isLocked.value) form.value.items.splice(index, 1); };
const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);

const emitReceipt = () => {
  const doc = new jsPDF();
  const client = dbClients.value.find(c => c.id === form.value.cliente_id) || { nome: 'Consumidor' };
  const dateStr = new Date().toLocaleDateString('pt-BR');
  doc.setDrawColor(86, 166, 193);
  doc.setLineWidth(0.5);
  doc.rect(10, 10, 190, 40);
  doc.addImage(logoImg, 'PNG', 15, 15, 35, 30);
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.text('RECIBO DE PRESTAÇÃO DE SERVIÇO', 60, 25);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text('WK VIDROS - Forros e PVC', 60, 32);
  doc.text('CNPJ: 55.952.245/0001-00', 60, 37);
  doc.text('Avenida 21 de Abril - Telefone: (62) 99876-6290', 60, 42);
  doc.setFont('helvetica', 'bold');
  doc.text('DADOS DO CLIENTE', 10, 60);
  doc.line(10, 62, 200, 62);
  doc.setFont('helvetica', 'normal');
  doc.text(`NOME: ${client.nome}`, 10, 68);
  doc.text(`CPF/CNPJ: ${client.documento || '---'}`, 10, 73);
  doc.text(`TELEFONE: ${client.telefone || '---'}`, 10, 78);
  doc.text(`DATA DE EMISSÃO: ${dateStr}`, 140, 68);
  doc.text(`O.S. Nº: ${form.value.id}`, 140, 73);
  const rows = form.value.items.map(i => [i.descricao_item, i.quantidade, formatCurrency(i.valor_unitario), formatCurrency(i.quantidade * i.valor_unitario)]);
  autoTable(doc, { startY: 85, head: [['Descrição', 'Qtd', 'Unitário', 'Total']], body: rows, theme: 'grid', headStyles: { fillColor: [86, 166, 193] } });
  const finalY = doc.lastAutoTable.finalY + 10;
  doc.setFont('helvetica', 'bold');
  doc.text(`SUBTOTAL: ${formatCurrency(subtotalItems.value)}`, 140, finalY);
  doc.text(`DESCONTO: ${formatCurrency(form.value.desconto)}`, 140, finalY + 5);
  doc.setFontSize(12);
  doc.text(`TOTAL PAGO: ${formatCurrency(form.value.valor_total)}`, 140, finalY + 12);
  doc.save(`Recibo_OS_${form.value.id}.pdf`);
};
</script>

<style scoped>
.board-container { padding: 20px; background: #f8fafc; min-height: 100vh; font-family: 'Inter', sans-serif; }
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

@media (max-width: 768px) {
  .board-header { flex-direction: column; align-items: stretch; }
  .header-controls { justify-content: space-between; }
  .kanban-container { gap: 15px; }
  .kanban-column { min-width: 85vw; }
}
</style>