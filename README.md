# SentinelScan

**Plataforma em desenvolvimento para organizar engajamentos de Red Team autorizados.**

Interface responsiva e API local para registrar escopo, alvos de laboratório e eventos de auditoria.

> [!IMPORTANT]
> Esta versão não executa varreduras. Números, eventos e alvos exibidos são fictícios. A confirmação no cadastro registra a declaração do operador, mas não comprova autorização.

## Capturas de tela

![Painel SentinelScan — dados demonstrativos](docs/images/dashboard-desktop.png)

![Achados e diário do engajamento — dados demonstrativos](docs/images/findings-and-activity.png)

## Funcionalidades

- Painel responsivo em HTML, CSS e JavaScript.
- API REST em FastAPI para cadastrar, consultar e desativar alvos.
- Registro de escopo, exclusões e referência de autorização declarada.
- Persistência local em SQLite e trilha de auditoria.
- Testes automatizados dos endpoints.

**Ainda não implementados:** conexão do painel com a API, reconhecimento DNS, Nmap, verificações web, OWASP ZAP e relatórios PDF.

## Tecnologias

HTML5 · CSS3 · JavaScript · Python · FastAPI · SQLite · pytest · HTTPX

## Executar localmente

Requisitos: Python 3.10+ e pip. No PowerShell, na raiz do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Se `py` não estiver disponível, use `python -m venv .venv`.

- Aplicação: <http://127.0.0.1:8000>
- Documentação da API: <http://127.0.0.1:8000/docs>
- Estado da API: <http://127.0.0.1:8000/api/health>

## Endpoints

| Método | Endpoint | Ação |
| --- | --- | --- |
| `GET` | `/api/health` | Verificar estado |
| `GET` | `/api/targets` | Listar alvos ativos |
| `GET` | `/api/targets?active_only=false` | Listar todos os alvos |
| `POST` | `/api/targets` | Cadastrar alvo e escopo |
| `DELETE` | `/api/targets/{id}` | Desativar alvo |
| `GET` | `/api/audit` | Consultar auditoria |

O cadastro exige `authorization_confirmed: true`, descrição do escopo e um host, não uma URL. Isso registra a confirmação do operador; não verifica a autorização de forma independente.

## Testes

```powershell
python -m pytest
```

## Uso responsável

Use somente laboratórios próprios ou ativos com autorização explícita. Antes de integrar scanners, implemente autenticação, validação do escopo em cada execução, limites operacionais e proteções contra destinos fora do escopo. Não exponha esta API na rede nem a utilize para executar testes.
