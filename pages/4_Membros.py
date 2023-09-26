import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageOps
import os
from backend.background import set_background

set_background(r'.\fig\fundos\planeta.jpg')
# Função para aplicar um recorte arredondado a uma imagem
def aplicar_recorte_arredondado(imagem):
    largura, altura = imagem.size
    tamanho = min(largura, altura)
    mascara = Image.new("L", (tamanho, tamanho), 0)
    desenho = ImageDraw.Draw(mascara)
    desenho.ellipse((0, 0, tamanho, tamanho), fill=255)
    mascara = ImageOps.fit(mascara, (largura, altura))
    imagem.putalpha(mascara)
    return imagem



# Ler os dados do arquivo TXT com delimitador '|' e especificar a codificação
def ler_dados_de_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    header = lines[0].strip().split('|')  # Usar '|' como delimitador
    data = [line.strip().split('|') for line in lines[1:]]
    return header, data



# Pasta onde as imagens dos membros da equipe estão localizadas
pasta_imagens = r".\fig\membros"

# Defina um estilo CSS personalizado para o título com a fonte "Helvetica"
titulo_style = """
    font-size: 36px;
    font-weight: bold;
    font-family: "Helvetica", sans-serif;
    border: 2px solid #333;
    padding: 10px 20px;
    text-align: center;
    background-color: #f0f0f0;
    color: #333;
"""

# Use o título personalizado
st.markdown(f'<p style="{titulo_style}">Membros da Empresa</p>', unsafe_allow_html=True)
# Ler os dados do arquivo
header, data = ler_dados_de_arquivo(r".\backend\membros_desc.txt")

# Criar o DataFrame
df = pd.DataFrame(data, columns=header)

# Largura e altura desejadas para as imagens
largura_desejada = 240  # Ajuste conforme necessário
altura_desejada = 267   # Proporção 3:4

# Loop pelos membros da equipe e exibir suas informações
# Loop pelos membros da equipe e exibir suas informações
for index, row in df.iterrows():
    imagem_path = os.path.join(pasta_imagens, row['Foto'])
    
    # Abrir a imagem usando a PIL
    imagem = Image.open(imagem_path)
    
    # Redimensionar a imagem para as dimensões desejadas
    imagem_redimensionada = imagem.resize((largura_desejada, altura_desejada))
    
    # Aplicar recorte arredondado à imagem
    imagem_recortada = aplicar_recorte_arredondado(imagem_redimensionada)
    
    # Exibir a imagem recortada no Streamlit sem legenda
    st.image(imagem_recortada, use_column_width=False, output_format='JPG')
    
    # Aplicar estilo CSS para alinhar as imagens à esquerda
    st.markdown(
        f"""<style>
        div.stImage > img {{
            width: {largura_desejada}px !important;
            height: {altura_desejada}px !important;
            float: left !important;
            margin-right: 10px !important;
            border-radius: 50%; /* Adicionar um recorte arredondado */
        }}
        </style>""",
        unsafe_allow_html=True
    )
    
    # Exibir o nome, cargo e descrição ao lado da imagem
    st.markdown(
        f'<div style="float: left; padding-left: 20px;">'
        f'<h3>{row["Nome"]}</h3>'
        f'<p><strong>Cargo:</strong> <em><b>{row["Cargo"]}</b></em></p>'
        f'<p><strong>Descrição:</strong> {row["Descrição"]}</p>'
        f'<p><strong>Formação:</strong> {row["Formação"]}</p>'
        f'<p><strong>Linha de Pesquisa:</strong> {row["Linha de Pesquisa"]}</p>'
        f'<p><strong>Palavra chave:</strong> {row["Palavra chave"]}</p>'
        f'<p><strong>CV:</strong> <a href="{row["CV"]}">{row["CV"]}</a></p>'
        f'<p><strong>Contato:</strong> <a href="{row["Contato"]}">{row["Contato"]}</a></p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    st.write("---")
