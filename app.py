from datetime import datetime
import io
import urllib.parse
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st
from supabase import Client, create_client

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E DESIGN CLEAN (MODERNO E PROFISSIONAL)
# ==========================================
st.set_page_config(
    page_title="Fênix • Gestão Tecnológica", page_icon="⚡", layout="wide"
)

st.markdown(
    """
    <style>
        .main {
            background-color: #f8fafc;
            color: #0f172a;
        }
        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #2563eb;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            text-align: center;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        [data-testid="stSidebar"] * {
            color: #1e293b !important;
        }
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
            background-color: #2563eb;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
        }
        .stButton>button:hover {
            background-color: #1d4ed8;
        }
    </style>
""",
    unsafe_allow_html=True,
)

URL: str = "https://umkfhbyuawnymnltsdka.supabase.co"
KEY: str = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6In"
    "Vta2ZoYnl1YXdueW1ubHRzZGthIiwicm9sZSI6InVub24iLCJpYXQiOjE3ODU3NTU4ODcs"
    "ImV4cCI6MjEwMTMzMTg4N30.XxPe6T-iGTvJjU-1txfxyD6148P3mKwOyqG5m6MHy7c"
)


@st.cache_resource
def init_supabase():
  return create_client(URL, KEY)


supabase = init_supabase()

# ==========================================
# CONTROLE DE SESSÃO (LOGIN)
# ==========================================
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if not st.session_state.autenticado:
  col1, col2, col3 = st.columns([1, 1.2, 1])
  with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='text-align: center; color: #1e293b;'>⚡ Fênix • Gestão"
        " Tecnológica</h2>",
        unsafe_allow_html=True,
    )
    with st.form("form_login"):
      usuario = st.text_input("Usuário").strip()
      senha = st.text_input("Senha", type="password").strip()
      st.markdown("<br>", unsafe_allow_html=True)
      if st.form_submit_button("Entrar no Sistema", use_container_width=True):
        if usuario == "admin" and senha == "fenix123":
          st.session_state.autenticado = True
          st.rerun()
        else:
          st.error("⚠️ Usuário ou senha incorretos!")
  st.stop()

# ==========================================
# MENU LATERAL LIMPO E ORGANIZADO
# ==========================================
st.sidebar.markdown(
    "<h3 style='color: #2563eb; text-align: center;'>⚡ FÊNIX TECH</h3>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação Principal",
    [
        "📊 Dashboard Geral",
        "📦 Produtos & Estoque",
        "👥 Clientes & Cadastros",
        "📄 Ordem de Serviço",
        "🧾 Nota Fiscal (PDF)",
        "💬 WhatsApp & Histórico",
    ],
)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair do Sistema"):
  st.session_state.autenticado = False
  st.rerun()

# ==========================================
# 1. DASHBOARD GERAL
# ==========================================
if menu == "📊 Dashboard Geral":
  st.markdown("## 📊 Painel de Controle Geral")
  st.markdown("---")
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
    with c1:
      st.markdown(
          f"""<div class='metric-card'><h4 style='color: #64748b;'>📦 Total de"
          " Produtos</h4><h2 style='color:"
          f" #2563eb;'>{total_produtos}</h2></div>""",
          unsafe_allow_html=True,
      )
    with c2:
      st.markdown(
          f"""<div class='metric-card'><h4 style='color: #64748b;'>👥 Total de"
          " Clientes</h4><h2 style='color: #2563eb;'>{total_clientes}</h2></div>""",
          unsafe_allow_html=True,
      )
    with c3:
      st.markdown(
          f"""<div class='metric-card'><h4 style='color: #64748b;'>💰 Valor em"
          " Estoque</h4><h2 style='color: #2563eb;'>R$"
          f" {val_estoque:,.2f}</h2></div>""",
          unsafe_allow_html=True,
      )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚠️ Alertas Críticos de Reposição (Estoque <= 2)")
    baixo_estoque = [
        p
        for p in produtos
        if p.get("qtdestoque") is not None
        and int(p.get("qtdestoque")) <= 2
    ]
    if baixo_estoque:
      st.dataframe(pd.DataFrame(baixo_estoque), use_container_width=True)
    else:
      st.success("✨ Estoque normalizado. Nenhum item crítico no momento.")
  except Exception as e:
    st.error(f"Erro ao carregar dashboard: {e}")

# ==========================================
# 2. PRODUTOS & ESTOQUE (CADASTRO E EDIÇÃO UNIFICADOS)
# ==========================================
elif menu == "📦 Produtos & Estoque":
  st.markdown("## 📦 Gestão de Produtos e Estoque")
  st.markdown("---")

  col_cad, col_list = st.columns([1, 1.5])

  with col_cad:
    st.subheader("➕ Novo Produto")
    with st.form("form_novo_prod_limpo", clear_on_submit=True):
      pid = st.text_input("Código / ID (Ex: P001)").strip()
      nome = st.text_input("Nome do Produto").strip()
      preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
      qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1)
      desc = st.text_input("Descrição Opcional").strip()
      if st.form_submit_button("💾 Salvar Produto"):
        if pid and nome:
          supabase.table("Produtos").insert({
              "id": pid,
              "nomeproduto": nome,
              "preco": preco,
              "qtdestoque": qtd,
              "descricao": desc,
          }).execute()
          st.success("✅ Produto cadastrado!")
          st.rerun()
        else:
          st.warning("Preencha o ID e o Nome do Produto.")

  with col_list:
    st.subheader("📋 Produtos Cadastrados")
    try:
      res = supabase.table("Produtos").select("*").execute()
      dados = res.data or []
      if dados:
        termo = st.text_input("🔎 Pesquisar produto:").lower()
        if termo:
          dados = [
              d for d in dados if termo in str(d.get("nomeproduto", "")).lower()
          ]
        st.dataframe(pd.DataFrame(dados), use_container_width=True)
      else:
        st.info("Nenhum produto cadastrado.")
    except Exception as e:
      st.error(f"Erro: {e}")

# ==========================================
# 3. CLIENTES & CADASTROS
# ==========================================
elif menu == "👥 Clientes & Cadastros":
  st.markdown("## 👥 Base de Clientes e Aparelhos")
  st.markdown("---")

  col_cad_cli, col_list_cli = st.columns([1, 1.5])

  with col_cad_cli:
    st.subheader("👤 Novo Cliente")
    with st.form("form_novo_cli_limpo", clear_on_submit=True):
      nome_c = st.text_input("Nome Completo *").strip()
      tel_c = st.text_input("Telefone / WhatsApp").strip()
      end_c = st.text_input("Endereço").strip()
      m_ap = st.text_input("Modelo do Aparelho").strip()
      if st.form_submit_button("💾 Salvar Cliente"):
        if nome_c:
          supabase.table("Clientes").insert({
              "nome": nome_c,
              "telefone": tel_c,
              "endereco": end_c,
              "modeloaparelho": m_ap,
              "dataentrada": datetime.now().strftime("%d/%m/%Y"),
          }).execute()
          st.success("✅ Cliente cadastrado!")
          st.rerun()
        else:
          st.warning("O campo Nome é obrigatório.")

  with col_list_cli:
    st.subheader("📋 Clientes Cadastrados")
    try:
      res = supabase.table("Clientes").select("*").execute()
      clientes = res.data or []
      if clientes:
        st.dataframe(pd.DataFrame(clientes), use_container_width=True)
      else:
        st.info("Nenhum cliente cadastrado.")
    except Exception as e:
      st.error(f"Erro: {e}")

# ==========================================
# 4. ORDEM DE SERVIÇO & VENDA
# ==========================================
elif menu == "📄 Ordem de Serviço":
  st.markdown("## 📄 Ordem de Serviço & Venda de Peças")
  st.markdown(
      "Selecione o cliente, adicione peças do estoque com baixa automática e"
      " gere o PDF completo."
  )
  st.markdown("---")

  try:
    res_cli = supabase.table("Clientes").select("*").execute()
    clientes = res_cli.data or []
    res_prod = supabase.table("Produtos").select("*").execute()
    produtos = res_prod.data or []

    if clientes:
      opcoes_os_dict = {
          f"ID: {c.get('id')} - {c.get('nome')} ({c.get('modeloaparelho', 'Sem Aparelho')})": c
          for c in clientes
      }
      escolha_os_label = st.selectbox(
          "Selecione o Cliente:", list(opcoes_os_dict.keys())
      )
      cli_os = opcoes_os_dict[escolha_os_label]

      with st.form("form_os_completa"):
        st.subheader("🛠️ Laudo e Informações Técnicas")
        c1, c2 = st.columns(2)
        with c1:
          defeito_relatado = st.text_area(
              "Defeito Relatado:",
              value="Aparelho apresentando instabilidade de funcionamento.",
          )
          laudo_tecnico = st.text_area(
              "Serviço Técnico / Mão de Obra:",
              value="Substituição de componentes e testes rigorosos.",
          )
        with c2:
          valor_mao_obra = st.number_input(
              "Valor da Mão de Obra (R$):",
              min_value=0.0,
              value=120.0,
              format="%.2f",
          )
          prazo_entrega = st.text_input(
              "Prazo Estimado de Entrega:", value="2 dias úteis"
          )
          obs_extras = st.text_area(
              "Observações / Garantia:", value="Garantia de 90 dias sobre o serviço."
          )

        st.markdown("---")
        st.subheader("🛒 Peças / Produtos do Estoque")
        produtos_escolhidos = []
        opcoes_prod = {}
        if produtos:
          opcoes_prod = {
              f"{p.get('nomeproduto')} (Disponível: {p.get('qtdestoque')} | R$ {p.get('preco')})": p
              for p in produtos
          }
          produtos_escolhidos = st.multiselect(
              "Selecione as peças utilizadas:", list(opcoes_prod.keys())
          )

        btn_gerar_os = st.form_submit_button("🖨️ Compilar e Salvar O.S.")

      if btn_gerar_os:
        qtd_por_produto = {}
        total_pecas = 0.0

        if produtos_escolhidos:
          for prod_label in produtos_escolhidos:
            p_obj = opcoes_prod[prod_label]
            q_venda = 1
            qtd_por_produto[p_obj.get("id")] = {
                "obj": p_obj,
                "qtd": q_venda,
                "subtotal": float(p_obj.get("preco", 0)) * q_venda,
            }
            total_pecas += float(p_obj.get("preco", 0)) * q_venda

        valor_total_geral = valor_mao_obra + total_pecas

        for pid_str, info in qtd_por_produto.items():
          p_obj = info["obj"]
          novo_estoque = int(p_obj.get("qtdestoque", 0)) - info["qtd"]
          supabase.table("Produtos").update(
              {"qtdestoque": max(0, novo_estoque)}
          ).eq("id", pid_str).execute()

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 750, "FÊNIX • ASSISTÊNCIA TÉCNICA ESPECIALIZADA")
        p.setFont("Helvetica", 9)
        p.drawString(50, 735, "Ordem de Serviço & Venda de Peças")
        p.line(50, 725, 560, 725)

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 700, "1. Dados do Cliente:")
        p.setFont("Helvetica", 10)
        p.drawString(50, 682, f"Cliente: {cli_os.get('nome', '')}")
        p.drawString(50, 667, f"Telefone: {cli_os.get('telefone', '')}")
        p.drawString(
            50,
            652,
            f"Aparelho: {cli_os.get('modeloaparelho', 'Não informado')}",
        )

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 622, "2. Laudo Técnico e Observações:")
        p.setFont("Helvetica", 10)
        p.drawString(50, 604, f"Defeito: {defeito_relatado}")
        p.drawString(50, 589, f"Serviço Executado: {laudo_tecnico}")
        p.drawString(50, 574, f"Observações: {obs_extras}")

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 544, "3. Peças Aplicadas:")
        p.setFont("Helvetica", 10)
        y_pos = 526
        if qtd_por_produto:
          for item in qtd_por_produto.values():
            p.drawString(
                50,
                y_pos,
                f"- {item['qtd']}x {item['obj'].get('nomeproduto')} | Subtotal:"
                f" R$ {item['subtotal']:.2f}",
            )
            y_pos -= 15
        else:
          p.drawString(50, y_pos, "Nenhuma peça aplicada.")
          y_pos -= 15

        y_pos -= 10
        p.line(50, y_pos, 560, y_pos)
        y_pos -= 20
        p.setFont("Helvetica-Bold", 11)
        p.drawString(
            50,
            y_pos,
            f"Mão de Obra: R$ {valor_mao_obra:.2f} | Peças: R$ {total_pecas:.2f}"
            f" | Total Geral: R$ {valor_total_geral:.2f}",
        )
        y_pos -= 20
        p.setFont("Helvetica", 10)
        p.drawString(50, y_pos, f"Prazo de Entrega: {prazo_entrega}")

        p.showPage()
        p.save()
        buffer.seek(0)

        st.success("🎉 O.S. gerada com sucesso e estoque atualizado!")
        st.download_button(
            label="📥 Baixar PDF da Ordem de Serviço",
            data=buffer,
            file_name=f"OS_Cliente_{cli_os.get('id', 'geral')}.pdf",
            mime="application/pdf",
        )
    else:
      st.info("Cadastre clientes para emitir Ordens de Serviço.")
  except Exception as e:
    st.error(f"Erro: {e}")

# ==========================================
# 5. NOTA FISCAL (PDF)
# ==========================================
elif menu == "🧾 Nota Fiscal (PDF)":
  st.markdown("## 🧾 Emissor de Nota Fiscal de Serviços (PDF)")
  st.markdown("---")
  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []
    if clientes:
      opcoes_nf_dict = {
          f"ID: {c.get('id')} - {c.get('nome')} ({c.get('modeloaparelho', 'Sem Aparelho')})": c
          for c in clientes
      }
      escolha_nf = st.selectbox(
          "Selecione o Cliente para a Nota Fiscal:",
          list(opcoes_nf_dict.keys()),
      )
      cli_nf = opcoes_nf_dict[escolha_nf]

      with st.form("form_emissao_nf_clean"):
        st.subheader("📋 Dados da Nota Fiscal")
        c1, c2 = st.columns(2)
        with c1:
          desc_servico = st.text_area(
              "Discriminação dos Serviços:",
              value=(
                  "Prestação de serviços técnicos especializados em"
                  " manutenção de equipamentos de TI."
              ),
          )
        with c2:
          val_serv = st.number_input(
              "Valor dos Serviços (R$):", min_value=0.0, value=150.0, format="%.2f"
          )
          forma_pagto = st.selectbox(
              "Forma de Pagamento:", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Boleto"]
          )

        submitted_nf = st.form_submit_button("Preparar Nota Fiscal PDF")

      if submitted_nf or "gerar_nf_pdf" in st.session_state:
        st.session_state.gerar_nf_pdf = True

        buffer_nf = io.BytesIO()
        p = canvas.Canvas(buffer_nf, pagesize=letter)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 750, "FÊNIX • GESTÃO TECNOLÓGICA")
        p.setFont("Helvetica", 9)
        p.drawString(50, 735, "NOTA FISCAL DE PRESTAÇÃO DE SERVIÇOS (NFS-e)")
        p.line(50, 725, 560, 725)

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 700, "1. Dados do Tomador:")
        p.setFont("Helvetica", 10)
        p.drawString(50, 682, f"Nome / Razão Social: {cli_nf.get('nome', '')}")
        p.drawString(50, 667, f"Telefone: {cli_nf.get('telefone', '')}")
        p.drawString(
            50,
            652,
            f"Endereço: {cli_nf.get('endereco', 'Não informado')}",
        )
        p.drawString(
            50,
            637,
            f"Referência Aparelho: {cli_nf.get('modeloaparelho', 'N/A')}",
        )

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 607, "2. Discriminação dos Serviços:")
        p.setFont("Helvetica", 10)
        p.drawString(50, 589, f"- {desc_servico}")

        p.line(50, 530, 560, 530)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(
            50,
            510,
            f"Valor Total dos Serviços: R$ {val_serv:.2f}",
        )
        p.setFont("Helvetica", 10)
        p.drawString(50, 492, f"Forma de Pagamento: {forma_pagto}")
        p.drawString(
            50,
            477,
            f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        )

        p.showPage()
        p.save()
        buffer_nf.seek(0)

        st.success("🎉 Nota Fiscal gerada e pronta para download!")
        st.download_button(
            label="📥 Baixar Nota Fiscal em PDF",
            data=buffer_nf,
            file_name=f"Nota_Fiscal_{cli_nf.get('id', 'geral')}.pdf",
            mime="application/pdf",
        )
    else:
      st.info("Cadastre clientes para emitir Notas Fiscais.")
  except Exception as e:
    st.error(f"Erro: {e}")

# ==========================================
# 6. WHATSAPP & HISTÓRICO
# ==========================================
elif menu == "💬 WhatsApp & Histórico":
  st.markdown("## 💬 Envio Rápido via WhatsApp")
  st.markdown("---")
  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []
    if clientes:
      opcoes_hist = {
          f"ID: {c.get('id')} - {c.get('nome')}": c for c in clientes
      }
      escolha_h = st.selectbox(
          "Selecione o Cliente:", list(opcoes_hist.keys())
      )
      cli_hist = opcoes_hist[escolha_h]
      tel = "".join(filter(str.isdigit, str(cli_hist.get("telefone", ""))))
      msg = f"Olá {cli_hist.get('nome')}, aqui é da Fênix Assistência Técnica! ⚡"
      link = f"https://wa.me/55{tel}?text={urllib.parse.quote(msg)}"
      st.markdown(
          f"""<a href="{link}" target="_blank"><button style="background-color:"
          "#16a34a; color: white; padding: 0.6rem 1.2rem; border: none;"
          " border-radius: 6px; font-weight: bold; cursor: pointer;">💬 Abrir"
          " WhatsApp com Mensagem Pronta</button></a>""",
          unsafe_allow_html=True,
      )
    else:
      st.info("Nenhum cliente disponível.")
  except Exception as e:
    st.error(f"Erro: {e}")
