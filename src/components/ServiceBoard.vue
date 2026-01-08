<template>
  <div class="board-container">
    <div class="board-header">
      <div class="header-left">
        <button class="btn-new" @click="openModal()"><span>+</span> NOVA OS</button>
        <h1>QUADRO DE SERVIÇOS</h1>
      </div>
      <div class="view-toggle">
        <button :class="{ active: viewMode === 'kanban' }" @click="viewMode = 'kanban'">⊞</button>
        <button :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">☰</button>
      </div>
    </div>

    <transition name="fade-view" mode="out-in">
      <div v-if="viewMode === 'kanban'" class="kanban-scroll-container">
        <div class="kanban-board">
          <div 
            v-for="column in columns" 
            :key="column.title" 
            class="kanban-column"
            @dragover.prevent
            @drop="onDrop(column.title)"
          >
            <div class="column-header" :style="{ borderTopColor: column.color }">
              <h3>{{ column.title.toUpperCase() }}</h3>
              <span class="task-count">{{ column.orders.length }}</span>
            </div>
            <transition-group name="card-list" tag="div" class="column-body">
              <div 
                v-for="order in column.orders" 
                :key="order.id" 
                class="kanban-card" 
                @click="openModal(order)"
                draggable="true"
                @dragstart="onDragStart(order)"
              >
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
              <td>#{{ order.id }}</td><td>{{ order.clientes.nome }}</td><td class="accent-text">{{ formatCurrency(order.valor_total) }}</td><td><span class="status-badge" :class="order.status">{{ order.status.toUpperCase() }}</span></td>
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
                  <select v-model="form.cliente_id" class="modern-input" :disabled="isLocked">
                    <option value="" disabled>Selecione um cliente...</option>
                    <option v-for="client in dbClients" :key="client.id" :value="client.id">
                      {{ client.nome }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Status Atual</label>
                  <select v-model="form.status" class="modern-input" :disabled="isLocked">
                    <option v-for="opt in statusOptions" :key="opt.key" :value="opt.key">{{ opt.label }}</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Observações / Laudo Técnico</label>
                  <textarea v-model="form.observacoes" rows="5" class="modern-input" placeholder="Detalhes técnicos do serviço..." :disabled="isLocked"></textarea>
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
                      <div class="item-edit-grid">
                        <input type="text" v-model="item.descricao_item" class="mini-input desc" placeholder="Item" :disabled="isLocked" />
                        <input type="number" v-model.number="item.quantidade" class="mini-input qty" placeholder="Qtd" :disabled="isLocked" />
                        <input type="number" v-model.number="item.valor_unitario" class="mini-input val" placeholder="Valor" :disabled="isLocked" />
                        <button v-if="!isLocked" class="btn-remove-mini" @click="removeItem(index)">×</button>
                      </div>
                    </div>
                  </div>

                  <div class="summary-area">
                    <div class="summary-row">
                      <span>Subtotal</span>
                      <span>{{ formatCurrency(subtotalItems) }}</span>
                    </div>
                    <div class="summary-row discount-row">
                      <span>Desconto</span>
                      <div class="discount-input-wrapper">
                        R$ <input type="number" v-model.number="form.desconto" class="mini-input discount" :disabled="isLocked" />
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
          </div>

          <div class="modal-footer">
            <div class="footer-left">
              <button class="btn-secondary" @click="emitReceipt" :disabled="!isEditing">Emitir recibo</button>
              <button class="btn-secondary" disabled>Emitir NFe</button>
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
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import logoImg from '../logo.png';

const viewMode = ref('kanban');
const ordens = ref(demoData.ordens);
const draggedOrder = ref(null);

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
    if (!acc[status]) {
      acc[status] = [];
    }
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

const showModal = ref(false);
const isEditing = ref(false);
const saving = ref(false);
const form = ref(null);
const dbClients = ref(demoData.clientes);

const statusOptions = [
  { key: 'pending', label: 'Pendente' },
  { key: 'production', label: 'Em Produção' },
  { key: 'billed', label: 'NFe Emitida' },
  { key: 'completed', label: 'Concluído' }
];

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
    form.value = { 
      id: null, 
      cliente_id: "", 
      status: 'pending', 
      observacoes: '', 
      items: [], 
      desconto: 0,
      valor_total: 0 
    };
  }
  showModal.value = true;
};

const closeModal = () => { showModal.value = false; form.value = null; };

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
  setTimeout(() => { saving.value = false; closeModal(); }, 500);
};

const addItem = () => { 
  if (isLocked.value) return; 
  form.value.items.push({ descricao_item: '', quantidade: 1, valor_unitario: 0 }); 
};

const removeItem = (index) => { 
  if (isLocked.value) return; 
  form.value.items.splice(index, 1); 
};

const formatCurrency = (value) => { 
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0); 
};

const emitReceipt = () => {
  const doc = new jsPDF();
  const client = dbClients.value.find(c => c.id === form.value.cliente_id) || { nome: 'Consumidor', documento: '', telefone: '' };
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

  const rows = form.value.items.map(i => [
    i.descricao_item,
    i.quantidade,
    formatCurrency(i.valor_unitario),
    formatCurrency(i.quantidade * i.valor_unitario)
  ]);

  autoTable(doc, {
    startY: 85,
    head: [['Descrição do Serviço/Peça', 'Qtd', 'Unitário', 'Total']],
    body: rows,
    theme: 'grid',
    headStyles: { fillColor: [86, 166, 193] }
  });

  const finalY = doc.lastAutoTable.finalY + 10;
  doc.setFont('helvetica', 'bold');
  doc.text(`SUBTOTAL: ${formatCurrency(subtotalItems.value)}`, 140, finalY);
  doc.text(`DESCONTO: ${formatCurrency(form.value.desconto)}`, 140, finalY + 5);
  doc.setFontSize(12);
  doc.text(`TOTAL PAGO: ${formatCurrency(form.value.valor_total)}`, 140, finalY + 12);

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text('_________________________________________________', 105, 250, { align: 'center' });
  doc.text('ASSINATURA DO PRESTADOR', 105, 255, { align: 'center' });

  doc.save(`Recibo_OS_${form.value.id}.pdf`);
};

const onDragStart = (order) => { draggedOrder.value = order; };

const onDrop = (targetColumnTitle) => {
  if (!draggedOrder.value) return;
  const titleToStatus = { 'Pendente': 'pending', 'Em Produção': 'production', 'Concluído': 'completed', 'NFe Emitida': 'billed' };
  const newStatus = titleToStatus[targetColumnTitle];
  const orderIndex = ordens.value.findIndex(o => o.id === draggedOrder.value.id);
  if (orderIndex !== -1) ordens.value[orderIndex].status = newStatus;
  draggedOrder.value = null;
};
</script>

<style scoped>
.board-container { padding: 20px; height: 100%; display: flex; flex-direction: column; background: #f4f7f6; }
.board-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.header-left { display: flex; align-items: center; gap: 15px; }
.header-left h1 { color: #333; font-size: 1.1rem; letter-spacing: 2px; font-weight: 800; margin: 0; }
.btn-new { background: #56a6c1; color: #fff; padding: 12px 20px; border-radius: 4px; font-weight: 900; border: none; cursor: pointer; font-size: 0.8rem; box-shadow: 0 4px 12px rgba(86, 166, 193, 0.2); }
.view-toggle { background: #e0e6ed; padding: 4px; border-radius: 4px; display: flex; }
.view-toggle button { background: none; border: none; padding: 8px 12px; color: #7f8c8d; cursor: pointer; }
.view-toggle button.active { color: #56a6c1; background: #fff; border-radius: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.kanban-scroll-container { flex: 1; overflow-x: auto; padding-bottom: 15px; }
.kanban-board { display: flex; gap: 20px; min-width: min-content; height: 100%; }
.kanban-column { width: 300px; background: #ebf0f3; border-radius: 8px; display: flex; flex-direction: column; flex-shrink: 0; border: 1px solid #dfe6e9; }
.column-header { display: flex; justify-content: space-between; align-items: center; padding: 15px; border-top: 4px solid; background: #fff; border-radius: 8px 8px 0 0; }
.column-header h3 { font-size: 0.75rem; color: #444; font-weight: 800; letter-spacing: 1px; margin: 0; }
.task-count { background: #f0f3f7; color: #7f8c8d; font-size: 0.7rem; font-weight: bold; padding: 2px 8px; border-radius: 10px; }
.column-body { flex: 1; overflow-y: auto; padding: 12px; min-height: 100px; }
.kanban-card { background: #fff; padding: 15px; border-left: 4px solid #56a6c1; border-radius: 6px; cursor: pointer; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform 0.2s; }
.kanban-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.id { font-size: 0.8rem; font-weight: bold; color: #999; }
.kanban-card h4 { color: #2d3436; font-size: 0.9rem; margin: 0; font-weight: 600; }
.card-footer { margin-top: 15px; text-align: right; }
.price { color: #56a6c1; font-weight: 800; font-size: 1rem; }
.badge-late { background: #e74c3c; color: #fff; padding: 3px 6px; font-size: 0.6rem; border-radius: 3px; font-weight: bold; }
.empty-column { padding: 20px; text-align: center; color: #95a5a6; font-size: 0.8rem; }
.table-view-container { background: #fff; border: 1px solid #e0e6ed; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
.service-table { width: 100%; border-collapse: collapse; }
.service-table th { background: #f8f9fa; color: #7f8c8d; padding: 15px; text-align: left; font-size: 0.7rem; text-transform: uppercase; border-bottom: 1px solid #f0f3f7; }
.service-table td { padding: 18px 15px; border-bottom: 1px solid #f8f9fa; font-size: 0.85rem; color: #444; }
.accent-text { color: #56a6c1; font-weight: 800; }
.status-badge { padding: 5px 12px; border-radius: 20px; font-size: 0.65rem; font-weight: 800; background: #eee; color: #777; }
.status-badge.pending { background: #fff4e5; color: #f39c12; }
.status-badge.production { background: #edf7fa; color: #56a6c1; }
.status-badge.completed { background: #eefaf3; color: #2ecc71; }
.status-badge.billed { background: #f5effa; color: #9b59b6; }
.modal-backdrop { position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.3); z-index: 1000; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(4px); }
.modal-content { background: #fff; border-top: 6px solid #56a6c1; border-radius: 12px; width: 95%; max-height: 95vh; box-shadow: 0 20px 50px rgba(0,0,0,0.15); display: flex; flex-direction: column; }
.large-modal { max-width: 950px; }
.modal-header { padding: 20px 25px; border-bottom: 1px solid #f0f3f7; display: flex; justify-content: space-between; }
.modal-header h2 { font-size: 1.3rem; font-weight: 800; color: #2d3436; margin: 0; }
.subtitle { color: #95a5a6; font-size: 0.85rem; margin-top: 5px; }
.btn-close { background: none; border: none; color: #ccc; font-size: 2rem; cursor: pointer; }
.modal-body { padding: 25px; overflow-y: auto; flex: 1; }
.modal-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 30px; }
.form-group label { font-size: 0.7rem; color: #7f8c8d; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; display: block; }
.modern-input { background: #f8f9fa; border: 1px solid #e0e6ed; color: #333; padding: 12px; border-radius: 6px; width: 100%; outline: none; }
.modern-input:focus { border-color: #56a6c1; background: #fff; box-shadow: 0 0 0 3px rgba(86,166,193,0.1); }
.items-card { background: #f8f9fa; border: 1px solid #e0e6ed; border-radius: 8px; display: flex; flex-direction: column; }
.btn-new-item { width: 100%; background: #fff; color: #56a6c1; border: 1px dashed #56a6c1; padding: 10px; font-weight: 700; border-radius: 6px; cursor: pointer; }
.items-list-wrapper { max-height: 250px; overflow-y: auto; padding: 10px; }
.item-edit-grid { display: grid; grid-template-columns: 2fr 0.5fr 1fr auto; gap: 10px; align-items: center; margin-bottom: 8px; }
.mini-input { background: #fff; border: 1px solid #e0e6ed; padding: 8px; border-radius: 4px; width: 100%; font-size: 0.85rem; }
.mini-input:focus { border-color: #56a6c1; outline: none; }
.summary-area { padding: 15px; background: #fff; border-top: 1px solid #eee; border-radius: 0 0 8px 8px; }
.summary-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 0.9rem; color: #7f8c8d; }
.discount-row { color: #e74c3c; font-weight: 600; }
.discount-input-wrapper { display: flex; align-items: center; gap: 5px; }
.mini-input.discount { width: 80px; color: #e74c3c; font-weight: bold; }
.total-display { padding: 15px 0 0 0; border-top: 2px solid #f4f7f6; display: flex; justify-content: space-between; align-items: center; }
.total-value { font-size: 1.5rem; color: #56a6c1; font-weight: 900; }
.modal-footer { padding: 20px 25px; border-top: 1px solid #f0f3f7; display: flex; justify-content: space-between; align-items: center; background: #fcfdfe; }
.footer-left { display: flex; gap: 10px; }
.btn-secondary { background: #fff; border: 1px solid #e0e6ed; color: #56a6c1; padding: 10px 15px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer; }
.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }
.footer-right { display: flex; gap: 12px; }
.btn-cancel { background: #f1f2f6; color: #7f8c8d; border: none; padding: 12px 25px; border-radius: 6px; font-weight: 700; cursor: pointer; }
.btn-save { background: #56a6c1; color: #fff; border: none; padding: 12px 30px; border-radius: 6px; font-weight: 800; cursor: pointer; box-shadow: 0 4px 10px rgba(86,166,193,0.3); }
@media (max-width: 768px) { .modal-grid { grid-template-columns: 1fr; } .modal-content { height: 100%; border-radius: 0; } }
</style>