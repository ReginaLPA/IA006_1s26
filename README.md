# 🧪 JupyterLab Environment Health Check

![Python](https://img.shields.io/badge/Python-3.11-blue)
![JupyterLab](https://img.shields.io/badge/JupyterLab-ready-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-red)
![CLI](https://img.shields.io/badge/CLI-supported-success)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Ferramenta para diagnóstico de ambiente Python/JupyterLab, com suporte a **CLI** e **dashboard Streamlit**.

---

## 🚀 Funcionalidades

- Verificação de pacotes Python
- Diagnóstico de módulos importáveis
- Checagem de versões
- Verificação de proxy
- Teste de acesso à rede
- Diagnóstico de pastas e permissões
- Teste de IA local com Ollama
- Exportação de relatório `.txt`
- Interface CLI e dashboard visual

---

## 📁 Estrutura

```text
IA006_1s26/
├── check.py
├── app_streamlit.py
├── requirements.txt
├── README.md
├── Dockerfile
├── .gitignore
├── src/
│   └── health_core.py
├── assets/
│   ├── demo_placeholder.txt
│   └── screenshot_placeholder.txt
└── notebooks/
    ├── 01_13_usando_ia_local_do_simserv.ipynb
    ├── 01_14_exemplo_codigo_com_apoio_de_llm.ipynb
    ├── 01_17_caso_problemas_enviar_diagnostico.ipynb
    ├── 01_18_avaliar_exequibilidade_minima_projeto_abm_com_llm.ipynb
    ├── 01_19_Launcher_JupyterLab_Icones_Funcoes_SimServ.ipynb
    └── 01_20check_ambiente_Python_Jupyter.ipynb
```

---

## ⚙️ Instalação

```bash
pip install -r requirements.txt
```

Em ambiente com proxy problemático:

```bash
unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY
```

---

## ▶️ Uso via CLI

Diagnóstico simples:

```bash
python check.py
```

Diagnóstico completo:

```bash
python check.py --full
```

Salvar relatório:

```bash
python check.py --full --save output/diagnostico.txt
```

Saída em JSON:

```bash
python check.py --full --json
```

Salvar JSON:

```bash
python check.py --full --json --save output/diagnostico.json
```

---

## 📊 Uso via Streamlit

```bash
streamlit run app_streamlit.py
```

Depois abra o endereço informado no terminal.

---

## 🧪 Exemplo de saída

```text
HEALTH CHECK - PYTHON/JUPYTER
========================================
jupyterlab-lsp          | jupyterlab_lsp     | NÃO ENCONTRADO
jupyter-lsp             | jupyter_lsp        | OK
python-lsp-server       | pylsp              | NÃO ENCONTRADO
jedi                    | jedi               | OK
```

---

## ⚠️ Problemas comuns

### Proxy retornando 503

```text
Tunnel connection failed: 503 Service Unavailable
```

Solução temporária:

```bash
unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY
```

### Diferença entre nome do pacote e nome do módulo

| Instalação pip | Import Python |
|---|---|
| jupyterlab-lsp | jupyterlab_lsp |
| python-lsp-server | pylsp |

---

## 👩‍💻 Autora

Regina Lacerda Pinheiro  Araujo
UNICAMP — Sistemas Inteligentes, Ciência de Dados e Complexidade