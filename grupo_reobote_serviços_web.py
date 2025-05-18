import streamlit as st
from datetime import datetime
from PIL import Image
import json
import os

# Funções de carregamento e salvamento

def carregar_dados(arquivo, padrao):
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Caminhos dos arquivos
ARQUIVO_AGENDAMENTOS = 'agendamentos.json'
ARQUIVO_ARTISTAS = 'artistas.json'
ARQUIVO_ADMINS = 'admins.json'

# Inicialização do estado
if 'agendamentos' not in st.session_state:
    st.session_state.agendamentos = carregar_dados(ARQUIVO_AGENDAMENTOS, [])
if 'admin_principal' not in st.session_state:
    st.session_state.admin_principal = {'email': 'admin@admin.com', 'senha': 'admin123'}
if 'admins' not in st.session_state:
    st.session_state.admins = carregar_dados(ARQUIVO_ADMINS, [])
if 'whatsapp' not in st.session_state:
    st.session_state.whatsapp = '+5599999999999'
if 'empresa' not in st.session_state:
    st.session_state.empresa = {'nome': 'Grupo Reobote Serviços', 'descricao': 'Sistema de Agendamento e Assessoria'}
if 'artistas_disponiveis' not in st.session_state:
    st.session_state.artistas_disponiveis = carregar_dados(ARQUIVO_ARTISTAS, [])

# Interface pública
st.title(st.session_state.empresa['nome'])
st.write(st.session_state.empresa['descricao'])

st.header("Agendar um Artista")

if not st.session_state.artistas_disponiveis:
    st.warning("Nenhum artista disponível para agendamento.")
else:
    artista_nomes = [a['nome'] for a in st.session_state.artistas_disponiveis]
    artista_selecionado = st.selectbox("Escolha um artista", artista_nomes)
    artista_info = next(a for a in st.session_state.artistas_disponiveis if a['nome'] == artista_selecionado)

    st.write("**Descrição:**", artista_info.get('descricao', ''))
    st.write("**Categoria:**", artista_info.get('categoria', ''))
    if artista_info.get('redes'):
        st.write("**Redes sociais:**")
        for rede in artista_info['redes']:
            st.markdown(f"- [{rede}]({rede})")

    servico_opcoes = [f"{s['nome']} - R$ {s['preco']:.2f}" for s in artista_info['servicos']]
    servico_escolhido = st.selectbox("Escolha o serviço", servico_opcoes)

    nome_cliente = st.text_input("Seu nome")
    email_cliente = st.text_input("Email")
    telefone_cliente = st.text_input("Telefone")
    cidade_cliente = st.text_input("Cidade")
    data_evento = st.date_input("Data do evento")
    hora_inicio = st.time_input("Hora de início")
    hora_fim = st.time_input("Hora de término")

    if st.button("Confirmar Agendamento"):
        inicio = datetime.combine(data_evento, hora_inicio)
        fim = datetime.combine(data_evento, hora_fim)
        conflito = any(
            ag['artista'] == artista_selecionado and not (fim <= datetime.fromisoformat(ag['inicio']) or inicio >= datetime.fromisoformat(ag['fim']))
            for ag in st.session_state.agendamentos
        )
        if conflito:
            st.error("Esse horário já está ocupado para este artista.")
        elif not nome_cliente or not email_cliente:
            st.error("Por favor, preencha seu nome e email.")
        else:
            novo_agendamento = {
                'artista': artista_selecionado,
                'servico': servico_escolhido,
                'cliente': nome_cliente,
                'email': email_cliente,
                'telefone': telefone_cliente,
                'cidade': cidade_cliente,
                'inicio': inicio.isoformat(),
                'fim': fim.isoformat()
            }
            st.session_state.agendamentos.append(novo_agendamento)
            salvar_dados(ARQUIVO_AGENDAMENTOS, st.session_state.agendamentos)
            st.success("Agendamento realizado com sucesso!")

st.markdown("---")

st.header("Parcerias com a Empresa")
nome_parceira = st.text_input("Nome da Empresa Parceira", key="parceria_nome")
email_parceira = st.text_input("Email para Contato", key="parceria_email")
mensagem_parceira = st.text_area("Mensagem ou Proposta", key="parceria_mensagem")
if st.button("Enviar Proposta de Parceria"):
    if nome_parceira and email_parceira:
        st.success("Proposta de parceria enviada com sucesso!")
    else:
        st.error("Preencha nome e email para enviar a proposta.")

st.markdown("---")

st.header("Quero ser Assessorado")
nome_assessorado = st.text_input("Nome Completo", key="assessoria_nome")
email_assessorado = st.text_input("Email", key="assessoria_email")
descricao_assessorado = st.text_area("Conte-nos sobre você e seu trabalho artístico", key="assessoria_descricao")
if st.button("Enviar Solicitação de Vínculo"):
    if nome_assessorado and email_assessorado:
        st.success("Solicitação de vínculo enviada com sucesso!")
    else:
        st.error("Preencha nome e email para enviar a solicitação.")

st.markdown("---")

# Botão WhatsApp
if st.session_state.whatsapp:
    whatsapp_link = f"https://wa.me/{st.session_state.whatsapp.replace('+', '').replace(' ', '')}"
    st.markdown(f"[Fale conosco no WhatsApp]({whatsapp_link})", unsafe_allow_html=True)

st.markdown("---")

with st.expander("Área do Administrador"):
    login_email = st.text_input("Email do administrador", key="login_email")
    login_senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Entrar", key="botao_entrar"):
        if login_email == st.session_state.admin_principal['email'] and login_senha == st.session_state.admin_principal['senha']:
            st.session_state.admin_logado = 'principal'
            st.success("Login como administrador principal!")
        elif any(a['email'] == login_email and a['senha'] == login_senha for a in st.session_state.admins):
            st.session_state.admin_logado = login_email
            st.success("Login como administrador!")
        else:
            st.error("Credenciais inválidas.")

if st.session_state.get('admin_logado') == 'principal':
    st.header("Painel do Administrador Principal")

    st.subheader("Cadastrar Novo Administrador")
    novo_admin_email = st.text_input("Email do novo administrador")
    novo_admin_senha = st.text_input("Senha do novo administrador", type="password")
    if st.button("Cadastrar Novo Administrador"):
        st.session_state.admins.append({"email": novo_admin_email, "senha": novo_admin_senha})
        salvar_dados(ARQUIVO_ADMINS, st.session_state.admins)
        st.success("Novo administrador cadastrado com sucesso!")

    st.subheader("Cadastrar Novo Artista")
    nome_artista = st.text_input("Nome do artista")
    descricao_artista = st.text_area("Descrição")
    categoria_artista = st.text_input("Categoria")
    redes_artista = st.text_area("Redes sociais (separadas por vírgula)")
    servicos_artista = st.text_area("Serviços e preços (formato: nome:preço, um por linha)")

    if st.button("Salvar Artista"):
        lista_redes = [r.strip() for r in redes_artista.split(',') if r.strip()]
        lista_servicos = []
        for linha in servicos_artista.split('\n'):
            if ':' in linha:
                nome, preco = linha.split(':', 1)
                try:
                    lista_servicos.append({"nome": nome.strip(), "preco": float(preco.strip())})
                except:
                    continue
        novo_artista = {
            "nome": nome_artista,
            "descricao": descricao_artista,
            "categoria": categoria_artista,
            "foto": None,
            "redes": lista_redes,
            "servicos": lista_servicos
        }
        st.session_state.artistas_disponiveis.append(novo_artista)
        salvar_dados(ARQUIVO_ARTISTAS, st.session_state.artistas_disponiveis)
        st.success("Artista cadastrado com sucesso!")

    st.subheader("Excluir Artista")
    nomes_para_excluir = [a['nome'] for a in st.session_state.artistas_disponiveis]
    artista_excluir = st.selectbox("Selecione o artista", nomes_para_excluir)
    if st.button("Excluir Artista"):
        st.session_state.artistas_disponiveis = [a for a in st.session_state.artistas_disponiveis if a['nome'] != artista_excluir]
        salvar_dados(ARQUIVO_ARTISTAS, st.session_state.artistas_disponiveis)
        st.success("Artista excluído com sucesso!")
                  
