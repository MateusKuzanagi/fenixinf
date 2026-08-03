from datetime import datetime
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st
from supabase import Client, create_client

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E SUPABASE
# ==========================================
st.set_page_config(
    page_title="Fênix Assistência Técnica", page_icon="💻", layout="wide"
)

URL: str = "https://umkfhbyuawnymnltsdka.supabase.co"
KEY: str = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6In"
    "Vta2ZoYnl1YXdueW1ubHRzZGthIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NTU4ODcs"
    "ImV4cCI6MjEwMTMzMTg4N30.XxPe6T-iGTvJjU-1txfxyD6148P3mKwOyqG5m6MHy7c"
)


@st.cache_resource
def init_supabase():
  return create_client(URL, KEY)


supabase = init_supabase()

# ==========================================
# CONTROLE DE SESSÃO (TELA DE LOGIN)
# ==========================================
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if not st.session_state.autenticado:
  st.title("🔒 Fênix • Acesso Restrito ao Sistema")
  st.markdown("Por favor, digite as credenciais de acesso para entrar.")

  with st.form("form_login"):
    usuario = st.text_input("Usuário").strip()
    senha = st.text_input("Senha", type="password").strip()
    btn_login = st.form_submit_button("Entrar no Sistema")

    if btn_login:
      if usuario == "admin" and senha == "fenix123":
        st.session_state.autenticado = True
        st.success("Login realizado com sucesso! Carregando sistema...")
        st.rerun()
      else:
        st.error("Usuário ou senha incorretos!")
  st.stop()

# ==========================================
# MENU LATERAL PROFISSIONAL
# ==========================================
st.sidebar.title("🛠️ Fênix • Painel Web")
st.sidebar.write("Bem-vindo ao sistema integrado!")

menu = st.sidebar.selectbox(
    "Navegação Principal",
    [
        "📊 Dashboard Executivo",
        "📦 Gestão de Estoque / Produtos",
        "➕ Cadastrar Produto",
        "👥 Clientes e Aparelhos",
        "➕ Cadastrar Novo Cliente",
        "📜 Histórico e Extrato de Cliente",
        "📄 Gerar Ordem de Serviço (PDF)",
    ],
)

if st.sidebar.button("🔒 Sair / Logout"):
  st.session_state.autenticado = False
  st.rerun()

# ==========================================
# 1. DASHBOARD EXECUTIVO
# ==========================================
if menu == "📊 Dashboard Executivo":
  st.title("📊 Painel Executivo e Métricas")
  st.write("Visão geral em tempo real conectada ao Supabase.")

  try:
    res_prod = supabase.table("Produtos").select("*").execute()
    produtos = res_prod.data or []

    res_cli = supabase.table("Clientes").select("*").execute()
    clientes = res_cli.data or []

    total_produtos = len(produtos)
    total_clientes = len(clientes)
    val_estoque = sum([
        float(p.get("preco", 0) or 0) * int(p.get("qtdestoque", 0) or 0)
        for p in produtos
    ])

    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Total de Produtos", total_produtos)
    c2.metric("👥 Total de Clientes", total_clientes)
    c3.metric("💰 Valor Total em Estoque", f"R$ {val_estoque:.2f}")

    st.markdown("---")
    st.subheader("⚠️ Alertas de Estoque Crítico (<= 2 unidades)")
    baixo_estoque = [
        p
        for p in produtos
        if p.get("qtdestoque") is not None
        and int(p.get("qtdestoque")) <= 2
    ]

    if baixo_estoque:
      df_baixo = pd.DataFrame(baixo_estoque)
      st.dataframe(
          df_baixo[["id", "nomeproduto", "qtdestoque", "preco"]],
          use_container_width=True,
      )
    else:
      st.success("Parabéns! Nenhum produto com estoque crítico no momento.")

  except Exception as e:
    st.error(f"Erro ao carregar dados do Dashboard: {e}")

# ==========================================
# 2. GESTÃO DE ESTOQUE / PRODUTOS
# ==========================================
elif menu == "📦 Gestão de Estoque / Produtos":
  st.title("📦 Controle de Estoque e Peças")

  termo = st.text_input("🔎 Pesquisar no estoque por nome ou código:").lower()

  try:
    res = supabase.table("Produtos").select("*").execute()
    dados = res.data or []

    if termo:
      dados = [
          d
          for d in dados
          if termo in str(d.get("id", "")).lower()
          or termo in str(d.get("nomeproduto", "")).lower()
      ]

    if dados:
      df = pd.DataFrame(dados)
      df_exibicao = df.rename(
          columns={
              "id": "Código",
              "nomeproduto": "Produto",
              "descricao": "Descrição",
              "preco": "Preço (R$)",
              "qtdestoque": "Qtd Estoque",
          }
      )
      st.dataframe(df_exibicao, use_container_width=True)
    else:
      st.info("Nenhum produto encontrado.")
  except Exception as e:
    st.error(f"Erro ao buscar estoque: {e}")

# ==========================================
# 3. CADASTRAR PRODUTO
# ==========================================
elif menu == "➕ Cadastrar Produto":
  st.title("➕ Cadastro de Novo Produto / Peça")

  with st.form("form_cad_prod", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
      pid = st.text_input("Código / ID do Produto (Ex: P001)").strip()
      nome = st.text_input("Nome do Produto / Peça").strip()
      preco = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f")
    with c2:
      qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1)
      desc = st.text_input("Descrição Detalhada").strip()

    btn_salvar_prod = st.form_submit_button("💾 Salvar Produto na Nuvem")
    if btn_salvar_prod:
      if not pid or not nome:
        st.warning("Preencha o Código e o Nome do Produto!")
      else:
        try:
          payload = {
              "id": pid,
              "nomeproduto": nome,
              "descricao": desc,
              "preco": preco,
              "qtdestoque": qtd,
          }
          supabase.table("Produtos").insert(payload).execute()
          st.success("Produto cadastrado com sucesso no Supabase!")
        except Exception as e:
          st.error(
              f"Erro ao salvar produto (Verifique se o código já existe): {e}"
          )

# ==========================================
# 4. CLIENTES E APARELHOS
# ==========================================
elif menu == "👥 Clientes e Aparelhos":
  st.title("👥 Consulta de Clientes e Aparelhos Registrados")

  termo_cli = st.text_input(
      "🔎 Buscar cliente por nome, telefone ou modelo do aparelho:"
  ).lower()

  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []

    if termo_cli:
      clientes = [
          c
          for c in clientes
          if termo_cli in str(c.get("nome", "")).lower()
          or termo_cli in str(c.get("modeloaparelho", "")).lower()
          or termo_cli in str(c.get("telefone", "")).lower()
      ]

    if clientes:
      df_cli = pd.DataFrame(clientes)
      st.dataframe(df_cli, use_container_width=True)
    else:
      st.info("Nenhum cliente encontrado.")
  except Exception as e:
    st.error(f"Erro ao buscar clientes: {e}")

# ==========================================
# 5. CADASTRAR NOVO CLIENTE
# ==========================================
elif menu == "➕ Cadastrar Novo Cliente":
  st.title("➕ Cadastro de Cliente e Aparelho para Manutenção")

  with st.form("form_cad_cli", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
      nome = st.text_input("Nome Completo do Cliente *").strip()
      telefone = st.text_input("Telefone / WhatsApp").strip()
      endereco = st.text_input("Endereço").strip()
      tipo_aparelho = st.text_input(
          "Tipo de Aparelho (Ex: Notebook / Smartphone)"
      ).strip()
    with c2:
      modelo_aparelho = st.text_input(
          "Modelo do Aparelho (Ex: iPhone 12 / Dell Inspiron)"
      ).strip()
      imei = st.text_input("Número de Série / IMEI").strip()
      senha = st.text_input("Senha / PIN de Desbloqueio").strip()
      data_entrada = st.text_input(
          "Data de Entrada", value=datetime.now().strftime("%d/%m/%Y")
      ).strip()

    btn_salvar_cli = st.form_submit_button("💾 Salvar Cliente no Supabase")
    if btn_salvar_cli:
      if not nome:
        st.warning("O nome do cliente é obrigatório!")
      else:
        try:
          payload_cli = {
              "nome": nome,
              "telefone": telefone,
              "endereco": endereco,
              "tipoaparelho": tipo_aparelho,
              "modeloaparelho": modelo_aparelho,
              "numeroserieimei": imei,
              "senhaaparelho": senha,
              "dataentrada": data_entrada,
              "datasaida": "",
          }
          supabase.table("Clientes").insert(payload_cli).execute()
          st.success("Cliente e aparelho cadastrados com sucesso!")
        except Exception as e:
          st.error(f"Erro ao cadastrar cliente: {e}")

# ==========================================
# 6. HISTÓRICO E EXTRATO DE CLIENTE
# ==========================================
elif menu == "📜 Histórico e Extrato de Cliente":
  st.title("📜 Extrato e Histórico de Atendimentos")
  st.write(
      "Consulte o histórico detalhado dos aparelhos e manutenções vinculadas ao"
      " cliente."
  )

  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []

    if clientes:
      nomes_clientes = [
          f"{c.get('id')} - {c.get('nome')} ({c.get('modeloaparelho')})"
          for c in clientes
      ]
      escolha = st.selectbox("Selecione o Cliente / Aparelho:", nomes_clientes)

      if escolha:
        id_selecionado = int(escolha.split(" - ")[0])
        cliente_atual = next(
            (c for c in clientes if c.get("id") == id_selecionado), None
        )

        if cliente_atual:
          st.markdown("---")
          st.subheader(f"📋 Ficha Completa: {cliente_atual.get('nome')}")

          col_ex1, col_ex2 = st.columns(2)
          with col_ex1:
            st.write(f"**📞 Telefone:** {cliente_atual.get('telefone')}")
            st.write(f"**🏠 Endereço:** {cliente_atual.get('endereco')}")
            st.write(
                f"**💻 Aparelho:** {cliente_atual.get('tipoaparelho')} -"
                f" {cliente_atual.get('modeloaparelho')}"
            )
          with col_ex2:
            st.write(
                f"**🔢 Nº Série / IMEI:**"
                f" {cliente_atual.get('numeroserieimei')}"
            )
            st.write(
                f"**📅 Data de Entrada:** {cliente_atual.get('dataentrada')}"
            )
            st.write(
                f"**🚪 Data de Saída:** {cliente_atual.get('datasaida') or 'Em"
                " Andamento / Na Oficina'}"
            )

          st.info(
              "Histórico de movimentações registrado com sucesso na nuvem para"
              " auditoria e controle interno."
          )
    else:
      st.info("Nenhum cliente cadastrado para gerar extrato.")
  except Exception as e:
    st.error(f"Erro ao carregar histórico: {e}")

# ==========================================
# 7. GERAR ORDEM DE SERVIÇO EM PDF
# ==========================================
elif menu == "📄 Gerar Ordem de Serviço (PDF)":
  st.title("📄 Gerador de Ordem de Serviço em PDF")
  st.write(
      "Selecione um cliente cadastrado para gerar o PDF oficial pronto para"
      " impressão ou envio via WhatsApp."
  )

  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []

    if clientes:
      nomes_os = [
          f"{c.get('id')} - {c.get('nome')} ({c.get('modeloaparelho')})"
          for c in clientes
      ]
      escolha_os = st.selectbox("Selecione o Cliente para a O.S.:", nomes_os)

      if escolha_os:
        id_os = int(escolha_os.split(" - ")[0])
        cli_os = next((c for c in clientes if c.get("id") == id_os), None)

        if cli_os and st.button("🖨️ Gerar Arquivo PDF da O.S."):
          buffer = io.BytesIO()
          p = canvas.Canvas(buffer, pagesize=letter)

          # Cabeçalho da OS
          p.setFont("Helvetica-Bold", 16)
          p.drawString(50, 750, "FÊNIX • ASSISTÊNCIA TÉCNICA E SOLUÇÕES DE TI")
          p.setFont("Helvetica", 10)
          p.drawString(
              50, 735, "Ordem de Serviço de Entrada de Aparelho / Manutenção"
          )
          p.line(50, 725, 560, 725)

          # Dados do Cliente
          p.setFont("Helvetica-Bold", 12)
          p.drawString(50, 695, "Dados do Cliente:")
          p.setFont("Helvetica", 11)
          p.drawString(50, 675, f"Nome: {cli_os.get('nome', '')}")
          p.drawString(50, 655, f"Telefone: {cli_os.get('telefone', '')}")
          p.drawString(50, 635, f"Endereço: {cli_os.get('endereco', '')}")

          # Dados do Aparelho
          p.setFont("Helvetica-Bold", 12)
          p.drawString(50, 595, "Especificações do Aparelho:")
          p.setFont("Helvetica", 11)
          p.drawString(50, 575, f"Tipo: {cli_os.get('tipoaparelho', '')}")
          p.drawString(50, 555, f"Modelo: {cli_os.get('modeloaparelho', '')}")
          p.drawString(
              50, 535, f"Nº Série / IMEI: {cli_os.get('numeroserieimei', '')}"
          )
          p.drawString(
              50, 515, f"Data de Entrada: {cli_os.get('dataentrada', '')}"
          )

          # Termos e Assinatura
          p.line(50, 470, 560, 470)
          p.setFont("Helvetica-Oblique", 9)
          p.drawString(
              50,
              450,
              "Declaro estar de acordo com os termos de serviço e orçamento da"
              " Fênix Assistência Técnica.",
          )
          p.drawString(
              50, 250, "__________________________________________________"
          )
          p.drawString(50, 235, "Assinatura do Cliente")

          p.showPage()
          p.save()

          buffer.seek(0)

          st.success("Ordem de Serviço gerada com sucesso!")
          st.download_button(
              label="📥 Baixar PDF da Ordem de Serviço",
              data=buffer,
              file_name=f"OS_Cliente_{cli_os.get('id')}.pdf",
              mime="application/pdf",
          )
    else:
      st.info("Nenhum cliente disponível para gerar PDF.")
  except Exception as e:
    st.error(f"Erro ao gerar PDF: {e}")
