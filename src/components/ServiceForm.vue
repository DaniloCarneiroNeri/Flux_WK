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
                  <input 
                    type="text" 
                    list="produtos-lista" 
                    v-model="item.descricao_item" 
                    @input="updateItemData(item)"
                    placeholder="Descrição da peça ou serviço" 
                    class="m-input" 
                  />
                </div>
                <div :class="['row-details', { 'has-m2': item.unid === 'MT²' }]">
                  <div class="mini-field">
                    <label>QTD</label>
                    <input type="number" v-model.number="item.quantidade" class="m-input" />
                  </div>
                  <div class="mini-field" v-if="item.unid === 'MT²'">
                    <label>M²</label>
                    <input type="number" v-model.number="item.m2" class="m-input" step="0.01" />
                  </div>
                  <div class="mini-field">
                    <label>VALOR UNIT.</label>
                    <input type="number" v-model.number="item.valor_unitario" class="m-input" step="0.01" />
                  </div>
                  <div class="item-subtotal">
                    {{ formatCurrency(getItemTotal(item)) }}
                  </div>
                  <button type="button" @click="removeItem(index)" class="btn-remove">✕</button>
                </div>
              </div>
            </div>
            
            <datalist id="produtos-lista">
              <option v-for="p in produtos" :key="p.id" :value="p.descricao"></option>
            </datalist>
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

    <transition name="modal">
      <div v-if="osModal.show" class="modal-overlay" @click.self="closeOsModal">
        <div class="modal-card mini-modal">
          <div class="modal-header">
            <h3>{{ osModal.type === 'error' ? 'Atenção' : 'Sucesso' }}</h3>
            <button class="close-x" @click="closeOsModal">×</button>
          </div>
          <div class="modal-body">
            <p>{{ osModal.message }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn-pri" @click="closeOsModal">OK</button>
          </div>
        </div>
      </div>
    </transition>
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
const produtos = ref([]);
const selectedClientId = ref(null);
const itens = ref([]);
const isEditing = ref(false);
const editingId = ref(null);

const osModal = ref({ show: false, message: '', type: 'success' });

const loadData = async () => {
  try {
    const [resClientes, resOrcamentos, resProdutos] = await Promise.all([
      api.get('/clientes'),
      api.get('/orcamentos'),
      api.get('/produtos')
    ]);
    clientes.value = resClientes;
    orcamentosSalvos.value = resOrcamentos;
    produtos.value = resProdutos;
  } catch (e) {
    console.error(e);
  }
};

onMounted(loadData);

const closeOsModal = () => {
  osModal.value.show = false;
};

const addItem = () => { 
  itens.value.push({ 
    descricao_item: '', 
    quantidade: 1, 
    valor_unitario: 0,
    produto_id: null,
    cfop: '',
    unid: 'UN',
    m2: 0
  }); 
};

const removeItem = (index) => { itens.value.splice(index, 1); };

const updateItemData = (item) => {
  const matched = produtos.value.find(p => p.descricao === item.descricao_item);
  if (matched) {
    item.produto_id = matched.id;
    item.cfop = matched.cfop;
    item.unid = matched.unid;
  } else {
    item.produto_id = null;
    item.cfop = '';
    item.unid = 'UN';
  }
};

const getItemTotal = (item) => {
  if (item.unid === 'MT²') {
    return item.quantidade * (item.m2 || 0) * item.valor_unitario;
  }
  return item.quantidade * item.valor_unitario;
};

const totalOrcamento = computed(() => itens.value.reduce((total, item) => total + getItemTotal(item), 0));
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
        valor_unitario: i.valor_unitario,
        produto_id: i.produto_id || null,
        cfop: i.cfop || '',
        unid: i.unid || 'UN',
        m2: i.unid === 'MT²' ? i.m2 : 0
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
    osModal.value = { show: true, message: "Erro ao salvar: Verifique os campos", type: 'error' };
  }
};

const editOrcamento = (orc) => {
  isEditing.value = true;
  editingId.value = orc.id;
  selectedClientId.value = orc.cliente_id;
  itens.value = JSON.parse(JSON.stringify(orc.itens_orcamento || orc.items || [])).map(i => ({
    ...i,
    m2: i.m2 || 0
  }));
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const downloadPDF = (orc) => {
  const doc = new jsPDF();
  const cliente = clientes.value.find(c => c.id === orc.cliente_id) || { nome: '' };
  
  doc.addImage(logoImg, 'PNG', 14, 10, 30, 30);
  
  doc.setFontSize(14);
  doc.setFont("helvetica", "bold");
  doc.text('Andressa Oliveira', 50, 16);
  
  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.text('CPF/CNPJ: 55952245000100', 50, 22);
  doc.text('Avenida 21 de abril', 50, 27);
  doc.text('Telefone(s): 62998766290', 50, 32);
  doc.text('E-mail:', 50, 37);
  
  doc.setFontSize(10);
  doc.setFont("helvetica", "bold");
  doc.text(`Orçamento nº: ${orc.id || ''}`, 140, 16);
  
  doc.setFont("helvetica", "normal");
  const dataEmissao = orc.data || new Date().toLocaleDateString('pt-BR');
  doc.text(`Emitido em: ${dataEmissao}`, 140, 22);
  doc.text('Válido até: ', 140, 27);
  
  doc.line(14, 42, 196, 42);
  
  doc.setFont("helvetica", "bold");
  doc.text(`Cliente: ${cliente.nome}`, 14, 48);
  
  doc.setFont("helvetica", "normal");
  doc.text('Endereço: ', 14, 53);
  doc.text('Fone: ', 14, 58);
  doc.text('CPF: ', 140, 48);
  
  doc.line(14, 62, 196, 62);
  
  const itemsSource = orc.itens_orcamento || orc.items || [];
  const tableRows = itemsSource.map(item => {
    return [
      String(item.quantidade),
      item.unid || 'UN',
      item.descricao_item,
      formatCurrency(item.valor_unitario),
      formatCurrency(getItemTotal(item))
    ];
  });

  autoTable(doc, {
    startY: 65,
    head: [['Quant.', 'Unid.', 'Descrição', 'Unitário', 'Total']],
    body: tableRows,
    theme: 'plain',
    headStyles: { fontStyle: 'bold', textColor: 0 },
    styles: { fontSize: 10, cellPadding: 2 },
    columnStyles: {
      0: { halign: 'center' },
      1: { halign: 'center' },
      3: { halign: 'right' },
      4: { halign: 'right' }
    }
  });
  
  const finalY = doc.lastAutoTable.finalY + 10;
  const subtotal = itemsSource.reduce((acc, item) => acc + getItemTotal(item), 0);
  
  autoTable(doc, {
    startY: finalY,
    head: [['Subtotal', 'Desconto', 'Acréscimo', 'Total']],
    body: [[
      formatCurrency(subtotal),
      'R$ 0,00',
      'R$ 0,00',
      formatCurrency(subtotal)
    ]],
    theme: 'plain',
    headStyles: { fontStyle: 'bold', textColor: 0, halign: 'center', fillColor: [240, 240, 240] },
    bodyStyles: { halign: 'center', fontStyle: 'bold' }
  });

  const obsY = doc.lastAutoTable.finalY + 15;
  doc.setFont("helvetica", "bold");
  doc.text('OBSERVAÇÕES', 14, obsY);
  
  const sigY = obsY + 40;
  doc.line(30, sigY, 90, sigY);
  doc.setFont("helvetica", "normal");
  doc.text('Andressa Oliveira', 60, sigY + 5, { align: 'center' });
  
  doc.line(120, sigY, 180, sigY);
  doc.text(cliente.nome, 150, sigY + 5, { align: 'center' });

  doc.save(`Orcamento_${orc.id || 'doc'}.pdf`);
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
        valor_unitario: i.valor_unitario,
        produto_id: i.produto_id || null,
        cfop: i.cfop || '',
        unid: i.unid || 'UN',
        m2: i.unid === 'MT²' ? i.m2 : 0
      }))
    };
    await api.post('/ordens', payload);
    osModal.value = { show: true, message: 'Ordem de Serviço gerada com sucesso!', type: 'success' };
  } catch (e) {
    osModal.value = { show: true, message: e.message || 'Erro ao gerar OS.', type: 'error' };
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
.row-details.has-m2 { grid-template-columns: 80px 100px 120px 1fr auto; }
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

.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal-card.mini-modal { background: #fff; width: 100%; max-width: 400px; border-radius: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; }
.modal-header { padding: 20px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { font-size: 1.1rem; font-weight: 800; color: #1e293b; margin: 0; }
.close-x { background: transparent; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; line-height: 1; }
.modal-body { padding: 24px; color: #475569; font-size: 0.95rem; line-height: 1.5; }
.modal-footer { padding: 16px 24px; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; background: #f8fafc; }

@media (max-width: 768px) {
  .form-view-container { padding: 16px; }
  .form-top-row { grid-template-columns: 1fr; gap: 16px; }
  .row-details { grid-template-columns: 1fr 1fr; }
  .row-details.has-m2 { grid-template-columns: 1fr 1fr; }
  .item-subtotal { grid-column: span 2; text-align: center; }
  .btn-pri { width: 100%; }
}
</style>