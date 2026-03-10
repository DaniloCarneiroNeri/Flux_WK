<template>
  <div class="form-view-container">
    <div class="form-header">
      <h2>ORÇAMENTOS</h2>
      <p>Gestão de Vendas WK Vidros</p>
    </div>
    <div class="form-card main-form">
      <form @submit.prevent="save" class="flux-form">
        <div class="top-row">
          <div class="form-group">
            <label>CLIENTE</label>
            <select v-model="selectedClientId" class="modern-input" required>
              <option :value="null" disabled>Selecione um cliente...</option>
              <option v-for="client in clientes" :key="client.id" :value="client.id">
                {{ client.nome }}
              </option>
            </select>
          </div>
          <div class="form-group total-box">
             <label>VALOR TOTAL</label>
             <div class="total-val">{{ formatCurrency(totalOrcamento) }}</div>
          </div>
        </div>
        <div class="items-section">
          <div class="items-header">ITENS DO ORÇAMENTO</div>
          <div class="items-list">
            <div v-if="itens.length === 0" class="empty-items">
              <p>Nenhum item adicionado.</p>
            </div>
            <div v-for="(item, index) in itens" :key="index" class="item-row">
              <input type="text" v-model="item.descricao" placeholder="Descrição do item" class="item-input desc" />
              <input type="number" v-model.number="item.quantidade" placeholder="Qtd" class="item-input qty" />
              <input type="number" v-model.number="item.valor" placeholder="Valor" class="item-input price" />
              <span class="item-total">{{ formatCurrency(item.quantidade * item.valor) }}</span>
              <button type="button" @click="removeItem(index)" class="btn-remove-item">✕</button>
            </div>
          </div>
          <button type="button" class="btn-add" @click="addItem">+ ADICIONAR ITEM</button>
        </div>
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="resetForm">DESCARTAR</button>
          <button type="submit" class="btn-primary">{{ isEditing ? 'ATUALIZAR' : 'GERAR' }} ORÇAMENTO</button>
        </div>
      </form>
    </div>

    <div class="list-section">
      <div class="section-header">
        <h3>ORÇAMENTOS SALVOS</h3>
      </div>
      <div class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>CLIENTE</th>
              <th>DATA</th>
              <th>TOTAL</th>
              <th>AÇÕES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="orc in orcamentosSalvos" :key="orc.id">
              <td>#{{ orc.id }}</td>
              <td>{{ getClienteNome(orc.cliente_id) }}</td>
              <td>{{ orc.data }}</td>
              <td class="highlight">{{ formatCurrency(orc.total) }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-action edit" @click="editOrcamento(orc)" title="Editar">✎</button>
                  <button class="btn-action pdf" @click="downloadPDF(orc)" title="Baixar PDF">PDF</button>
                  <button class="btn-action os" @click="gerarOS(orc)" title="Gerar O.S.">📋</button>
                  <button class="btn-action delete" @click="deleteOrcamento(orc.id)" title="Excluir">✕</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
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
  const [resClientes, resOrcamentos] = await Promise.all([
    api.get('/clientes'),
    api.get('/orcamentos')
  ]);
  clientes.value = resClientes;
  orcamentosSalvos.value = resOrcamentos;
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
      items: itens.value
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
  itens.value = JSON.parse(JSON.stringify(orc.itens_orcamento || []));
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const downloadPDF = (orc) => {
  const doc = new jsPDF();
  const cliente = clientes.value.find(c => c.id === orc.cliente_id) || { nome: '' };
  doc.setDrawColor(0); doc.setLineWidth(0.3); doc.rect(10, 10, 190, 38); doc.addImage(logoImg, 'JPG', 25, 12, 45, 33);
  doc.setFontSize(14); doc.setFont('helvetica', 'bold'); doc.text('W&K vidros', 140, 20, { align: 'center' });
  const tableRows = orc.itens_orcamento.map(item => [item.quantidade, '', item.descricao_item, item.valor_unitario.toFixed(2), (item.quantidade * item.valor_unitario).toFixed(2)]);
  autoTable(doc, { startY: 80, head: [['Quant.', 'Unid.', 'Descrição', 'Unitário', 'Total']], body: tableRows, theme: 'grid' });
  doc.save(`Orcamento_WK_${orc.id}.pdf`);
};

const gerarOS = async (orc) => {
  try {
    const payload = {
      cliente_id: orc.cliente_id,
      valor_total: orc.valor_total,
      status: 'pending',
      items: orc.itens_orcamento
    };
    await api.post('/ordens', payload);
    alert('Ordem de Serviço gerada com sucesso!');
  } catch (e) {
    alert(e.message);
  }
};
</script>

<style scoped>
.form-view-container { padding: 30px; background: #f4f7f6; }
.form-header { margin-bottom: 25px; }
.form-header h2 { color: #2d3436; font-size: 1.5rem; font-weight: 900; }
.form-header p { color: #95a5a6; font-size: 0.9rem; }
.main-form { background: #fff; border-radius: 8px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 30px; border-left: 5px solid #56a6c1; }
.top-row { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
.total-val { font-size: 2rem; font-weight: 900; color: #56a6c1; }
.items-section { margin: 25px 0; border: 1px solid #e0e6ed; border-radius: 8px; background: #fcfdfe; }
.items-header { background: #f8f9fa; padding: 15px; font-size: 0.75rem; font-weight: 800; color: #7f8c8d; border-bottom: 1px solid #e0e6ed; }
.item-row { display: grid; grid-template-columns: 3fr 1fr 1fr 1fr auto; gap: 12px; padding: 15px; border-bottom: 1px solid #f0f3f7; align-items: center; }
.item-input { background: #fff; border: 1px solid #e0e6ed; padding: 10px; border-radius: 6px; width: 100%; outline: none; }
.item-input:focus { border-color: #56a6c1; }
.btn-add { width: 100%; border: none; color: #56a6c1; padding: 15px; font-weight: 800; cursor: pointer; background: transparent; }
.form-actions { display: flex; justify-content: flex-end; gap: 15px; margin-top: 25px; }
.btn-primary { background: #56a6c1; color: #fff; border: none; padding: 14px 30px; font-weight: 900; border-radius: 6px; cursor: pointer; }
.btn-cancel { background: #f1f2f6; color: #7f8c8d; border: none; padding: 14px 30px; border-radius: 6px; cursor: pointer; }
.list-section { background: #fff; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.modern-table { width: 100%; border-collapse: collapse; }
.modern-table th { text-align: left; padding: 15px; color: #95a5a6; border-bottom: 1px solid #f0f3f7; font-size: 0.7rem; text-transform: uppercase; }
.modern-table td { padding: 15px; border-bottom: 1px solid #f8f9fa; color: #2d3436; }
.highlight { color: #56a6c1; font-weight: 800; }
.action-buttons { display: flex; gap: 8px; }
.btn-action { background: #f8f9fa; border: 1px solid #e0e6ed; color: #56a6c1; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; font-weight: bold; }
.btn-action:hover { background: #56a6c1; color: #fff; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 0.7rem; color: #7f8c8d; font-weight: 700; text-transform: uppercase; }
.modern-input { background: #f8f9fa; border: 1px solid #e0e6ed; color: #333; padding: 14px; border-radius: 6px; width: 100%; outline: none; transition: border-color 0.2s; }
.modern-input:focus { border-color: #56a6c1; background: #fff; }
</style>