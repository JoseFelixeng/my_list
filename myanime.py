import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date

# Funções auxiliares
def carregar_csv(path, colunas):
	if not os.path.exists(path):
		return pd.DataFrame(columns=colunas)
	return pd.read_csv(path)

def salvar_csv(df, path):
	df.to_csv(path, index=False)

# Caminhos dos CSVs
CSV_ANIMES = "anime_lista.csv"
CSV_TEMPORADA = "temporada_animes.csv"
CSV_MANGAS = "mangas_livros.csv"

# Carregamento
COL_ANIMES = ["List", "Name", "Note", "Categoria", "Genero", "Descrição"]
COL_TEMP = COL_ANIMES + ["Temporada", "Episodios", "Assistido", "Atualizado"]
COL_MANGAS = ["ID", "Nome", "Tipo", "Gênero", "Descrição", "Progresso"]

df_animes = carregar_csv(CSV_ANIMES, COL_ANIMES)
df_temp = carregar_csv(CSV_TEMPORADA, COL_TEMP)
df_mangas = carregar_csv(CSV_MANGAS, COL_MANGAS)

# Estilo customizado
st.markdown("""
	<style>
		#MainMenu, footer {visibility: hidden;}
		.css-1v0mbdj, .stDataFrame {
			font-family: 'Segoe UI', sans-serif;
			font-size: 16px;
		}
	</style>
""", unsafe_allow_html=True)

st.title("📺 Aplicativo de Gerenciamento de Animes, Mangás e Livros")
menu = st.sidebar.radio("Navegar", ["📋 Ver Lista", "➕ Adicionar Anime", "✏️ Editar Anime", "📅 Temporada", "📖 Mangás e Livros"])

# ------------------------ Ver Lista ------------------------
if menu == "📋 Ver Lista":
	st.subheader("📃 Lista de Animes")
	df_mostrar = df_animes.copy()
	df_mostrar["Descrição"] = df_mostrar["Descrição"].apply(lambda x: x[:100] + "..." if len(x) > 100 else x)
	tab1, tab2 = st.tabs(["🌤 Buscar por Nome", "🎭 Buscar por Gênero"])

	with tab1:
		nomes = sorted(df_mostrar["Name"].dropna().unique())
		nome_selecionados = st.multiselect("Filtrar por Nome:", options=nomes)

	with tab2:
		generos = sorted(df_mostrar["Genero"].dropna().unique())
		genero_selecionados = st.multiselect("Filtrar por Gênero:", options=generos)

	df_filtrado = df_mostrar.copy()
	if nome_selecionados:
		df_filtrado = df_filtrado[df_filtrado["Name"].isin(nome_selecionados)]
	if genero_selecionados:
		df_filtrado = df_filtrado[df_filtrado["Genero"].isin(genero_selecionados)]

	st.markdown("### 📄 Resultado da Busca")
	st.dataframe(df_filtrado, use_container_width=True, hide_index=True, height=500)
	st.write(f"🔍 Exibindo {len(df_filtrado)} de {len(df_mostrar)} animes")

	st.markdown("### 📊 Quantidade por Gênero")
	if not df_filtrado.empty:
		genero_counts = df_filtrado["Genero"].value_counts().reset_index()
		genero_counts.columns = ["Genero", "Quantidade"]
		fig = px.bar(genero_counts, x="Genero", y="Quantidade", title="Animes por Gênero", color="Genero")
		st.plotly_chart(fig, use_container_width=True)
	else:
		st.info("Nenhum dado para exibir o gráfico.")

# ------------------------ Adicionar Anime ------------------------
elif menu == "➕ Adicionar Anime":
	st.subheader("➕ Cadastrar Novo Anime")
	with st.form("form_add_anime"):
		list_id = st.number_input("ID", min_value=1, step=1, value=int(df_animes["List"].max() + 1 if not df_animes.empty else 1))
		name = st.text_input("Nome")
		note = st.text_input("Nota")
		categoria = st.selectbox("Categoria", ["Anime", "Mangá", "Filme", "Desenho", "Outro"])
		genero = st.text_input("Gênero")
		descricao = st.text_area("Descrição")
		submit = st.form_submit_button("Salvar")

		if submit and name:
			novo = {"List": list_id, "Name": name, "Note": note, "Categoria": categoria, "Genero": genero, "Descrição": descricao}
			df_animes = pd.concat([df_animes, pd.DataFrame([novo])], ignore_index=True)
			salvar_csv(df_animes, CSV_ANIMES)
			st.success("✅ Anime salvo com sucesso!")

# ------------------------ Editar Anime ------------------------
elif menu == "✏️ Editar Anime":
	st.subheader("✏️ Editar Anime")
	anime_nomes = df_animes["Name"].tolist()
	anime_escolhido = st.selectbox("Selecione um anime para editar", anime_nomes)
	anime_info = df_animes[df_animes["Name"] == anime_escolhido].iloc[0]

	with st.form("editar_form"):
		list_id = st.number_input("ID", min_value=1, value=int(anime_info["List"]))
		name = st.text_input("Nome", anime_info["Name"])
		note = st.text_input("Nota", anime_info["Note"])
		categoria = st.selectbox("Categoria", ["Anime", "Mangá", "Filme", "Desenho", "Outro"], index=["Anime", "Mangá", "Filme", "Desenho", "Outro"].index(anime_info["Categoria"]))
		genero = st.text_input("Gênero", anime_info["Genero"])
		descricao = st.text_area("Descrição", anime_info["Descrição"])
		atualizar = st.form_submit_button("Atualizar")

		if atualizar:
			idx = df_animes[df_animes["Name"] == anime_escolhido].index[0]
			df_animes.loc[idx] = [list_id, name, note, categoria, genero, descricao]
			salvar_csv(df_animes, CSV_ANIMES)
			st.success("✅ Anime atualizado com sucesso!")

# -------------------- Temporada --------------------
elif menu == "📅 Temporada":
	st.subheader("📅 Animes da Temporada")

	with st.form("form_temporada"):
		nome = st.text_input("🎬 Nome do Anime")
		nota = st.text_input("⭐ Nota (ex: 7.5)")
		categoria = st.selectbox("📁 Categoria", ["Anime", "Mangá", "Filme", "Desenho", "Outro"])
		genero = st.text_input("🎭 Gênero")
		temporada = st.text_input("📆 Temporada (ex: Verão 2025)")
		episodios = st.number_input("📺 Total de Episódios", min_value=1, value=12)
		assistido = st.number_input("👁️ Episódios Assistidos", min_value=0, value=0)
		data_atual = st.date_input("📅 Data de Atualização", value=date.today())
		submit = st.form_submit_button("Adicionar à Temporada")

		if submit:
			if nome.strip() == "":
				st.warning("O nome do anime é obrigatório.")
			else:
				nome_lower = nome.strip().lower()
				novo_id = int(df_animes["List"].max()) + 1 if not df_animes.empty else 1

				if nome_lower not in df_animes["Name"].str.lower().values:
					novo = {"List": novo_id, "Name": nome, "Note": nota or "6.0", "Categoria": categoria, "Genero": genero or "Desconhecido", "Descrição": "anime novo"}
					df_animes = pd.concat([df_animes, pd.DataFrame([novo])], ignore_index=True)
					salvar_csv(df_animes, CSV_ANIMES)

				novo_temp = {"List": novo_id, "Name": nome, "Note": nota or "6.0", "Categoria": categoria, "Genero": genero or "Desconhecido", "Descrição": "anime novo", "Temporada": temporada or "Não especificado", "Episodios": episodios, "Assistido": assistido, "Atualizado": str(data_atual)}
				df_temp = pd.concat([df_temp, pd.DataFrame([novo_temp])], ignore_index=True)
				salvar_csv(df_temp, CSV_TEMPORADA)
				st.success("Anime adicionado à temporada!")

	st.markdown("### 📋 Lista da Temporada")
	st.dataframe(df_temp, use_container_width=True)

	st.markdown("### ✏️ Atualizar Episódios Assistidos")
	if not df_temp.empty:
		anime_selec = st.selectbox("Selecione o anime", df_temp["Name"].tolist())
		episodio_novo = st.number_input("Novo Episódio Assistido", min_value=0)
		if st.button("Atualizar Progresso"):
			idx = df_temp[df_temp["Name"] == anime_selec].index[0]
			df_temp.at[idx, "Assistido"] = episodio_novo
			salvar_csv(df_temp, CSV_TEMPORADA)
			st.success("Progresso atualizado!")

	st.markdown("### ❌ Remover Anime da Temporada")
	if not df_temp.empty:
		anime_remover = st.selectbox("Selecione o anime para remover", df_temp["Name"].tolist())
		if st.button("Remover"):
			df_temp = df_temp[df_temp["Name"] != anime_remover]
			salvar_csv(df_temp, CSV_TEMPORADA)
			st.success("Anime removido da temporada!")

# -------------------- Mangás e Livros --------------------
elif menu == "📖 Mangás e Livros":
	st.subheader("📖 Mangás e Livros em Leitura")

	nome = st.text_input("Nome")
	tipo = st.selectbox("Tipo", ["Mangá", "Livro"])
	genero = st.text_input("Gênero")
	descricao = st.text_area("Descrição")
	progresso = st.text_input("Progresso")

	if st.button("Adicionar à Leitura"):
		if nome.strip() == "":
			st.warning("O nome é obrigatório.")
		else:
			novo_id = int(df_mangas["ID"].max()) + 1 if not df_mangas.empty else 1
			novo = {"ID": novo_id, "Nome": nome, "Tipo": tipo, "Gênero": genero or "Desconhecido", "Descrição": descricao or "Sem descrição", "Progresso": progresso or "Em progresso"}
			df_mangas = pd.concat([df_mangas, pd.DataFrame([novo])], ignore_index=True)
			salvar_csv(df_mangas, CSV_MANGAS)
			st.success("Leitura adicionada com sucesso!")

	st.markdown("### 📚 Em Leitura")
	st.dataframe(df_mangas, use_container_width=True)
