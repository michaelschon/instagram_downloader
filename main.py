import streamlit as st
import subprocess
import os
from pathlib import Path
import time
import threading
import shutil

st.set_page_config(page_title="Instagram Video Downloader", page_icon="📹")

# Função para limpar arquivos antigos após 5 minutos
def cleanup_old_files(directory, delay=300):
    """Remove arquivos do diretório após o delay especificado (padrão: 5 minutos)"""
    time.sleep(delay)
    try:
        if directory.exists():
            for file in directory.glob("*"):
                if file.is_file():
                    file.unlink()
            st.toast("🧹 Arquivos temporários limpos automaticamente", icon="✅")
    except Exception as e:
        print(f"Erro ao limpar arquivos: {e}")

# Função para agendar limpeza em background
def schedule_cleanup(directory):
    """Agenda a limpeza do diretório em uma thread separada"""
    cleanup_thread = threading.Thread(target=cleanup_old_files, args=(directory,), daemon=True)
    cleanup_thread.start()

st.title("📹 Instagram Video Downloader")
st.write("Cole a URL de um post ou reels do Instagram para baixar o vídeo")

# Criar diretório de downloads se não existir
downloads_dir = Path("./downloads")
downloads_dir.mkdir(exist_ok=True)

# Configurações
with st.expander("⚙️ Configurações Avançadas"):
    use_cookies = st.checkbox("Usar cookies do navegador (necessário se estiver bloqueado)", value=True)
    if use_cookies:
        browser = st.selectbox(
            "Selecione seu navegador:",
            ["chrome", "firefox", "edge", "brave", "safari", "chromium", "opera"],
            index=0
        )
        st.info("💡 Certifique-se de estar logado no Instagram no navegador selecionado")
    else:
        st.warning("⚠️ Sem cookies, pode não funcionar devido às restrições do Instagram")

st.markdown("---")

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
                    "--no-warnings",
                    "-o", output_template,
                ]
                
                # Adicionar cookies se habilitado
                if use_cookies:
                    command.extend(["--cookies-from-browser", browser])
                
                command.append(url)
                
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
                        
                        # Agendar limpeza automática após 5 minutos
                        schedule_cleanup(downloads_dir)
                        st.info("🕐 Os arquivos serão removidos automaticamente em 5 minutos")
                        
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
                    error_msg = result.stderr.lower()
                    
                    if "login required" in error_msg or "rate-limit" in error_msg:
                        st.error("🔒 **Instagram bloqueou o acesso!**")
                        st.markdown("""
                        **Soluções:**
                        1. ✅ **Marque** a opção "Usar cookies do navegador"
                        2. 🌐 Certifique-se de estar **logado no Instagram** no navegador escolhido
                        3. 🔄 Tente novamente
                        4. 🕐 Se continuar, aguarde alguns minutos (limite de taxa)
                        """)
                    elif "unable to extract" in error_msg:
                        st.error("❌ Não foi possível extrair o vídeo")
                        st.info("💡 Verifique se a URL está correta e se o post contém um vídeo")
                    else:
                        st.error(f"Erro ao baixar: {result.stderr}")
                        
                    with st.expander("🔍 Ver detalhes do erro"):
                        st.code(result.stderr)
                    
            except Exception as e:
                st.error(f"Erro: {str(e)}")

st.markdown("---")
st.markdown("### ℹ️ Como usar:")
st.markdown("""
1. **Faça login no Instagram** no seu navegador (Chrome, Firefox, etc.)
2. Copie a URL do post ou reels que deseja baixar
3. Cole a URL no campo acima
4. Marque "Usar cookies do navegador" e selecione seu navegador
5. Clique em 'Baixar Vídeo'
6. Aguarde o download e clique no botão para salvar o arquivo

**⚠️ Por que preciso de cookies?**
O Instagram bloqueou downloads anônimos. Os cookies do seu navegador permitem que o app acesse o Instagram como se fosse você (apenas para download).
""")

st.markdown("---")
st.caption("⚠️ Use este aplicativo de forma responsável e respeite os direitos autorais.")
