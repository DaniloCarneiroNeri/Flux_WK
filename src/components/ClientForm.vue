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
              <input type="text" v-model="form.nome" class="modern-input" required />
            </div>
            <div class="form-row-mobile">
              <div class="form-group">
                <label>DOCUMENTO (CPF/CNPJ)</label>
                <input type="text" v-model="form.documento" class="modern-input" />
              </div>
              <div class="form-group">
                <label>TELEFONE</label>
                <input type="text" v-model="form.telefone" class="modern-input" />
              </div>
            </div>
            <div class="form-group">
              <label>ENDEREÇO</label>
              <input type="text" v-model="form.endereco" class="modern-input" />
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
          <table class="modern-table">
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
  if (form.value && form.value.id === id) form.value = null;
};
</script>

<style scoped>
.form-view-container { padding: 30px; background: #f4f7f6; min-height: 100%; }
.form-header { margin-bottom: 25px; border-bottom: 1px solid #e0e6ed; padding-bottom: 15px; }
.form-header h2 { color: #2d3436; font-size: 1.5rem; font-weight: 900; }
.form-header p { color: #95a5a6; font-size: 0.9rem; }
.responsive-layout { display: flex; gap: 30px; }
.main-card { flex: 1; border-left: 5px solid #56a6c1; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.list-card { flex: 1.5; background: #fff; padding: 0; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); overflow: hidden; }
.form-title { font-size: 0.8rem; color: #56a6c1; font-weight: 800; margin-bottom: 25px; letter-spacing: 1px; }
.flux-form { display: flex; flex-direction: column; gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-row-mobile { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.form-actions-mobile { display: flex; gap: 12px; margin-top: 15px; }
label { font-size: 0.7rem; color: #7f8c8d; font-weight: 700; text-transform: uppercase; }
.modern-input { background: #f8f9fa; border: 1px solid #e0e6ed; color: #333; padding: 14px; border-radius: 6px; outline: none; }
.modern-input:focus { border-color: #56a6c1; background: #fff; box-shadow: 0 0 0 3px rgba(86,166,193,0.1); }
.btn-primary { flex: 1; background: #56a6c1; color: #fff; border: none; padding: 14px; font-weight: 900; border-radius: 6px; cursor: pointer; box-shadow: 0 4px 10px rgba(86,166,193,0.2); }
.btn-cancel { flex: 1; background: #f1f2f6; border: none; color: #7f8c8d; padding: 14px; border-radius: 6px; font-weight: 700; }
.list-header { display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #f8f9fa; border-bottom: 1px solid #f0f3f7; }
.list-header h4 { font-size: 0.7rem; color: #444; font-weight: 800; letter-spacing: 1px; }
.btn-new-client { background: #56a6c1; color: #fff; border: none; padding: 8px 16px; font-weight: 700; border-radius: 6px; cursor: pointer; font-size: 0.75rem; }
.table-container { flex: 1; overflow-y: auto; }
.modern-table { width: 100%; border-collapse: collapse; }
.modern-table th { color: #95a5a6; padding: 15px 20px; text-align: left; font-size: 0.7rem; text-transform: uppercase; background: #fcfdfe; }
.modern-table td { padding: 15px 20px; border-bottom: 1px solid #f0f3f7; }
.client-cell strong { color: #2d3436; font-size: 0.95rem; display: block; }
.client-cell span { color: #95a5a6; font-size: 0.8rem; }
.text-right { text-align: right; }
.btn-circle { width: 36px; height: 36px; border-radius: 50%; border: 1px solid #f0f3f7; cursor: pointer; margin-left: 8px; background: #fff; transition: all 0.2s; }
.edit { color: #56a6c1; }
.edit:hover { background: #56a6c1; color: #fff; }
.del { color: #e74c3c; }
.del:hover { background: #e74c3c; color: #fff; }
.placeholder-form { text-align: center; color: #95a5a6; margin: auto; padding: 40px; }
.icon-placeholder { font-size: 4rem; opacity: 0.2; }
@media (max-width: 900px) { .responsive-layout { flex-direction: column; } .form-row-mobile { grid-template-columns: 1fr; } }
</style>