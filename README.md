# Automação de envio de e-mails — Projeto Lamarr

Script em Python para automatizar o envio de um e-mail (template HTML) para uma lista de destinatários via SMTP, com lista de teste separada da lista real, confirmação antes de disparar e log de envios.

## Índice

- [Como funciona](#como-funciona)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração do SMTP](#configuração-do-smtp)
- [Uso](#uso)
- [Segurança e privacidade](#segurança-e-privacidade)
- [Limitações](#limitações)

## Como funciona

O script lê um template de e-mail em HTML e uma lista de destinatários em CSV, e envia o e-mail um a um via SMTP, com um pequeno intervalo entre cada envio. Antes de disparar, ele mostra um resumo (quantos destinatários, assunto, remetente, servidor) e pede confirmação explícita. Cada envio é registrado em `logs/log_envios.csv`, com data/hora e status (sucesso ou falha).

Existem dois modos, para evitar disparo acidental para a lista real:

- `--teste`: envia apenas para os endereços em `destinatarios/teste.csv`
- `--real`: envia para todos os endereços em `destinatarios/reais.csv`

## Estrutura do projeto

```
.
├── config.example.ini          # modelo de configuração do SMTP
├── enviar_emails.py            # script principal
├── template/
│   └── template.html           # corpo do e-mail
├── destinatarios/
│   ├── teste.csv                # lista de teste
│   └── reais.example.csv        # exemplo de formato da lista real
└── logs/
    └── log_envios.csv           # gerado automaticamente a cada envio
```

Os arquivos `config.ini`, `destinatarios/reais.csv` e `logs/` não são versionados (veja [`.gitignore`](.gitignore)) porque contêm credenciais e dados pessoais.

Os caminhos usados pelo script ficam centralizados em um único bloco no topo de `enviar_emails.py` — se a estrutura de pastas mudar, é só ajustar ali.

## Pré-requisitos

- Python 3.8 ou superior
- Nenhuma dependência externa — o script usa apenas a biblioteca padrão (`smtplib`, `email`, `csv`, `configparser`)

## Instalação

```bash
git clone <url-deste-repositorio>
cd <pasta-do-repositorio>
cp config.example.ini config.ini
```

Edite `config.ini` com seus dados de SMTP (veja a seção abaixo) e crie `destinatarios/reais.csv` com as colunas `nome,email` (use `destinatarios/reais.example.csv` como referência de formato).

## Configuração do SMTP

Abra `config.ini` e preencha:

```ini
[smtp]
smtp_host = smtp.gmail.com
smtp_port = 587
smtp_user = seuemail@gmail.com
smtp_password = sua_senha_de_app_aqui

[envio]
remetente_nome = Projeto Lamarr
remetente_email = seuemail@gmail.com
assunto = Projeto Lamarr — Confirmação de inscrição
delay_segundos = 3
```

**Gmail:** não aceita a senha normal da conta via SMTP. É necessário gerar uma senha de app:

1. Ative a verificação em duas etapas em [myaccount.google.com/security](https://myaccount.google.com/security)
2. Gere uma senha de app em [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use essa senha de 16 letras no campo `smtp_password`

**Outlook/Hotmail:** use `smtp_host = smtp.office365.com`, porta `587`.

Para outros provedores, consulte a documentação de SMTP do serviço.

## Uso

Sempre rode o modo de teste primeiro, com seus próprios e-mails em `destinatarios/teste.csv`:

```bash
python3 enviar_emails.py --teste
```

Depois de confirmar que o e-mail chegou corretamente (imagens carregando, links funcionando), rode o envio real:

```bash
python3 enviar_emails.py --real
```

Em ambos os casos, o script exibe um resumo e só dispara após você digitar `sim`.

## Segurança e privacidade

- `config.ini` contém credenciais de e-mail — nunca faça commit dele nem o compartilhe.
- `destinatarios/reais.csv` e `logs/` contêm dados pessoais de terceiros (nomes e e-mails) — mantenha-os fora do controle de versão e trate-os conforme a LGPD.
- Este repositório assume que você tem consentimento dos destinatários para o envio (por exemplo, inscrição voluntária em um formulário).

## Limitações

- Provedores como o Gmail limitam o número de e-mails enviados por dia em contas pessoais (por volta de 500/dia). Para volumes maiores, considere um serviço dedicado de envio (SendGrid, Amazon SES, Mailgun, etc.).
- O script envia o mesmo conteúdo para todos os destinatários (sem personalização por nome). Para mail merge, seria necessário adaptar o template e o script para substituir variáveis por destinatário.
