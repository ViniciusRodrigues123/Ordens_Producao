// URL base da API Flask
const API_URL = 'http://127.0.0.1:5000';

// Variável global para sabermos se estamos criando ou editando
let idEmEdicao = null; 

// 1. VERIFICAR STATUS (GET)
async function verificarStatus() {
    const badge = document.getElementById('status-badge');
    try {
        const res = await fetch(`${API_URL}/status`);
        if(res.ok) {
            const data = await res.json();
            badge.innerText = `🟢 API ONLINE (${data.versao})`;
            badge.style.background = '#bbf7d0'; badge.style.color = '#166534'; badge.style.borderColor = '#86efac';
        }
    } catch (error) {
        badge.innerText = '🔴 API OFFLINE';
        badge.style.background = '#fecaca'; badge.style.color = '#991b1b'; badge.style.borderColor = '#f87171';
    }
}

// 2. BUSCAR ORDENS NO BANCO (GET)
async function carregarOrdens() {
    const tbody = document.getElementById('tabela-corpo');
    try {
        const res = await fetch(`${API_URL}/ordens`);
        const ordens = await res.json();
        
        tbody.innerHTML = ''; 
        
        if(ordens.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #a1a1aa; font-style: italic;">Nenhuma ordem no banco de dados.</td></tr>`;
            return;
        }

        ordens.forEach(ordem => {
            let classeStatus = 'status-badge ';
            let textoExibicao = ordem.status; 
            
            if(ordem.status === 'Pendente') classeStatus += 'status-pendente';
            else if(ordem.status === 'Em andamento') classeStatus += 'status-andamento';
            else if(ordem.status === 'Concluida' || ordem.status === 'Concluída') {
                classeStatus += 'status-concluida';
                textoExibicao = 'Concluída'; 
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>#${ordem.id.toString().padStart(4, '0')}</strong></td>
                <td>${ordem.produto}</td>
                <td>${ordem.quantidade}</td>
                <td><span class="${classeStatus}">${textoExibicao}</span></td>
                <td>${ordem.criado_em}</td>
                <td>
                    <button class="btn-edit" onclick="prepararEdicao(${ordem.id}, '${ordem.produto}', ${ordem.quantidade}, '${ordem.status}')">Editar</button>
                    <button class="btn-danger" onclick="excluirOrdemNoBanco(${ordem.id})">Excluir</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #c8102e; font-style: italic;">Erro ao conectar com a API Flask.</td></tr>`;
    }
}

// 3. PREPARAR O FORMULÁRIO PARA EDIÇÃO (NOVA FUNÇÃO)
window.prepararEdicao = function(id, produto, quantidade, status) {
    // Rola a tela para cima suavemente
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Preenche os campos de input com os dados da ordem selecionada
    document.getElementById('input-produto').value = produto;
    document.getElementById('input-qtd').value = quantidade;
    
    // Tratamento do acento para o Select
    let statusSelect = (status === "Concluida") ? "Concluída" : status;
    document.getElementById('input-status').value = statusSelect;

    // Muda o comportamento do sistema para "Modo Edição"
    idEmEdicao = id;
    
    // Muda o estilo e texto do botão principal
    const btn = document.getElementById('btn-cadastrar');
    btn.innerText = 'Salvar Alterações';
    btn.style.background = '#eab308'; // Amarelo/Dourado do Vasco para chamar atenção
    btn.style.boxShadow = '0 4px 12px rgba(234, 179, 8, 0.25)';
    btn.style.color = '#111111';
}

// 4. BOTÃO PRINCIPAL (SERVE PARA CADASTRAR E SALVAR EDIÇÃO)
document.getElementById('btn-cadastrar').addEventListener('click', async function() {
    const produto = document.getElementById('input-produto').value.trim();
    const qtd = document.getElementById('input-qtd').value;
    let status = document.getElementById('input-status').value; 

    if(produto === '' || qtd === '' || qtd <= 0) {
        alert('Preencha os campos corretamente.');
        return;
    }

    // Tratamento do acento para enviar ao Python
    if(status === "Concluída") status = "Concluida";

    const pacoteDeDados = { produto: produto, quantidade: parseInt(qtd), status: status };

    const btn = document.getElementById('btn-cadastrar');
    const textoOriginal = btn.innerText;
    btn.innerText = 'Processando...';

    try {
        let url = `${API_URL}/ordens`;
        let metodo = 'POST'; // Padrão é criar novo

        // MAS, se a variável idEmEdicao não estiver vazia, significa que estamos editando!
        if(idEmEdicao !== null) {
            url = `${API_URL}/ordens/${idEmEdicao}`;
            metodo = 'PUT';
        }

        const res = await fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pacoteDeDados)
        });

        if(res.ok) {
            await carregarOrdens(); 
            
            // Limpa o formulário
            document.getElementById('input-produto').value = '';
            document.getElementById('input-qtd').value = '';
            document.getElementById('input-status').value = 'Pendente';
            
            // Tira o sistema do "Modo Edição" e volta o botão ao normal
            idEmEdicao = null;
            btn.innerText = 'Cadastrar Ordem';
            btn.style.background = '#c8102e';
            btn.style.boxShadow = '0 4px 12px rgba(200, 16, 46, 0.25)';
            btn.style.color = 'white';

        } else {
            alert('Erro no servidor ao processar a ordem.');
        }
    } catch (error) {
        alert('Erro de conexão com a API.');
    } finally {
        if(idEmEdicao === null) btn.innerText = 'Cadastrar Ordem';
    }
});

// 5. EXCLUIR DO BANCO (DELETE)
window.excluirOrdemNoBanco = async function(id) {
    if(confirm(`Tem certeza que deseja apagar permanentemente a Ordem #${id}?`)) {
        try {
            const res = await fetch(`${API_URL}/ordens/${id}`, { method: 'DELETE' });
            if(res.ok) await carregarOrdens(); 
            else alert('Erro ao excluir do servidor.');
        } catch (error) {
            alert('Erro de conexão ao tentar excluir.');
        }
    }
}

// Botoes e Load
document.getElementById('btn-atualizar').addEventListener('click', carregarOrdens);
window.onload = () => { verificarStatus(); carregarOrdens(); };