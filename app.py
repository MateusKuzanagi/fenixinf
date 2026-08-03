from datetime import datetime
import io
import urllib.parse
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st
from supabase import Client, create_client

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E ESTILIZAÇÃO TECNOLÓGICA
# ==========================================
st.set_page_config(
    page_title="Fênix • Gestão Tecnológica", page_icon="⚡", layout="wide"
)

st.markdown(
    """
    <style>
        .main {
            background-color: #f4f7fc;
        }
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #cbd5e1;
            border-left: 5px solid #0ea5e9;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(14, 165, 233, 0.08);
            text-align: center;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b132b 0%, #1c2541 100%);
            color: #ffffff;
            border-right: 1px solid #3a506b;
        }
        [data-testid="stSidebar"] * {
            color: #e0f2fe !important;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #0284c7 0%, #1d4ed8 100%);
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
# CONTROLE DE SESSÃO (TELA DE LOGIN)
# ==========================================
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if not st.session_state.autenticado:
  col1, col2, col3 = st.columns([1, 1.2, 1])
  with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='text-align: center; color: #0b132b;'>⚡ Fênix • Gestão"
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
# MENU LATERAL REFINADO
# ==========================================
st.sidebar.markdown(
    "<h2 style='color: #0ea5e9; text-align: center;'>⚡ FÊNIX TECH</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação",
    [
        "📊 Dashboard Executivo",
        "📦 Gestão e Edição de Estoque",
        "👥 Clientes e Edição de Cadastros",
        "➕ Novo Cadastro (Produto/Cliente)",
        "📄 Ordens de Serviço & Venda de Peças",
        "🧾 Gerar Nota Fiscal (PDF)",
        "💬 Histórico e Envio WhatsApp",
    ],
)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Encerrar Sessão"):
  st.session_state.autenticado = False
  st.rerun()

# ==========================================
# 1. DASHBOARD EXECUTIVO
# ==========================================
if menu == "📊 Dashboard Executivo":
  st.markdown("## 📊 Painel de Controle Executivo")
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
          f"""<div class='metric-card'><h4 style='color: #334155;'>📦 Total"
          " Produtos</h4><h2 style='color:"
          f" #0ea5e9;'>{total_produtos}</h2></div>""",
          unsafe_allow_html=True,
      )
    with c2:
      st.markdown(
          f"""<div class='metric-card'><h4 style='color: #334155;'>👥 Base"
          " Clientes</h4><h2 style='color: #0ea5e9;'>{total_clientes}</h2></div>""",
          unsafe_allow_html=True,
      )
    with c3:
      st.markdown(
          f"""<div class='metric-card'><h4 style='color: #334155;'>💰 Valor em"
          " Estoque</h4><h2 style='color: #0ea5e9;'>R$"
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
      st.success("✨ Tudo sob controle! Nenhum produto com estoque crítico.")
  except Exception as e:
    st.error(f"Erro: {e}")

# ==========================================
# 2. GESTÃO E EDIÇÃO DE ESTOQUE
# ==========================================
elif menu == "📦 Gestão e Edição de Estoque":
  st.markdown("## 📦 Catálogo de Produtos e Gestão de Estoque")
  st.markdown("---")
  try:
    res = supabase.table("Produtos").select("*").execute()
    dados = res.data or []
    if dados:
      termo = st.text_input("🔎 Pesquisa rápida por nome do produto:").lower()
      if termo:
        dados = [
            d for d in dados if termo in str(d.get("nomeproduto", "")).lower()
        ]
      st.dataframe(pd.DataFrame(dados), use_container_width=True)

      st.markdown("### ✏️ Painel de Edição de Produto")
      prod_selecionado_id = st.selectbox(
          "Selecione o Código do Produto:", [str(p.get("id")) for p in dados]
      )
      if prod_selecionado_id:
        p_atual = next(
            (p for p in dados if str(p.get("id")) == prod_selecionado_id), None
        )
        if p_atual:
          with st.form("form_edit_produto"):
            c1, c2 = st.columns(2)
            with c1:
              novo_nome = st.text_input(
                  "Nome do Produto", value=p_atual.get("nomeproduto", "")
              )
              novo_preco = st.number_input(
                  "Preço Unitário (R$)",
                  value=float(p_atual.get("preco", 0) or 0),
                  format="%.2f",
              )
            with c2:
              nova_qtd = st.number_input(
                  "Quantidade em Estoque",
                  value=int(p_atual.get("qtdestoque", 0) or 0),
                  step=1,
              )
              nova_desc = st.text_input(
                  "Descrição", value=p_atual.get("descricao", "")
              )
            if st.form_submit_button("💾 Salvar Alterações"):
              supabase.table("Produtos").update({
                  "nomeproduto": novo_nome,
                  "preco": novo_preco,
                  "qtdestoque": nova_qtd,
                  "descricao": nova_desc,
              }).eq("id", prod_selecionado_id).execute()
              st.success("✅ Produto atualizado!")
  except Exception as e:
    st.error(f"Erro: {e}")

# ==========================================
# 3. CLIENTES E EDIÇÃO DE CADASTROS
# ==========================================
elif menu == "👥 Clientes e Edição de Cadastros":
  st.markdown("## 👥 Base de Clientes e Aparelhos")
  st.markdown("---")
  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []
    if clientes:
      st.dataframe(pd.DataFrame(clientes), use_container_width=True)
      st.markdown("### ✏️ Edição de Dados do Cliente")
      opcoes_cli_dict = {
          f"ID: {c.get('id')} - {c.get('nome')}": c for c in clientes
      }
      escolha = st.selectbox("Selecione:", list(opcoes_cli_dict.keys()))
      c_atual = opcoes_cli_dict[escolha]
      with st.form("form_edit_cliente"):
        e_nome = st.text_input("Nome", value=c_atual.get("nome", ""))
        e_tel = st.text_input("Telefone", value=c_atual.get("telefone", ""))
        e_end = st.text_input("Endereço", value=c_atual.get("endereco", ""))
        e_modelo = st.text_input(
            "Modelo Aparelho", value=c_atual.get("modeloaparelho", "")
        )
        if st.form_submit_button("💾 Atualizar"):
          supabase.table("Clientes").update({
              "nome": e_nome,
              "telefone": e_tel,
              "endereco": e_end,
              "modeloaparelho": e_modelo,
          }).eq("id", c_atual.get("id")).execute()
          st.success("✅ Atualizado com sucesso!")
  except Exception as e:
    st.error(f"Erro: {e}")

# ==========================================
# 4. NOVO CADASTRO (PRODUTO/CLIENTE)
# ==========================================
elif menu == "➕ Novo Cadastro (Produto/Cliente)":
  st.markdown("## ➕ Central de Cadastros Rápidos")
  st.markdown("---")
  tab1, tab2 = st.tabs(["📦 Cadastrar Produto", "👤 Cadastrar Cliente"])
  with tab1:
    with st.form("form_novo_prod", clear_on_submit=True):
      pid = st.text_input("Código / ID (Ex: P002)").strip()
      nome = st.text_input("Nome do Produto").strip()
      preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
      qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1)
      if st.form_submit_button("🚀 Salvar Produto"):
        supabase.table("Produtos").insert({
            "id": pid,
            "nomeproduto": nome,
            "preco": preco,
            "qtdestoque": qtd,
        }).execute()
        st.success("✅ Produto cadastrado!")
  with tab2:
    with st.form("form_novo_cli", clear_on_submit=True):
      nome_c = st.text_input("Nome Completo *").strip()
      tel_c = st.text_input("Telefone / WhatsApp").strip()
      m_ap = st.text_input("Modelo do Aparelho").strip()
      if st.form_submit_button("🚀 Salvar Cliente"):
        supabase.table("Clientes").insert({
            "nome": nome_c,
            "telefone": tel_c,
            "modeloaparelho": m_ap,
            "dataentrada": datetime.now().strftime("%d/%m/%Y"),
        }).execute()
        st.success("✅ Cliente cadastrado!")

# ==========================================
# 5. ORDENS DE SERVIÇO & VENDA DE PEÇAS
# ==========================================
elif menu == "📄 Ordens de Serviço & Venda de Peças":
  st.markdown("## 📄 Ordem de Serviço & Venda de Peças / Serviços Extras")
  st.markdown(
      "Selecione o cliente, adicione peças do estoque (com baixa automática),"
      " defina serviços extras e gere o PDF completo."
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

      with st.form("form_custom_os_venda"):
        st.subheader("🛠️ Detalhes da Ordem de Serviço e Laudo")
        c1, c2 = st.columns(2)
        with c1:
          defeito_relatado = st.text_area(
              "Defeito Relatado:",
              value="Aparelho com falha de funcionamento.",
          )
          laudo_tecnico = st.text_area(
              "Serviço Técnico / Mão de Obra:",
              value="Manutenção e testes gerais.",
          )
        with c2:
          valor_mao_obra = st.number_input(
              "Valor da Mão de Obra (R$):",
              min_value=0.0,
              value=100.0,
              format="%.2f",
          )
          prazo_entrega = st.text_input(
              "Prazo Estimado de Entrega:", value="2 dias úteis"
          )
          obs_extras = st.text_area(
              "Observações / Serviços Extras:",
              value="Nenhum adicional registrado.",
          )

        st.markdown("---")
        st.subheader("🛒 Venda de Peças / Produtos do Estoque")

        pecas_selecionadas = []
        total_pecas = 0.0
        produtos_escolhidos = []
        opcoes_prod = {}

        if produtos:
          opcoes_prod = {
              f"{p.get('nomeproduto')} (Disponível: {p.get('qtdestoque')} | R$ {p.get('preco')})": p
              for p in produtos
          }

          produtos_escolhidos = st.multiselect(
              "Selecione as peças a serem aplicadas/vendidas para este cliente:",
              list(opcoes_prod.keys()),
          )

        btn_gerar_pdf_venda = st.form_submit_button(
            "🖨️ Compilar e Salvar O.S."
        )

      # Processamento fora do form para capturar dinamicamente os inputs de quantidade sem erro de chave
      if btn_gerar_pdf_venda:
        qtd_por_produto = {}
        total_pecas = 0.0

        if produtos_escolhidos:
          for prod_label in produtos_escolhidos:
            p_obj = opcoes_prod[prod_label]
            max_estoque = int(p_obj.get("qtdestoque", 0))
            # Quantidade fixa padrão ou controlada
            q_venda = 1
            qtd_por_produto[p_obj.get("id")] = {
                "obj": p_obj,
                "qtd": q_venda,
                "subtotal": float(p_obj.get("preco", 0)) * q_venda,
            }
            total_pecas += float(p_obj.get("preco", 0)) * q_venda

        valor_total_geral = valor_mao_obra + total_pecas

        # Atualiza o estoque no Supabase para cada peça vendida
        for pid_str, info in qtd_por_produto.items():
          p_obj = info["obj"]
          qtd_vendida = info["qtd"]
          novo_estoque = int(p_obj.get("qtdestoque", 0)) - qtd_vendida

          supabase.table("Produtos").update(
              {"qtdestoque": max(0, novo_estoque)}
          ).eq("id", pid_str).execute()

        # Gera o PDF da OS com os itens e observações
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        p.setFont("Helvetica-Bold", 14)
        p.drawString(
            50, 750, "FÊNIX • ASSISTÊNCIA TÉCNICA E VENDA DE PEÇAS"
        )
        p.setFont("Helvetica", 9)
        p.drawString(
            50, 735, "Ordem de Serviço, Venda de Peças e Serviços Extras"
        )
        p.line(50, 725, 560, 725)

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 700, "1. Dados do Cliente:")
        p.setFont("Helvetica", 10)
        p.drawString(50, 682, f"Cliente: {cli_os.get('nome', '')}")
        p.drawString(50, 667, f"Telefone: {cli_os.get('telefone', '')}")
        p.drawString(
            50,
            652,
            f"Aparelho: {cli_os.get('tipoaparelho', '')} -"
            f" {cli_os.get('modeloaparelho', '')}",
        )

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 622, "2. Relatório Técnico e Serviços Extras:")
        p.setFont("Helvetica", 10)
        p.drawString(50, 604, f"Defeito: {defeito_relatado}")
        p.drawString(50, 589, f"Serviço Executado: {laudo_tecnico}")
        p.drawString(50, 574, f"Observações / Extras: {obs_extras}")

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 544, "3. Peças / Produtos Aplicados (Baixa em Estoque):")
        p.setFont("Helvetica", 10)
        y_pos = 526
        if qtd_por_produto:
          for item in qtd_por_produto.values():
            nome_prod = item["obj"].get("nomeproduto")
            q_v = item["qtd"]
            sub = item["subtotal"]
            p.drawString(
                50,
                y_pos,
                f"- {q_v}x {nome_prod} | Subtotal: R$ {sub:.2f}",
            )
            y_pos -= 15
        else:
          p.drawString(50, y_pos, "Nenhuma peça avulsa selecionada.")
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

        st.success(
            "🎉 O.S. gerada com sucesso e estoque atualizado automaticamente!"
        )
        st.download_button(
            label="📥 Baixar PDF da O.S. com Venda de Peças",
            data=buffer,
            file_name=f"OS_Venda_Cliente_{cli_os.get('id', 'geral')}.pdf",
            mime="application/pdf",
        )
    else:
      st.info("Nenhum cliente cadastrado.")
  except Exception as e:
    st.error(f"Erro ao processar Ordem de Serviço e Venda: {e}")

# ==========================================
# 6. GERAR NOTA FISCAL (PDF)
# ==========================================
elif menu == "🧾 Gerar Nota Fiscal (PDF)":
  st.markdown("## 🧾 Emissor de Nota Fiscal de Serviços (PDF)")
  st.markdown("---")
  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []
    if clientes:
      opcoes_nf_dict = {
          f"ID: {c.get('id')} - {c.get('nome')}": c for c in clientes
      }
      escolha_nf = st.selectbox(
          "Selecione o Cliente:", list(opcoes_nf_dict.keys())
      )
      cli_nf = opcoes_nf_dict[escolha_nf]

      with st.form("form_emissao_nf"):
        val_serv = st.number_input(
            "Valor dos Serviços (R$):", value=150.0, format="%.2f"
        )
        submitted = st.form_submit_button("Preparar Nota Fiscal PDF")

      if submitted or "gerar_nf_pdf" in st.session_state:
        st.session_state.gerar_nf_pdf = True

        buffer_nf = io.BytesIO()
        p = canvas.Canvas(buffer_nf, pagesize=letter)
        p.setFont("Helvetica-Bold", 12)
        p.drawString(
            50,
            750,
            f"NOTA FISCAL DE SERVIÇOS - Tomador: {cli_nf.get('nome')}",
        )
        p.drawString(50, 730, f"Valor Total: R$ {val_serv:.2f}")
        p.showPage()
        p.save()
        buffer_nf.seek(0)

        st.success("🎉 Nota Fiscal pronta para download!")
        st.download_button(
            label="📥 Baixar Nota Fiscal em PDF",
            data=buffer_nf,
            file_name="Nota_Fiscal.pdf",
            mime="application/pdf",
        )
  except Exception as e:
    st.error(f"Erro: {e}")

# ==========================================
# 7. HISTÓRICO E ENVIO WHATSAPP
# ==========================================
elif menu == "💬 Histórico e Envio WhatsApp":
  st.markdown("## 💬 Histórico de Atendimento e Envio WhatsApp")
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
          "#25d366; color: white; padding: 0.6rem; border: none; border-radius:"
          " 8px; font-weight: bold; cursor: pointer;">💬 Abrir WhatsApp com"
          " Mensagem Pronta</button></a>""",
          unsafe_allow_html=True,
      )
  except Exception as e:
    st.error(f"Erro: {e}")
