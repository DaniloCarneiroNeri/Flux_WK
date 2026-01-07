<template>
  <div class="report-container">
    <div class="filter-card">
      <form @submit.prevent="generate" class="filter-grid">
        <div class="form-group"><label>INICIAL</label><input type="date" class="dark-input" /></div>
        <div class="form-group"><label>FINAL</label><input type="date" class="dark-input" /></div>
        <button type="submit" class="btn-gen">GERAR ANÁLISE</button>
      </form>
    </div>
    <div class="metrics-grid">
      <div class="metric-box"><span class="label">ENTRADAS</span><h3 class="val">R$ 0,00</h3></div>
      <div class="metric-box"><span class="label">SAÍDAS</span><h3 class="val neg">R$ 0,00</h3></div>
      <div class="metric-box highlight"><span class="label">LÍQUIDO WK</span><h3 class="val">R$ 0,00</h3></div>
    </div>
  </div>
</template>

<style scoped>
.report-container { padding: 30px; background: #050505; }
.filter-card { background: #0a0a0a; padding: 25px; border: 1px solid #1a1a1a; margin-bottom: 30px; }
.filter-grid { display: grid; grid-template-columns: 1fr 1fr auto; gap: 20px; align-items: flex-end; }
.btn-gen { background: #40c4ff; color: #000; font-weight: 900; border: none; padding: 15px 30px; border-radius: 4px; }
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.metric-box { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 30px; text-align: center; border-radius: 4px; }
.metric-box.highlight { border-color: #40c4ff; background: #0e0e0e; }
.label { font-size: 0.7rem; color: #555; font-weight: 900; }
.val { font-size: 1.6rem; font-weight: 900; margin-top: 15px; }
.neg { color: #c0392b; }
@media (max-width: 768px) { .filter-grid { grid-template-columns: 1fr; } .metrics-grid { grid-template-columns: 1fr; } }
</style>