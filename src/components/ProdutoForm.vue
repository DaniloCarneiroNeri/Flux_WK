<template>
  <div class="board-container">
    <header class="board-header">
      <div class="header-info">
        <h1>PRODUTOS</h1>
      </div>
      <div class="header-controls">
        <button class="btn-primary-action" @click="openModal()">+ NOVO PRODUTO</button>
      </div>
    </header>

    <div class="content-area">
      <div class="table-view-wrapper">
        <div class="responsive-table">
          <table class="modern-grid">
            <thead>
              <tr>
                <th>CFOP</th>
                <th>DESCRIÇÃO</th>
                <th>UNIDADE</th>
                <th class="text-right">AÇÕES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="produto in produtos" :key="produto.id" class="row-hover">
                <td><strong>{{ produto.cfop }}</strong></td>
                <td>{{ produto.descricao }}</td>
                <td><span class="status-tag billed">{{ produto.unid }}</span></td>
                <td class="text-right">
                  <button class="btn-edit-small" @click="openModal(produto)" style="margin-right: 8px;">EDITAR</button>
                  <button class="btn-edit-small" style="background: #ef4444;" @click="deleteProduto(produto.id)">EXCLUIR</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="produtos.length === 0" style="padding: 20px; text-align: center; color: #64748b;">
            Nenhum produto cadastrado.
          </div>
        </div>
      </div>
    </div>

    <transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header">
            <div class="header-title">
              <h3>{{ isEditing ? 'Editar Produto' : 'Novo Produto' }}</h3>
            </div>
            <button class="close-x" @click="closeModal">×</button>
          </div>
          
          <div class="modal-body">
            <div class="form-grid">
              <div class="field-group">
                <label>CFOP</label>
                <input type="text" v-model="form.cfop" class="custom-input" />
              </div>
              <div class="field-group">
                <label>UNIDADE</label>
                <select v-model="form.unid" class="custom-input">
                  <option value="UN">UN</option>
                  <option value="MT²">MT²</option>
                </select>
              </div>
              <div class="field-group full-width">
                <label>DESCRIÇÃO</label>
                <input type="text" v-model="form.descricao" class="custom-input" />
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-sec" @click="closeModal">CANCELAR</button>
            <button class="btn-pri" @click="saveProduto" :disabled="saving">
              {{ saving ? 'SALVANDO...' : 'SALVAR' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../services/api';

const produtos = ref([]);
const showModal = ref(false);
const isEditing = ref(false);
const saving = ref(false);
const form = ref({ id: null, cfop: '', descricao: '', unid: 'UN' });

const loadData = async () => {
  try {
    produtos.value = await api.get('/produtos');
  } catch (e) {
    console.error(e);
  }
};

onMounted(loadData);

const openModal = (produto = null) => {
  if (produto) {
    isEditing.value = true;
    form.value = { ...produto };
  } else {
    isEditing.value = false;
    form.value = { id: null, cfop: '', descricao: '', unid: 'UN' };
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveProduto = async () => {
  saving.value = true;
  try {
    if (isEditing.value) {
      await api.put(`/produtos/${form.value.id}`, form.value);
    } else {
      await api.post('/produtos', form.value);
    }
    await loadData();
    closeModal();
  } catch (e) {
    console.error(e);
  } finally {
    saving.value = false;
  }
};

const deleteProduto = async (id) => {
  if (!confirm('Deseja realmente excluir este produto?')) return;
  try {
    await api.delete(`/produtos/${id}`);
    await loadData();
  } catch (e) {
    console.error(e);
  }
};
</script>

<style scoped>
.board-container { padding: 24px; background: #f8fafc; min-height: 100vh; }
.board-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; gap: 20px; flex-wrap: wrap; }
.header-info h1 { font-size: 1.5rem; font-weight: 900; color: #1e293b; margin: 0; }
.btn-primary-action { background: #56a6c1; color: #fff; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; box-shadow: 0 10px 15px -3px rgba(86,166,193,0.3); }
.table-view-wrapper { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #edf2f7; }
.modern-grid { width: 100%; border-collapse: collapse; }
.modern-grid th { text-align: left; padding: 16px; color: #94a3b8; font-size: 0.75rem; border-bottom: 1px solid #f1f5f9; text-transform: uppercase; font-weight: 800; }
.modern-grid td { padding: 16px; border-bottom: 1px solid #f8fafc; font-size: 0.9rem; color: #1e293b; }
.row-hover:hover { background-color: #f8fafc; }
.status-tag { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; }
.status-tag.billed { background: #f3e8ff; color: #9333ea; }
.btn-edit-small { background: #56a6c1; border: none; padding: 8px 16px; border-radius: 8px; color: #fff; font-weight: 800; cursor: pointer; font-size: 0.7rem; }
.text-right { text-align: right; }
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal-card { background: #fff; width: 100%; max-width: 650px; border-radius: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); display: flex; flex-direction: column; max-height: 95vh; }
.modal-header { padding: 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.modal-body { padding: 24px; overflow-y: auto; flex: 1; }
.modal-footer { padding: 20px 24px; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; align-items: center; gap: 12px; }
.close-x { background: transparent; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.field-group { display: flex; flex-direction: column; gap: 8px; }
.full-width { grid-column: span 2; }
.custom-input { background: #f8fafc; border: 1.5px solid #e2e8f0; padding: 12px; border-radius: 12px; font-size: 0.9rem; outline: none; transition: 0.2s; color: #1e293b; }
.custom-input:focus { border-color: #56a6c1; background: #fff; box-shadow: 0 0 0 4px rgba(86,166,193,0.1); }
.header-title { display: flex; align-items: center; gap: 12px; }
.btn-pri { background: #1e293b; color: #fff; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.2s; }
.btn-sec { background: transparent; color: #94a3b8; border: none; font-weight: 700; cursor: pointer; padding: 12px; }
label { font-size: 0.75rem; font-weight: 800; color: #94a3b8; }
</style>