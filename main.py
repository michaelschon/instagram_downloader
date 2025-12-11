import streamlit as st
import subprocess
import os
from pathlib import Path
import time

st.set_page_config(page_title="Instagram Video Downloader", page_icon="📹")

st.title("📹 Instagram Video Downloader")
st.write("Cole a URL de um post ou reels do Instagram para baixar o vídeo")

# Criar diretório de downloads se não existir
downloads_dir = Path("./downloads")
downloads_dir.mkdir(exist_ok=True)

# Input da URL
url = st.text_input("URL do Instagram:", placeholder="https://www.instagram.com/p/...")

if st.button("Baixar Vídeo", type="primary"):
    if not url:
        st.error("Por favor, insira uma URL válida!")
    elif "instagram.com" not in url:
        st.error("A URL deve ser do Instagram!")
    else:
        with st.spinner("Baixando vídeo... Por favor aguarde."):
            try:
                # Nome único para o arquivo
                timestamp = int(time.time())
                output_template = str(downloads_dir / f"instagram_video_{timestamp}.%(ext)s")
                
                # Comando yt-dlp para baixar o vídeo
                command = [
                    "yt-dlp",
                    "-f", "best",  # Melhor qualidade disponível
                    "-o", output_template,
                    url
                ]
                
                # Executar o comando
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Encontrar o arquivo baixado
                    video_files = list(downloads_dir.glob(f"instagram_video_{timestamp}.*"))
                    
                    if video_files:
                        video_file = video_files[0]
                        st.success("✅ Vídeo baixado com sucesso!")
                        
                        # Ler o arquivo e oferecer para download
                        with open(video_file, "rb") as f:
                            video_bytes = f.read()
                        
                        st.download_button(
                            label="⬇️ Clique aqui para baixar o vídeo",
                            data=video_bytes,
                            file_name=video_file.name,
                            mime="video/mp4"
                        )
                        
                        # Mostrar preview (opcional)
                        st.video(video_bytes)
                        
                    else:
                        st.error("Arquivo não encontrado após o download.")
                else:
                    st.error(f"Erro ao baixar o vídeo: {result.stderr}")
                    
            except Exception as e:
                st.error(f"Erro: {str(e)}")

st.markdown("---")
st.markdown("### ℹ️ Como usar:")
st.markdown("""
1. Abra o Instagram e encontre o vídeo que deseja baixar
2. Copie a URL do post ou reels
3. Cole a URL no campo acima
4. Clique em 'Baixar Vídeo'
5. Aguarde o download e clique no botão para salvar o arquivo
""")

st.markdown("---")
st.caption("⚠️ Use este aplicativo de forma responsável e respeite os direitos autorais.")
