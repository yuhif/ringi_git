from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(to):
    # 送信に必要な情報を定数で定義
    ID = "stesuto6@gmail.com"
    PASS = "morijyobi567"
    HOST = "smtp.gmail.com"
    PORT = 587
    subject = "稟議書承認依頼"
    body = "承認待ちの稟議書があります。"
    # メール本文を設定
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, "html"))

    # 件名、送信元アドレス、送信先アドレスを設定
    msg["Subject"] = subject
    msg["From"] = ID
    msg["To"] = to

    # SMTPサーバへ接続し、TLS通信開始
    server=SMTP(HOST, PORT)
    server.starttls()   # TLS通信開始

    server.login(ID, PASS) # ログイン認証処理

    server.send_message(msg)    # メール送信処理

    server.quit()       # TLS通信終了
    print("メール送信完了！")
