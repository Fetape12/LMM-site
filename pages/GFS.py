import streamlit as st
from backend.GFS_data import get_GFS, plot_GFS
# Suponha que você já tenha o conjunto ncss.variables
# Converta o conjunto para uma lista para uso com st.selectbox
variaveis_disponiveis = list(get_GFS().variables)

# Crie a caixa de seleção no aplicativo Streamlit
opcao_selecionada = st.selectbox("Selecione uma variável:", variaveis_disponiveis)

# Exiba a opção selecionada pelo usuário
st.write("Você selecionou:", opcao_selecionada)
if opcao_selecionada and st.button("Gerar Mapa"):
    try:
        st.pyplot(plot_GFS(get_GFS(),opcao_selecionada))

    finally:
        st.stop()