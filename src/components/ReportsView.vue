<template>
  <div class="report-container">
    <div class="filter-card">
      <form @submit.prevent="generateReport" class="filter-grid">
        <div class="form-group">
          <label>INICIAL</label>
          <input type="date" v-model="filters.startDate" class="dark-input" />
        </div>
        <div class="form-group">
          <label>FINAL</label>
          <input type="date" v-model="filters.endDate" class="dark-input" />
        </div>
        <button type="submit" class="btn-generate">ANALISAR</button>
      </form>
    </div>

    <div v-if="hasSearched" class="results-area">
      <div class="metrics-grid">
        <div class="metric-box">
          <span class="m-label">ENTRADAS</span>
          <h3 class="m-val pos">R$ {{ formatMoney(totals.revenue) }}</h3>
        </div>
        <div class="metric-box">
          <span class="m-label">SAÍDAS</span>
          <h3 class="m-val neg">R$ {{ formatMoney(totals.variableExpenses + totals.fixedExpensesTotal) }}</h3>
        </div>
        <div class="metric-box highlight">
          <span class="m-label">LÍQUIDO</span>
          <h3 class="m-val" :class="totals.balance >= 0 ? 'pos' : 'neg'">R$ {{ formatMoney(totals.balance) }}</h3>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.report-container { padding: 20px; background: #050505; }
.filter-card { background: #0a0a0a; padding: 20px; border-radius: 4px; border: 1px solid #1a1a1a; margin-bottom: 20px; }
.filter-grid { display: grid; grid-template-columns: 1fr 1fr auto; gap: 15px; align-items: flex-end; }

.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
.metric-box { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 25px 15px; text-align: center; border-radius: 4px; }
.metric-box.highlight { border-color: #40c4ff; background: #0e0e0e; }
.m-label { font-size: 0.65rem; color: #555; font-weight: 800; letter-spacing: 1px; }
.m-val { font-size: 1.4rem; font-weight: 900; margin-top: 10px; }
.pos { color: #fff; }
.neg { color: #c0392b; }

@media (max-width: 768px) {
  .filter-grid { grid-template-columns: 1fr; }
  .metrics-grid { grid-template-columns: 1fr; }
  .btn-generate { width: 100%; padding: 18px; }
}
</style>