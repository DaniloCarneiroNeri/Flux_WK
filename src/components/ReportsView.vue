<template>
  <div class="view-container">
    <header class="view-header">
      <div>
        <h2>RELATÓRIOS E ANÁLISES</h2>
        <p>Desempenho financeiro e visão estratégica</p>
      </div>
    </header>

    <div class="filter-bar">
      <div class="date-picker-group">
        <div class="d-field">
          <label>INÍCIO</label>
          <input type="date" v-model="filters.start" class="m-date" />
        </div>
        <div class="d-field">
          <label>FIM</label>
          <input type="date" v-model="filters.end" class="m-date" />
        </div>
      </div>
      <button class="btn-refresh" @click="generate">ATUALIZAR DADOS</button>
    </div>

    <div class="metrics-row">
      <div class="m-card green">
        <span class="m-label">ENTRADAS (O.S.)</span>
        <h3 class="m-value">{{ formatCurrency(metrics.entradas) }}</h3>
      </div>
      <div class="m-card red">
        <span class="m-label">SAÍDAS (DESPESAS)</span>
        <h3 class="m-value">{{ formatCurrency(metrics.saidas) }}</h3>
      </div>
      <div class="m-card blue">
        <span class="m-label">LÍQUIDO ESTIMADO</span>
        <h3 class="m-value" :class="{ 'neg': metrics.liquido < 0 }">{{ formatCurrency(metrics.liquido) }}</h3>
      </div>
    </div>

    <div class="details-grid">
      <div class="d-card">
        <div class="d-head">ENTRADAS POR PERÍODO</div>
        <div class="d-body">
          <table class="min-table">
            <thead>
              <tr><th>DATA</th><th>O.S.</th><th>VALOR</th></tr>
            </thead>
            <tbody>
              <tr v-for="os in filteredData.ordens" :key="os.id">
                <td>{{ formatDate(os.data_conclusao) }}</td>
                <td>#{{ os.id }}</td>
                <td class="text-green">{{ formatCurrency(os.valor_total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="d-card">
        <div class="d-head">SAÍDAS DETALHADAS</div>
        <div class="d-body">
          <table class="min-table">
            <thead>
              <tr><th>DATA</th><th>DESCRIÇÃO</th><th>VALOR</th></tr>
            </thead>
            <tbody>
              <tr v-for="desp in filteredData.despesas" :key="desp.id">
                <td>{{ formatDate(desp.vencimento) }}</td>
                <td>{{ desp.descricao }}</td>
                <td class="text-red">{{ formatCurrency(desp.valor) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue';
import { api } from '../services/api';

const filters = reactive({ start: '', end: '' });
const metrics = reactive({ entradas: 0, saidas: 0, liquido: 0 });
const filteredData = reactive({ ordens: [], despesas: [] });

const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
const formatDate = (dateStr) => { 
  if (!dateStr) return ''; 
  const pureDate = dateStr.split('T')[0];
  const [year, month, day] = pureDate.split('-'); 
  return `${day}/${month}/${year}`; 
};

const generate = async () => {
  const [allOrdens, allDespesas] = await Promise.all([
    api.get('/ordens'),
    api.get('/despesas')
  ]);

  const start = new Date(filters.start);
  const end = new Date(filters.end);

  filteredData.ordens = allOrdens.filter(os => {
    const d = new Date(os.data_conclusao || os.data_abertura);
    return os.status === 'completed' && d >= start && d <= end;
  });

  filteredData.despesas = allDespesas.filter(desp => {
    const d = new Date(desp.data_vencimento || desp.data_cadastro);
    return d >= start && d <= end;
  });

  metrics.entradas = filteredData.ordens.reduce((sum, os) => sum + os.valor_total, 0);
  metrics.saidas = filteredData.despesas.reduce((sum, desp) => sum + desp.valor, 0);
  metrics.liquido = metrics.entradas - metrics.saidas;
};

onMounted(() => {
  const now = new Date();
  filters.start = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
  filters.end = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0];
  generate();
});
</script>

<style scoped>
.view-container { padding: 32px; background: #f8fafc; min-height: 100vh; }
.view-header { margin-bottom: 32px; }
.view-header h2 { font-size: 1.5rem; font-weight: 900; color: #1e293b; }

.filter-bar { background: #fff; padding: 20px 32px; border-radius: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; margin-bottom: 32px; flex-wrap: wrap; }
.date-picker-group { display: flex; gap: 16px; }
.d-field { display: flex; flex-direction: column; gap: 6px; }
label { font-size: 0.65rem; font-weight: 800; color: #94a3b8; }
.m-date { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px 14px; border-radius: 10px; font-size: 0.9rem; outline: none; }
.btn-refresh { background: #1e293b; color: #fff; border: none; padding: 12px 24px; border-radius: 10px; font-weight: 800; cursor: pointer; height: 44px; }

.metrics-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-bottom: 32px; }
.m-card { background: #fff; padding: 32px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border-bottom: 5px solid #e2e8f0; }
.m-card.green { border-color: #10b981; }
.m-card.red { border-color: #ef4444; }
.m-card.blue { border-color: #56a6c1; }
.m-label { font-size: 0.75rem; font-weight: 800; color: #94a3b8; letter-spacing: 0.5px; }
.m-value { font-size: 2rem; font-weight: 950; margin-top: 12px; color: #1e293b; }
.m-value.neg { color: #ef4444; }

.details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.d-card { background: #fff; border-radius: 20px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #edf2f7; }
.d-head { padding: 20px 24px; background: #fcfdfe; border-bottom: 1px solid #edf2f7; font-size: 0.8rem; font-weight: 800; color: #56a6c1; }
.min-table { width: 100%; border-collapse: collapse; }
.min-table th { text-align: left; padding: 12px 24px; font-size: 0.65rem; color: #94a3b8; border-bottom: 1px solid #f1f5f9; }
.min-table td { padding: 12px 24px; font-size: 0.85rem; border-bottom: 1px solid #fcfdfe; }
.text-green { color: #10b981; font-weight: 700; }
.text-red { color: #ef4444; font-weight: 700; }

@media (max-width: 1024px) {
  .details-grid { grid-template-columns: 1fr; }
}
</style>