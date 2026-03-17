<template>
  <div class="board-container">
    <header class="board-header">
      <div class="header-info">
        <h1>PROMISSÓRIAS</h1>
        <p>Gestão de recebimentos parcelados e controle de clientes</p>
      </div>
      <div class="header-controls">
        <button class="btn-primary-action" @click="openCreateModal()">+ NOVA PROMISSÓRIA</button>
      </div>
    </header>

    <div class="content-area">
      <div v-if="promissorias.length === 0" class="empty-state">
        Nenhuma promissória cadastrada.
      </div>
      <div v-else class="promissorias-grid">
        <div 
          v-for="promissoria in promissorias" 
          :key="promissoria.id" 
          class="client-card" 
          @click="openDetailsModal(promissoria)"
        >
          <div class="card-header">
            <h3 class="client-name">{{ getClientName(promissoria.cliente_id) }}</h3>
            <span class="card-id">#{{ promissoria.id }}</span>
          </div>
          <div class="card-body">
            <p class="product-name">{{ getProductName(promissoria.produto_id) }}</p>
            <div class="financial-summary">
              <div class="summary-item">
                <span class="label">Total</span>
                <span class="value total">{{ formatCurrency(promissoria.valor_total) }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Restante</span>
                <span class="value remaining">{{ formatCurrency(getRemainingValue(promissoria)) }}</span>
              </div>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar" :style="{ width: getProgress(promissoria) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <transition name="modal">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
        <div class="modal-card">
          <div class="modal-header">
            <h3>{{ isEditing ? 'Editar Promissória' : 'Nova Promissória' }}</h3>
            <button class="close-x" @click="closeCreateModal">×</button>
          </div>
          
          <div class="modal-body scrollable">
            <div class="form-grid">
              <div class="field-group full-width">
                <label>CLIENTE</label>
                <select v-model="formCreate.cliente_id" class="custom-input">
                  <option value="" disabled>Selecione um cliente</option>
                  <option v-for="c in dbClients" :key="c.id" :value="c.id">{{ c.nome }}</option>
                </select>
              </div>

              <div class="field-group full-width">
                <label>PRODUTO / SERVIÇO</label>
                <select v-model="formCreate.produto_id" class="custom-input" @change="updateProductValue">
                  <option value="" disabled>Selecione um produto</option>
                  <option v-for="p in dbProducts" :key="p.id" :value="p.id">{{ p.nome }}</option>
                </select>
              </div>

              <div class="field-group">
                <label>VALOR UNIT/M²</label>
                <input type="number" v-model.number="formCreate.valor_unitario" class="custom-input" @input="calculateTotal" />
              </div>
              <div class="field-group">
                <label>QUANTIDADE</label>
                <input type="number" v-model.number="formCreate.quantidade" class="custom-input" @input="calculateTotal" />
              </div>

              <div class="field-group">
                <label>QUANTIDADE DE PARCELAS</label>
                <input type="number" v-model.number="formCreate.num_parcelas" class="custom-input" @input="generateInstallments" min="1" />
              </div>
              <div class="field-group">
                <label>VENCIMENTO 1ª PARCELA</label>
                <input type="date" v-model="formCreate.primeiro_vencimento" class="custom-input" @change="generateInstallments" />
              </div>

              <div class="items-summary-section full-width">
                <div class="section-title">VALOR TOTAL: {{ formatCurrency(formCreate.valor_total) }}</div>
                <div class="items-list-box" v-if="formCreate.parcelas.length > 0">
                  <div v-for="(parc, idx) in formCreate.parcelas" :key="idx" class="os-item-row">
                    <div class="item-desc">
                      <span class="qty">{{ idx + 1 }}ª Parcela</span>
                      <span class="name">Vencimento: {{ formatDate(parc.data_vencimento) }}</span>
                    </div>
                    <div class="item-val">{{ formatCurrency(parc.valor) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <div class="footer-actions-right">
              <button class="btn-sec" @click="closeCreateModal">CANCELAR</button>
              <button class="btn-pri" @click="savePromissoria" :disabled="saving || !formCreate.cliente_id || !formCreate.produto_id">
                {{ saving ? 'SALVANDO...' : (isEditing ? 'SALVAR ALTERAÇÕES' : 'CADASTRAR PROMISSÓRIA') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <transition name="modal">
      <div v-if="showDetailsModal && selectedPromissoria" class="modal-overlay" @click.self="closeDetailsModal">
        <div class="modal-card details-modal">
          <div class="modal-header">
            <div class="header-title">
              <h3>Detalhes da Promissória #{{ selectedPromissoria.id }}</h3>
            </div>
            <button class="close-x" @click="closeDetailsModal">×</button>
          </div>
          
          <div class="modal-body scrollable">
            <div class="details-header-box">
              <h2 class="dh-client">{{ getClientName(selectedPromissoria.cliente_id) }}</h2>
              <p class="dh-product">{{ getProductName(selectedPromissoria.produto_id) }}</p>
              
              <div class="dh-finances">
                <div class="fin-box">
                  <span>TOTAL</span>
                  <strong class="text-total">{{ formatCurrency(selectedPromissoria.valor_total) }}</strong>
                </div>
                <div class="fin-box">
                  <span>PAGO</span>
                  <strong class="text-paid">{{ formatCurrency(getPaidValue(selectedPromissoria)) }}</strong>
                </div>
                <div class="fin-box">
                  <span>RESTANTE</span>
                  <strong class="text-remaining">{{ formatCurrency(getRemainingValue(selectedPromissoria)) }}</strong>
                </div>
              </div>
            </div>

            <div class="installments-section">
              <div class="section-title">PARCELAS</div>
              <div class="installments-list">
                <div 
                  v-for="(parcela, idx) in decoratedInstallments" 
                  :key="parcela.id || idx" 
                  class="installment-row"
                  :class="parcela.statusColor"
                >
                  <div class="inst-info">
                    <span class="inst-number">{{ idx + 1 }}ª Parcela</span>
                    <span class="inst-date">{{ formatDate(parcela.data_vencimento) }}</span>
                  </div>
                  <div class="inst-value">{{ formatCurrency(parcela.valor) }}</div>
                  <div class="inst-action">
                    <button 
                      v-if="parcela.status !== 'pago'" 
                      class="btn-pay" 
                      @click="markAsPaid(parcela)"
                    >
                      BAIXAR
                    </button>
                    <span v-else class="badge-paid">PAGO</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer footer-space-between">
            <button class="btn-danger" @click="deletePromissoria">EXCLUIR</button>
            <div class="footer-actions-right">
              <button class="btn-sec" @click="closeDetailsModal">FECHAR</button>
              <button class="btn-pri" @click="openEditModal">EDITAR</button>
            </div>
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
import { ref, computed, onMounted, reactive } from 'vue';
import { api } from '../services/api';

const promissorias = ref([]);
const dbClients = ref([]);
const dbProducts = ref([]);

const showCreateModal = ref(false);
const showDetailsModal = ref(false);
const isEditing = ref(false);
const saving = ref(false);
const selectedPromissoria = ref(null);

const formCreate = ref({
  id: null,
  cliente_id: '',
  produto_id: '',
  valor_unitario: 0,
  quantidade: 1,
  valor_total: 0,
  num_parcelas: 1,
  primeiro_vencimento: '',
  parcelas: []
});

const notify = reactive({ show: false, title: '', message: '', type: 'success' });

const triggerNotify = (title, message, type = 'success') => {
  notify.title = title; notify.message = message; notify.type = type; notify.show = true;
};

const loadData = async () => {
  try {
    const [resClients, resProducts, resPromissorias] = await Promise.all([
      api.get('/clientes'),
      api.get('/produtos'),
      api.get('/promissorias').catch(() => []) 
    ]);
    dbClients.value = resClients;
    dbProducts.value = resProducts;

    if (Array.isArray(resPromissorias)) {
      resPromissorias.forEach(prom => {
        if (Array.isArray(prom.parcelas)) {
          prom.parcelas.sort((a, b) => {
            if (a.id && b.id) return a.id - b.id;
            return a.data_vencimento.localeCompare(b.data_vencimento);
          });
        }
      });
    }

    promissorias.value = resPromissorias;
  } catch (e) {
    triggerNotify('Erro de Conexão', 'Não foi possível carregar os dados.', 'error');
  }
};

onMounted(() => {
  loadData();
});

const getClientName = (id) => {
  const c = dbClients.value.find(c => c.id === id);
  return c ? c.nome : 'Cliente não encontrado';
};

const getProductName = (id) => {
  const p = dbProducts.value.find(p => p.id === id);
  return p ? p.nome : 'Produto não encontrado';
};

const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);

const formatDate = (dateString) => {
  if (!dateString) return '';
  const [year, month, day] = dateString.split('-');
  return `${day}/${month}/${year}`;
};

const openCreateModal = () => {
  isEditing.value = false;
  const today = new Date().toISOString().split('T')[0];
  formCreate.value = {
    id: null,
    cliente_id: '',
    produto_id: '',
    valor_unitario: 0,
    quantidade: 1,
    valor_total: 0,
    num_parcelas: 1,
    primeiro_vencimento: today,
    parcelas: []
  };
  showCreateModal.value = true;
};

const openEditModal = () => {
  isEditing.value = true;
  const promCopy = JSON.parse(JSON.stringify(selectedPromissoria.value));
  
  if (Array.isArray(promCopy.parcelas)) {
    promCopy.parcelas.sort((a, b) => {
      if (a.id && b.id) return a.id - b.id;
      return a.data_vencimento.localeCompare(b.data_vencimento);
    });
  }
  
  formCreate.value = promCopy;
  showDetailsModal.value = false;
  showCreateModal.value = true;
};

const closeCreateModal = () => {
  showCreateModal.value = false;
};

const openDetailsModal = (promissoria) => {
  selectedPromissoria.value = JSON.parse(JSON.stringify(promissoria));
  showDetailsModal.value = true;
};

const closeDetailsModal = () => {
  showDetailsModal.value = false;
  selectedPromissoria.value = null;
};

const updateProductValue = () => {
  const p = dbProducts.value.find(prod => prod.id === formCreate.value.produto_id);
  if (p) {
    formCreate.value.valor_unitario = p.preco_venda || p.valor || 0;
    calculateTotal();
  }
};

const calculateTotal = () => {
  formCreate.value.valor_total = formCreate.value.valor_unitario * formCreate.value.quantidade;
  generateInstallments();
};

const generateInstallments = () => {
  const { valor_total, num_parcelas, primeiro_vencimento } = formCreate.value;
  if (!valor_total || !num_parcelas || !primeiro_vencimento || num_parcelas < 1) {
    formCreate.value.parcelas = [];
    return;
  }

  const parcelas = [];
  const valorParcela = valor_total / num_parcelas;
  let currentDate = new Date(primeiro_vencimento + 'T12:00:00'); 

  for (let i = 0; i < num_parcelas; i++) {
    const dataVencimento = new Date(currentDate);
    parcelas.push({
      valor: valorParcela,
      data_vencimento: dataVencimento.toISOString().split('T')[0],
      status: 'pendente'
    });
    currentDate.setMonth(currentDate.getMonth() + 1);
  }
  formCreate.value.parcelas = parcelas;
};

const savePromissoria = async () => {
  saving.value = true;
  try {
    const payload = { ...formCreate.value };
    payload.parcelas = payload.parcelas.map(p => ({
      valor: p.valor,
      data_vencimento: p.data_vencimento,
      status: p.status
    }));

    if (isEditing.value) {
      await api.put(`/promissorias/${payload.id}`, payload);
      triggerNotify('Sucesso', 'Promissória atualizada com sucesso.', 'success');
    } else {
      await api.post('/promissorias', payload);
      triggerNotify('Sucesso', 'Promissória cadastrada com sucesso.', 'success');
    }
    
    await loadData();
    closeCreateModal();
  } catch (e) {
    triggerNotify('Erro ao Salvar', e.message || 'Falha na comunicação com o servidor', 'error');
  } finally {
    saving.value = false;
  }
};

const deletePromissoria = async () => {
  if (!confirm("Tem certeza que deseja excluir esta promissória e todas as suas parcelas?")) return;
  
  try {
    await api.delete(`/promissorias/${selectedPromissoria.value.id}`);
    await loadData();
    closeDetailsModal();
    triggerNotify('Sucesso', 'Promissória excluída com sucesso.', 'success');
  } catch (e) {
    triggerNotify('Erro', 'Não foi possível excluir a promissória.', 'error');
  }
};

const getPaidValue = (promissoria) => {
  if (!promissoria || !promissoria.parcelas) return 0;
  return promissoria.parcelas.filter(p => p.status === 'pago').reduce((acc, p) => acc + p.valor, 0);
};

const getRemainingValue = (promissoria) => {
  if (!promissoria || !promissoria.parcelas) return 0;
  return promissoria.valor_total - getPaidValue(promissoria);
};

const getProgress = (promissoria) => {
  if (!promissoria || promissoria.valor_total === 0) return 0;
  return (getPaidValue(promissoria) / promissoria.valor_total) * 100;
};

const decoratedInstallments = computed(() => {
  if (!selectedPromissoria.value || !selectedPromissoria.value.parcelas) return [];
  
  const todayStr = new Date().toISOString().split('T')[0];
  let foundProxima = false;

  const sortedParcelas = [...selectedPromissoria.value.parcelas].sort((a, b) => {
    if (a.id && b.id) return a.id - b.id;
    return a.data_vencimento.localeCompare(b.data_vencimento);
  });

  return sortedParcelas.map(p => {
    let statusColor = '';

    if (p.status === 'pago') {
      statusColor = 'status-paga';
    } else if (p.data_vencimento < todayStr) {
      statusColor = 'status-vencida';
    } else {
      if (!foundProxima) {
        statusColor = 'status-proxima';
        foundProxima = true;
      } else {
        statusColor = 'status-futura';
      }
    }

    return { ...p, statusColor };
  });
});

const markAsPaid = async (parcela) => {
  try {
    const originalStatus = parcela.status;
    parcela.status = 'pago';
    
    await api.patch(`/promissorias/parcelas/${parcela.id}`, { status: 'pago' });
    
    const index = promissorias.value.findIndex(p => p.id === selectedPromissoria.value.id);
    if (index !== -1) {
      const pIndex = promissorias.value[index].parcelas.findIndex(x => x.id === parcela.id);
      if (pIndex !== -1) {
        promissorias.value[index].parcelas[pIndex].status = 'pago';
      }
    }
    triggerNotify('Sucesso', 'Parcela baixada com sucesso.', 'success');
  } catch (e) {
    parcela.status = originalStatus;
    triggerNotify('Erro', 'Não foi possível baixar a parcela.', 'error');
  }
};
</script>

<style scoped>
.board-container { padding: 24px; background: #f8fafc; min-height: 100vh; }
.board-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; gap: 20px; flex-wrap: wrap; }
.header-info h1 { font-size: 1.5rem; font-weight: 900; color: #1e293b; margin: 0; }
.header-info p { color: #64748b; font-size: 0.9rem; margin-top: 4px; }
.btn-primary-action { background: #56a6c1; color: #fff; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; box-shadow: 0 10px 15px -3px rgba(86,166,193,0.3); }

.empty-state { text-align: center; padding: 40px; color: #94a3b8; font-weight: 600; background: #fff; border-radius: 16px; border: 1px dashed #cbd5e1; }

.promissorias-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.client-card { background: #fff; border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); cursor: pointer; border: 1px solid #f1f5f9; transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s; }
.client-card:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #56a6c1; }

.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.client-name { font-size: 1.1rem; font-weight: 800; color: #1e293b; margin: 0; }
.card-id { font-size: 0.75rem; font-weight: 800; color: #cbd5e1; }

.card-body { margin-top: 10px; }
.product-name { font-size: 0.85rem; color: #64748b; margin-bottom: 16px; font-weight: 600; }

.financial-summary { display: flex; justify-content: space-between; margin-bottom: 12px; }
.summary-item { display: flex; flex-direction: column; gap: 4px; }
.summary-item .label { font-size: 0.7rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; }
.summary-item .value { font-size: 1rem; font-weight: 900; }
.value.total { color: #1e293b; }
.value.remaining { color: #ef4444; }

.progress-bar-container { width: 100%; height: 6px; background: #f1f5f9; border-radius: 4px; overflow: hidden; }
.progress-bar { height: 100%; background: #2ecc71; transition: width 0.3s ease; }

.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal-card { background: #fff; width: 100%; max-width: 600px; border-radius: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); display: flex; flex-direction: column; max-height: 95vh; }
.modal-header { padding: 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.2rem; color: #1e293b; font-weight: 800; }
.close-x { background: transparent; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
.modal-body { padding: 24px; overflow-y: auto; flex: 1; }
.modal-footer { padding: 20px 24px; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; }
.footer-space-between { justify-content: space-between; }
.footer-actions-right { display: flex; gap: 12px; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.field-group { display: flex; flex-direction: column; gap: 8px; }
.full-width { grid-column: span 2; }
.field-group label { font-size: 0.7rem; font-weight: 800; color: #64748b; }
.custom-input { background: #f8fafc; border: 1.5px solid #e2e8f0; padding: 12px; border-radius: 12px; font-size: 0.9rem; outline: none; transition: 0.2s; color: #1e293b; }
.custom-input:focus { border-color: #56a6c1; background: #fff; box-shadow: 0 0 0 4px rgba(86,166,193,0.1); }

.items-summary-section { margin-top: 10px; background: #f8fafc; padding: 20px; border-radius: 16px; border: 1px solid #e2e8f0; }
.section-title { font-size: 0.8rem; font-weight: 900; color: #475569; margin-bottom: 15px; letter-spacing: 0.5px; }
.os-item-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
.item-desc { display: flex; gap: 10px; font-size: 0.9rem; }
.qty { color: #56a6c1; font-weight: 900; }
.name { color: #1e293b; font-weight: 600; }
.item-val { font-weight: 800; color: #64748b; font-size: 0.9rem; }

.btn-pri { background: #1e293b; color: #fff; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.2s; }
.btn-pri:hover { background: #0f172a; }
.btn-pri:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-sec { background: transparent; color: #94a3b8; border: none; font-weight: 700; cursor: pointer; padding: 12px; }
.btn-danger { background: #fee2e2; color: #ef4444; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.2s; }
.btn-danger:hover { background: #fca5a5; }

.details-modal { max-width: 650px; }
.details-header-box { background: #f8fafc; padding: 24px; border-radius: 16px; margin-bottom: 24px; border: 1px solid #e2e8f0; }
.dh-client { font-size: 1.3rem; font-weight: 900; color: #1e293b; margin: 0 0 4px 0; }
.dh-product { display: inline-block; background: #f1f5f9; color: #64748b; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; margin: 0 0 20px 0; border: 1px solid #e2e8f0; }

.dh-finances { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; border-top: 1px dashed #cbd5e1; padding-top: 16px; }
.fin-box { display: flex; flex-direction: column; gap: 4px; }
.fin-box span { font-size: 0.7rem; font-weight: 800; color: #94a3b8; }
.fin-box strong { font-size: 1.2rem; font-weight: 900; }
.text-total { color: #1e293b; }
.text-paid { color: #2ecc71; }
.text-remaining { color: #ef4444; }

.installments-section { margin-top: 20px; }
.installments-list { display: flex; flex-direction: column; gap: 10px; }

.installment-row { display: flex; align-items: center; justify-content: space-between; padding: 16px; border-radius: 12px; border-left: 6px solid; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

.status-vencida { border-left-color: #ef4444; background: #fef2f2; }
.status-vencida .inst-date { color: #ef4444; font-weight: 800; }

.status-proxima { border-left-color: #f59e0b; background: #fffbeb; }
.status-proxima .inst-date { color: #d97706; font-weight: 800; }

.status-futura { border-left-color: #94a3b8; background: #f8fafc; }
.status-futura .inst-date { color: #94a3b8; }

.status-paga { border-left-color: #2ecc71; background: #f0fdf4; }
.status-paga .inst-date { color: #16a34a; text-decoration: line-through; }
.status-paga .inst-value { color: #16a34a; }

.inst-info { display: flex; flex-direction: column; gap: 4px; }
.inst-number { font-size: 0.9rem; font-weight: 800; color: #1e293b; }
.inst-date { font-size: 0.8rem; }
.inst-value { font-size: 1.1rem; font-weight: 900; color: #1e293b; flex: 1; text-align: right; padding-right: 20px; }

.btn-pay { background: #1e293b; color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 800; font-size: 0.75rem; cursor: pointer; transition: 0.2s; }
.btn-pay:hover { background: #0f172a; }
.badge-paid { background: #dcfce7; color: #16a34a; padding: 6px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 900; }

.custom-alert-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); z-index: 2000; display: flex; align-items: center; justify-content: center; }
.alert-box { background: #fff; padding: 32px; border-radius: 24px; max-width: 400px; width: 90%; text-align: center; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.alert-icon { width: 50px; height: 50px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold; }
.success .alert-icon { background: #dcfce7; color: #16a34a; }
.error .alert-icon { background: #fee2e2; color: #ef4444; }
.alert-content h4 { font-size: 1.2rem; color: #1e293b; margin-bottom: 10px; }
.alert-content p { color: #64748b; margin-bottom: 24px; line-height: 1.5; }
.btn-close-alert { width: 100%; background: #1e293b; color: #fff; border: none; padding: 12px; border-radius: 12px; font-weight: 800; cursor: pointer; }

@media (max-width: 768px) {
  .dh-finances { grid-template-columns: 1fr; }
  .installment-row { flex-direction: column; align-items: flex-start; gap: 12px; }
  .inst-value { text-align: left; padding-right: 0; width: 100%; }
  .inst-action { width: 100%; }
  .btn-pay { width: 100%; }
  .footer-space-between { flex-direction: column-reverse; gap: 12px; }
  .footer-actions-right { width: 100%; justify-content: space-between; gap: 8px; }
  .btn-danger, .btn-sec, .btn-pri { flex: 1; text-align: center; }
}
</style>