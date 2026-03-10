<template>
  <div class="form-view-container">
    <header class="view-header">
      <div class="title-group">
        <h2>ORÇAMENTOS</h2>
        <p>Gere e gerencie orçamentos para a WK Vidros</p>
      </div>
    </header>

    <main class="main-content">
      <div class="card-glass editor-card">
        <form @submit.prevent="save" class="modern-form">
          <div class="form-top-row">
            <div class="field-wrap">
              <label>SELECIONAR CLIENTE</label>
              <select v-model="selectedClientId" class="m-input" required>
                <option :value="null" disabled>Escolha um cliente na base...</option>
                <option v-for="client in clientes" :key="client.id" :value="client.id">{{ client.nome }}</option>
              </select>
            </div>
            <div class="value-highlight">
              <span class="v-label">VALOR ESTIMADO</span>
              <h3 class="v-amount">{{ formatCurrency(totalOrcamento) }}</h3>
            </div>
          </div>

          <div class="items-section">
            <div class="items-header">
              <h3>ITENS DO SERVIÇO</h3>
              <button type="button" class="btn-add" @click="addItem">+ ADICIONAR ITEM</button>
            </div>
            
            <div class="items-list">
              <div v-if="itens.length === 0" class="empty-msg">Nenhum item adicionado ao orçamento.</div>
              <div v-for="(item, index) in itens" :key="index" class="item-row">
                <div class="row-main">
                  <input type="text" v-model="item.descricao_item" placeholder="Descrição da peça ou serviço" class="m-input" />
                </div>
                <div class="row-details">
                  <div class="mini-field">
                    <label>QTD</label>
                    <input type="number" v-model.number="item.quantidade" class="m-input" />
                  </div>
                  <div class="mini-field">
                    <label>VALOR UNIT.</label>
                    <input type="number" v-model.number="item.valor_unitario" class="m-input" step="0.01" />
                  </div>
                  <div class="item-subtotal">
                    {{ formatCurrency(item.quantidade * item.valor_unitario) }}
                  </div>
                  <button type="button" @click="removeItem(index)" class="btn-remove">✕</button>
                </div>
              </div>
            </div>
          </div>

          <div class="form-footer">
            <button type="button" class="btn-sec" @click="resetForm">DESCARTAR</button>
            <button type="submit" class="btn-pri">{{ isEditing ? 'ATUALIZAR' : 'SALVAR' }} ORÇAMENTO</button>
          </div>
        </form>
      </div>

      <section class="recent-section">
        <h3 class="section-title">ORÇAMENTOS RECENTES</h3>
        <div class="history-grid">
          <div v-for="orc in orcamentosSalvos" :key="orc.id" class="history-card">
            <div class="h-top">
              <span class="h-id">#{{ orc.id }}</span>
              <span class="h-date">{{ orc.data }}</span>
            </div>
            <h4 class="h-client">{{ getClienteNome(orc.cliente_id) }}</h4>
            <div class="h-total">{{ formatCurrency(orc.valor_total || orc.total) }}</div>
            <div class="h-actions">
              <button @click="editOrcamento(orc)" class="h-btn">✎ Editar</button>
              <button @click="downloadPDF(orc)" class="h-btn pdf">PDF</button>
              <button @click="gerarOS(orc)" class="h-btn os">📋 OS</button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '../services/api';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import logoImg from '../logo.png';

const clientes = ref([]);
const orcamentosSalvos = ref([]);
const selectedClientId = ref(null);
const itens = ref([]);
const isEditing = ref(false);
const editingId = ref(null);

const loadData = async () => {
  try {
    const [resClientes, resOrcamentos] = await Promise.all([
      api.get('/clientes'),
      api.get('/orcamentos')
    ]);
    clientes.value = resClientes;
    orcamentosSalvos.value = resOrcamentos;
  } catch (e) {
    console.error(e);
  }
};

onMounted(loadData);

const addItem = () => { itens.value.push({ descricao_item: '', quantidade: 1, valor_unitario: 0 }); };
const removeItem = (index) => { itens.value.splice(index, 1); };
const totalOrcamento = computed(() => itens.value.reduce((total, item) => total + (item.quantidade * item.valor_unitario), 0));
const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
const getClienteNome = (id) => clientes.value.find(c => c.id === id)?.nome || 'Cliente N/A';

const resetForm = () => { selectedClientId.value = null; itens.value = []; isEditing.value = false; editingId.value = null; };

const save = async () => {
  try {
    const payload = {
      cliente_id: selectedClientId.value,
      valor_total: totalOrcamento.value,
      items: itens.value.map(i => ({
        descricao_item: i.descricao_item,
        quantidade: i.quantidade,
        valor_unitario: i.valor_unitario
      }))
    };
    if (isEditing.value) {
      await api.put(`/orcamentos/${editingId.value}`, payload);
    } else {
      await api.post('/orcamentos', payload);
    }
    await loadData();
    resetForm();
  } catch (e) {
    alert("Erro ao salvar: Verifique os campos");
  }
};

const editOrcamento = (orc) => {
  isEditing.value = true;
  editingId.value = orc.id;
  selectedClientId.value = orc.cliente_id;
  itens.value = JSON.parse(JSON.stringify(orc.itens_orcamento || orc.items || []));
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const downloadPDF = (orc) => {
  const doc = new jsPDF();
  const cliente = clientes.value.find(c => c.id === orc.cliente_id) || { nome: '' };
  doc.setFontSize(14);
  doc.text('ORÇAMENTO - WK VIDROS', 10, 20);
  doc.text(`Cliente: ${cliente.nome}`, 10, 30);
  const itemsSource = orc.itens_orcamento || orc.items || [];
  const tableRows = itemsSource.map(item => [
    item.quantidade, 
    item.descricao_item, 
    (item.valor_unitario).toFixed(2), 
    (item.quantidade * item.valor_unitario).toFixed(2)
  ]);
  autoTable(doc, { startY: 40, head: [['Qtd', 'Descrição', 'Unitário', 'Total']], body: tableRows });
  doc.save(`Orcamento_${orc.id}.pdf`);
};

const gerarOS = async (orc) => {
  try {
    const payload = {
      cliente_id: orc.cliente_id,
      valor_total: orc.valor_total || orc.total,
      status: 'pending',
      items: (orc.itens_orcamento || orc.items).map(i => ({
        descricao_item: i.descricao_item,
        quantidade: i.quantidade,
        valor_unitario: i.valor_unitario
      }))
    };
    await api.post('/ordens', payload);
    alert('Ordem de Serviço gerada com sucesso!');
  } catch (e) {
    alert(e.message);
  }
};
</script>

<style scoped>
.form-view-container { padding: 32px; min-height: 100%; }
.view-header { margin-bottom: 32px; }
.view-header h2 { font-weight: 900; font-size: 1.8rem; color: #0f172a; letter-spacing: -1px; }
.view-header p { color: #64748b; font-size: 0.95rem; }

.card-glass { background: #fff; border-radius: 24px; padding: 32px; box-shadow: 0 10px 25px rgba(0,0,0,0.03); border: 1px solid #edf2f7; }

.form-top-row { display: grid; grid-template-columns: 2fr 1fr; gap: 32px; margin-bottom: 40px; align-items: end; }
.field-wrap { display: flex; flex-direction: column; gap: 8px; }
label { font-size: 0.7rem; font-weight: 800; color: #94a3b8; letter-spacing: 0.5px; }

.m-input { background: #f8fafc; border: 1.5px solid #e2e8f0; padding: 14px; border-radius: 12px; font-size: 0.95rem; width: 100%; outline: none; transition: 0.2s; }
.m-input:focus { border-color: #56a6c1; background: #fff; box-shadow: 0 0 0 4px rgba(86,166,193,0.1); }

.value-highlight { background: #f1f5f9; padding: 24px; border-radius: 16px; text-align: right; border: 1px solid #56a6c1; }
.v-label { font-size: 0.65rem; font-weight: 800; color: #56a6c1; }
.v-amount { font-size: 2.2rem; font-weight: 900; color: #1e293b; margin-top: 4px; line-height: 1; }

.items-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.items-header h3 { font-size: 0.85rem; font-weight: 800; color: #475569; }
.btn-add { background: transparent; border: 1.5px dashed #56a6c1; color: #56a6c1; padding: 8px 16px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 0.8rem; }

.item-row { display: grid; grid-template-columns: 1fr; gap: 16px; padding: 20px; background: #f8fafc; border-radius: 16px; margin-bottom: 12px; border: 1px solid #f1f5f9; }
.row-details { display: grid; grid-template-columns: 80px 120px 1fr auto; gap: 16px; align-items: end; }
.item-subtotal { font-weight: 900; color: #56a6c1; font-size: 1.1rem; text-align: right; padding-bottom: 10px; }
.btn-remove { background: #fee2e2; color: #ef4444; border: none; width: 40px; height: 40px; border-radius: 10px; cursor: pointer; font-weight: bold; }

.form-footer { margin-top: 40px; padding-top: 32px; border-top: 1px solid #f1f5f9; display: flex; gap: 16px; justify-content: flex-end; }
.btn-pri { background: #1e293b; color: #fff; border: none; padding: 14px 32px; border-radius: 12px; font-weight: 800; cursor: pointer; }
.btn-sec { background: transparent; color: #94a3b8; border: none; font-weight: 700; cursor: pointer; }

.recent-section { margin-top: 60px; }
.section-title { font-size: 0.9rem; font-weight: 900; color: #1e293b; margin-bottom: 24px; letter-spacing: 1px; }
.history-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }
.history-card { background: #fff; padding: 24px; border-radius: 20px; border-bottom: 4px solid #e2e8f0; transition: 0.3s; }
.history-card:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.05); }
.h-top { display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8; font-weight: 700; margin-bottom: 8px; }
.h-client { font-size: 1rem; color: #1e293b; font-weight: 700; margin-bottom: 12px; }
.h-total { font-size: 1.5rem; font-weight: 900; color: #56a6c1; margin-bottom: 20px; }
.h-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.h-btn { flex: 1; padding: 8px; border-radius: 8px; border: 1.5px solid #f1f5f9; background: #fff; font-size: 0.75rem; font-weight: 700; color: #64748b; cursor: pointer; }

@media (max-width: 768px) {
  .form-view-container { padding: 16px; }
  .form-top-row { grid-template-columns: 1fr; gap: 16px; }
  .row-details { grid-template-columns: 1fr 1fr; }
  .item-subtotal { grid-column: span 2; text-align: center; }
  .btn-pri { width: 100%; }
}
</style>