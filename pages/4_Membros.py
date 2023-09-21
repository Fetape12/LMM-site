import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageOps
import os

# Criar um DataFrame de exemplo com os dados dos membros da equipe
data = {
    'Nome': ['Felipe Tartaro Pereira', 'Membro 2', 'Membro 3'],
    'Cargo': ['CEO', 'Designer', 'Engenheiro'],
    'Descrição': ['Elon Reeve Musk FRS (Pretória, 28 de junho de 1971) é um empreendedor,[3] empresário e filantropo sul-africano-canadense, naturalizado estadunidense. Ele é o fundador, diretor executivo e diretor técnico da SpaceX; CEO da Tesla, Inc.; vice-presidente da OpenAI, fundador e CEO da Neuralink; cofundador, presidente da SolarCity e proprietário do Twitter. Em dezembro de 2022, tinha uma fortuna avaliada em US$ 139 bilhões de dólares, tornou-se a segunda pessoa mais rica do mundo, de acordo com a Bloomberg, atrás apenas do empresário Jeff Bezos.', 'Descrição do Membro 2', 'Descrição do Membro 3'],
    'Foto': ['fotominha.jpg', 'fotominha.jpg', 'fotominha.jpg']
}
# Largura e altura desejadas para as imagens
largura_desejada = 200  # Ajuste conforme necessário
altura_desejada = 267   # Proporção 3:4

df = pd.DataFrame(data)

# Pasta onde as imagens dos membros da equipe estão localizadas
pasta_imagens = r"C:\Users\LUCAS\Documents\GitHub\LMM-site\fig"

# Configurar o título do aplicativo
st.title('Membros da Empresa')

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
    st.image(imagem_recortada, use_column_width=False, output_format='PNG')
    
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
        f'<p><strong>Cargo:</strong> {row["Cargo"]}</p>'
        f'<p><strong>Descrição:</strong> {row["Descrição"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    st.write("---")
