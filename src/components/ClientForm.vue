<template>
  <div class="form-view-container">
    <div class="form-header">
      <h2>GESTÃO DE CLIENTES</h2>
      <p>Base de dados de clientes e fornecedores</p>
    </div>

    <div class="responsive-layout">
      <div class="form-card main-card">
        <div v-if="form" class="form-wrapper">
          <h3 class="form-title">{{ form.id ? 'EDITAR CLIENTE' : 'NOVO CLIENTE' }}</h3>
          <form @submit.prevent="handleSubmit" class="flux-form">
            <div class="form-group">
              <label>NOME COMPLETO / RAZÃO SOCIAL</label>
              <input type="text" v-model="form.nome" class="dark-input" required />
            </div>
            <div class="form-row-mobile">
              <div class="form-group">
                <label>DOCUMENTO (CPF/CNPJ)</label>
                <input type="text" v-model="form.documento" class="dark-input" />
              </div>
              <div class="form-group">
                <label>TELEFONE</label>
                <input type="text" v-model="form.telefone" class="dark-input" />
              </div>
            </div>
            <div class="form-group">
              <label>ENDEREÇO</label>
              <input type="text" v-model="form.endereco" class="dark-input" />
            </div>
            <div class="form-actions-mobile">
              <button type="button" class="btn-cancel" @click="cancelForm">CANCELAR</button>
              <button type="submit" class="btn-primary">{{ form.id ? 'ATUALIZAR' : 'SALVAR' }}</button>
            </div>
          </form>
        </div>
        <div v-else class="placeholder-form">
          <div class="icon-placeholder">👤</div>
          <h3>Nenhum cliente selecionado</h3>
          <p>Selecione um cliente na lista para editar ou adicione um novo.</p>
        </div>
      </div>

      <div class="form-card list-card">
        <div class="list-header">
          <h4>CLIENTES CADASTRADOS</h4>
          <button class="btn-new-client" @click="showNewForm">+ NOVO CLIENTE</button>
        </div>
        <div class="table-container">
          <table class="dark-table">
            <thead>
              <tr><th>CLIENTE</th><th class="text-right">AÇÕES</th></tr>
            </thead>
            <tbody>
              <tr v-for="cliente in clientes" :key="cliente.id">
                <td class="client-cell">
                  <strong>{{ cliente.nome }}</strong>
                  <span>{{ cliente.documento }}</span>
                </td>
                <td class="text-right">
                  <button class="btn-circle edit" @click="editClient(cliente)">✎</button>
                  <button class="btn-circle del" @click="deleteClient(cliente.id)">✕</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import demoData from '../data/demoData.json';

const clientes = ref(demoData.clientes);
const form = ref(null);

const showNewForm = () => { form.value = { id: null, nome: '', documento: '', telefone: '', endereco: '' }; };
const cancelForm = () => { form.value = null; };
const editClient = (cliente) => { form.value = { ...cliente }; };

const handleSubmit = () => {
  if (form.value.id) {
    const index = clientes.value.findIndex(c => c.id === form.value.id);
    if (index !== -1) clientes.value[index] = { ...form.value };
  } else {
    clientes.value.unshift({ ...form.value, id: Date.now() });
  }
  form.value = null;
};

const deleteClient = (id) => {
  clientes.value = clientes.value.filter(c => c.id !== id);
  if (form.value && form.value.id === id) {
    form.value = null;
  }
};
</script>

<style scoped>
.form-view-container { padding: 20px; background: #050505; min-height: 100%; }
.form-header { margin-bottom: 25px; border-bottom: 1px solid #1a1a1a; padding-bottom: 15px; }
.form-header h2 { color: #fff; font-size: 1.5rem; font-weight: 900; }
.form-header p { color: #666; font-size: 0.9rem; }
.responsive-layout { display: flex; gap: 20px; }
.main-card { flex: 1; border-left: 4px solid #40c4ff; background: #0a0a0a; padding: 20px; border-radius: 4px; display: flex; flex-direction: column; }
.list-card { flex: 1.5; background: #0a0a0a; padding: 0; border-radius: 4px; display: flex; flex-direction: column; overflow: hidden; }
.form-wrapper { width: 100%; }
.form-title { font-size: 0.8rem; color: #40c4ff; font-weight: 700; margin-bottom: 20px; letter-spacing: 1px; }
.flux-form { display: flex; flex-direction: column; gap: 15px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-row-mobile { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.form-actions-mobile { display: flex; gap: 10px; margin-top: 10px; }
label { font-size: 0.7rem; color: #666; font-weight: 600; text-transform: uppercase; }
.dark-input { background: #000; border: 1px solid #222; color: #fff; padding: 14px; border-radius: 4px; outline: none; }
.dark-input:focus { border-color: #40c4ff; }
.btn-primary { flex: 1; background: #40c4ff; color: #000; border: none; padding: 14px; font-weight: 900; border-radius: 4px; cursor: pointer; }
.btn-cancel { flex: 1; background: #1a1a1a; border: 1px solid #333; color: #888; padding: 14px; border-radius: 4px; }
.list-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #111; border-bottom: 1px solid #1a1a1a; }
.list-header h4 { font-size: 0.7rem; color: #555; font-weight: 800; letter-spacing: 1px; }
.btn-new-client { background: #40c4ff; color: #000; border: none; padding: 8px 12px; font-weight: 700; border-radius: 4px; cursor: pointer; font-size: 0.7rem; }
.table-container { flex: 1; overflow-y: auto; }
.dark-table { width: 100%; border-collapse: collapse; }
.dark-table thead tr { position: sticky; top: 0; background: #111; }
.dark-table th { color: #555; padding: 12px 20px; text-align: left; font-size: 0.7rem; text-transform: uppercase; }
.dark-table td { padding: 15px 20px; border-bottom: 1px solid #1a1a1a; }
.dark-table tr:last-child td { border-bottom: none; }
.client-cell { display: flex; flex-direction: column; }
.client-cell strong { color: #fff; font-size: 0.9rem; }
.client-cell span { color: #555; font-size: 0.75rem; margin-top: 2px; }
.text-right { text-align: right; }
.btn-circle { width: 34px; height: 34px; border-radius: 50%; border: 1px solid #222; cursor: pointer; margin-left: 8px; font-weight: bold; background: #111; transition: all 0.2s; }
.edit { color: #40c4ff; }
.edit:hover { background: #40c4ff; color: #000; }
.del { color: #c0392b; }
.del:hover { background: #c0392b; color: #fff; }
.placeholder-form { text-align: center; color: #444; margin: auto; }
.icon-placeholder { font-size: 3rem; line-height: 1; }
.placeholder-form h3 { color: #666; margin: 15px 0 5px 0; font-size: 1rem; }
.placeholder-form p { font-size: 0.8rem; max-width: 250px; margin: 0 auto; }
@media (max-width: 900px) { .responsive-layout { flex-direction: column; } .form-row-mobile { grid-template-columns: 1fr; } .list-card { margin-top: 20px; } }
</style>