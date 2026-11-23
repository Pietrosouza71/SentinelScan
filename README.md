# SentinelScan

O SentinelScan é um projeto em desenvolvimento para ajudar profissionais de segurança a organizar testes de segurança feitos com autorização. Esse tipo de trabalho também é conhecido como **Red Team**.

O projeto tem um site e um programa que salva informações sobre os sistemas que poderão ser testados, as partes incluídas no teste e o histórico de alterações.

> [!IMPORTANT]
> Por enquanto, o SentinelScan não testa sites nem redes. Os números, nomes e resultados que aparecem no site são apenas exemplos. Ao cadastrar um sistema, a pessoa confirma que tem autorização, mas o programa não consegue verificar isso.

## Imagens do projeto

![Painel do SentinelScan em um computador. As informações são exemplos.](docs/images/dashboard-desktop.png)

![Exemplos de problemas encontrados e de atividade. Nada foi testado de verdade.](docs/images/findings-and-activity.png)

## O que já funciona

- O site se adapta a diferentes tamanhos de tela.
- É possível iniciar o programa no computador e abrir o site pelo navegador.
- O programa salva, mostra e desativa sistemas de laboratório cadastrados.
- É possível anotar quais partes estão incluídas ou excluídas de um teste.
- As alterações ficam salvas em um banco de dados local.
- Há testes automáticos para conferir se algumas partes do programa funcionam.

**Ainda está sendo desenvolvido:** ligar os botões do site ao programa, consultar informações de domínio, verificar sites e redes, criar relatórios em PDF e conectar ferramentas como Nmap e OWASP ZAP. Por isso, esses recursos ainda não fazem testes.

## Tecnologias usadas

- HTML, CSS e JavaScript para o site.
- Python e FastAPI para o programa que atende às solicitações do site.
- SQLite para salvar as informações no computador.
- pytest e HTTPX para os testes automáticos.

## Como abrir no computador

Você precisa instalar o **Python 3.10 ou mais recente**.

1. Abra o PowerShell dentro da pasta do projeto.
2. Crie um espaço separado para instalar os componentes:

   ```powershell
   py -m venv .venv
   ```

3. Ative esse espaço:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Instale os componentes necessários:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Inicie o programa:

   ```powershell
   python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
   ```

Se `py` não funcionar, tente `python` no lugar dele no passo 2.

Com o programa ligado, abra:

- Site: <http://127.0.0.1:8000>
- Página para testar e entender as solicitações do programa: <http://127.0.0.1:8000/docs>
- Verificação para confirmar que o programa iniciou: <http://127.0.0.1:8000/api/health>

O programa aceita conexões somente do próprio computador.

## O que o programa pode fazer

| Solicitação | Para que serve |
| --- | --- |
| `GET /api/health` | Conferir se o programa iniciou |
| `GET /api/targets` | Ver os sistemas cadastrados como ativos |
| `GET /api/targets?active_only=false` | Ver todos os sistemas, inclusive os desativados |
| `POST /api/targets` | Cadastrar um sistema e descrever o que está incluído no teste |
| `DELETE /api/targets/{id}` | Desativar um sistema sem apagar seu histórico |
| `GET /api/audit` | Ver o histórico de alterações |

Ao cadastrar um sistema, informe um nome, o endereço sem `https://`, o que pode ser incluído no teste e confirme que tem autorização. Essa confirmação fica registrada, mas não é conferida por outra pessoa ou serviço.

## Como executar os testes automáticos

Com os componentes instalados, execute na pasta do projeto:

```powershell
python -m pytest
```

## Segurança

Use testes de segurança somente em sistemas seus ou para os quais recebeu autorização explícita. Antes de permitir testes reais, ainda será necessário proteger o acesso ao programa e garantir que cada teste respeite os sistemas e limites autorizados. **Não use a versão atual para testar sistemas.**
