#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automação de envio de e-mails — Projeto Lamarr
================================================

Uso:
    python3 enviar_emails.py --teste
        -> envia o e-mail apenas para os endereços em destinatarios_teste.csv

    python3 enviar_emails.py --real
        -> envia o e-mail para todos os endereços em destinatarios_reais.csv
           (pede confirmação antes de disparar, mostrando quantos destinatários)

Arquivos necessários na mesma pasta:
    - config.ini                (copie de config.example.ini e preencha)
    - template.html             (corpo do e-mail)
    - destinatarios_teste.csv   (colunas: nome,email)
    - destinatarios_reais.csv   (colunas: nome,email) — já gerado a partir da planilha

Cada envio é registrado em log_envios.csv (sucesso/falha, data/hora).
"""

import argparse
import configparser
import csv
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.ini"
TEMPLATE_PATH = BASE_DIR / "template.html"
LOG_PATH = BASE_DIR / "log_envios.csv"


def carregar_config():
    if not CONFIG_PATH.exists():
        sys.exit(
            f"[ERRO] Não encontrei {CONFIG_PATH.name}.\n"
            f"Copie config.example.ini para config.ini e preencha com seus dados de SMTP."
        )
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH, encoding="utf-8")
    return cfg


def carregar_destinatarios(caminho_csv: Path):
    if not caminho_csv.exists():
        sys.exit(f"[ERRO] Não encontrei {caminho_csv.name}.")
    destinatarios = []
    with open(caminho_csv, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            email = (linha.get("email") or "").strip()
            nome = (linha.get("nome") or "").strip()
            if email:
                destinatarios.append({"nome": nome, "email": email})
    return destinatarios


def carregar_template():
    if not TEMPLATE_PATH.exists():
        sys.exit(f"[ERRO] Não encontrei {TEMPLATE_PATH.name}.")
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def registrar_log(linhas):
    novo_arquivo = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novo_arquivo:
            w.writerow(["data_hora", "email", "status", "detalhe"])
        for linha in linhas:
            w.writerow(linha)


def enviar(cfg, destinatarios, corpo_html, modo):
    smtp_host = cfg.get("smtp", "smtp_host")
    smtp_port = cfg.getint("smtp", "smtp_port")
    smtp_user = cfg.get("smtp", "smtp_user")
    smtp_password = cfg.get("smtp", "smtp_password")

    remetente_nome = cfg.get("envio", "remetente_nome")
    remetente_email = cfg.get("envio", "remetente_email")
    assunto = cfg.get("envio", "assunto")
    delay = cfg.getfloat("envio", "delay_segundos", fallback=3)

    print(f"\nModo: {modo.upper()}")
    print(f"Destinatários: {len(destinatarios)}")
    print(f"Assunto: {assunto}")
    print(f"Remetente: {remetente_nome} <{remetente_email}>")
    print(f"Servidor SMTP: {smtp_host}:{smtp_port}\n")

    resposta = input("Confirma o envio? Digite 'sim' para continuar: ").strip().lower()
    if resposta != "sim":
        print("Envio cancelado.")
        return

    contexto = ssl.create_default_context()
    logs = []
    sucesso, falha = 0, 0

    with smtplib.SMTP(smtp_host, smtp_port) as servidor:
        servidor.ehlo()
        servidor.starttls(context=contexto)
        servidor.ehlo()
        servidor.login(smtp_user, smtp_password)

        for i, destinatario in enumerate(destinatarios, start=1):
            email_destino = destinatario["email"]
            nome_destino = destinatario["nome"]

            msg = MIMEMultipart("alternative")
            msg["Subject"] = assunto
            msg["From"] = f"{remetente_nome} <{remetente_email}>"
            msg["To"] = email_destino

            msg.attach(MIMEText(corpo_html, "html", "utf-8"))

            try:
                servidor.sendmail(remetente_email, email_destino, msg.as_string())
                print(f"[{i}/{len(destinatarios)}] Enviado para {nome_destino} <{email_destino}>")
                logs.append([datetime.now().isoformat(timespec="seconds"), email_destino, "sucesso", ""])
                sucesso += 1
            except Exception as e:
                print(f"[{i}/{len(destinatarios)}] FALHOU para {email_destino}: {e}")
                logs.append([datetime.now().isoformat(timespec="seconds"), email_destino, "falha", str(e)])
                falha += 1

            if i < len(destinatarios):
                time.sleep(delay)

    registrar_log(logs)
    print(f"\nConcluído. Sucesso: {sucesso} | Falhas: {falha}")
    print(f"Log salvo em: {LOG_PATH.name}")


def main():
    parser = argparse.ArgumentParser(description="Envio automatizado de e-mails — Projeto Lamarr")
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--teste", action="store_true", help="Envia para a lista de teste (destinatarios_teste.csv)")
    grupo.add_argument("--real", action="store_true", help="Envia para a lista real (destinatarios_reais.csv)")
    args = parser.parse_args()

    cfg = carregar_config()
    corpo_html = carregar_template()

    if args.teste:
        destinatarios = carregar_destinatarios(BASE_DIR / "destinatarios_teste.csv")
        enviar(cfg, destinatarios, corpo_html, modo="teste")
    else:
        destinatarios = carregar_destinatarios(BASE_DIR / "destinatarios_reais.csv")
        enviar(cfg, destinatarios, corpo_html, modo="real")


if __name__ == "__main__":
    main()
