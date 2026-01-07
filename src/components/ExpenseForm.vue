<template>
  <div class="form-view-container">
    <div class="form-header">
      <h2>LANÇAMENTO DE DESPESAS</h2>
      <p>Registro de custos operacionais e fixos.</p>
    </div>

    <div class="content-wrapper-centered">
      <div class="form-card expense-card">
        <div class="card-header card-header-red">
          <h3>NOVA SAÍDA FINANCEIRA</h3>
        </div>

        <form @submit.prevent="handleSubmit" class="flux-form">
          
          <div class="form-group highlight-group">
            <label>DESCRIÇÃO DA DESPESA <span class="req">*</span></label>
            <input 
              type="text" 
              v-model="form.descricao" 
              class="dark-input large-input" 
              placeholder="Ex: Conta de Energia Celesc - Mês 05" 
              required
              autofocus
            />
          </div>

          <div class="form-row-split">
            <div class="form-group">
              <label>VALOR (R$) <span class="req">*</span></label>
              <input 
                type="number" 
                v-model.number="form.valor" 
                class="dark-input currency-input" 
                step="0.01" 
                min="0.01"
                placeholder="0,00"
                required 
              />
            </div>
            <div class="form-group">
              <label>DATA DE COMPETÊNCIA <span class="req">*</span></label>
              <input 
                type="date" 
                v-model="form.data_despesa" 
                class="dark-input" 
                required 
              />
            </div>
          </div>

          <div class="form-row-split align-end">
             <div class="form-group">
                <label>CATEGORIA <span class="req">*</span></label>
                <select v-model="form.categoria" class="dark-input category-select" required>
                  <option value="" disabled selected>Selecione o tipo...</option>
                  <option value="fixa">CUSTO FIXO (Aluguel, Salários...)</option>
                  <option value="variavel">CUSTO VARIÁVEL (Materiais, Comissões...)</option>
                </select>
              </div>

              <div class="form-group checkbox-group">
                <label class="checkbox-container">
                  <input type="checkbox" v-model="form.recorrente" />
                  <span class="checkmark"></span>
                  <span class="checkbox-label">DESPESA MENSAL RECORRENTE</span>
                </label>
              </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="$emit('cancel')">CANCELAR</button>
            <button type="submit" class="btn-danger-action">REGISTRAR SAÍDA</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
// (Mantendo a lógica original intacta)
import { reactive } from 'vue';

const emit = defineEmits(['cancel', 'save']);
const API_URL = import.meta.env.DEV ? 'http://localhost:8000' : '';

const form = reactive({
  descricao: '',
  valor: null,
  data_despesa: new Date().toISOString().split('T')[0],
  categoria: '',
  recorrente: false
});

const handleSubmit = async () => {
  try {
    const response = await fetch(`${API_URL}/despesas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });

    if (response.ok) {
      emit('save');
    }
  } catch (error) {
    console.error("Erro ao salvar despesa:", error);
  }
};
</script>

<style scoped>
.form-view-container { padding: 30px; background: #050505; min-height: 100%; }
.form-header { margin-bottom: 30px; border-bottom: 1px solid #1a1a1a; padding-bottom: 20px; text-align: center; }
.form-header h2 { color: #ffffff; font-size: 1.5rem; letter-spacing: 3px; font-weight: 800; margin: 0; }
.form-header p { color: #888; font-size: 0.9rem; margin-top: 8px; letter-spacing: 1px; }

.content-wrapper-centered { display: flex; justify-content: center; }

.form-card.expense-card {
  background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 4px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.4); width: 600px; max-width: 100%;
  border-left: 4px solid #c0392b; /* Red accent for expenses */
}

.card-header { padding: 25px; border-bottom: 1px solid #1a1a1a; }
.card-header h3 { color: #fff; font-size: 1rem; font-weight: 700; letter-spacing: 2px; margin: 0; }
.req { color: #c0392b; }

.flux-form { padding: 30px; display: flex; flex-direction: column; gap: 25px; }
.form-group { display: flex; flex-direction: column; gap: 10px; }
.form-row-split { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.align-end { align-items: flex-end; }

label { color: #888; font-size: 0.7rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; }

.dark-input {
  background: #111; border: 1px solid #222; color: #fff; padding: 15px;
  border-radius: 3px; font-size: 1rem; outline: none; width: 100%;
  transition: all 0.3s;
}
.dark-input:focus { border-color: #c0392b; background: #0e0e0e; } /* Red focus for expenses */
.large-input { font-size: 1.1rem; padding: 18px; font-weight: bold; }
.currency-input { color: #c0392b; font-weight: bold; font-size: 1.2rem; }
.category-select { cursor: pointer; }

/* Custom Checkbox style */
.checkbox-group { padding-bottom: 5px; }
.checkbox-container { display: flex; align-items: center; position: relative; padding-left: 35px; cursor: pointer; user-select: none; height: 50px; }
.checkbox-container input { position: absolute; opacity: 0; cursor: pointer; height: 0; width: 0; }
.checkmark { position: absolute; left: 0; height: 25px; width: 25px; background-color: #111; border: 2px solid #333; border-radius: 4px; transition: 0.3s; }
.checkbox-container:hover input ~ .checkmark { background-color: #222; border-color: #555; }
.checkbox-container input:checked ~ .checkmark { background-color: #c0392b; border-color: #c0392b; }
.checkmark:after { content: ""; position: absolute; display: none; }
.checkbox-container input:checked ~ .checkmark:after { display: block; }
.checkbox-container .checkmark:after { left: 9px; top: 5px; width: 5px; height: 10px; border: solid white; border-width: 0 3px 3px 0; transform: rotate(45deg); }
.checkbox-label { color: #fff; font-weight: 700; font-size: 0.8rem; letter-spacing: 1px; }

.form-actions { display: flex; justify-content: flex-end; gap: 15px; margin-top: 10px; padding-top: 25px; border-top: 1px solid #1a1a1a; }
.btn-cancel, .btn-danger-action {
  padding: 16px 30px; border-radius: 3px; font-weight: 800; font-size: 0.9rem;
  letter-spacing: 1px; cursor: pointer; border: none; transition: all 0.3s;
}
.btn-cancel { background: transparent; color: #888; border: 2px solid #333; }
.btn-cancel:hover { border-color: #fff; color: #fff; }
.btn-danger-action { background: #c0392b; color: #fff; }
.btn-danger-action:hover { background: #e74c3c; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(192, 57, 43, 0.3); }

@media (max-width: 650px) {
    .form-row-split { grid-template-columns: 1fr; gap: 15px; }
    .align-end { align-items: flex-start; }
    .checkbox-container { height: auto; margin-top: 15px; }
}
</style>