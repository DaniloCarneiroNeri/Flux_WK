<template>
  <div class="board-container">
    <div class="board-header">
      <div class="header-left">
        <button class="btn-new" @click="openNewOrder">
          <span class="plus">+</span> <span class="btn-text">NOVA ORDEM</span>
        </button>
        <h1>QUADRO</h1>
      </div>
      <div class="view-toggle">
        <button :class="{ active: viewMode === 'kanban' }" @click="viewMode = 'kanban'">⊞</button>
        <button :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">☰</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Sincronizando WK...</p>
    </div>

    <div v-else-if="viewMode === 'kanban'" class="kanban-scroll-area">
      <div class="kanban-wrapper">
        <div v-for="col in columns" :key="col.key" class="kanban-column">
          <div class="column-header" :style="{ borderTopColor: col.color }">
            <h3>{{ col.label.toUpperCase() }}</h3>
            <span class="count">{{ getServicesByStatus(col.key).length }}</span>
          </div>
          <div class="column-body">
            <div v-for="item in getServicesByStatus(col.key)" :key="item.id" class="kanban-card" @click="editOrder(item)">
              <div class="card-top">
                <span class="service-id">#{{ item.id }}</span>
                <span v-if="isOrderLocked(item)">🔒</span>
              </div>
              <h4 class="card-client">{{ item.clientes?.nome || 'CLIENTE FINAL' }}</h4>
              <div class="card-desc">
                <p v-if="item.itens_ordem?.length">
                  <span class="cyan-bullet">■</span> {{ item.itens_ordem[0].descricao_item }} 
                </p>
              </div>
              <div class="card-footer">
                <span class="card-date">{{ formatDate(item.data_abertura) }}</span>
                <span class="price-tag">R$ {{ formatCurrency(item.valor_total) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="table-responsive-wrapper">
      <table class="flux-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>CLIENTE</th>
            <th class="hide-mobile">ITENS</th>
            <th>TOTAL</th>
            <th>STATUS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in services" :key="item.id" @click="editOrder(item)" class="clickable-row">
            <td class="id-col">#{{ item.id }}</td>
            <td class="fw-bold">{{ item.clientes?.nome || '---' }}</td>
            <td class="desc-col hide-mobile">{{ item.itens_ordem?.length ? item.itens_ordem[0].descricao_item : '---' }}</td>
            <td class="value-col">R$ {{ formatCurrency(item.valor_total) }}</td>
            <td><span class="status-badge" :class="item.status">{{ getStatusLabel(item.status).toUpperCase() }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.board-container { padding: 20px; height: 100%; display: flex; flex-direction: column; background: #050505; }
.board-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-left h1 { color: #ffffff; font-size: 1.1rem; letter-spacing: 2px; font-weight: 800; margin: 0; }

.btn-new { background: #40c4ff; color: #000; padding: 12px 18px; border-radius: 4px; font-weight: 800; border: none; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.view-toggle { background: #111; padding: 4px; border-radius: 4px; display: flex; border: 1px solid #222; }
.view-toggle button { background: none; border: none; padding: 8px 12px; color: #444; cursor: pointer; font-size: 1.1rem; }
.view-toggle button.active { color: #40c4ff; background: #222; border-radius: 2px; }

.kanban-scroll-area { flex: 1; overflow-x: auto; padding-bottom: 10px; }
.kanban-wrapper { display: flex; gap: 15px; min-width: min-content; height: 100%; }
.kanban-column { width: 280px; background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 4px; display: flex; flex-direction: column; }
.column-header { padding: 15px; border-top: 3px solid #333; display: flex; justify-content: space-between; align-items: center; }
.column-header h3 { font-size: 0.75rem; letter-spacing: 1px; color: #666; }
.count { color: #40c4ff; font-weight: bold; font-size: 0.8rem; }
.column-body { flex: 1; overflow-y: auto; padding: 10px; }

.kanban-card { background: #111; padding: 16px; margin-bottom: 12px; border: 1px solid #1a1a1a; border-radius: 4px; cursor: pointer; transition: border-color 0.2s; }
.kanban-card:active { border-color: #40c4ff; background: #151515; }
.card-top { display: flex; justify-content: space-between; font-size: 0.65rem; color: #444; margin-bottom: 8px; font-weight: bold; }
.card-client { color: #fff; font-size: 0.9rem; font-weight: 700; margin-bottom: 6px; }
.card-desc { font-size: 0.8rem; color: #666; margin-bottom: 12px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #1a1a1a; padding-top: 12px; }
.price-tag { color: #40c4ff; font-weight: 800; font-size: 0.95rem; }
.card-date { font-size: 0.7rem; color: #333; }

.table-responsive-wrapper { overflow-x: auto; border-radius: 4px; border: 1px solid #1a1a1a; }
.flux-table { width: 100%; border-collapse: collapse; min-width: 500px; }
.flux-table th { background: #111; color: #555; padding: 12px; font-size: 0.7rem; text-transform: uppercase; text-align: left; }
.flux-table td { padding: 14px 12px; border-bottom: 1px solid #111; font-size: 0.85rem; color: #ccc; }
.status-badge { padding: 4px 8px; border-radius: 2px; font-size: 0.65rem; font-weight: 800; }
.orcamento { border: 1px solid #444; color: #444; }
.pendente { border: 1px solid #40c4ff; color: #40c4ff; }
.concluido { background: #40c4ff; color: #000; }

@media (max-width: 600px) {
  .hide-mobile { display: none; }
  .btn-text { display: none; }
  .btn-new { padding: 12px; }
  .kanban-column { width: 85vw; }
  .board-container { padding: 15px; }
}
</style>