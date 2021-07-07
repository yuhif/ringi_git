from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# メール送信処理のメソッド
# 引数は送信先、件名、本文
def send_mail(to, PW):
    # 送信に必要な情報を定数で定義
    ID = "numatakazuya.1234@gmail.com"
    PASS = "yutakuma1334"
    HOST = "smtp.gmail.com"
    PORT = 587
    subject = "登録内容"
    body = "登録完了！<br>PWはこちらになります。<br> PW:" + PW
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

if __name__ == "__main__":

    # メール送信処理の呼び出し
    send_mail(to="yuta0304fy@gmail.com", PW = "yuta0304fy")


