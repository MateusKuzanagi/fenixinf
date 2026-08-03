from datetime import datetime
import streamlit as st
from supabase import Client, create_client

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E SUPABASE
# ==========================================
st.set_page_config(
    page_title="Fênix Assistência Técnica", page_icon="💻", layout="wide"
)

# Conexão com o Supabase (utilizando os dados do seu código)
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
# INTERFACE WEB - STREAMLIT
# ==========================================
st.title("🔥 Fênix • Assistência Técnica e Soluções de TI")
st.write(
    "Sistema gerenciado na nuvem via Supabase. Acesse de qualquer computador ou"
    " celular!"
)

# Menu Lateral (Abas do Sistema)
menu = st.sidebar.selectbox(
    "Menu de Navegação", ["Estoque / Produtos", "Cadastrar Novo Produto"]
)

# ------------------------------------------
# ABA 1: ESTOQUE E PRODUTOS
# ------------------------------------------
if menu == "Estoque / Produtos":
  st.subheader("📦 Consulta de Produtos e Peças")

  # Barra de pesquisa
  termo_busca = st.text_input(
      "🔎 Buscar por código ou nome do produto:", ""
  ).lower()

  try:
    response = supabase.table("Produtos").select("*").execute()
    produtos = response.data or []

    # Filtrar produtos se houver termo de busca
    if termo_busca:
      produtos = [
          p
          for p in produtos
          if termo_busca in str(p.get("id", "")).lower()
          or termo_busca in str(p.get("nomeproduto", "")).lower()
      ]

    if produtos:
      # Exibindo métricas rápidas no topo
      total_itens_qtd = sum(
          [int(p.get("qtdestoque", 0) or 0) for p in produtos]
      )
      col1, col2 = st.columns(2)
      col1.metric("Total de Cadastrados", len(produtos))
      col2.metric("Quantidade Total em Estoque", total_itens_qtd)

      st.markdown("---")

      # Formatando os dados para exibir numa tabela limpa na web
      dados_tabela = []
      for p in produtos:
        dados_tabela.append({
            "Código": p.get("id"),
            "Produto": p.get("nomeproduto"),
            "Descrição": p.get("descricao"),
            "Preço (R$)": f"R$ {float(p.get('preco', 0) or 0):.2f}",
            "Estoque": p.get("qtdestoque"),
        })

      st.dataframe(dados_tabela, use_container_width=True)
    else:
      st.info("Nenhum produto encontrado.")

  except Exception as e:
    st.error(f"Erro ao carregar dados do Supabase: {e}")

# ------------------------------------------
# ABA 2: CADASTRAR NOVO PRODUTO
# ------------------------------------------
elif menu == "Cadastrar Novo Produto":
  st.subheader("➕ Cadastro de Novo Produto ou Peça")

  with st.form("form_cadastro_produto"):
    col1, col2 = st.columns(2)
    with col1:
      cod_produto = st.text_input(
          "Código / ID do Produto (Ex: PROD01)"
      ).strip()
      nome_produto = st.text_input("Nome do Produto / Peça").strip()
      preco_produto = st.number_input(
          "Preço Unitário (R$)", min_value=0.0, format="%.2f"
      )

    with col2:
      qtd_produto = st.number_input(
          "Quantidade em Estoque", min_value=0, step=1
      )
      desc_produto = st.text_input("Descrição do Produto").strip()

    submitted = st.form_submit_button("💾 Salvar no Supabase")

    if submitted:
      if not cod_produto or not nome_produto:
        st.warning("Preencha o Código e o Nome do Produto!")
      else:
        try:
          novo_dado = {
              "id": cod_produto,
              "nomeproduto": nome_produto,
              "descricao": desc_produto,
              "preco": preco_produto,
              "qtdestoque": qtd_produto,
          }

          supabase.table("Produtos").insert(novo_dado).execute()
          st.success("Produto cadastrado com sucesso na nuvem!")
        except Exception as e:
          st.error(
              "Erro ao salvar. Verifique se o código já existe no Supabase:"
              f" {e}"
          )