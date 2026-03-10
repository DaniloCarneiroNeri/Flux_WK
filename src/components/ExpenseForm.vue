<template>
  <div class="view-container">
    <header class="view-header">
      <div>
        <h2>REGISTRAR DESPESA</h2>
        <p>Gestão de fluxo de caixa e saídas operacionais</p>
      </div>
    </header>

    <div class="layout-flex">
      <div class="expense-form-card">
        <form @submit.prevent="save" class="exp-form">
          <div class="f-group">
            <label>DESCRIÇÃO</label>
            <input type="text" v-model="form.descricao" class="m-input-lg" placeholder="Ex: Compra de Vidro Laminado" required />
          </div>
          <div class="f-row">
            <div class="f-group">
              <label>VALOR (R$)</label>
              <input type="number" v-model.number="form.valor" class="m-input-lg highlight-red" step="0.01" required />
            </div>
            <div class="f-group">
              <label>VENCIMENTO</label>
              <input type="date" v-model="form.vencimento" class="m-input-lg" required />
            </div>
          </div>
          <div class="f-actions">
            <button v-if="isEditing" type="button" class="btn-cancel" @click="resetForm">CANCELAR</button>
            <button type="submit" class="btn-save-exp">
              {{ isEditing ? 'ATUALIZAR' : 'CONFIRMAR LANÇAMENTO' }}
            </button>
          </div>
        </form>
      </div>

      <div class="expense-list-card">
        <div class="list-head">
          <h3>ÚLTIMOS LANÇAMENTOS</h3>
        </div>
        <div class="table-responsive">
          <table class="m-table">
            <thead>
              <tr>
                <th>DESCRIÇÃO</th>
                <th>DATA</th>
                <th>VALOR</th>
                <th class="text-center">AÇÕES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="exp in expenses" :key="exp.id">
                <td><strong>{{ exp.descricao }}</strong></td>
                <td>{{ formatDate(exp.vencimento) }}</td>
                <td class="val-red">{{ formatCurrency(exp.valor) }}</td>
                <td class="text-center">
                  <div class="action-row">
                    <button class="b-icon" @click="editExpense(exp)">✎</button>
                    <button class="b-icon del" @click="deleteExpense(exp.id)">✕</button>
                  </div>
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
.view-container { padding: 32px; background: #f8fafc; min-height: 100vh; }
.view-header { margin-bottom: 32px; }
.view-header h2 { font-size: 1.5rem; font-weight: 900; color: #1e293b; }
.view-header p { color: #64748b; font-size: 0.9rem; }

.layout-flex { display: flex; flex-direction: column; gap: 32px; }
.expense-form-card { background: #fff; border-left: 6px solid #ef4444; padding: 32px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
.exp-form { display: flex; flex-direction: column; gap: 24px; }
.f-row { display: flex; gap: 24px; flex-wrap: wrap; }
.f-group { flex: 1; min-width: 250px; display: flex; flex-direction: column; gap: 8px; }
label { font-size: 0.7rem; font-weight: 800; color: #94a3b8; }
.m-input-lg { background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 12px; font-size: 1.1rem; color: #1e293b; outline: none; }
.highlight-red { color: #ef4444; font-weight: 900; }
.btn-save-exp { background: #ef4444; color: #fff; border: none; padding: 18px 32px; border-radius: 12px; font-weight: 800; cursor: pointer; flex: 1; transition: 0.2s; }
.btn-save-exp:hover { background: #dc2626; box-shadow: 0 8px 16px rgba(239, 68, 68, 0.2); }

.expense-list-card { background: #fff; border-radius: 20px; padding: 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #edf2f7; overflow: hidden; }
.list-head { padding: 24px; border-bottom: 1px solid #edf2f7; background: #fcfdfe; }
.list-head h3 { font-size: 0.8rem; font-weight: 800; color: #475569; margin: 0; }
.m-table { width: 100%; border-collapse: collapse; }
.m-table th { text-align: left; padding: 16px 24px; font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; background: #f8fafc; }
.m-table td { padding: 16px 24px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }
.val-red { color: #ef4444; font-weight: 800; }
.action-row { display: flex; gap: 10px; justify-content: center; }
.b-icon { background: #f1f5f9; border: none; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; color: #56a6c1; }
.b-icon.del { color: #94a3b8; }
.b-icon.del:hover { color: #ef4444; background: #fee2e2; }

@media (max-width: 768px) {
  .view-container { padding: 16px; }
  .f-row { gap: 16px; }
}
</style>