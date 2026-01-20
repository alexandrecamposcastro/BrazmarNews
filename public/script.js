document.addEventListener('DOMContentLoaded', function() {
    const containerNoticias = document.getElementById('containerNoticias');
    const semNoticias = document.getElementById('semNoticias');
    const contadorNoticias = document.getElementById('contadorNoticias');
    const dataAtualizacao = document.getElementById('dataAtualizacao');
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');
    const modal = document.getElementById('modalNoticia');
    const modalClose = document.getElementById('modalClose');
    const btnAtualizar = document.getElementById('btnAtualizar');
    const btnAtualizar2 = document.getElementById('btnAtualizar2');
    const btnBuscar = document.getElementById('btnBuscar');
    const buscaInput = document.getElementById('buscaInput');
    const ordenarSelect = document.getElementById('ordenarSelect');
    
    // Estado
    let noticias = [];
    let noticiasFiltradas = [];
    let filtroAtual = 'todas';
    let termoBusca = '';
    
    // Palavras-chave para extrair tags
    const PALAVRAS_CHAVE = [
        "porto", "navio", "embarcação", "graneleiro", "petroleiro", "rebocador",
        "praticagem", "ancoradouro", "terminais", "carga", "descarga", "demurrage",
        "arresto", "marinha", "capitania", "antaq", "ibama", "receita federal",
        "óleo", "vazamento", "normam", "lastro", "casco", "afretamento", "itaqui",
        "suape", "operacional", "mercante", "acidente", "desembargo", "complexo"
    ];
    
    init();
    
    function init() {
        setupEventListeners();
        atualizarData();
        carregarNoticias();
    }
    
    function setupEventListeners() {
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }
        
        if (modalClose) {
            modalClose.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }
        
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
        
        if (btnAtualizar) {
            btnAtualizar.addEventListener('click', atualizarNoticias);
        }
        if (btnAtualizar2) {
            btnAtualizar2.addEventListener('click', atualizarNoticias);
        }
        
        document.querySelectorAll('.filtro-tag').forEach(tag => {
            tag.addEventListener('click', function() {
                document.querySelectorAll('.filtro-tag').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                filtroAtual = this.dataset.filtro;
                aplicarFiltrosEBusca();
            });
        });
        
        if (btnBuscar) {
            btnBuscar.addEventListener('click', aplicarBusca);
        }
        if (buscaInput) {
            buscaInput.addEventListener('keyup', function(e) {
                if (e.key === 'Enter') aplicarBusca();
            });
        }
        
        if (ordenarSelect) {
            ordenarSelect.addEventListener('change', aplicarOrdenacao);
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'flex') {
                modal.style.display = 'none';
            }
        });
    }
    
    function atualizarData() {
        const agora = new Date();
        const dataFormatada = agora.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        if (dataAtualizacao) {
            dataAtualizacao.textContent = dataFormatada;
        }
    }
    
    function carregarNoticias() {
        if (containerNoticias) {
            containerNoticias.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Carregando notícias do noticias.json...</p>
                </div>
            `;
        }
        
        fetch('noticias.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Notícias carregadas:', data);
                noticias = Array.isArray(data) ? data : [];
                noticiasFiltradas = [...noticias];
                renderizarNoticias();
                atualizarData();
            })
            .catch(error => {
                console.error('Erro ao carregar noticias.json:', error);
                
                fetch('noticias.json', { method: 'HEAD' })
                    .then(res => {
                        if (!res.ok) {
                            mostrarErro('Arquivo noticias.json não encontrado. Execute o bot.py primeiro.');
                        }
                    })
                    .catch(() => {
                        mostrarErro('Erro de conexão. Verifique se o servidor está rodando.');
                    });
            });
    }
    
    function mostrarErro(mensagem) {
        if (containerNoticias) {
            containerNoticias.innerHTML = `
                <div class="loading">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #dc3545; margin-bottom: 1rem;"></i>
                    <h4 style="color: #dc3545;">Erro ao carregar notícias</h4>
                    <p>${mensagem}</p>
                    <p><strong>Execute o bot Python primeiro:</strong></p>
                    <code style="background: #f8f9fa; padding: 10px; border-radius: 4px; display: block; margin: 10px 0;">
                        python bot.py
                    </code>
                    <button class="btn-primary" onclick="location.reload()">
                        <i class="fas fa-redo"></i> Tentar novamente
                    </button>
                </div>
            `;
        }
    }
    
    function extrairTags(titulo) {
        if (!titulo) return [];
        
        const tituloLower = titulo.toLowerCase();
        const tagsEncontradas = [];
        
        PALAVRAS_CHAVE.forEach(palavra => {
            if (tituloLower.includes(palavra.toLowerCase()) && !tagsEncontradas.includes(palavra)) {
                tagsEncontradas.push(palavra);
            }
        });

        return tagsEncontradas.slice(0, 5);
    }
    
    function aplicarFiltrosEBusca() {
        let resultado = [...noticias];
        
        if (filtroAtual !== 'todas') {
            resultado = resultado.filter(noticia => {
                if (!noticia || !noticia.titulo) return false;
                
                const tituloLower = noticia.titulo.toLowerCase();
                const tags = extrairTags(noticia.titulo);
                
                if (filtroAtual === 'itaqui') {
                    return tituloLower.includes('itaqui');
                }
                
                return tags.some(tag => tag.toLowerCase().includes(filtroAtual)) || 
                       tituloLower.includes(filtroAtual) ||
                       (noticia.tag && noticia.tag.toLowerCase().includes(filtroAtual));
            });
        }
        
        if (termoBusca.trim() !== '') {
            const busca = termoBusca.toLowerCase();
            resultado = resultado.filter(noticia => {
                if (!noticia) return false;
                
                const tituloMatch = noticia.titulo && noticia.titulo.toLowerCase().includes(busca);
                const fonteMatch = noticia.fonte && noticia.fonte.toLowerCase().includes(busca);
                const tagsMatch = extrairTags(noticia.titulo).some(tag => tag.toLowerCase().includes(busca));
                
                return tituloMatch || fonteMatch || tagsMatch;
            });
        }
        
        noticiasFiltradas = resultado;
        aplicarOrdenacao();
    }
    
    function aplicarBusca() {
        if (buscaInput) {
            termoBusca = buscaInput.value;
            aplicarFiltrosEBusca();
        }
    }
    
    function aplicarOrdenacao() {
        const ordem = ordenarSelect ? ordenarSelect.value : 'recentes';
        
        switch (ordem) {
            case 'antigos':
                noticiasFiltradas.sort((a, b) => {
                    const dateA = a.data ? parseDate(a.data) : new Date(0);
                    const dateB = b.data ? parseDate(b.data) : new Date(0);
                    return dateA - dateB;
                });
                break;
            case 'titulo':
                noticiasFiltradas.sort((a, b) => {
                    const tituloA = a.titulo || '';
                    const tituloB = b.titulo || '';
                    return tituloA.localeCompare(tituloB);
                });
                break;
            case 'recentes':
            default:
                noticiasFiltradas.sort((a, b) => {
                    const dateA = a.data ? parseDate(a.data) : new Date(0);
                    const dateB = b.data ? parseDate(b.data) : new Date(0);
                    return dateB - dateA;
                });
                break;
        }
        
        renderizarNoticias();
    }
    
    function parseDate(dataStr) {
        if (!dataStr) return new Date(0);
        
        // Formato dd/mm/yyyy
        const parts = dataStr.split('/');
        if (parts.length === 3) {
            return new Date(parts[2], parts[1] - 1, parts[0]);
        }
        
        return new Date(dataStr);
    }
    
    function renderizarNoticias() {
        if (!containerNoticias || !semNoticias || !contadorNoticias) return;
        
        const total = noticiasFiltradas.length;
        contadorNoticias.textContent = total;
        
        if (total === 0) {
            containerNoticias.style.display = 'none';
            semNoticias.style.display = 'block';
            return;
        }
        
        containerNoticias.style.display = 'grid';
        semNoticias.style.display = 'none';
        
        let html = '';
        
        noticiasFiltradas.forEach(noticia => {
            if (!noticia) return;
            
            const titulo = noticia.titulo || 'Sem título';
            const link = noticia.link || '#';
            const data = noticia.data || 'Data desconhecida';
            const fonte = noticia.fonte || 'Fonte desconhecida';
            const tag = noticia.tag || 'Geral';
            
            const tags = extrairTags(titulo);
            const tagsHtml = tags.map(tag => 
                `<span class="tag-item">${tag}</span>`
            ).join('');
            
            const tituloEscapado = titulo.replace(/'/g, "\\'");
            const fonteEscapada = fonte.replace(/'/g, "\\'");
            
            html += `
                <div class="noticia-card">
                    <div class="noticia-header">
                        <h3 class="noticia-titulo">${titulo}</h3>
                    </div>
                    <div class="noticia-body">
                        <div class="noticia-info">
                            <span class="noticia-data">
                                <i class="far fa-calendar-alt"></i> ${data}
                            </span>
                            <span class="noticia-fonte">
                                <i class="far fa-newspaper"></i> ${fonte}
                            </span>
                        </div>
                        <span class="noticia-tag">${tag}</span>
                        ${tagsHtml ? `<div class="tags-container">${tagsHtml}</div>` : ''}
                    </div>
                    <div class="noticia-footer">
                        <button class="btn-ver-mais" onclick="abrirModal('${tituloEscapado}', '${link}', '${fonteEscapada}', '${data}', '${tag}')">
                            <i class="fas fa-external-link-alt"></i> Ver detalhes
                        </button>
                    </div>
                </div>
            `;
        });
        
        containerNoticias.innerHTML = html;
    }
    
    function atualizarNoticias(e) {
        if (e) e.preventDefault();
        
        const btn = e ? e.currentTarget : btnAtualizar;
        if (!btn) return;
        
        const icon = btn.querySelector('i');
        if (icon) {
            icon.classList.add('fa-spin');
        }
        
        btn.disabled = true;

        setTimeout(() => {
            carregarNoticias();
            if (icon) {
                icon.classList.remove('fa-spin');
            }
            btn.disabled = false;
        }, 800);
    }
    
window.abrirModal = function(titulo, link, fonte, data, tag) {
    const modal = document.getElementById('modalNoticia');
    if (!modal) return;
    
    document.getElementById('modalTitulo').textContent = titulo;
    document.getElementById('modalLink').href = link;
    document.getElementById('modalFonte').textContent = fonte;
    document.getElementById('modalData').textContent = data;
    document.getElementById('modalTag').textContent = tag;
    
    const tags = extrairTags(titulo);
    const tagsContainer = document.getElementById('modalTags');
    if (tagsContainer) {
        tagsContainer.innerHTML = tags.length > 0 
            ? tags.map(tag => `<span class="tag-item">${tag}</span>`).join('')
            : '<span style="color: var(--gray); font-style: italic;">Nenhuma palavra-chave identificada</span>';
    }

    modal.style.display = 'flex';
    
    document.body.classList.add('modal-open');
};

function fecharModal() {
    const modal = document.getElementById('modalNoticia');
    if (modal) {
        modal.style.display = 'none';
        document.body.classList.remove('modal-open');
    }
}
    
    window.recarregarNoticias = carregarNoticias;
});


async function atualizarNoticiasAPI() {
    const btn = event ? event.currentTarget : document.getElementById('btnAtualizar');
    const icon = btn ? btn.querySelector('i') : null;
    
    if (icon) {
        icon.classList.add('fa-spin');
    }
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Atualizando...';
    }
    
    try {
        const response = await fetch('/api/update-news');
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem('Notícias atualizadas com sucesso!', 'success');
            setTimeout(() => {
                carregarNoticias();
            }, 1000);
        } else {
            throw new Error(data.error || 'Erro ao atualizar notícias');
        }
    } catch (error) {
        console.error('Erro na atualização:', error);
        mostrarMensagem(`Erro: ${error.message}`, 'error');
    } finally {
        if (icon) {
            icon.classList.remove('fa-spin');
        }
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sync-alt"></i> Atualizar';
        }
    }
}

function mostrarMensagem(texto, tipo = 'info') {
    const mensagemAnterior = document.getElementById('mensagem-flutuante');
    if (mensagemAnterior) {
        mensagemAnterior.remove();
    }
    
    const mensagem = document.createElement('div');
    mensagem.id = 'mensagem-flutuante';
    mensagem.className = `mensagem-flutuante mensagem-${tipo}`;
    mensagem.innerHTML = `
        <span>${texto}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    document.body.appendChild(mensagem);
    
    setTimeout(() => {
        if (mensagem.parentNode) {
            mensagem.remove();
        }
    }, 5000);
}

async function verificarStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'online') {
            const lastUpdate = new Date(data.lastUpdate);
            const agora = new Date();
            const diffHoras = Math.floor((agora - lastUpdate) / (1000 * 60 * 60));
            
            if (diffHoras > 4) {
                mostrarMensagem(`As notícias têm ${diffHoras} horas. Atualize para obter as mais recentes.`, 'info');
            }
        }
    } catch (error) {
        console.log('Status API não disponível, modo offline');
    }
}

verificarStatus();