<template>
  <div class="form-container">
    <header class="form-header">
      <div class="title-group">
        <h2>ORÇAMENTOS</h2>
        <p>Gere e gerencie orçamentos para a WK Vidros</p>
      </div>
    </header>

    <main class="main-layout">
      <section class="editor-section">
        <div class="glass-card">
          <form @submit.prevent="save" class="modern-form">
            <div class="form-top-grid">
              <div class="input-wrap">
                <label>SELECIONAR CLIENTE</label>
                <select v-model="selectedClientId" class="m-input" required>
                  <option :value="null" disabled>Escolha um cliente na base...</option>
                  <option v-for="client in clientes" :key="client.id" :value="client.id">{{ client.nome }}</option>
                </select>
              </div>
              <div class="total-display-card">
                <span class="total-label">VALOR ESTIMADO</span>
                <span class="total-amount">{{ formatCurrency(totalOrcamento) }}</span>
              </div>
            </div>

            <div class="items-area">
              <div class="items-header">
                <h3>ITENS DO SERVIÇO</h3>
                <button type="button" class="btn-add-item" @click="addItem">+ ADICIONAR</button>
              </div>
              
              <div class="items-list">
                <div v-if="itens.length === 0" class="empty-list">Nenhum item adicionado ao orçamento.</div>
                <div v-for="(item, index) in itens" :key="index" class="item-entry">
                  <div class="entry-main">
                    <input type="text" v-model="item.descricao_item" placeholder="Descrição da peça ou serviço" class="m-input desc" />
                  </div>
                  <div class="entry-details">
                    <input type="number" v-model.number="item.quantidade" placeholder="Qtd" class="m-input qty" />
                    <input type="number" v-model.number="item.valor_unitario" placeholder="R$ Unit." class="m-input price" />
                    <div class="item-subtotal">{{ formatCurrency(item.quantidade * item.valor_unitario) }}</div>
                    <button type="button" @click="removeItem(index)" class="btn-del">✕</button>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-footer">
              <button type="button" class="btn-secondary" @click="resetForm">DESCARTAR</button>
              <button type="submit" class="btn-primary">{{ isEditing ? 'ATUALIZAR' : 'SALVAR' }} ORÇAMENTO</button>
            </div>
          </form>
        </div>
      </section>

      <section class="history-section">
        <div class="section-title">
          <h3>ORÇAMENTOS RECENTES</h3>
        </div>
        <div class="history-grid">
          <div v-for="orc in orcamentosSalvos" :key="orc.id" class="history-card">
            <div class="h-card-info">
              <span class="h-id">#{{ orc.id }}</span>
              <span class="h-date">{{ orc.data }}</span>
            </div>
            <h4 class="h-client">{{ getClienteNome(orc.cliente_id) }}</h4>
            <div class="h-total">{{ formatCurrency(orc.total || orc.valor_total) }}</div>
            <div class="h-actions">
              <button @click="editOrcamento(orc)" class="h-btn">✎ Editar</button>
              <button @click="downloadPDF(orc)" class="h-btn pdf">PDF</button>
              <button @click="gerarOS(orc)" class="h-btn os">📋 Gerar OS</button>
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
        descricao_item: i.descricao_item || i.descricao,
        quantidade: i.quantidade,
        valor_unitario: i.valor_unitario || i.valor
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
    alert(e.message);
  }
};

const deleteOrcamento = async (id) => {
  if (confirm('Excluir orçamento?')) {
    await api.delete(`/orcamentos/${id}`);
    await loadData();
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
  doc.setDrawColor(0); doc.setLineWidth(0.3); doc.rect(10, 10, 190, 38); doc.addImage(logoImg, 'JPG', 25, 12, 45, 33);
  doc.setFontSize(14); doc.setFont('helvetica', 'bold'); doc.text('W&K vidros', 140, 20, { align: 'center' });
  const itemsSource = orc.itens_orcamento || orc.items || [];
  const tableRows = itemsSource.map(item => [
    item.quantidade, 
    '', 
    item.descricao_item || item.descricao, 
    (item.valor_unitario || item.valor).toFixed(2), 
    (item.quantidade * (item.valor_unitario || item.valor)).toFixed(2)
  ]);
  autoTable(doc, { startY: 80, head: [['Quant.', 'Unid.', 'Descrição', 'Unitário', 'Total']], body: tableRows, theme: 'grid' });
  doc.save(`Orcamento_WK_${orc.id}.pdf`);
};

const gerarOS = async (orc) => {
  try {
    const payload = {
      cliente_id: orc.cliente_id,
      valor_total: orc.valor_total || orc.total,
      status: 'pending',
      items: (orc.itens_orcamento || orc.items).map(i => ({
        descricao_item: i.descricao_item || i.descricao,
        quantidade: i.quantidade,
        valor_unitario: i.valor_unitario || i.valor
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
.form-container { padding: 30px; background: #f1f5f9; min-height: 100vh; }
.form-header { margin-bottom: 30px; }
.title-group h2 { color: #0f172a; font-weight: 900; margin: 0; }
.title-group p { color: #64748b; font-size: 0.9rem; }

.main-layout { display: flex; flex-direction: column; gap: 30px; }
.glass-card { background: #fff; padding: 32px; border-radius: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.7); }

.form-top-grid { display: grid; grid-template-columns: 2fr 1.2fr; gap: 24px; margin-bottom: 32px; }
.total-display-card { background: #f8fafc; padding: 20px; border-radius: 16px; display: flex; flex-direction: column; align-items: flex-end; border: 2px solid #56a6c1; }
.total-label { font-size: 0.7rem; font-weight: 800; color: #56a6c1; }
.total-amount { font-size: 2.2rem; font-weight: 950; color: #1e293b; line-height: 1; }

.items-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.items-header h3 { font-size: 0.8rem; font-weight: 800; color: #475569; }
.btn-add-item { background: #f1f5f9; color: #56a6c1; border: 1px dashed #56a6c1; padding: 8px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; }

.item-entry { display: grid; grid-template-columns: 1fr; gap: 12px; padding: 16px; background: #f8fafc; border-radius: 12px; margin-bottom: 12px; }
.entry-details { display: grid; grid-template-columns: 1fr 1.5fr 1fr auto; gap: 12px; align-items: center; }
.item-subtotal { font-weight: 800; color: #56a6c1; text-align: right; }

.history-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.history-card { background: #fff; padding: 20px; border-radius: 16px; border-bottom: 4px solid #e2e8f0; }
.h-card-info { display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8; font-weight: 700; margin-bottom: 8px; }
.h-client { margin: 0 0 12px 0; color: #1e293b; }
.h-total { font-size: 1.4rem; font-weight: 900; color: #56a6c1; margin-bottom: 16px; }
.h-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.h-btn { flex: 1; padding: 8px; border-radius: 6px; border: 1px solid #e2e8f0; background: #fff; cursor: pointer; font-size: 0.75rem; font-weight: 700; color: #64748b; }

@media (max-width: 768px) {
  .form-top-grid { grid-template-columns: 1fr; }
  .total-display-card { align-items: center; }
  .entry-details { grid-template-columns: 1fr 1fr; }
  .item-subtotal { grid-column: span 2; text-align: center; font-size: 1.2rem; }
}
</style>