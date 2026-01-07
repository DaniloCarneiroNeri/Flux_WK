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
          <input type="text" class="dark-input" placeholder="Ex: Compra de material" required />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>VALOR (R$)</label>
            <input type="number" class="dark-input red-text" placeholder="0,00" step="0.01" required />
          </div>
          <div class="form-group">
            <label>DATA DE VENCIMENTO</label>
            <input type="date" class="dark-input" required />
          </div>
        </div>
        <button type="submit" class="btn-save-exp">REGISTRAR DESPESA</button>
      </form>
    </div>
  </div>
</template>

<script setup>
const save = () => {};
</script>

<style scoped>
.form-view-container { padding: 20px; background: #050505; min-height: 100%; }
.form-header { margin-bottom: 25px; }
.form-header h2 { color: #fff; font-size: 1.5rem; font-weight: 900; }
.form-header p { color: #666; font-size: 0.9rem; }
.expense-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-left: 4px solid #c0392b; padding: 25px; border-radius: 4px; max-width: 800px; margin: 0 auto; }
.flux-form label { font-size: 0.7rem; color: #666; font-weight: 600; text-transform: uppercase; margin-bottom: 6px; display: block; }
.dark-input { background: #000; border: 1px solid #222; color: #fff; padding: 14px; border-radius: 4px; outline: none; width: 100%; font-size: 0.9rem; }
.dark-input:focus { border-color: #c0392b; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0; }
.red-text { color: #c0392b; font-weight: 700; font-size: 1.1rem; }
.btn-save-exp { background: #c0392b; color: #fff; border: none; padding: 16px; font-weight: 900; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 10px; font-size: 0.9rem; }
</style>