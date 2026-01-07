<template>
  <div class="form-view-container">
    <div class="form-header">
      <h2>ORÇAMENTOS</h2>
      <p>Gestão de Vendas WK Vidros</p>
    </div>
    <div class="form-card main-form">
      <form @submit.prevent="save" class="flux-form">
        <div class="top-row">
          <div class="form-group">
            <label>CLIENTE</label>
            <select v-model="selectedClientId" class="dark-input">
              <option :value="null" disabled>Selecione um cliente...</option>
              <option v-for="client in clientes" :key="client.id" :value="client.id">
                {{ client.nome }}
              </option>
            </select>
          </div>
          <div class="form-group total-box">
             <label>VALOR TOTAL</label>
             <div class="total-val">{{ formatCurrency(totalOrcamento) }}</div>
          </div>
        </div>
        <div class="items-section">
          <div class="items-header">ITENS DO ORÇAMENTO</div>
          <div class="items-list">
            <div v-if="itens.length === 0" class="empty-items">
              <p>Nenhum item adicionado.</p>
            </div>
            <div v-for="(item, index) in itens" :key="index" class="item-row">
              <input type="text" v-model="item.descricao" placeholder="Descrição do item" class="item-input desc" />
              <input type="number" v-model.number="item.quantidade" placeholder="Qtd" class="item-input qty" />
              <input type="number" v-model.number="item.valor" placeholder="Valor" class="item-input price" />
              <span class="item-total">{{ formatCurrency(item.quantidade * item.valor) }}</span>
              <button type="button" @click="removeItem(index)" class="btn-remove-item">✕</button>
            </div>
          </div>
          <button type="button" class="btn-add" @click="addItem">+ ADICIONAR ITEM</button>
        </div>
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="$emit('cancel')">DESCARTAR</button>
          <button type="submit" class="btn-primary">GERAR ORÇAMENTO</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import demoData from '../data/demoData.json';

defineEmits(['cancel']);

const clientes = ref(demoData.clientes);
const selectedClientId = ref(null);
const itens = ref([]);

const addItem = () => {
  itens.value.push({ descricao: '', quantidade: 1, valor: 0 });
};

const removeItem = (index) => {
  itens.value.splice(index, 1);
};

const totalOrcamento = computed(() => {
  return itens.value.reduce((total, item) => total + (item.quantidade * item.valor), 0);
});

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
};

const save = () => {
  // Lógica para salvar o orçamento
  console.log({
    clienteId: selectedClientId.value,
    itens: itens.value,
    total: totalOrcamento.value
  });
};
</script>

<style scoped>
.form-view-container { padding: 30px; background: #050505; }
.form-header { margin-bottom: 30px; }
.form-header h2 { color: #fff; font-size: 1.5rem; font-weight: 900; }
.form-header p { color: #666; font-size: 0.9rem; }
.flux-form label { font-size: 0.7rem; color: #666; font-weight: 600; text-transform: uppercase; margin-bottom: 6px; display: block; }
.dark-input { background: #000; border: 1px solid #222; color: #fff; padding: 14px; border-radius: 4px; outline: none; width: 100%; font-size: 0.9rem; }
.dark-input:focus { border-color: #40c4ff; }
.main-form { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 30px; border-radius: 4px; }
.top-row { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
.total-val { font-size: 2rem; font-weight: 900; color: #40c4ff; margin-top: 5px; }
.items-section { margin: 30px 0; border: 1px solid #1a1a1a; border-radius: 4px; background: #000; }
.items-header { background: #111; padding: 15px; font-size: 0.7rem; font-weight: 800; color: #555; }
.items-list { padding: 10px; }
.empty-items { padding: 20px; text-align: center; color: #444; }
.item-row { display: grid; grid-template-columns: 3fr 1fr 1fr 1fr auto; gap: 10px; align-items: center; padding: 10px; border-bottom: 1px solid #1a1a1a; }
.item-row:last-child { border-bottom: none; }
.item-input { background: #0a0a0a; border: 1px solid #222; color: #fff; padding: 10px; border-radius: 4px; font-size: 0.85rem; }
.item-input.price { text-align: right; }
.item-total { font-weight: bold; color: #ccc; text-align: right; font-size: 0.9rem; }
.btn-remove-item { background: none; border: none; color: #c0392b; font-size: 1.2rem; cursor: pointer; }
.btn-add { width: 100%; background: transparent; border: none; color: #40c4ff; padding: 15px; font-weight: 800; cursor: pointer; }
.form-actions { display: flex; justify-content: flex-end; gap: 15px; border-top: 1px solid #1a1a1a; padding-top: 25px; }
.btn-primary { background: #40c4ff; color: #000; border: none; padding: 15px 30px; font-weight: 900; border-radius: 4px; cursor: pointer; }
.btn-cancel { background: transparent; color: #555; border: 1px solid #222; padding: 15px 30px; border-radius: 4px; }
@media (max-width: 768px) { .top-row { grid-template-columns: 1fr; gap: 20px; } .form-actions { flex-direction: column-reverse; } .item-row { grid-template-columns: 1fr; gap: 8px; } }
</style>