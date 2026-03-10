<template>
  <div class="form-view-container">
    <div class="form-header">
      <h2>REGISTRAR DESPESA</h2>
      <p>Adicione uma nova saída no fluxo de caixa.</p>
    </div>
    <div class="form-card expense-card">
      <form @submit.prevent="save" class="flux-form">
        <div class="form-group">
          <label>DESCRIÇÃO DA DESPESA</label>
          <input type="text" v-model="form.descricao" class="modern-input" placeholder="Ex: Compra de material" required />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>VALOR (R$)</label>
            <input type="number" v-model.number="form.valor" class="modern-input expense-text" placeholder="0,00" step="0.01" required />
          </div>
          <div class="form-group">
            <label>DATA DE VENCIMENTO</label>
            <input type="date" v-model="form.vencimento" class="modern-input" required />
          </div>
        </div>
        <div class="form-actions-row">
          <button v-if="isEditing" type="button" class="btn-cancel-edit" @click="resetForm">CANCELAR</button>
          <button type="submit" class="btn-save-exp">
            {{ isEditing ? 'ATUALIZAR DESPESA' : 'REGISTRAR DESPESA' }}
          </button>
        </div>
      </form>
    </div>

    <div class="list-section">
      <div class="section-header">
        <h3>DESPESAS REGISTRADAS</h3>
      </div>
      <div class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>DESCRIÇÃO</th>
              <th>VENCIMENTO</th>
              <th>VALOR</th>
              <th>AÇÕES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="expense in expenses" :key="expense.id">
              <td>#{{ expense.id }}</td>
              <td>{{ expense.descricao }}</td>
              <td>{{ formatDate(expense.vencimento) }}</td>
              <td class="expense-text-table">{{ formatCurrency(expense.valor) }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-action edit" @click="editExpense(expense)" title="Editar">✎</button>
                  <button class="btn-action delete" @click="deleteExpense(expense.id)" title="Excluir">✕</button>
                </div>
              </td>
            </tr>
            <tr v-if="expenses.length === 0">
              <td colspan="5" class="empty-cell">Nenhuma despesa registrada.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../services/api';

const expenses = ref([]);
const isEditing = ref(false);
const editingId = ref(null);
const form = ref({ descricao: '', valor: null, categoria: 'Outros', data: new Date().toISOString().split('T')[0], fixa: false });

const loadExpenses = async () => {
  try {
    expenses.value = await api.get('/despesas');
  } catch (e) {
    console.error(e);
  }
};

onMounted(loadExpenses);

const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
const formatDate = (dateStr) => { if (!dateStr) return ''; const [year, month, day] = dateStr.split('T')[0].split('-'); return `${day}/${month}/${year}`; };
const resetForm = () => { form.value = { descricao: '', valor: null, categoria: 'Outros', data: new Date().toISOString().split('T')[0], fixa: false }; isEditing.value = false; editingId.value = null; };

const save = async () => {
  try {
    await api.post('/despesas', form.value);
    await loadExpenses();
    resetForm();
  } catch (e) {
    alert(e.message);
  }
};

const deleteExpense = async (id) => {
  if (confirm('Excluir despesa?')) {
    try {
      await api.delete(`/despesas/${id}`);
      await loadExpenses();
    } catch (e) {
      alert(e.message);
    }
  }
};

const editExpense = (expense) => {
  isEditing.value = true;
  editingId.value = expense.id;
  form.value = { ...expense, data: expense.data_cadastro || expense.data };
};
</script>

<style scoped>
.form-view-container { padding: 30px; background: #f4f7f6; min-height: 100%; }
.form-header { margin-bottom: 25px; }
.form-header h2 { color: #2d3436; font-size: 1.5rem; font-weight: 900; }
.expense-card { background: #fff; border-left: 5px solid #e74c3c; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 30px; }
label { font-size: 0.7rem; color: #7f8c8d; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; display: block; }
.modern-input { background: #f8f9fa; border: 1px solid #e0e6ed; padding: 14px; border-radius: 6px; width: 100%; outline: none; }
.modern-input:focus { border-color: #56a6c1; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
.expense-text { color: #e74c3c; font-weight: 800; }
.btn-save-exp { background: #56a6c1; color: #fff; border: none; padding: 16px; font-weight: 900; border-radius: 6px; cursor: pointer; width: 100%; font-size: 0.95rem; }
.list-section { background: #fff; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.modern-table { width: 100%; border-collapse: collapse; }
.modern-table th { text-align: left; padding: 15px; color: #95a5a6; border-bottom: 1px solid #f0f3f7; font-size: 0.7rem; text-transform: uppercase; }
.modern-table td { padding: 15px; border-bottom: 1px solid #f8f9fa; color: #2d3436; }
.expense-text-table { color: #e74c3c; font-weight: 800; }
.action-buttons { display: flex; gap: 8px; }
.btn-action { background: #f8f9fa; border: 1px solid #e0e6ed; padding: 8px; border-radius: 6px; cursor: pointer; color: #56a6c1; }
</style>