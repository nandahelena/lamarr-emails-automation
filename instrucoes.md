# Automação de envio — Projeto Lamarr

## Estrutura de pastas

```
projeto-lamarr-emails/
├── config.ini                  ← suas credenciais (crie a partir do example, não compartilhe)
├── config.example.ini          ← modelo de configuração do SMTP
├── enviar_emails.py            ← o script que faz o envio
├── LEIA-ME.md
├── template/
│   └── template.html           ← o e-mail de boas-vindas (seu template original)
├── destinatarios/
│   ├── teste.csv                ← lista de teste, já com os 2 e-mails que você passou
│   └── reais.csv                ← lista real, extraída da planilha (coluna "Endereço de e-mail"), 38 destinatárias, sem duplicados/inválidos
└── logs/
    └── log_envios.csv          ← criado automaticamente a cada envio
```

Se quiser reprocessar a lista real a partir de uma planilha nova, é só repetir a extração — me chama que eu gero o `destinatarios/reais.csv` de novo.

Os caminhos ficam todos centralizados no topo do `enviar_emails.py`, num bloco chamado `CAMINHOS` — se algum dia quiser mudar a estrutura de novo, só mexe ali, não precisa procurar no resto do script.

## Passo a passo

### 1. Configure o SMTP

Copie `config.example.ini` para `config.ini`:

```
cp config.example.ini config.ini
```

Abra `config.ini` e preencha `smtp_user` e `smtp_password` com seus dados.

**Se for usar Gmail:** o Gmail não aceita a senha normal da conta via SMTP. Você precisa gerar uma "senha de app":

1. Ative a verificação em duas etapas em https://myaccount.google.com/security
2. Gere uma senha de app em https://myaccount.google.com/apppasswords
3. Cole essa senha de 16 letras no campo `smtp_password`

### 2. Instale a dependência (só usa biblioteca padrão do Python, nada a instalar)

O script usa apenas `smtplib`, `email`, `csv` e `configparser`, que já vêm com o Python. Não precisa instalar nada.

### 3. Rode o teste primeiro

```
python3 enviar_emails.py --teste
```

Isso envia o e-mail apenas para:
- helenafernanda78ko@gmail.com
- lucaomino@gmail.com

O script mostra um resumo e pede confirmação (`sim`) antes de disparar. Confira se o e-mail chegou certinho, com as imagens carregando e o botão do WhatsApp funcionando.

### 4. Rode o envio real

Depois de confirmar que o teste ficou bom:

```
python3 enviar_emails.py --real
```

Isso envia para as 38 destinatárias reais da planilha. O script mostra a contagem e pede confirmação antes de disparar de verdade.

### 5. Confira o log

Depois do envio, um arquivo `log_envios.csv` é criado (ou atualizado) com data/hora, e-mail e status (sucesso/falha) de cada envio, para você conferir se alguém não recebeu.

## Observações importantes

- O template usa imagens hospedadas no GitHub (raw.githubusercontent.com) — elas já estão com link público, então vão carregar normalmente no e-mail dos destinatários.
- O delay entre envios (padrão 3 segundos) evita que o Gmail/Outlook marque o envio como spam por volume. Se notar problemas, aumente esse valor em `config.ini`.
- Gmail tem limite de ~500 envios/dia em conta pessoal — 38 e-mails está bem dentro do limite.
- **Nunca compartilhe o `config.ini`** (tem sua senha) nem suba ele para repositórios públicos.
