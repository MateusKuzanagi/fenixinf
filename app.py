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
        /* Fundo geral da aplicação - Tom tecnológico claro/limpo */
        .main {
            background-color: #f4f7fc;
        }
        
        /* Cartões de métricas estilo Glassmorphism / Tech */
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #cbd5e1;
            border-left: 5px solid #0ea5e9;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(14, 165, 233, 0.08);
            text-align: center;
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 20px -3px rgba(14, 165, 233, 0.15);
        }
        
        /* Barra lateral estilo Painel Tech (Azul Noite Profundo) */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b132b 0%, #1c2541 100%);
            color: #ffffff;
            border-right: 1px solid #3a506b;
        }
        [data-testid="stSidebar"] * {
            color: #e0f2fe !important;
        }
        
        /* Botões modernos com destaque tecnológico */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #0284c7 0%, #1d4ed8 100%);
            box-shadow: 0 6px 16px rgba(14, 165, 233, 0.5);
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
    st.markdown(
        "<p style='text-align: center; color: #475569;'>Acesse o ecossistema"
        " inteligente com suas credenciais.</p>",
        unsafe_allow_html=True,
    )

    with st.form("form_login"):
      usuario = st.text_input("Usuário").strip()
      senha = st.text_input("Senha", type="password").strip()
      st.markdown("<br>", unsafe_allow_html=True)
      btn_login = st.form_submit_button(
          "Entrar no Sistema", use_container_width=True
      )

      if btn_login:
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
        "📄 Ordens de Serviço Customizadas",
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
  st.markdown(
      "Visão centralizada de indicadores e fluxo operacional da sua"
      " assistência."
  )
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
          f"""<div class='metric-card'><h4 style='color: #334155;'>📦 Total Produtos</h4><h2 style='color: #0ea5e9;'>{total_produtos}</h2></div>""",
          unsafe_allow_html=True,
      )
    with c2:
      st.markdown(
          f"""<div class='metric-card'><h4 style='color: #334155;'>👥 Base Clientes</h4><h2 style='color: #0ea5e9;'>{total_clientes}</h2></div>""",
          unsafe_allow_html=True,
      )
    with c3:
      st.markdown(
          f"""<div class='metric-card'><h4 style='color: #334155;'>💰 Valor em Estoque</h4><h2 style='color: #0ea5e9;'>R$ {val_estoque:,.2f}</h2></div>""",
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
      df_baixo = pd.DataFrame(baixo_estoque)
      st.dataframe(
          df_baixo[["id", "nomeproduto", "qtdestoque", "preco"]],
          use_container_width=True,
      )
    else:
      st.success("✨ Tudo sob controle! Nenhum produto com estoque crítico.")

  except Exception as e:
    st.error(f"Erro ao conectar com o banco de dados: {e}")

# ==========================================
# 2. GESTÃO E EDIÇÃO DE ESTOQUE
# ==========================================
elif menu == "📦 Gestão e Edição de Estoque":
  st.markdown("## 📦 Catálogo de Produtos e Gestão de Estoque")
  st.markdown(
      "Pesquise, visualize e altere informações ou quantidades dos produtos em"
      " tempo real."
  )
  st.markdown("---")

  try:
    res = supabase.table("Produtos").select("*").execute()
    dados = res.data or []

    if dados:
      termo = st.text_input(
          "🔎 Pesquisa rápida por código ou nome do produto:"
      ).lower()
      if termo:
        dados = [
            d
            for d in dados
            if termo in str(d.get("id", "")).lower()
            or termo in str(d.get("nomeproduto", "")).lower()
        ]

      df = pd.DataFrame(dados)
      st.dataframe(df, use_container_width=True)

      st.markdown("### ✏️ Painel de Edição de Produto")
      ids_disponiveis = [str(p.get("id")) for p in dados]
      prod_selecionado_id = st.selectbox(
          "Selecione o Código do Produto que deseja alterar:", ids_disponiveis
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

            btn_atualizar_prod = st.form_submit_button(
                "💾 Salvar Alterações do Produto"
            )
            if btn_atualizar_prod:
              supabase.table("Produtos").update({
                  "nomeproduto": novo_nome,
                  "preco": novo_preco,
                  "qtdestoque": nova_qtd,
                  "descricao": nova_desc,
              }).eq("id", prod_selecionado_id).execute()
              st.success(
                  "✅ Produto atualizado com sucesso! Atualize a página para ver"
                  " as mudanças."
              )
    else:
      st.info("Nenhum produto cadastrado no momento.")
  except Exception as e:
    st.error(f"Erro ao gerenciar produtos: {e}")

# ==========================================
# 3. CLIENTES E EDIÇÃO DE CADASTROS
# ==========================================
elif menu == "👥 Clientes e Edição de Cadastros":
  st.markdown("## 👥 Base de Clientes, Aparelhos e Prontuários")
  st.markdown(
      "Consulte os dados dos clientes e edite informações de aparelhos ou"
      " status quando necessário."
  )
  st.markdown("---")

  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []

    if clientes:
      termo_cli = st.text_input(
          "🔎 Buscar por cliente, modelo ou telefone:"
      ).lower()
      if termo_cli:
        clientes = [
            c
            for c in clientes
            if termo_cli in str(c.get("nome", "")).lower()
            or termo_cli in str(c.get("modeloaparelho", "")).lower()
            or termo_cli in str(c.get("telefone", "")).lower()
        ]

      df_cli = pd.DataFrame(clientes)
      st.dataframe(df_cli, use_container_width=True)

      st.markdown("### ✏️ Prontuário e Edição de Dados do Cliente")
      opcoes_cli_dict = {}
      for c in clientes:
        cid = c.get("id", "S/ID")
        cnome = c.get("nome", "Sem Nome")
        camarelho = c.get("modeloaparelho", "Sem Aparelho")
        rotulo = f"ID: {cid} - {cnome} ({camarelho})"
        opcoes_cli_dict[rotulo] = c

      escolha_cli_edit_label = st.selectbox(
          "Selecione o registro para edição:", list(opcoes_cli_dict.keys())
      )

      if escolha_cli_edit_label:
        c_atual = opcoes_cli_dict[escolha_cli_edit_label]
        id_edit = c_atual.get("id")

        if c_atual:
          with st.form("form_edit_cliente"):
            c1, c2 = st.columns(2)
            with c1:
              e_nome = st.text_input(
                  "Nome do Cliente", value=c_atual.get("nome", "")
              )
              e_tel = st.text_input(
                  "Telefone", value=c_atual.get("telefone", "")
              )
              e_end = st.text_input(
                  "Endereço", value=c_atual.get("endereco", "")
              )
              e_tipo = st.text_input(
                  "Tipo de Aparelho", value=c_atual.get("tipoaparelho", "")
              )
            with c2:
              e_modelo = st.text_input(
                  "Modelo do Aparelho", value=c_atual.get("modeloaparelho", "")
              )
              e_imei = st.text_input(
                  "Número de Série / IMEI",
                  value=c_atual.get("numeroserieimei", ""),
              )
              e_saida = st.text_input(
                  "Data de Saída / Status", value=c_atual.get("datasaida", "")
              )
              e_senha = st.text_input(
                  "Senha / PIN", value=c_atual.get("senhaaparelho", "")
              )

            btn_salvar_cli = st.form_submit_button(
                "💾 Atualizar Dados do Cliente"
            )
            if btn_salvar_cli:
              query = supabase.table("Clientes").update({
                  "nome": e_nome,
                  "telefone": e_tel,
                  "endereco": e_end,
                  "tipoaparelho": e_tipo,
                  "modeloaparelho": e_modelo,
                  "numeroserieimei": e_imei,
                  "datasaida": e_saida,
                  "senhaaparelho": e_senha,
              })
              if id_edit is not None:
                query.eq("id", id_edit).execute()
              else:
                query.eq("nome", e_nome).execute()
              st.success(
                  "✅ Cliente atualizado com sucesso! Atualize a página para"
                  " refletir as mudanças."
              )
    else:
      st.info("Nenhum cliente cadastrado.")
  except Exception as e:
    st.error(f"Erro ao carregar clientes: {e}")

# ==========================================
# 4. NOVO CADASTRO (PRODUTO/CLIENTE)
# ==========================================
elif menu == "➕ Novo Cadastro (Produto/Cliente)":
  st.markdown("## ➕ Central de Cadastros Rápidos")
  st.markdown(
      "Insira novos itens no estoque ou novos clientes/aparelhos na base de"
      " dados."
  )
  st.markdown("---")

  tab1, tab2 = st.tabs(["📦 Cadastrar Produto / Peça", "👤 Cadastrar Cliente"])

  with tab1:
    with st.form("form_novo_prod", clear_on_submit=True):
      c1, c2 = st.columns(2)
      with c1:
        pid = st.text_input("Código / ID (Ex: P002)").strip()
        nome = st.text_input("Nome do Produto").strip()
        preco = st.number_input(
            "Preço Unitário (R$)", min_value=0.0, format="%.2f"
        )
      with c2:
        qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1)
        desc = st.text_input("Descrição Opcional").strip()

      if st.form_submit_button("🚀 Salvar Novo Produto"):
        if not pid or not nome:
          st.warning("Preencha o Código e o Nome do Produto.")
        else:
          try:
            supabase.table("Produtos").insert({
                "id": pid,
                "nomeproduto": nome,
                "descricao": desc,
                "preco": preco,
                "qtdestoque": qtd,
            }).execute()
            st.success("✅ Produto cadastrado com sucesso!")
          except Exception as e:
            st.error(
                f"Erro ao salvar produto (Verifique se o código já existe): {e}"
            )

  with tab2:
    with st.form("form_novo_cli", clear_on_submit=True):
      c1, c2 = st.columns(2)
      with c1:
        nome_c = st.text_input("Nome Completo *").strip()
        tel_c = st.text_input("Telefone / WhatsApp").strip()
        end_c = st.text_input("Endereço").strip()
        t_ap = st.text_input(
            "Tipo de Aparelho (Notebook/Smartphone)"
        ).strip()
      with c2:
        m_ap = st.text_input("Modelo do Aparelho").strip()
        imei_c = st.text_input("Número de Série / IMEI").strip()
        senha_c = st.text_input("Senha / PIN de Desbloqueio").strip()
        dt_ent = st.text_input(
            "Data de Entrada", value=datetime.now().strftime("%d/%m/%Y")
        ).strip()

      if st.form_submit_button("🚀 Salvar Novo Cliente"):
        if not nome_c:
          st.warning("O nome do cliente é obrigatório.")
        else:
          try:
            supabase.table("Clientes").insert({
                "nome": nome_c,
                "telefone": tel_c,
                "endereco": end_c,
                "tipoaparelho": t_ap,
                "modeloaparelho": m_ap,
                "numeroserieimei": imei_c,
                "senhaaparelho": senha_c,
                "dataentrada": dt_ent,
                "datasaida": "",
            }).execute()
            st.success("✅ Cliente e aparelho cadastrados com sucesso!")
          except Exception as e:
            st.error(f"Erro ao cadastrar cliente: {e}")

# ==========================================
# 5. ORDENS DE SERVIÇO CUSTOMIZADAS
# ==========================================
elif menu == "📄 Ordens de Serviço Customizadas":
  st.markdown("## 📄 Editor Avançado de Ordem de Serviço (PDF)")
  st.markdown(
      "Personalize valores, serviços executados e observações antes de gerar"
      " o documento oficial."
  )
  st.markdown("---")

  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []

    if clientes:
      opcoes_os_dict = {}
      for c in clientes:
        cid = c.get("id", "S/ID")
        cnome = c.get("nome", "Sem Nome")
        camarelho = c.get("modeloaparelho", "Sem Aparelho")
        rotulo = f"ID: {cid} - {cnome} ({camarelho})"
        opcoes_os_dict[rotulo] = c

      escolha_os_label = st.selectbox(
          "Selecione o Cliente para emitir a O.S.:", list(opcoes_os_dict.keys())
      )

      if escolha_os_label:
        cli_os = opcoes_os_dict[escolha_os_label]

        if cli_os:
          st.markdown("### 📝 Ajustes Específicos para esta O.S.")
          with st.form("form_custom_os"):
            c1, c2 = st.columns(2)
            with c1:
              defeito_relatado = st.text_area(
                  "Defeito Relatado / Problema:",
                  value="Aparelho não liga / Falha de funcionamento geral.",
              )
              laudo_tecnico = st.text_area(
                  "Laudo Técnico / Serviços a Executar:",
                  value=(
                      "Manutenção preventiva, substituição de componentes"
                      " danificados e testes finais."
                  ),
              )
            with c2:
              valor_orcamento = st.number_input(
                  "Valor Orçado / Total (R$):",
                  min_value=0.0,
                  value=150.0,
                  format="%.2f",
              )
              prazo_entrega = st.text_input(
                  "Prazo Estimado de Entrega:", value="3 dias úteis"
              )

            btn_gerar_pdf = st.form_submit_button(
                "🖨️ Compilar e Gerar PDF da O.S."
            )

          if btn_gerar_pdf:
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)

            p.setFont("Helvetica-Bold", 16)
            p.drawString(
                50, 750, "FÊNIX • ASSISTÊNCIA TÉCNICA E SOLUÇÕES CORPORATIVAS"
            )
            p.setFont("Helvetica", 10)
            p.drawString(
                50, 735, "Comprovante de Entrada e Ordem de Serviço Oficial"
            )
            p.line(50, 725, 560, 725)

            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 695, "1. Dados do Cliente:")
            p.setFont("Helvetica", 10)
            p.drawString(
                50, 675, f"Cliente: {cli_os.get('nome', 'Não informado')}"
            )
            p.drawString(
                50, 660, f"Telefone: {cli_os.get('telefone', 'Não informado')}"
            )
            p.drawString(
                50, 645, f"Endereço: {cli_os.get('endereco', 'Não informado')}"
            )

            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 615, "2. Especificações do Aparelho:")
            p.setFont("Helvetica", 10)
            p.drawString(
                50,
                595,
                f"Aparelho: {cli_os.get('tipoaparelho', '')} -"
                f" {cli_os.get('modeloaparelho', '')}",
            )
            p.drawString(
                50, 580, f"Nº Série / IMEI: {cli_os.get('numeroserieimei', '')}"
            )
            p.drawString(
                50, 565, f"Data de Entrada: {cli_os.get('dataentrada', '')}"
            )

            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 535, "3. Relatório e Custos:")
            p.setFont("Helvetica", 10)
            p.drawString(50, 515, f"Defeito: {defeito_relatado}")
            p.drawString(50, 500, f"Serviço: {laudo_tecnico}")
            p.drawString(
                50,
                485,
                f"Valor Total Estimado: R$ {valor_orcamento:.2f} | Prazo:"
                f" {prazo_entrega}",
            )

            p.line(50, 440, 560, 440)
            p.setFont("Helvetica-Oblique", 8)
            p.drawString(
                50,
                425,
                "Aparelhos não retirados no prazo de 90 dias passarão a"
                " incidir taxas de guarda e armazenamento.",
            )
            p.drawString(
                50, 300, "__________________________________________________"
            )
            p.drawString(50, 285, "Assinatura do Cliente")

            p.showPage()
            p.save()
            buffer.seek(0)

            st.success("🎉 Ordem de Serviço compilada com sucesso!")
            st.download_button(
                label="📥 Baixar Documento PDF Oficial",
                data=buffer,
                file_name=(
                    f"OS_Fenix_Cliente_{cli_os.get('id', 'geral')}.pdf"
                ),
                mime="application/pdf",
            )
    else:
      st.info("Nenhum cliente cadastrado para gerar O.S.")
  except Exception as e:
    st.error(f"Erro ao gerar relatório PDF: {e}")

# ==========================================
# 6. GERAR NOTA FISCAL (PDF)
# ==========================================
elif menu == "🧾 Gerar Nota Fiscal (PDF)":
  st.markdown("## 🧾 Emissor de Nota Fiscal de Serviços (PDF)")
  st.markdown(
      "Preencha os campos fiscais, impostos e discriminação para emitir a"
      " Nota Fiscal do cliente."
  )
  st.markdown("---")

  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []

    if clientes:
      opcoes_nf_dict = {}
      for c in clientes:
        cid = c.get("id", "S/ID")
        cnome = c.get("nome", "Sem Nome")
        camarelho = c.get("modeloaparelho", "Sem Aparelho")
        rotulo = f"ID: {cid} - {cnome} ({camarelho})"
        opcoes_nf_dict[rotulo] = c

      escolha_cli_nf_label = st.selectbox(
          "Selecione o Cliente para faturamento:", list(opcoes_nf_dict.keys())
      )

      if escolha_cli_nf_label:
        cli_nf = opcoes_nf_dict[escolha_cli_nf_label]

        if cli_nf:
          with st.form("form_emissao_nf"):
            st.subheader("📋 Informações Fiscais e do Tomador")
            c1, c2 = st.columns(2)
            with c1:
              doc_cliente = st.text_input(
                  "CPF / CNPJ do Tomador:", value="000.000.000-00"
              )
              inscricao_mun = st.text_input(
                  "Inscrição Municipal (Opcional):", value=""
              )
              email_nf = st.text_input("E-mail para Envio:", value="")
            with c2:
              numero_nf = st.text_input(
                  "Número da Nota Fiscal:",
                  value=datetime.now().strftime("2026%m%d01"),
              )
              data_emissao = st.text_input(
                  "Data de Emissão:",
                  value=datetime.now().strftime("%d/%m/%Y %H:%M"),
              )
              natureza_operacao = st.text_input(
                  "Natureza da Operação:",
                  value="Prestação de Serviços de Manutenção",
              )

            st.markdown("---")
            st.subheader("💼 Discriminação dos Serviços e Valores")
            discriminacao = st.text_area(
                "Discriminação dos Serviços Executados:",
                value=(
                    f"Serviço técnico especializado prestado no equipamento"
                    f" {cli_nf.get('tipoaparelho', '')} -"
                    f" {cli_nf.get('modeloaparelho', '')} (Série/IMEI:"
                    f" {cli_nf.get('numeroserieimei', '')})."
                ),
            )

            c3, c4, c5 = st.columns(3)
            with c3:
              valor_servicos = st.number_input(
                  "Valor dos Serviços (R$):",
                  min_value=0.0,
                  value=150.0,
                  format="%.2f",
              )
            with c4:
              aliquota_iss = st.number_input(
                  "Alíquota ISS (%):",
                  min_value=0.0,
                  value=5.0,
                  format="%.2f",
              )
            with c5:
              outras_deducoes = st.number_input(
                  "Descontos / Deduções (R$):",
                  min_value=0.0,
                  value=0.0,
                  format="%.2f",
              )

            btn_gerar_nf = st.form_submit_button(
                "🖨️ Processar e Gerar Nota Fiscal PDF"
            )

          if btn_gerar_nf:
            val_liquido = valor_servicos - outras_deducoes
            val_iss = val_liquido * (aliquota_iss / 100.0)

            buffer_nf = io.BytesIO()
            p = canvas.Canvas(buffer_nf, pagesize=letter)

            p.setFont("Helvetica-Bold", 14)
            p.drawString(
                50, 750, "PREFEITURA MUNICIPAL • NOTA FISCAL DE SERVIÇOS (NFS-e)"
            )
            p.setFont("Helvetica", 9)
            p.drawString(50, 735, "Fênix Assistência Técnica e Soluções Ltda")
            p.drawString(
                50, 722, "CNPJ: 00.000.000/0001-00 | Inscrição Municipal: 123456"
            )
            p.line(50, 712, 560, 712)

            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, 692, f"Nota Fiscal Nº: {numero_nf}")
            p.setFont("Helvetica", 10)
            p.drawString(300, 692, f"Data/Hora Emissão: {data_emissao}")
            p.drawString(50, 677, f"Natureza da Operação: {natureza_operacao}")

            p.line(50, 667, 560, 667)
            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, 647, "IDENTIFICAÇÃO DO TOMADOR DE SERVIÇOS")
            p.setFont("Helvetica", 10)
            p.drawString(
                50, 627, f"Nome/Razão Social: {cli_nf.get('nome', '')}"
            )
            p.drawString(50, 612, f"CPF/CNPJ: {doc_cliente}")
            p.drawString(50, 597, f"Endereço: {cli_nf.get('endereco', '')}")
            p.drawString(300, 597, f"Telefone: {cli_nf.get('telefone', '')}")

            p.line(50, 582, 560, 582)
            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, 562, "DISCRIMINAÇÃO DOS SERVIÇOS")

            text_object = p.beginText(50, 542)
            text_object.setFont("Helvetica", 10)
            for linha in discriminacao.split("\n"):
              text_object.textLine(linha)
            p.drawText(text_object)

            p.line(50, 440, 560, 440)
            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, 420, "VALORES E TRIBUTOS")
            p.setFont("Helvetica", 10)
            p.drawString(50, 400, f"Valor dos Serviços: R$ {valor_servicos:.2f}")
            p.drawString(250, 400, f"Deduções: R$ {outras_deducoes:.2f}")
            p.drawString(400, 400, f"Valor Líquido: R$ {val_liquido:.2f}")
            p.drawString(
                50,
                380,
                f"Alíquota ISS: {aliquota_iss:.2f}% | Valor do ISS: R$"
                f" {val_iss:.2f}",
            )

            p.line(50, 330, 560, 330)
            p.setFont("Helvetica-Oblique", 8)
            p.drawString(
                50,
                315,
                "Documento emitido por sistema eletrônico de gestão Fênix."
                " Válido como comprovante fiscal de prestação de serviços.",
            )

            p.showPage()
            p.save()
            buffer_nf.seek(0)

            st.success("🎉 Nota Fiscal gerada com sucesso!")
            st.download_button(
                label="📥 Baixar Nota Fiscal em PDF",
                data=buffer_nf,
                file_name=f"Nota_Fiscal_{numero_nf}.pdf",
                mime="application/pdf",
            )
    else:
      st.info("Nenhum cliente cadastrado para gerar Nota Fiscal.")
  except Exception as e:
    st.error(f"Erro ao gerar Nota Fiscal: {e}")

# ==========================================
# 7. HISTÓRICO E ENVIO WHATSAPP
# ==========================================
elif menu == "💬 Histórico e Envio WhatsApp":
  st.markdown("## 💬 Histórico de Compras/Serviços e Envio via WhatsApp")
  st.markdown(
      "Visualize o histórico detalhado do cliente e envie mensagens"
      " automáticas direto pelo WhatsApp."
  )
  st.markdown("---")

  try:
    res = supabase.table("Clientes").select("*").execute()
    clientes = res.data or []

    if clientes:
      opcoes_hist_dict = {}
      for c in clientes:
        cid = c.get("id", "S/ID")
        cnome = c.get("nome", "Sem Nome")
        camarelho = c.get("modeloaparelho", "Sem Aparelho")
        rotulo = f"ID: {cid} - {cnome} ({camarelho})"
        opcoes_hist_dict[rotulo] = c

      escolha_hist_label = st.selectbox(
          "Selecione o Cliente para consultar o histórico:",
          list(opcoes_hist_dict.keys()),
      )

      if escolha_hist_label:
        cli_hist = opcoes_hist_dict[escolha_hist_label]

        st.markdown(f"### 📋 Prontuário de: {cli_hist.get('nome', '')}")
        col_h1, col_h2 = st.columns(2)

        with col_h1:
          st.info(f"📱 **Telefone/WhatsApp:** {cli_hist.get('telefone', '')}")
          st.info(f"🏠 **Endereço:** {cli_hist.get('endereco', '')}")
        with col_h2:
          st.info(
              f"💻 **Aparelho:** {cli_hist.get('tipoaparelho', '')} -"
              f" {cli_hist.get('modeloaparelho', '')}"
          )
          st.info(
              f"📅 **Data de Entrada:** {cli_hist.get('dataentrada', '')}"
          )

        st.markdown("---")
        st.subheader("🚀 Ações de Envio Automático via WhatsApp")

        # Mensagem padrão personalizada para o cliente
        nome_cliente = cli_hist.get("nome", "Cliente")
        telefone_cliente = "".join(
            filter(str.isdigit, str(cli_hist.get("telefone", "")))
        )
        aparelho = cli_hist.get("modeloaparelho", "seu equipamento")

        texto_msg = (
            f"Olá {nome_cliente}, aqui é da Fênix Assistência Técnica! ⚡\n\n"
            f"Estamos entrando em contato referente ao seu histórico de atendimento"
            f" do aparelho *{aparelho}*.\n"
            f"Data de entrada: {cli_hist.get('dataentrada', 'N/D')}.\n\n"
            f"Qualquer dúvida estamos à disposição!"
        )

        texto_codificado = urllib.parse.quote(texto_msg)
        link_whatsapp = f"https://wa.me/55{telefone_cliente}?text={texto_codificado}"

        c_w1, c_w2 = st.columns(2)
        with c_w1:
          st.markdown(
              f"""
                    <a href="{link_whatsapp}" target="_blank">
                        <button style="width: 100%; background-color: #25d366; color: white; padding: 0.6rem; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);">
                            💬 Abrir WhatsApp com Mensagem Pronta
                        </button>
                    </a>
                    """,
              unsafe_allow_html=True,
          )
        with c_w2:
          st.success(
              "💡 *Dica:* Baixe o PDF da Ordem de Serviço ou Nota Fiscal no menu"
              " correspondente e envie o arquivo junto no chat do WhatsApp."
          )

    else:
      st.info("Nenhum cliente cadastrado no momento.")
  except Exception as e:
    st.error(f"Erro ao carregar histórico: {e}")
