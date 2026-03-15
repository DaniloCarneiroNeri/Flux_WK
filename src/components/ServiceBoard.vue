<template>
  <div class="board-container">
    <header class="board-header">
      <div class="header-info">
        <h1>QUADRO DE SERVIÇOS</h1>
        <p>Gestão de produção e fluxo de trabalho</p>
      </div>
      <div class="header-controls">
        <div class="view-switch">
          <button :class="{ active: viewMode === 'kanban' }" @click="viewMode = 'kanban'">Grade</button>
          <button :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">Lista</button>
        </div>
        <button class="btn-primary-action" @click="openModal()">+ NOVA O.S.</button>
      </div>
    </header>

    <div class="content-area">
      <transition name="fade" mode="out-in">
        <div v-if="viewMode === 'kanban'" class="kanban-container">
          <div 
            v-for="column in columns" 
            :key="column.title" 
            class="kanban-column"
            @dragover.prevent
            @drop="onDrop(column.title)"
          >
            <div class="column-title" :style="{ borderTopColor: column.color }">
              <span class="status-dot" :style="{ backgroundColor: column.color }"></span>
              <h3>{{ column.title }}</h3>
              <span class="badge-count">{{ column.orders.length }}</span>
            </div>
            
            <div class="column-cards">
              <div 
                v-for="order in column.orders" 
                :key="order.id" 
                class="service-card" 
                @click="openModal(order)"
                draggable="true"
                @dragstart="onDragStart(order)"
              >
                <div class="card-top">
                  <span class="os-number">#{{ order.id }}</span>
                  <span v-if="order.status === 'late'" class="tag-late">ATRASADO</span>
                </div>
                <h4 class="client-name">{{ order.clientes.nome }}</h4>
                <div class="card-bottom">
                  <span class="total-price">{{ formatCurrency(order.valor_total) }}</span>
                  <span class="icon-drag">⋮⋮</span>
                </div>
              </div>
              <div v-if="column.orders.length === 0" class="empty-state">Sem ordens</div>
            </div>
          </div>
        </div>

        <div v-else class="table-view-wrapper">
          <div class="responsive-table">
            <table class="modern-grid">
              <thead>
                <tr>
                  <th>O.S.</th>
                  <th>CLIENTE</th>
                  <th>VALOR TOTAL</th>
                  <th>STATUS</th>
                  <th class="text-right">AÇÕES</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in ordens" :key="order.id" class="row-hover">
                  <td><strong>#{{ order.id }}</strong></td>
                  <td>{{ order.clientes.nome }}</td>
                  <td class="price-col">{{ formatCurrency(order.valor_total) }}</td>
                  <td><span class="status-tag" :class="order.status">{{ getStatusLabel(order.status) }}</span></td>
                  <td class="text-right">
                    <button class="btn-edit-small" @click="openModal(order)">ABRIR DETALHES</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </transition>
    </div>

    <transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card os-details">
          <div class="modal-header">
            <div class="header-title">
              <span class="os-id-badge">O.S. #{{ form.id || 'NOVA' }}</span>
              <h3>{{ isEditing ? 'Detalhes do Serviço' : 'Nova Ordem de Serviço' }}</h3>
            </div>
            <button class="close-x" @click="closeModal">×</button>
          </div>
          
          <div class="modal-body scrollable">
            <div class="form-grid">
              <div class="field-group">
                <label>CLIENTE</label>
                <select v-model="form.cliente_id" class="custom-input" :disabled="isLocked">
                  <option v-for="client in dbClients" :key="client.id" :value="client.id">{{ client.nome }}</option>
                </select>
              </div>
              <div class="field-group">
                <label>STATUS DA PRODUÇÃO</label>
                <select v-model="form.status" class="custom-input" :disabled="isLocked">
                  <option value="pending">Pendente</option>
                  <option value="production">Em Produção</option>
                  <option value="completed">Concluído</option>
                  <option value="billed">NFe Emitida</option>
                </select>
              </div>

              <div class="items-summary-section full-width">
                <div class="section-title">ITENS E MEDIÇÕES</div>
                <div class="items-list-box">
                  <div v-if="form.items.length === 0 && !form.desconto" class="empty-items">Nenhum item registrado nesta O.S.</div>
                  
                  <div v-for="(item, idx) in form.items" :key="idx" class="os-item-row">
                    <div class="item-desc">
                      <span class="qty">{{ item.quantidade }}x</span>
                      <span class="name">{{ item.descricao_item }}</span>
                    </div>
                    <div class="item-val">{{ formatCurrency(item.valor_unitario * item.quantidade) }}</div>
                  </div>

                  <div v-if="form.desconto > 0" class="os-item-row discount-line">
                    <div class="item-desc">
                      <span class="qty">-</span>
                      <span class="name">Desconto Aplicado</span>
                    </div>
                    <div class="item-val text-discount">{{ formatCurrency(-form.desconto) }}</div>
                  </div>
                </div>
              </div>

              <div class="field-group full-width">
                <label>OBSERVAÇÕES DE FÁBRICA</label>
                <textarea v-model="form.observacoes" class="custom-input" rows="3" :disabled="isLocked"></textarea>
              </div>
            </div>

            <div class="os-financial-footer">
              <div class="fin-block">
                <span>SUBTOTAL</span>
                <strong>{{ formatCurrency(subtotalItems) }}</strong>
              </div>
              <div class="fin-block">
                <span>DESCONTO</span>
                <input type="number" v-model.number="form.desconto" class="mini-input" :disabled="isLocked" />
              </div>
              <div class="fin-block total">
                <span>TOTAL FINAL</span>
                <strong>{{ formatCurrency(form.valor_total) }}</strong>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <div class="footer-actions-left">
              <button class="btn-action-alt" @click="emitReceipt" :disabled="!isEditing">EMITIR RECIBO</button>
              <button class="btn-action-alt" @click="form.nf_emitida ? downloadNFe() : emitNFe()" :disabled="!isEditing">
                {{ form.nf_emitida ? 'BAIXAR NFE' : 'EMITIR NFE' }}
              </button>
            </div>
            <div class="footer-actions-right">
              <button class="btn-sec" @click="closeModal">FECHAR</button>
              <button class="btn-pri" @click="saveOrder" :disabled="saving || isLocked">
                {{ saving ? 'SALVANDO...' : 'ATUALIZAR O.S.' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="notify.show" class="custom-alert-overlay" @click="notify.show = false">
        <div class="alert-box" :class="notify.type">
          <div class="alert-icon">{{ notify.type === 'error' ? '✕' : '✓' }}</div>
          <div class="alert-content">
            <h4>{{ notify.title }}</h4>
            <p>{{ notify.message }}</p>
          </div>
          <button class="btn-close-alert" @click="notify.show = false">OK</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, reactive } from 'vue';
import { api } from '../services/api';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import logoImg from '../logo.png';

const viewMode = ref('kanban');
const ordens = ref([]);
const draggedOrder = ref(null);
const showModal = ref(false);
const isEditing = ref(false);
const saving = ref(false);
const form = ref(null);
const dbClients = ref([]);

const notify = reactive({ show: false, title: '', message: '', type: 'success' });

const triggerNotify = (title, message, type = 'success') => {
  notify.title = title; notify.message = message; notify.type = type; notify.show = true;
};

const loadData = async () => {
  try {
    const [resOrdens, resClientes] = await Promise.all([api.get('/ordens'), api.get('/clientes')]);
    ordens.value = resOrdens; dbClients.value = resClientes;
  } catch (e) {
    triggerNotify('Erro de Conexão', 'Não foi possível carregar os dados.', 'error');
  }
};

onMounted(loadData);

const columns = computed(() => {
  const statusMap = { pending: 'Pendente', late: 'Pendente', production: 'Em Produção', completed: 'Concluído', billed: 'NFe Emitida' };
  const grouped = ordens.value.reduce((acc, order) => {
    const status = statusMap[order.status] || 'Pendente';
    if (!acc[status]) acc[status] = [];
    acc[status].push(order);
    return acc;
  }, {});
  return [
    { title: 'Pendente', orders: grouped['Pendente'] || [], color: '#f39c12' },
    { title: 'Em Produção', orders: grouped['Em Produção'] || [], color: '#56a6c1' },
    { title: 'NFe Emitida', orders: grouped['NFe Emitida'] || [], color: '#9b59b6' },
    { title: 'Concluído', orders: grouped['Concluído'] || [], color: '#2ecc71' }
  ];
});

const getStatusLabel = (status) => {
  const labels = { pending: 'Pendente', production: 'Produção', completed: 'Concluído', billed: 'NFe Emitida', late: 'Atrasado' };
  return labels[status] || status;
};

const subtotalItems = computed(() => {
  if (!form.value || !form.value.items) return 0;
  return form.value.items.reduce((total, item) => total + (item.quantidade * item.valor_unitario), 0);
});

const isLocked = computed(() => isEditing.value && form.value?.status === 'billed');

watch(() => (form.value ? [form.value.items, form.value.desconto] : null), () => {
  if (form.value) { form.value.valor_total = subtotalItems.value - (parseFloat(form.value.desconto) || 0); }
}, { deep: true });

const openModal = (order = null) => {
  if (order) {
    isEditing.value = true;
    form.value = JSON.parse(JSON.stringify(order));
    form.value.items = form.value.itens_ordem || form.value.items || [];
    form.value.desconto = parseFloat(form.value.desconto) || 0;
    form.value.nf_emitida = !!form.value.nf_emitida;
    form.value.link_nf = form.value.link_nf || "";
  } else {
    isEditing.value = false;
    form.value = { id: null, cliente_id: "", status: 'pending', observacoes: '', items: [], desconto: 0, valor_total: 0, nf_emitida: false, link_nf: "" };
  }
  showModal.value = true;
};

const closeModal = () => { showModal.value = false; form.value = null; };

const saveOrder = async () => {
  saving.value = true;
  try {
    const payload = { ...form.value, desconto: parseFloat(form.value.desconto) || 0, itens_ordem: form.value.items };
    if (isEditing.value) { await api.put(`/ordens/${form.value.id}`, payload); }
    else { await api.post('/ordens', payload); }
    await loadData(); closeModal(); triggerNotify('Sucesso', 'Ordem de serviço salva.', 'success');
  } catch (e) { triggerNotify('Erro ao Salvar', e.message, 'error'); }
  finally { saving.value = false; }
};

const onDragStart = (order) => { draggedOrder.value = order; };

const onDrop = async (targetColumnTitle) => {
  if (!draggedOrder.value) return;
  const titleToStatus = { 'Pendente': 'pending', 'Em Produção': 'production', 'Concluído': 'completed', 'NFe Emitida': 'billed' };
  const newStatus = titleToStatus[targetColumnTitle];
  const oldStatus = draggedOrder.value.status;
  if (oldStatus === newStatus) return;
  const orderIndex = ordens.value.findIndex(o => o.id === draggedOrder.value.id);
  if (orderIndex !== -1) { ordens.value[orderIndex].status = newStatus; }
  try { await api.patch(`/ordens/${draggedOrder.value.id}/status`, { status: newStatus }); }
  catch (e) {
    if (orderIndex !== -1) { ordens.value[orderIndex].status = oldStatus; }
    triggerNotify('Erro ao Mover', 'Não foi possível atualizar o status.', 'error');
  }
  draggedOrder.value = null;
};

const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);

const generateDanfePdf = (xmlString) => {
  const parser = new DOMParser();
  const xml = parser.parseFromString(xmlString, "application/xml");
  const doc = new jsPDF('p', 'mm', 'a4');

  const getText = (tag, parent = xml) => parent.getElementsByTagName(tag)[0]?.textContent || "";

  const nNF = getText("nNF") || "000.000.000";
  const serie = getText("serie") || "0";
  const chave = xml.getElementsByTagName("infNFe")[0]?.getAttribute("Id")?.replace("NFe", "") || "".padEnd(44, "0");
  const nProt = getText("nProt");
  const dhEmiFull = getText("dhEmi");
  const dhEmi = dhEmiFull ? dhEmiFull.split("T")[0].split("-").reverse().join("/") : "";
  const dhSai = dhEmi;

  const emitNome = getText("xNome", xml.getElementsByTagName("emit")[0]) || "LUCAS ABRAAO NERI DE MELO";
  const emitCNPJ = getText("CNPJ", xml.getElementsByTagName("emit")[0]) || "55.952.245/0001-00";
  const emitIE = getText("IE", xml.getElementsByTagName("emit")[0]) || "201690195";
  const enderEmit = xml.getElementsByTagName("enderEmit")[0];
  const emitLgr = enderEmit ? getText("xLgr", enderEmit) : "AVENIDA 21 DE ABRIL, SN-QD 05 LT 10/11";
  const emitBairro = enderEmit ? getText("xBairro", enderEmit) : "SETOR SOLON AMARAL";
  const emitMun = enderEmit ? getText("xMun", enderEmit) : "Iaciara";
  const emitUF = enderEmit ? getText("UF", enderEmit) : "GO";

  const destNode = xml.getElementsByTagName("dest")[0];
  const destNome = getText("xNome", destNode);
  const destCNPJ = getText("CNPJ", destNode) || getText("CPF", destNode);
  const enderDest = destNode?.getElementsByTagName("enderDest")[0];
  const destLgr = enderDest ? `${getText("xLgr", enderDest)}, ${getText("nro", enderDest)}` : "";
  const destBairro = getText("xBairro", enderDest);
  const destMun = getText("xMun", enderDest);
  const destUF = getText("UF", enderDest);
  const destCEP = getText("CEP", enderDest);
  const destFone = getText("fone", enderDest);

  const natOp = getText("natOp") || "VENDAS";
  const icmsTot = xml.getElementsByTagName("ICMSTot")[0];
  const vBC = getText("vBC", icmsTot) || "0.00";
  const vICMS = getText("vICMS", icmsTot) || "0.00";
  const vBCST = getText("vBCST", icmsTot) || "0.00";
  const vST = getText("vST", icmsTot) || "0.00";
  const vProd = getText("vProd", icmsTot) || "0.00";
  const vFrete = getText("vFrete", icmsTot) || "0.00";
  const vSeg = getText("vSeg", icmsTot) || "0.00";
  const vDesc = getText("vDesc", icmsTot) || "0.00";
  const vOutro = getText("vOutro", icmsTot) || "0.00";
  const vIPI = getText("vIPI", icmsTot) || "0.00";
  const vNF = getText("vNF", icmsTot) || "0.00";

  const x = 5;
  let y = 5;

  doc.setLineWidth(0.2);
  doc.rect(x, y, 160, 15);
  doc.rect(x+160, y, 40, 15);
  doc.setFontSize(6);
  doc.setFont("helvetica", "normal");
  doc.text(`RECEBEMOS DE ${emitNome} OS PRODUTOS E/OU SERVIÇOS CONSTANTES DA NOTA FISCAL ELETRÔNICA INDICADA AO LADO`, x+2, y+3, { maxWidth: 156 });
  doc.line(x, y+6, x+160, y+6);
  doc.text("DATA DE RECEBIMENTO", x+2, y+9);
  doc.line(x+35, y+6, x+35, y+15);
  doc.text("IDENTIFICAÇÃO E ASSINATURA DO RECEBEDOR", x+37, y+9);
  doc.setFontSize(8);
  doc.setFont("helvetica", "bold");
  doc.text("NF-e", x+162, y+6);
  doc.setFontSize(10);
  doc.text(`Nº ${nNF}`, x+162, y+10);
  doc.text(`SÉRIE ${serie}`, x+162, y+14);

  y += 18;
  doc.line(x, y, x+200, y);

  y += 2;
  doc.rect(x, y, 85, 30);
  doc.addImage(logoImg, 'PNG', x+2, y+2, 20, 20);
  doc.setFontSize(8);
  doc.setFont("helvetica", "bold");
  doc.text(emitNome, x+25, y+5, { maxWidth: 60 });
  doc.setFontSize(6);
  doc.setFont("helvetica", "normal");
  doc.text(`${emitLgr}`, x+25, y+12, { maxWidth: 60 });
  doc.text(`${emitBairro} - ${emitMun}, ${emitUF}`, x+25, y+15, { maxWidth: 60 });

  doc.rect(x+85, y, 30, 30);
  doc.setFontSize(10);
  doc.setFont("helvetica", "bold");
  doc.text("DANFE", x+87, y+5);
  doc.setFontSize(6);
  doc.setFont("helvetica", "normal");
  doc.text("Documento Auxiliar da", x+87, y+8);
  doc.text("Nota Fiscal Eletrônica", x+87, y+11);
  doc.setFontSize(7);
  doc.text("0 - Entrada", x+87, y+15);
  doc.text("1 - Saída", x+87, y+18);
  doc.rect(x+105, y+13, 5, 5);
  doc.setFontSize(8);
  doc.setFont("helvetica", "bold");
  doc.text("1", x+106, y+17);
  doc.text(`Nº ${nNF}`, x+87, y+23);
  doc.text(`SÉRIE: ${serie}`, x+87, y+26);
  doc.text("Página 1 de 1", x+87, y+29);

  doc.rect(x+115, y, 85, 30);
  doc.setFontSize(6);
  doc.setFont("helvetica", "normal");
  doc.text("CONTROLE DO FISCO", x+117, y+4);

  doc.rect(x+117, y+6, 80, 10);
  doc.setFontSize(10);
  doc.text("||| |||| || ||| ||||| ||| ||", x+140, y+13);

  doc.setFontSize(6);
  doc.text("CHAVE DE ACESSO", x+117, y+20);
  doc.setFontSize(8);
  doc.setFont("helvetica", "bold");
  const formattedChave = chave.replace(/(.{4})/g, '$1 ').trim();
  doc.text(formattedChave, x+117, y+24);
  doc.setFontSize(6);
  doc.setFont("helvetica", "normal");
  doc.text("Consulta de autenticidade no portal nacional da NF-e", x+117, y+27);
  doc.text("www.nfe.fazenda.gov.br/portal ou no site da Sefaz Autorizadora", x+117, y+29);

  y += 30;
  doc.rect(x, y, 105, 8);
  doc.setFontSize(6);
  doc.text("NATUREZA DA OPERAÇÃO", x+2, y+3);
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text(natOp, x+2, y+7);

  doc.rect(x+105, y, 95, 8);
  doc.setFontSize(6);
  doc.setFont("helvetica", "normal");
  doc.text("PROTOCOLO DE AUTORIZAÇÃO DE USO", x+107, y+3);
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text(nProt || "", x+107, y+7);

  y += 8;
  doc.rect(x, y, 65, 8);
  doc.setFontSize(6);
  doc.setFont("helvetica", "normal");
  doc.text("INSCRIÇÃO ESTADUAL", x+2, y+3);
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text(emitIE, x+2, y+7);

  doc.rect(x+65, y, 65, 8);
  doc.setFontSize(6);
  doc.setFont("helvetica", "normal");
  doc.text("INSCRIÇÃO ESTADUAL DO SUBST. TRIB.", x+67, y+3);

  doc.rect(x+130, y, 70, 8);
  doc.text("CNPJ / CPF", x+132, y+3);
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text(emitCNPJ, x+132, y+7);

  y += 10;
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text("DESTINATÁRIO / REMETENTE", x, y);
  y += 2;
  doc.rect(x, y, 120, 8);
  doc.setFontSize(5);
  doc.setFont("helvetica", "normal");
  doc.text("NOME / RAZÃO SOCIAL", x+2, y+3);
  doc.setFontSize(7);
  doc.text(destNome, x+2, y+7);

  doc.rect(x+120, y, 50, 8);
  doc.setFontSize(5);
  doc.text("CNPJ / CPF", x+122, y+3);
  doc.setFontSize(7);
  doc.text(destCNPJ, x+122, y+7);

  doc.rect(x+170, y, 30, 8);
  doc.setFontSize(5);
  doc.text("DATA DA EMISSÃO", x+172, y+3);
  doc.setFontSize(7);
  doc.text(dhEmi, x+172, y+7);

  y += 8;
  doc.rect(x, y, 90, 8);
  doc.setFontSize(5);
  doc.text("ENDEREÇO", x+2, y+3);
  doc.setFontSize(7);
  doc.text(destLgr, x+2, y+7);

  doc.rect(x+90, y, 45, 8);
  doc.setFontSize(5);
  doc.text("BAIRRO / DISTRITO", x+92, y+3);
  doc.setFontSize(7);
  doc.text(destBairro, x+92, y+7);

  doc.rect(x+135, y, 35, 8);
  doc.setFontSize(5);
  doc.text("CEP", x+137, y+3);
  doc.setFontSize(7);
  doc.text(destCEP, x+137, y+7);

  doc.rect(x+170, y, 30, 8);
  doc.setFontSize(5);
  doc.text("DATA DE ENTRADA / SAÍDA", x+172, y+3);
  doc.setFontSize(7);
  doc.text(dhSai, x+172, y+7);

  y += 8;
  doc.rect(x, y, 90, 8);
  doc.setFontSize(5);
  doc.text("MUNICÍPIO", x+2, y+3);
  doc.setFontSize(7);
  doc.text(destMun, x+2, y+7);

  doc.rect(x+90, y, 15, 8);
  doc.setFontSize(5);
  doc.text("UF", x+92, y+3);
  doc.setFontSize(7);
  doc.text(destUF, x+92, y+7);

  doc.rect(x+105, y, 30, 8);
  doc.setFontSize(5);
  doc.text("FONE / FAX", x+107, y+3);
  doc.setFontSize(7);
  doc.text(destFone, x+107, y+7);

  doc.rect(x+135, y, 35, 8);
  doc.setFontSize(5);
  doc.text("INSCRIÇÃO ESTADUAL", x+137, y+3);

  doc.rect(x+170, y, 30, 8);
  doc.setFontSize(5);
  doc.text("HORA DE ENTRADA / SAÍDA", x+172, y+3);

  y += 10;
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text("CÁLCULO DO IMPOSTO", x, y);
  y += 2;
  let wI = 200 / 7;
  doc.rect(x, y, wI, 8); doc.setFontSize(5); doc.setFont("helvetica","normal"); doc.text("BASE DE CÁLCULO DO ICMS", x+2, y+3); doc.setFontSize(7); doc.text(vBC, x+2, y+7);
  doc.rect(x+wI, y, wI, 8); doc.setFontSize(5); doc.text("VALOR DO ICMS", x+wI+2, y+3); doc.setFontSize(7); doc.text(vICMS, x+wI+2, y+7);
  doc.rect(x+wI*2, y, wI, 8); doc.setFontSize(5); doc.text("BASE DE CÁLCULO DO ICMS ST", x+wI*2+2, y+3); doc.setFontSize(7); doc.text(vBCST, x+wI*2+2, y+7);
  doc.rect(x+wI*3, y, wI, 8); doc.setFontSize(5); doc.text("VALOR DO ICMS ST", x+wI*3+2, y+3); doc.setFontSize(7); doc.text(vST, x+wI*3+2, y+7);
  doc.rect(x+wI*4, y, wI*3, 8); doc.setFontSize(5); doc.text("VALOR TOTAL DOS PRODUTOS", x+wI*4+2, y+3); doc.setFontSize(7); doc.text(vProd, x+wI*4+2, y+7);

  y += 8;
  doc.rect(x, y, wI, 8); doc.setFontSize(5); doc.text("VALOR DO FRETE", x+2, y+3); doc.setFontSize(7); doc.text(vFrete, x+2, y+7);
  doc.rect(x+wI, y, wI, 8); doc.setFontSize(5); doc.text("VALOR DO SEGURO", x+wI+2, y+3); doc.setFontSize(7); doc.text(vSeg, x+wI+2, y+7);
  doc.rect(x+wI*2, y, wI, 8); doc.setFontSize(5); doc.text("DESCONTO", x+wI*2+2, y+3); doc.setFontSize(7); doc.text(vDesc, x+wI*2+2, y+7);
  doc.rect(x+wI*3, y, wI, 8); doc.setFontSize(5); doc.text("OUTRAS DESPESAS ACESSÓRIAS", x+wI*3+2, y+3); doc.setFontSize(7); doc.text(vOutro, x+wI*3+2, y+7);
  doc.rect(x+wI*4, y, wI, 8); doc.setFontSize(5); doc.text("VALOR DO IPI", x+wI*4+2, y+3); doc.setFontSize(7); doc.text(vIPI, x+wI*4+2, y+7);
  doc.rect(x+wI*5, y, wI*2, 8); doc.setFontSize(5); doc.text("VALOR TOTAL DA NOTA", x+wI*5+2, y+3); doc.setFontSize(7); doc.setFont("helvetica","bold"); doc.text(vNF, x+wI*5+2, y+7);

  y += 10;
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text("TRANSPORTADOR / VOLUMES TRANSPORTADOS", x, y);
  y += 2;
  doc.rect(x, y, 90, 8); doc.setFontSize(5); doc.setFont("helvetica","normal"); doc.text("RAZÃO SOCIAL", x+2, y+3);
  doc.rect(x+90, y, 30, 8); doc.text("FRETE POR CONTA", x+92, y+3); doc.setFontSize(6); doc.text("9 - Sem Frete", x+92, y+7); doc.setFontSize(5);
  doc.rect(x+120, y, 20, 8); doc.text("CÓDIGO ANTT", x+122, y+3);
  doc.rect(x+140, y, 20, 8); doc.text("PLACA DO VEÍCULO", x+142, y+3);
  doc.rect(x+160, y, 10, 8); doc.text("UF", x+162, y+3);
  doc.rect(x+170, y, 30, 8); doc.text("CNPJ / CPF", x+172, y+3);

  y += 8;
  doc.rect(x, y, 90, 8); doc.text("ENDEREÇO", x+2, y+3);
  doc.rect(x+90, y, 50, 8); doc.text("MUNICÍPIO", x+92, y+3);
  doc.rect(x+140, y, 20, 8); doc.text("UF", x+142, y+3);
  doc.rect(x+160, y, 40, 8); doc.text("INSCRIÇÃO ESTADUAL", x+162, y+3);

  y += 8;
  doc.rect(x, y, 25, 8); doc.text("QUANTIDADE", x+2, y+3);
  doc.rect(x+25, y, 40, 8); doc.text("ESPÉCIE", x+27, y+3);
  doc.rect(x+65, y, 40, 8); doc.text("MARCA", x+67, y+3);
  doc.rect(x+105, y, 35, 8); doc.text("NUMERAÇÃO", x+107, y+3);
  doc.rect(x+140, y, 30, 8); doc.text("PESO BRUTO", x+142, y+3);
  doc.rect(x+170, y, 30, 8); doc.text("PESO LÍQUIDO", x+172, y+3);

  y += 10;
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text("DADOS DO PRODUTO / SERVIÇO", x, y);

  const itens = Array.from(xml.getElementsByTagName("det")).map(det => {
    const prod = det.getElementsByTagName("prod")[0];
    const imposto = det.getElementsByTagName("imposto")[0];
    const icms = imposto?.getElementsByTagName("ICMS")[0];
    const ipi = imposto?.getElementsByTagName("IPI")[0];

    const cProd = getText("cProd", prod);
    const xProd = getText("xProd", prod);
    const ncm = getText("NCM", prod);
    const cfop = getText("CFOP", prod);
    const uCom = getText("uCom", prod);
    const qCom = parseFloat(getText("qCom", prod) || 0).toFixed(4);
    const vUnCom = parseFloat(getText("vUnCom", prod) || 0).toFixed(4);
    const vProdItem = parseFloat(getText("vProd", prod) || 0).toFixed(2);

    const cst = getText("CST", icms) || getText("CSOSN", icms) || "000";
    const vBCItem = getText("vBC", icms) || "0.00";
    const vICMSItem = getText("vICMS", icms) || "0.00";
    const vIPIItem = getText("vIPI", ipi) || "0.00";
    const pICMS = getText("pICMS", icms) || "0.00";
    const pIPI = getText("pIPI", ipi) || "0.00";

    return [
      cProd, xProd, ncm, cst, cfop, uCom, qCom, vUnCom, vProdItem, vBCItem, vICMSItem, vIPIItem, pICMS, pIPI
    ];
  });

  autoTable(doc, {
    startY: y + 2,
    margin: { left: x, right: x },
    head: [['CÓDIGO', 'DESCRIÇÃO DO PRODUTO / SERVIÇO', 'NCM/SH', 'CST', 'CFOP', 'UNID', 'QTD', 'VLR. UNIT', 'VLR. TOTAL', 'BC ICMS', 'VLR. ICMS', 'VLR. IPI', 'ALÍQ. ICMS', 'ALÍQ. IPI']],
    body: itens,
    theme: 'grid',
    styles: { fontSize: 5, cellPadding: 1, lineColor: [0, 0, 0], lineWidth: 0.2 },
    headStyles: { fillColor: false, textColor: [0, 0, 0], fontStyle: 'normal', halign: 'center', valign: 'middle' },
    columnStyles: {
      0: { cellWidth: 15 },
      1: { cellWidth: 'auto' },
      2: { cellWidth: 12 },
      3: { cellWidth: 8 },
      4: { cellWidth: 8 },
      5: { cellWidth: 8 },
      6: { cellWidth: 12, halign: 'right' },
      7: { cellWidth: 12, halign: 'right' },
      8: { cellWidth: 12, halign: 'right' },
      9: { cellWidth: 10, halign: 'right' },
      10: { cellWidth: 10, halign: 'right' },
      11: { cellWidth: 10, halign: 'right' },
      12: { cellWidth: 10, halign: 'right' },
      13: { cellWidth: 10, halign: 'right' }
    }
  });

  const finalY = doc.lastAutoTable.finalY + 5;
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text("CÁLCULO DO ISSQN", x, finalY);
  doc.rect(x, finalY + 2, 50, 8); doc.setFontSize(5); doc.setFont("helvetica","normal"); doc.text("INSCRIÇÃO MUNICIPAL", x+2, finalY+5);
  doc.rect(x+50, finalY + 2, 50, 8); doc.text("VALOR TOTAL DOS SERVIÇOS", x+52, finalY+5);
  doc.rect(x+100, finalY + 2, 50, 8); doc.text("BASE DE CÁLCULO DO ISSQN", x+102, finalY+5);
  doc.rect(x+150, finalY + 2, 50, 8); doc.text("VALOR DO ISSQN", x+152, finalY+5);

  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text("DADOS ADICIONAIS", x, finalY + 15);
  doc.rect(x, finalY + 17, 130, 25); doc.setFontSize(5); doc.setFont("helvetica","normal"); doc.text("INFORMAÇÕES COMPLEMENTARES", x+2, finalY+20);
  const infAdic = xml.getElementsByTagName("infAdic")[0];
  const infCpl = infAdic ? getText("infCpl", infAdic) : "";
  if (infCpl) {
    doc.setFontSize(6);
    const splitInfCpl = doc.splitTextToSize(infCpl, 126);
    doc.text(splitInfCpl, x+2, finalY+24);
  }
  doc.rect(x+130, finalY + 17, 70, 25); doc.setFontSize(5); doc.text("RESERVADO AO FISCO", x+132, finalY+20);

  doc.save(`DANFE_NFe_${nNF}.pdf`);
};

const emitNFe = async () => {
  try {
    const payload = {
      cliente_id: form.value.cliente_id,
      ordem_id: form.value.id,
      valor_servico: form.value.valor_total,
      discriminacao: form.value.items.map(i => `${i.quantidade}x ${i.descricao_item}`).join(' | ')
    };
    const res = await api.post('/nfe/emitir', payload);
    if (res.protocolo_sefaz) {
      form.value.link_nf = res.protocolo_sefaz;
      form.value.nf_emitida = true;
      form.value.status = 'billed';
      await api.put(`/ordens/${form.value.id}`, { ...form.value, desconto: parseFloat(form.value.desconto) || 0, itens_ordem: form.value.items });
      generateDanfePdf(res.protocolo_sefaz);
    }
    await loadData(); closeModal(); triggerNotify('Sucesso', 'NF-e Autorizada e DANFE gerada.', 'success');
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.message;
    triggerNotify('Erro na NF-e', errorMsg, 'error');
  }
};

const downloadNFe = () => {
  if (form.value.link_nf) {
    generateDanfePdf(form.value.link_nf);
    const blob = new Blob([form.value.link_nf], { type: 'application/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `NFe_${form.value.id}.xml`;
    a.click();
    URL.revokeObjectURL(url);
  } else {
    triggerNotify('Erro', 'XML da nota não encontrado.', 'error');
  }
};

const emitReceipt = () => {
  const doc = new jsPDF();
  const client = dbClients.value.find(c => c.id === form.value.cliente_id) || { nome: 'Consumidor' };
  doc.setDrawColor(86, 166, 193); doc.setLineWidth(0.5); doc.rect(10, 10, 190, 40);
  doc.addImage(logoImg, 'PNG', 15, 15, 35, 30);
  doc.setFontSize(16); doc.setFont('helvetica', 'bold'); doc.text('RECIBO DE PRESTAÇÃO DE SERVIÇO', 60, 25);
  doc.setFontSize(10); doc.setFont('helvetica', 'normal');
  doc.text('WK VIDROS - Lucas Abraao Neri de Melo', 60, 32);
  doc.text('CNPJ: 55.952.245/0001-00', 60, 37);
  doc.text('Avenida 21 de Abril - Telefone: (62) 99876-6290', 60, 42);
  doc.setFont('helvetica', 'bold'); doc.text('DADOS DO CLIENTE', 10, 60); doc.line(10, 62, 200, 62);
  doc.setFont('helvetica', 'normal'); doc.text(`NOME: ${client.nome}`, 10, 68);
  doc.text(`CPF/CNPJ: ${client.documento || '---'}`, 10, 73);
  doc.text(`O.S. Nº: ${form.value.id}`, 140, 73);
  const rows = form.value.items.map(i => [i.descricao_item, i.quantidade, formatCurrency(i.valor_unitario), formatCurrency(i.quantidade * i.valor_unitario)]);
  autoTable(doc, { startY: 85, head: [['Descrição', 'Qtd', 'Unitário', 'Total']], body: rows, theme: 'grid', headStyles: { fillColor: [86, 166, 193] } });
  const finalY = doc.lastAutoTable.finalY + 10;
  doc.setFont('helvetica', 'bold'); doc.text(`TOTAL PAGO: ${formatCurrency(form.value.valor_total)}`, 140, finalY + 12);
  doc.save(`Recibo_OS_${form.value.id}.pdf`);
};
</script>

<style scoped>
.board-container { padding: 24px; background: #f8fafc; min-height: 100vh; }
.board-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; gap: 20px; flex-wrap: wrap; }
.header-info h1 { font-size: 1.5rem; font-weight: 900; color: #1e293b; margin: 0; }
.header-info p { color: #64748b; font-size: 0.9rem; margin-top: 4px; }
.header-controls { display: flex; gap: 16px; align-items: center; }
.view-switch { background: #e2e8f0; padding: 4px; border-radius: 12px; display: flex; }
.view-switch button { border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; font-weight: 600; background: transparent; color: #64748b; transition: 0.3s; }
.view-switch button.active { background: #fff; color: #56a6c1; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
.btn-primary-action { background: #56a6c1; color: #fff; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; box-shadow: 0 10px 15px -3px rgba(86,166,193,0.3); }
.kanban-container { display: flex; gap: 20px; overflow-x: auto; padding-bottom: 20px; }
.kanban-column { min-width: 300px; flex: 1; background: #f1f5f9; border-radius: 16px; display: flex; flex-direction: column; max-height: 80vh; }
.column-title { padding: 16px; display: flex; align-items: center; gap: 10px; border-top: 4px solid; background: rgba(255,255,255,0.5); border-radius: 16px 16px 0 0; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.column-title h3 { font-size: 0.8rem; font-weight: 800; color: #475569; margin: 0; text-transform: uppercase; }
.badge-count { margin-left: auto; background: #fff; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; color: #94a3b8; }
.column-cards { padding: 12px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 12px; }
.service-card { background: #fff; padding: 16px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); cursor: pointer; border: 1px solid transparent; transition: 0.2s; }
.service-card:hover { transform: translateY(-2px); border-color: #56a6c1; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
.card-top { display: flex; justify-content: space-between; margin-bottom: 12px; }
.os-number { font-size: 0.75rem; font-weight: 800; color: #cbd5e1; }
.tag-late { background: #fee2e2; color: #ef4444; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: 800; }
.client-name { font-size: 0.95rem; color: #1e293b; margin: 0 0 16px 0; font-weight: 700; }
.card-bottom { display: flex; justify-content: space-between; align-items: center; }
.total-price { color: #56a6c1; font-weight: 900; font-size: 1.1rem; }
.icon-drag { color: #e2e8f0; font-size: 1.2rem; }
.table-view-wrapper { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #edf2f7; }
.modern-grid { width: 100%; border-collapse: collapse; }
.modern-grid th { text-align: left; padding: 16px; color: #94a3b8; font-size: 0.75rem; border-bottom: 1px solid #f1f5f9; text-transform: uppercase; font-weight: 800; }
.modern-grid td { padding: 16px; border-bottom: 1px solid #f8fafc; font-size: 0.9rem; color: #1e293b; }
.row-hover:hover { background-color: #f8fafc; }
.status-tag { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; }
.status-tag.pending { background: #fef3c7; color: #d97706; }
.status-tag.production { background: #e0f2fe; color: #0284c7; }
.status-tag.completed { background: #dcfce7; color: #16a34a; }
.status-tag.billed { background: #f3e8ff; color: #9333ea; }
.btn-edit-small { background: #56a6c1; border: none; padding: 8px 16px; border-radius: 8px; color: #fff; font-weight: 800; cursor: pointer; font-size: 0.7rem; }
.text-right { text-align: right; }
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal-card { background: #fff; width: 100%; max-width: 650px; border-radius: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); display: flex; flex-direction: column; max-height: 95vh; }
.modal-header { padding: 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.modal-body { padding: 24px; overflow-y: auto; flex: 1; }
.modal-footer { padding: 20px 24px; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.close-x { background: transparent; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
.footer-actions-left, .footer-actions-right { display: flex; gap: 12px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.field-group { display: flex; flex-direction: column; gap: 8px; }
.full-width { grid-column: span 2; }
.custom-input { background: #f8fafc; border: 1.5px solid #e2e8f0; padding: 12px; border-radius: 12px; font-size: 0.9rem; outline: none; transition: 0.2s; color: #1e293b; }
.custom-input:focus { border-color: #56a6c1; background: #fff; box-shadow: 0 0 0 4px rgba(86,166,193,0.1); }
.header-title { display: flex; align-items: center; gap: 12px; }
.os-id-badge { background: #f1f5f9; color: #56a6c1; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 900; }
.items-summary-section { margin: 20px 0; background: #f8fafc; padding: 20px; border-radius: 16px; border: 1px solid #e2e8f0; }
.section-title { font-size: 0.7rem; font-weight: 900; color: #94a3b8; margin-bottom: 15px; letter-spacing: 1px; }
.os-item-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
.item-desc { display: flex; gap: 10px; font-size: 0.9rem; }
.qty { color: #56a6c1; font-weight: 900; }
.name { color: #1e293b; font-weight: 600; }
.item-val { font-weight: 800; color: #64748b; font-size: 0.9rem; }
.os-financial-footer { display: grid; grid-template-columns: 1fr 1fr 1.5fr; gap: 20px; margin-top: 30px; padding-top: 20px; border-top: 2px solid #f1f5f9; }
.fin-block { display: flex; flex-direction: column; gap: 5px; }
.fin-block span { font-size: 0.65rem; font-weight: 800; color: #94a3b8; }
.fin-block strong { font-size: 1.1rem; color: #1e293b; }
.fin-block.total strong { color: #56a6c1; font-size: 1.4rem; font-weight: 950; }
.mini-input { background: #fff; border: 1px solid #cbd5e1; padding: 8px; border-radius: 8px; font-weight: 800; color: #ef4444; width: 100px; outline: none; }
.btn-pri { background: #1e293b; color: #fff; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.2s; }
.btn-pri:hover { background: #0f172a; }
.btn-pri:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-sec { background: transparent; color: #94a3b8; border: none; font-weight: 700; cursor: pointer; padding: 12px; }
.btn-action-alt { background: #fff; border: 1px solid #e2e8f0; color: #56a6c1; padding: 10px 16px; border-radius: 10px; font-weight: 700; font-size: 0.7rem; cursor: pointer; transition: 0.2s; }
.btn-action-alt:hover:not(:disabled) { background: #f8fafc; border-color: #56a6c1; }
.btn-action-alt:disabled { opacity: 0.5; cursor: not-allowed; }
.custom-alert-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); z-index: 2000; display: flex; align-items: center; justify-content: center; }
.alert-box { background: #fff; padding: 32px; border-radius: 24px; max-width: 400px; width: 90%; text-align: center; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.alert-icon { width: 50px; height: 50px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold; }
.success .alert-icon { background: #dcfce7; color: #16a34a; }
.error .alert-icon { background: #fee2e2; color: #ef4444; }
.alert-content h4 { font-size: 1.2rem; color: #1e293b; margin-bottom: 10px; }
.alert-content p { color: #64748b; margin-bottom: 24px; line-height: 1.5; }
.btn-close-alert { width: 100%; background: #1e293b; color: #fff; border: none; padding: 12px; border-radius: 12px; font-weight: 800; cursor: pointer; }
.discount-line { border-top: 1px dashed #e2e8f0; margin-top: 5px; }
.text-discount { color: #ef4444 !important; font-weight: 900; }
@media (max-width: 768px) {
  .modal-footer { flex-direction: column; height: auto; padding: 16px; gap: 16px; }
  .footer-actions-left, .footer-actions-right { width: 100%; justify-content: center; }
  .btn-action-alt, .btn-pri, .btn-sec { flex: 1; font-size: 0.65rem; }
}
</style>