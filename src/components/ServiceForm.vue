<template>
  <div class="form-view-container">
    <div class="form-header">
      <h2>ORDEM DE SERVIÇO</h2>
      <p>Detalhamento técnico e financeiro do serviço WK.</p>
    </div>

    <div class="form-card main-form-card">
      <div class="card-header-tabs">
        <h3>REGISTRO DA OS #{{ form.id ? form.id : 'NOVA' }}</h3>
        <div class="tabs-wrapper">
           </div>
      </div>
      
      <form @submit.prevent="saveService" class="flux-form">
        
        <div class="top-section-grid">
          <div class="client-selection-panel">
             <label>CLIENTE VINCULADO <span class="cyan-text">*</span></label>
             
             <div v-if="form.cliente_id" class="selected-client-card">
                <div class="client-info">
                  <span class="client-name">{{ clientes.find(c => c.id === form.cliente_id)?.nome }}</span>
                  <span class="client-details">ID: {{ form.cliente_id }}</span>
                </div>
                <button type="button" class="btn-change-client" @click="form.cliente_id = null">
                  TROCAR
                </button>
             </div>

             <div v-else class="client-search-box">
                <select v-model="form.cliente_id" class="dark-input select-client" required>
                  <option :value="null" disabled>SELECIONE UM CLIENTE DA BASE</option>
                  <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                    {{ cliente.nome }}
                  </option>
                </select>
                <div class="search-helper">Ou cadastre um novo cliente no menu lateral.</div>
             </div>
          </div>

          <div class="meta-data-panel">
             <div class="form-row-split">
                 <div class="form-group">
                    <label>DATA ABERTURA</label>
                    <input type="date" v-model="form.data_abertura" class="dark-input" required />
                 </div>
                 <div class="form-group">
                    <label>STATUS ATUAL</label>
                    <select v-model="form.status" class="dark-input status-select">
                      <option value="orcamento">ORÇAMENTO</option>
                      <option value="pendente">PENDENTE / EM ANDAMENTO</option>
                      <option value="concluido">CONCLUÍDO</option>
                      <option value="faturado">FATURADO</option>
                    </select>
                 </div>
             </div>
             <div class="form-group mt-3">
                  <label>FORMA DE PAGAMENTO</label>
                  <input type="text" v-model="form.forma_pagamento" class="dark-input" placeholder="Ex: PIX, Boleto 30 dias..." />
             </div>
          </div>
        </div>


        <div class="items-section">
          <div class="section-header">
            <h4>ITENS E MATERIAIS DA ORDEM</h4>
          </div>

          <div class="items-table-wrapper">
            <table class="dark-table items-table">
              <thead>
                <tr>
                  <th style="width: 50%">DESCRIÇÃO DO ITEM / SERVIÇO</th>
                  <th style="width: 15%">QTD.</th>
                  <th style="width: 20%">VALOR UNIT. (R$)</th>
                  <th style="width: 20%" class="text-right">SUBTOTAL</th>
                  <th style="width: 5%"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in form.itens_ordem" :key="index" class="item-row">
                  <td>
                    <input 
                      type="text" 
                      v-model="item.descricao_item" 
                      class="dark-input no-border" 
                      placeholder="Descreva o item ou serviço..." 
                      required
                    />
                  </td>
                  <td>
                    <input 
                      type="number" 
                      v-model.number="item.quantidade" 
                      class="dark-input no-border text-center" 
                      min="1" step="0.01" required
                    />
                  </td>
                  <td>
                    <input 
                      type="number" 
                      v-model.number="item.valor_unitario" 
                      class="dark-input no-border text-right" 
                      min="0" step="0.01" required
                    />
                  </td>
                  <td class="text-right subtotal-cell">
                    R$ {{ (item.quantidade * item.valor_unitario).toFixed(2) }}
                  </td>
                  <td class="text-center">
                     <button type="button" class="btn-icon delete-item" @click="removeItem(index)" v-if="form.itens_ordem.length > 1">
                       ✕
                     </button>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <button type="button" class="btn-add-item" @click="addItem">
              <span class="plus">+</span> ADICIONAR NOVO ITEM
            </button>
          </div>
        </div>

        <div class="footer-panel">
          <div class="totals-display">
             <span class="total-label">VALOR TOTAL DA ORDEM:</span>
             <span class="total-value">R$ {{ totalGeral.toFixed(2) }}</span>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="$emit('cancel')">DESCARTAR</button>
            <button type="submit" class="btn-primary">
              {{ form.id ? 'ATUALIZAR ORDEM' : 'GERAR ORDEM DE SERVIÇO' }}
            </button>
          </div>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
// (Mantendo a lógica original intacta)
import { ref, reactive, onMounted, computed } from 'vue';

const props = defineProps({
  serviceToEdit: { type: Object, default: null },
  preSelectedClient: { type: Object, default: null }
});

const emit = defineEmits(['cancel', 'save']);
const API_URL = import.meta.env.DEV ? 'http://localhost:8000' : '';

const clientes = ref([]);

const form = reactive({
  id: null,
  cliente_id: null,
  data_abertura: new Date().toISOString().split('T')[0],
  status: 'orcamento',
  forma_pagamento: '',
  itens_ordem: [
    { descricao_item: '', quantidade: 1, valor_unitario: 0.00 }
  ]
});

const totalGeral = computed(() => {
  return form.itens_ordem.reduce((total, item) => {
    return total + (item.quantidade * item.valor_unitario);
  }, 0);
});

onMounted(async () => {
  await fetchClientes();
  if (props.serviceToEdit) {
    loadServiceData(props.serviceToEdit);
  } else if (props.preSelectedClient) {
    form.cliente_id = props.preSelectedClient.id;
  }
});

const fetchClientes = async () => {
  try {
    const response = await fetch(`${API_URL}/clientes`);
    if (response.ok) clientes.value = await response.json();
  } catch (e) { console.error(e); }
};

const loadServiceData = (service) => {
  form.id = service.id;
  form.cliente_id = service.cliente_id;
  form.data_abertura = service.data_abertura;
  form.status = service.status;
  form.forma_pagamento = service.forma_pagamento;
  if (service.itens_ordem && service.itens_ordem.length > 0) {
    form.itens_ordem = service.itens_ordem.map(item => ({...item}));
  } else {
    form.itens_ordem = [{ descricao_item: '', quantidade: 1, valor_unitario: 0.00 }];
  }
};

const addItem = () => {
  form.itens_ordem.push({ descricao_item: '', quantidade: 1, valor_unitario: 0.00 });
};

const removeItem = (index) => {
  form.itens_ordem.splice(index, 1);
};

const saveService = async () => {
  const url = form.id ? `${API_URL}/servicos/${form.id}` : `${API_URL}/servicos`;
  const method = form.id ? 'PUT' : 'POST';
  
  try {
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });
    if (response.ok) emit('save');
  } catch (error) { console.error(error); }
};
</script>

<style scoped>
.form-view-container { padding: 30px; background: #050505; min-height: 100%; }
.form-header { margin-bottom: 30px; border-bottom: 1px solid #1a1a1a; padding-bottom: 20px; }
.form-header h2 { color: #ffffff; font-size: 1.5rem; letter-spacing: 3px; font-weight: 800; margin: 0; }
.form-header p { color: #888; font-size: 0.9rem; margin-top: 8px; letter-spacing: 1px; }

.main-form-card {
  background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 4px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3); overflow: hidden;
}
.card-header-tabs {
    background: #111; padding: 20px 25px; border-bottom: 1px solid #1a1a1a;
    display: flex; justify-content: space-between; align-items: center;
}
.card-header-tabs h3 { color: #fff; font-size: 1rem; font-weight: 700; letter-spacing: 2px; margin: 0; }
.cyan-text { color: #40c4ff; }

.flux-form { padding: 30px; display: flex; flex-direction: column; gap: 40px; }

/* Top Section Grid */
.top-section-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 30px; }
.client-selection-panel, .meta-data-panel { display: flex; flex-direction: column; gap: 15px; }

label { color: #666; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; }
.dark-input {
  background: #111; border: 1px solid #222; color: #fff; padding: 14px;
  border-radius: 3px; font-size: 0.95rem; outline: none; width: 100%;
  transition: all 0.3s;
}
.dark-input:focus { border-color: #40c4ff; background: #0e0e0e; }
.select-client { cursor: pointer; }

.selected-client-card {
    background: #151515; border: 1px solid #40c4ff; padding: 15px;
    border-radius: 3px; display: flex; justify-content: space-between; align-items: center;
}
.client-info { display: flex; flex-direction: column; }
.client-name { color: #fff; font-weight: 800; font-size: 1.1rem; }
.client-details { color: #40c4ff; font-size: 0.8rem; }
.btn-change-client {
    background: none; border: 1px solid #333; color: #888; padding: 8px 15px;
    border-radius: 3px; cursor: pointer; font-size: 0.75rem; font-weight: 800;
}
.btn-change-client:hover { border-color: #40c4ff; color: #40c4ff; }
.search-helper { font-size: 0.75rem; color: #555; margin-top: 5px; font-style: italic; }

.form-row-split { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.status-select { font-weight: bold; }
.mt-3 { margin-top: 15px; }

/* Items Section */
.items-section { border: 1px solid #1a1a1a; border-radius: 4px; overflow: hidden; }
.section-header { background: #111; padding: 15px 20px; border-bottom: 1px solid #1a1a1a; }
.section-header h4 { color: #888; font-size: 0.8rem; letter-spacing: 2px; margin: 0; }

.items-table-wrapper { background: #0a0a0a; }
.dark-table { width: 100%; border-collapse: collapse; color: #fff; text-align: left; }
.dark-table th {
  background: #151515; color: #666; font-size: 0.65rem; text-transform: uppercase;
  letter-spacing: 1px; padding: 12px 20px; border-bottom: 1px solid #222;
}
.dark-table td { padding: 5px 10px; border-bottom: 1px solid #1a1a1a; }
.item-row { background: #0a0a0a; transition: background 0.3s; }
.item-row:hover { background: #0f0f0f; }

.dark-input.no-border { border: none; background: transparent; padding: 15px 10px; }
.dark-input.no-border:focus { background: #111; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.subtotal-cell { font-weight: bold; color: #40c4ff; padding-right: 20px; }

.btn-icon.delete-item {
    background: none; border: none; color: #c0392b; font-size: 1.2rem;
    cursor: pointer; opacity: 0.5; transition: 0.3s;
}
.btn-icon.delete-item:hover { opacity: 1; transform: scale(1.1); }

.btn-add-item {
    width: 100%; background: #111; border: none; border-top: 1px solid #1a1a1a;
    color: #40c4ff; padding: 15px; font-weight: 800; letter-spacing: 1px;
    cursor: pointer; transition: 0.3s; text-align: center;
}
.btn-add-item:hover { background: #151515; color: #fff; }
.plus { margin-right: 10px; font-size: 1.2rem; }

/* Footer Panel */
.footer-panel {
    display: flex; justify-content: space-between; align-items: center;
    background: #111; padding: 30px; border-radius: 4px; border: 1px solid #222;
}
.totals-display { display: flex; flex-direction: column; align-items: flex-start; }
.total-label { color: #888; font-size: 0.8rem; letter-spacing: 2px; font-weight: 800; }
.total-value { color: #ffffff; font-size: 2.5rem; font-weight: 900; margin-top: 5px; }

.form-actions { display: flex; gap: 15px; }
.btn-primary, .btn-cancel {
  padding: 16px 30px; border-radius: 3px; font-weight: 800; font-size: 0.9rem;
  letter-spacing: 1px; cursor: pointer; border: none; transition: all 0.3s;
}
.btn-primary { background: #40c4ff; color: #000; }
.btn-primary:hover { background: #ffffff; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(64, 196, 255, 0.3); }
.btn-cancel { background: transparent; color: #888; border: 2px solid #333; }
.btn-cancel:hover { border-color: #fff; color: #fff; }

@media (max-width: 1100px) {
    .top-section-grid { grid-template-columns: 1fr; }
    .footer-panel { flex-direction: column; gap: 30px; align-items: stretch; text-align: center; }
    .totals-display { align-items: center; }
    .form-actions { justify-content: center; }
}
</style>