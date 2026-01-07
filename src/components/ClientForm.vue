<template>
  <div class="form-view-container">
    <div class="form-header">
      <h2>CLIENTES</h2>
      <p>Base de dados WK Vidros.</p>
    </div>

    <div class="responsive-layout">
      <div class="form-card main-card">
        <div class="card-header">
          <h3>{{ isEditing ? 'EDITAR DADOS' : 'NOVO CADASTRO' }}</h3>
        </div>
        <form @submit.prevent="handleSubmit" class="flux-form">
          <div class="form-group">
            <label>NOME / RAZÃO SOCIAL</label>
            <input type="text" v-model="form.nome" class="dark-input" required />
          </div>
          <div class="form-row-mobile">
            <div class="form-group">
              <label>TELEFONE</label>
              <input type="text" v-model="form.telefone" class="dark-input" />
            </div>
            <div class="form-group">
              <label>EMAIL</label>
              <input type="email" v-model="form.email" class="dark-input" />
            </div>
          </div>
          <div class="form-group">
            <label>ENDEREÇO</label>
            <input type="text" v-model="form.endereco" class="dark-input" />
          </div>
          <div class="form-actions-mobile">
            <button type="button" class="btn-cancel" @click="resetForm" v-if="isEditing">CANCELAR</button>
            <button type="submit" class="btn-primary">SALVAR REGISTRO</button>
          </div>
        </form>
      </div>

      <div class="form-card list-card">
        <div class="table-container">
          <table class="dark-table">
            <thead>
              <tr>
                <th>CLIENTE</th>
                <th class="text-right">AÇÕES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cliente in clientes" :key="cliente.id">
                <td class="client-name-cell">
                  <strong>{{ cliente.nome }}</strong>
                  <span>{{ cliente.telefone || 'Sem contato' }}</span>
                </td>
                <td class="text-right">
                  <button class="btn-circle edit" @click="editClient(cliente)">✎</button>
                  <button class="btn-circle del" @click="confirmDelete(cliente.id)">✕</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-view-container { padding: 20px; background: #050505; }
.form-header { margin-bottom: 25px; border-bottom: 1px solid #1a1a1a; padding-bottom: 15px; }
.form-header h2 { font-size: 1.3rem; letter-spacing: 2px; }

.responsive-layout { display: flex; gap: 20px; align-items: flex-start; }
.main-card { flex: 1; border-left: 4px solid #40c4ff; }
.list-card { flex: 1.2; }

.form-card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 20px; border-radius: 4px; }
.card-header h3 { font-size: 0.8rem; color: #555; letter-spacing: 1px; margin-bottom: 20px; }

.flux-form { display: flex; flex-direction: column; gap: 15px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-row-mobile { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
label { font-size: 0.65rem; color: #444; font-weight: 800; }

.dark-input { background: #111; border: 1px solid #222; color: #fff; padding: 14px; border-radius: 4px; outline: none; }
.dark-input:focus { border-color: #40c4ff; }

.form-actions-mobile { display: flex; gap: 10px; margin-top: 10px; }
.btn-primary { flex: 1; background: #40c4ff; color: #000; border: none; padding: 16px; font-weight: 800; border-radius: 4px; cursor: pointer; }
.btn-cancel { background: transparent; border: 1px solid #333; color: #666; padding: 16px; border-radius: 4px; cursor: pointer; }

.dark-table { width: 100%; border-collapse: collapse; }
.client-name-cell { display: flex; flex-direction: column; padding: 12px 0; }
.client-name-cell strong { color: #fff; font-size: 0.9rem; }
.client-name-cell span { color: #444; font-size: 0.75rem; }

.btn-circle { width: 32px; height: 32px; border-radius: 50%; border: none; cursor: pointer; margin-left: 8px; }
.edit { background: #111; color: #40c4ff; }
.del { background: #111; color: #c0392b; }

@media (max-width: 900px) {
  .responsive-layout { flex-direction: column; }
  .form-row-mobile { grid-template-columns: 1fr; }
  .form-actions-mobile { flex-direction: column-reverse; }
}
</style>