# Cloudflare mTLS Manager CLI

Este é um script CLI (Command Line Interface) em Python para automatizar o gerenciamento de certificados mTLS (Mutual TLS) e associações de hostnames na Cloudflare. Ele utiliza a API oficial v4 da Cloudflare.

O script permite importar bundles CA, associar hostnames a certificados e verificar associações existentes de forma programática.

## Pré-requisitos

* Python 3.8+
* Uma conta na Cloudflare com permissões para gerenciar SSL/mTLS.
* API Token da Cloudflare.

## 🚀 Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio

```

2. Instale as dependências necessárias:
```bash
pip install -r requirements.txt

```

*(Veja a seção "Dependências" abaixo para criar este arquivo se ainda não tiver)*

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto para armazenar suas credenciais com segurança. O script buscará automaticamente por este arquivo.

```env
# .env
CLOUDFLARE_API_KEY=seu_api_token_aqui

```

ou Adicione o token em uma váriavel de ambiente.

```bash
CLOUDFLARE_API_KEY=seu_api_token_aqui

```

> **Nota:** Nunca comite o arquivo `.env` no Git. Adicione-o ao seu `.gitignore`.

## 📖 Como Usar

O script `cf-mtls-byca.py` opera através de flags de comando. Você deve escolher uma ação principal (`--import-bundle`, `--update-associates` ou `--get-associates`) e fornecer os argumentos necessários.

### 1. Importar um Certificado CA (Bundle)

Envia um arquivo `.pem` para a Cloudflare e cria um novo certificado mTLS na conta especificada.

```bash
python cf-mtls-byca.py --import-bundle \
  --account "ID_DA_SUA_CONTA" \
  --bundle "caminho/para/arquivo_ca.pem"

```

### 2. Associar Hostnames

Associa um ou mais hostnames a um certificado mTLS já existente dentro de uma Zona específica.

```bash
python cf-mtls-byca.py --update-associates \
  --zone_id "ID_DA_ZONA" \
  --mtls_certificate_id "ID_DO_CERTIFICADO" \
  --hostnames app.exemplo.com.br api.exemplo.com.br

```

### 3. Verificar Associações

Busca os hostnames atualmente associados a um certificado mTLS.

```bash
python cf-mtls-byca.py --get-associates \
  --zone_id "ID_DA_ZONA" \
  --mtls_certificate_id "ID_DO_CERTIFICADO"

```

*Opcional:* Você pode adicionar `--hostnames` para verificar se um host específico está na lista retornada.

### Opções Adicionais

* **Ignorar SSL (Inseguro):** Se você estiver em um ambiente de desenvolvimento corporativo com proxy que intercepta SSL, use a flag `--insecure` para ignorar a validação do certificado HTTPS da API da Cloudflare.
```bash
python cf-mtls-byca.py --import-bundle ... --insecure

```


* **Ajuda:** Para ver todos os comandos disponíveis:
```bash
python cf-mtls-byca.py --help

```

## 📦 Dependências (requirements.txt)

Certifique-se de que seu arquivo `requirements.txt` contenha as seguintes bibliotecas:

```text
cloudflare
httpx
python-dotenv

```

## 🛡️ Segurança

* O `account_id` e `zone_id` são passados via linha de comando para permitir o uso em múltiplas contas (multi-tenant).
* O `CLOUDFLARE_API_KEY` deve ser mantido no arquivo `.env` para evitar exposição no histórico do terminal.

---

### Dica Extra para você:

Para que o passo de instalação funcione para outras pessoas, crie o arquivo `requirements.txt` rodando este comando na sua máquina antes de subir para o git:

```bash
pip freeze > requirements.txt

```
