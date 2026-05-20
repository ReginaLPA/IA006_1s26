import pandas as pd
import streamlit as st

from src.health_core import collect_health_check, format_text_report


st.set_page_config(
    page_title="Jupyter Health Check",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 JupyterLab Environment Health Check")
st.caption("Diagnóstico visual do ambiente Python/JupyterLab, incluindo pacotes, proxy, rede e Ollama.")

full = st.sidebar.checkbox("Executar diagnóstico completo", value=True)

if st.sidebar.button("Rodar diagnóstico"):
    st.session_state["health_data"] = collect_health_check(full=full)

if "health_data" not in st.session_state:
    st.info("Clique em **Rodar diagnóstico** na barra lateral.")
    st.stop()

data = st.session_state["health_data"]

col1, col2, col3 = st.columns(3)
col1.metric("Usuário", data.get("user", "-"))
col2.metric("Host", data.get("hostname", "-"))
col3.metric("Data/hora", data.get("generated_at", "-"))

st.subheader("📦 Pacotes")
df_packages = pd.DataFrame(data["packages"])
df_packages["status"] = df_packages["found"].map({True: "OK", False: "NÃO ENCONTRADO"})
st.dataframe(
    df_packages[["package", "module", "status", "version"]],
    use_container_width=True,
    hide_index=True
)

missing = df_packages[~df_packages["found"]]
if not missing.empty:
    st.warning("Pacotes/módulos não encontrados: " + ", ".join(missing["package"].tolist()))
else:
    st.success("Todos os pacotes verificados foram encontrados.")

if "directories" in data:
    st.subheader("📁 Pastas e permissões")
    st.dataframe(pd.DataFrame(data["directories"]), use_container_width=True, hide_index=True)

if "proxy" in data:
    st.subheader("🌐 Proxy")
    if data["proxy"]:
        st.json(data["proxy"])
    else:
        st.success("Nenhuma variável de proxy encontrada.")

if "network" in data:
    st.subheader("🔌 Rede")
    st.dataframe(pd.DataFrame(data["network"]).T.reset_index(names="serviço"), use_container_width=True, hide_index=True)

if "ollama" in data:
    st.subheader("🤖 IA local - Ollama")
    ollama = data["ollama"]
    if ollama["available"]:
        st.success(f"Ollama disponível em: {ollama['base_url']}")
        st.write("Modelos:", ", ".join(ollama["models"]) if ollama["models"] else "nenhum listado")
    else:
        st.error("Ollama não disponível nas URLs testadas.")

st.subheader("📄 Relatório em texto")
report = format_text_report(data)
st.code(report, language="text")

st.download_button(
    "Baixar relatório .txt",
    data=report,
    file_name="diagnostico_jupyterlab.txt",
    mime="text/plain"
)