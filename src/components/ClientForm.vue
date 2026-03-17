<template>
  <div class="view-container">
    <header class="view-header">
      <div>
        <h2>GESTÃO DE CLIENTES</h2>
        <p>Controle centralizado de parceiros e clientes</p>
      </div>
      <button class="btn-main" @click="showNewForm">+ NOVO CLIENTE</button>
    </header>

    <div class="layout-grid">
      <section class="form-section">
        <div class="card-glass" :class="{ empty: !form }">
          <div v-if="form" class="form-content">
            <h3 class="card-label">{{ form.id ? 'EDITAR DADOS' : 'CADASTRO RÁPIDO' }}</h3>
            <form @submit.prevent="handleSubmit" class="modern-grid-form">
              <div class="row">
                <div class="field">
                  <label>TIPO</label>
                  <select v-model="form.tipo_pessoa" class="m-input">
                    <option value="F">Pessoa Física</option>
                    <option value="J">Pessoa Jurídica</option>
                  </select>
                </div>
                <div class="field grow">
                  <label>NOME COMPLETO / RAZÃO</label>
                  <input type="text" v-model="form.nome" class="m-input" placeholder="Ex: João Silva" required />
                </div>
              </div>

              <div class="row">
                <div class="field">
                  <label>DOCUMENTO</label>
                  <input type="text" v-model="form.documento" class="m-input" placeholder="CPF ou CNPJ" />
                </div>
                <div class="field">
                  <label>INSC. ESTADUAL</label>
                  <input type="text" v-model="form.inscricao_estadual" class="m-input" placeholder="Opcional" />
                </div>
              </div>

              <div class="row">
                <div class="field">
                  <label>TELEFONE</label>
                  <input type="text" v-model="form.telefone" class="m-input" placeholder="(00) 00000-0000" />
                </div>
                <div class="field grow">
                  <label>E-MAIL</label>
                  <input type="email" v-model="form.email" class="m-input" placeholder="contato@email.com" />
                </div>
              </div>

              <div class="row">
                <div class="field">
                  <label>CEP</label>
                  <input type="text" v-model="form.cep" class="m-input" placeholder="00000-000" />
                </div>
                <div class="field grow">
                  <label>ENDEREÇO</label>
                  <input type="text" v-model="form.endereco" class="m-input" placeholder="Rua, Av..." />
                </div>
              </div>

              <div class="row multi">
                <div class="field mini">
                  <label>Nº</label>
                  <input type="text" v-model="form.numero" class="m-input" />
                </div>
                <div class="field">
                  <label>BAIRRO</label>
                  <input type="text" v-model="form.bairro" class="m-input" />
                </div>
                <div class="field">
                  <label>CIDADE</label>
                  <input type="text" v-model="form.municipio" class="m-input" />
                </div>
                <div class="field mini">
                  <label>UF</label>
                  <input type="text" v-model="form.uf" class="m-input" maxlength="2" />
                </div>
              </div>

              <div class="form-actions">
                <button type="button" class="btn-text" @click="cancelForm">DESCARTAR</button>
                <button type="submit" class="btn-save">SALVAR CLIENTE</button>
              </div>
            </form>
          </div>
          <div v-else class="empty-placeholder">
            <div class="icon">👤</div>
            <h4>Nenhum cliente selecionado</h4>
            <p>Escolha um cliente na lista ao lado ou crie um novo registro.</p>
          </div>
        </div>
      </section>

      <section class="list-section">
        <div class="list-card">
          <div class="list-header">
            <h4>LISTAGEM</h4>
            <span class="count">{{ clientes.length }}</span>
          </div>
          <div class="scroll-area">
            <div v-for="cliente in clientes" :key="cliente.id" class="client-item" @click="editClient(cliente)">
              <div class="client-info">
                <strong>{{ cliente.nome }}</strong>
                <small>{{ cliente.documento }} • {{ cliente.municipio }}/{{ cliente.uf }}</small>
              </div>
              <button class="btn-del-item" @click.stop="deleteClient(cliente.id)">✕</button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../services/api';

const clientes = ref([]);
const form = ref(null);

const loadClientes = async () => {
  try {
    clientes.value = await api.get('/clientes');
  } catch (e) {
    console.error("Erro ao carregar lista");
  }
};

onMounted(loadClientes);

const showNewForm = () => { 
  form.value = { 
    id: null, 
    nome: '', 
    documento: '', 
    telefone: '', 
    endereco: '',
    tipo_pessoa: 'F',
    inscricao_estadual: '',
    email: '',
    municipio: '',
    cep: '',
    numero: '',
    bairro: '',
    uf: ''
  }; 
};

const cancelForm = () => { form.value = null; };
const editClient = (cliente) => { form.value = { ...cliente }; };

const handleSubmit = async () => {
  try {
    const payload = { ...form.value };
    
    if (!payload.id) {
      delete payload.id;
    }

    if (form.value.id) {
      await api.put(`/clientes/${form.value.id}`, payload);
    } else {
      await api.post('/clientes', payload);
    }
    
    await loadClientes();
    form.value = null;
  } catch (e) {
    alert("Erro ao salvar: Verifique a conexão com o banco");
  }
};

const deleteClient = async (id) => {
  if (confirm('Deseja excluir este cliente?')) {
    try {
      await api.delete(`/clientes/${id}`);
      await loadClientes();
      if (form.value && form.value.id === id) form.value = null;
    } catch (e) {
      alert(e.message);
    }
  }
};
</script>

<style scoped>
.view-container { padding: 32px; background: #f8fafc; min-height: 100vh; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; flex-wrap: wrap; gap: 20px; }
.view-header h2 { font-size: 1.5rem; font-weight: 900; color: #1e293b; margin: 0; }
.view-header p { color: #64748b; font-size: 0.9rem; margin-top: 4px; }
.btn-main { background: #56a6c1; color: #fff; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; box-shadow: 0 4px 12px rgba(86, 166, 193, 0.25); }

.layout-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 32px; }
.card-glass { background: #fff; border-radius: 20px; padding: 32px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border: 1px solid #edf2f7; transition: 0.3s; }
.card-glass.empty { display: flex; align-items: center; justify-content: center; background: #f1f5f9; border-style: dashed; }
.card-label { font-size: 0.75rem; font-weight: 800; color: #56a6c1; margin-bottom: 24px; letter-spacing: 1px; }

.modern-grid-form { display: flex; flex-direction: column; gap: 20px; }
.row { display: flex; gap: 16px; flex-wrap: wrap; }
.field { display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 200px; }
.field.grow { flex: 2; }
.field.mini { flex: 0.3; min-width: 60px; }
label { font-size: 0.65rem; font-weight: 800; color: #94a3b8; }
.m-input { background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 10px; font-size: 0.9rem; color: #1e293b; outline: none; transition: 0.2s; }
.m-input:focus { border-color: #56a6c1; background: #fff; box-shadow: 0 0 0 4px rgba(86, 166, 193, 0.1); }

.form-actions { display: flex; justify-content: flex-end; gap: 16px; margin-top: 20px; border-top: 1px solid #f1f5f9; padding-top: 24px; }
.btn-text { background: transparent; border: none; color: #94a3b8; font-weight: 700; cursor: pointer; }
.btn-save { background: #1e293b; color: #fff; border: none; padding: 12px 32px; border-radius: 10px; font-weight: 800; cursor: pointer; }

.list-card { background: #fff; border-radius: 20px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #edf2f7; }
.list-header { padding: 20px 24px; background: #f8fafc; border-bottom: 1px solid #edf2f7; display: flex; justify-content: space-between; align-items: center; }
.list-header h4 { font-size: 0.75rem; font-weight: 800; color: #475569; }
.count { background: #e2e8f0; color: #64748b; font-size: 0.7rem; padding: 2px 8px; border-radius: 6px; font-weight: 800; }
.scroll-area { max-height: 600px; overflow-y: auto; }
.client-item { padding: 16px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: 0.2s; }
.client-item:hover { background: #f8fafc; }
.client-info strong { display: block; font-size: 0.95rem; color: #1e293b; }
.client-info small { color: #94a3b8; font-size: 0.75rem; }
.btn-del-item { background: transparent; border: none; color: #cbd5e1; cursor: pointer; font-size: 1rem; }
.btn-del-item:hover { color: #ef4444; }

@media (max-width: 1024px) {
  .layout-grid { grid-template-columns: 1fr; }
  .view-container { padding: 20px; }
}
</style>