<template>
  <div class="report-container">
    <div class="report-header">
      <h2>RELATÓRIOS E ANÁLISES</h2>
      <p>Acompanhamento financeiro de entradas e saídas.</p>
    </div>

    <div class="filter-card">
      <form @submit.prevent="generate" class="filter-grid">
        <div class="form-group">
          <label>DATA INICIAL</label>
          <input type="date" v-model="filters.start" class="modern-input" />
        </div>
        <div class="form-group">
          <label>DATA FINAL</label>
          <input type="date" v-model="filters.end" class="modern-input" />
        </div>
        <button type="submit" class="btn-gen">ATUALIZAR ANÁLISE</button>
      </form>
    </div>

    <div class="metrics-grid">
      <div class="metric-box">
        <span class="label">ENTRADAS (O.S. CONCLUÍDAS)</span>
        <h3 class="val positive">{{ formatCurrency(metrics.entradas) }}</h3>
      </div>
      <div class="metric-box">
        <span class="label">SAÍDAS (DESPESAS)</span>
        <h3 class="val negative">{{ formatCurrency(metrics.saidas) }}</h3>
      </div>
      <div class="metric-box highlight">
        <span class="label">LÍQUIDO ESTIMADO</span>
        <h3 class="val" :class="metrics.liquido >= 0 ? 'positive' : 'negative'">
          {{ formatCurrency(metrics.liquido) }}
        </h3>
      </div>
    </div>

    <div class="details-section">
      <div class="details-grid">
        <div class="table-card">
          <h4>DETALHAMENTO DE ENTRADAS</h4>
          <table class="report-table">
            <thead>
              <tr><th>DATA</th><th>O.S.</th><th>VALOR</th></tr>
            </thead>
            <tbody>
              <tr v-for="os in filteredData.ordens" :key="os.id">
                <td>{{ formatDate(os.data_conclusao) }}</td>
                <td>#{{ os.id }}</td>
                <td class="positive-text">{{ formatCurrency(os.valor_total) }}</td>
              </tr>
              <tr v-if="filteredData.ordens.length === 0">
                <td colspan="3" class="empty">Sem entradas no período.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="table-card">
          <h4>DETALHAMENTO DE SAÍDAS</h4>
          <table class="report-table">
            <thead>
              <tr><th>DATA</th><th>DESCRIÇÃO</th><th>VALOR</th></tr>
            </thead>
            <tbody>
              <tr v-for="desp in filteredData.despesas" :key="desp.id">
                <td>{{ formatDate(desp.vencimento) }}</td>
                <td>{{ desp.descricao }}</td>
                <td class="negative-text">{{ formatCurrency(desp.valor) }}</td>
              </tr>
              <tr v-if="filteredData.despesas.length === 0">
                <td colspan="3" class="empty">Sem saídas no período.</td>
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
import demoData from '../data/demoData.json';

const filters = reactive({ start: '', end: '' });
const metrics = reactive({ entradas: 0, saidas: 0, liquido: 0 });
const filteredData = reactive({ ordens: [], despesas: [] });

const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
const formatDate = (dateStr) => { if (!dateStr) return ''; const [year, month, day] = dateStr.split('-'); return `${day}/${month}/${year}`; };

const generate = () => {
  const start = new Date(filters.start); const end = new Date(filters.end);
  filteredData.ordens = (demoData.ordens || []).filter(os => { const d = new Date(os.data_conclusao); return os.status === 'completed' && d >= start && d <= end; });
  filteredData.despesas = (demoData.despesas || []).filter(desp => { const d = new Date(desp.vencimento); return d >= start && d <= end; });
  metrics.entradas = filteredData.ordens.reduce((sum, os) => sum + os.valor_total, 0);
  metrics.saidas = filteredData.despesas.reduce((sum, desp) => sum + desp.valor, 0);
  metrics.liquido = metrics.entradas - metrics.saidas;
};

onMounted(() => {
  const now = new Date(); filters.start = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
  filters.end = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0];
  generate();
});
</script>

<style scoped>
.report-container { padding: 30px; background: #f4f7f6; min-height: 100vh; }
.report-header h2 { color: #2d3436; font-size: 1.5rem; font-weight: 900; margin-bottom: 5px; }
.report-header p { color: #95a5a6; font-size: 0.9rem; margin-bottom: 30px; }
.filter-card { background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 30px; }
.filter-grid { display: grid; grid-template-columns: 1fr 1fr auto; gap: 20px; align-items: flex-end; }
.modern-input { background: #f8f9fa; border: 1px solid #e0e6ed; padding: 12px; border-radius: 6px; width: 100%; outline: none; }
.btn-gen { background: #56a6c1; color: #fff; border: none; padding: 0 30px; border-radius: 6px; font-weight: 800; cursor: pointer; height: 45px; }
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
.metric-box { background: #fff; padding: 30px; border-radius: 8px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border-bottom: 4px solid #e0e6ed; }
.metric-box.highlight { border-bottom-color: #56a6c1; }
.label { font-size: 0.7rem; color: #7f8c8d; font-weight: 800; letter-spacing: 1px; }
.val { font-size: 1.8rem; font-weight: 900; margin-top: 10px; }
.positive { color: #2ecc71; }
.negative { color: #e74c3c; }
.details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
.table-card { background: #fff; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.table-card h4 { font-size: 0.75rem; color: #56a6c1; font-weight: 800; margin-bottom: 20px; }
.report-table { width: 100%; border-collapse: collapse; }
.report-table th { text-align: left; padding: 12px; color: #95a5a6; font-size: 0.65rem; border-bottom: 1px solid #f0f3f7; }
.report-table td { padding: 12px; font-size: 0.85rem; border-bottom: 1px solid #fcfdfe; }
.positive-text { color: #2ecc71; font-weight: 700; }
.negative-text { color: #e74c3c; font-weight: 700; }
@media (max-width: 768px) { .filter-grid, .metrics-grid, .details-grid { grid-template-columns: 1fr; } }
</style>