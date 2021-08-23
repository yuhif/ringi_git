from typing import Mapping
from flask import Flask,render_template, request, redirect, url_for, session
import string
import random
from datetime import timedelta
import db,mail_input,mail_sample


app = Flask(__name__)

app.secret_key = "".join(random.choices(string.ascii_letters, k=256))

@app.route("/")  #ログインページ
def login_page():
    error = request.args.get("error")
    return render_template("login.html", error=error)

@app.route("/login", methods=["POST"])  #トップページ
def login():
    mail = request.form.get("mail")
    pw = request.form.get("pw")
    result = db.login(mail, pw)
    if(result != "failure"):
        session["user"] = result[0]  # user_idを入れる
        session["mail"] = result[1]
        #session["position"] = result[?]
        session["auth"] = result[4]
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        return redirect(url_for("top_page"))              #  トップページにリダイレクト 
    else:
        return redirect(url_for("login_page", error="パスワードかメールアドレスが違います。")) #失敗したとき

@app.route("/top") # トップページ
def top_page():
    error = request.args.get("error")
    if "user" in session:
        return render_template("main.html")
    else:
        return redirect(url_for("login_page", error="パスワードかメールアドレスが違います。")) #失敗したとき


@app.route("/auther_entry_page") #　管理者が登録するためのURL
def auther_entry_page():
    return render_template("kanrisha_account.html", auth=1) # 管理者がパスワードを入力する画面を表示　authも持って行ってその後共通のアカウント登録画面に移動

@app.route("/entry", methods=["POST"])   #　登録するためのページ
def entry():           # 上司のメールアドレスNULLもあり
    auth = request.form.get("auth")
    pw = request.form.get("pw")
    if "user" in session:
        return render_template("account2.html", auth=auth)
    elif(pw == "admin"):
        return render_template("account2.html", auth=auth)
    else:
        return redirect(url_for("login_page", error="パスワードが違います。")) #失敗したとき


@app.route("/entry_confirm", methods=["POST"])   # アカウント登録時、入力内容確認画面の表示
def entry_confirm():
    name = request.form.get("name")
    mail = request.form.get("mail")
    position = request.form.get("position")
    superier_mail = request.form.get("superier_mail")
    department = request.form.get("department")
    auth = request.form.get("auth")
    return render_template("account_confirm.html", name=name, mail=mail, position=position, superier_mail=superier_mail, department=department, auth=auth)

@app.route("/entry_complete", methods=["POST"]) # アカウント登録完了画面の表示とDB更新とメール送信
def entry_complete():
    name = request.form.get("name")
    mail = request.form.get("mail")
    position = request.form.get("position")
    superier_mail = request.form.get("superier_mail")
    department = request.form.get("department")
    auth = request.form.get("auth")
    result = db.entry(name, mail, department, position, superier_mail, auth)
    if (result != "failure"):
        result = mail_sample.send_mail(mail, result)  # [result]にパスワードが入ってるから引数にしてメール処理に渡す
        return render_template("result.html")  # アカウント登録完了画面を表示する
    else:
        return redirect(url_for("login_page", error="アカウント登録に失敗")) # 失敗した時ログインページにエラー付きで飛ぶ

@app.route("/show_document")
def show_document():
    if "user" in session:
        return render_template("main2.html", position="")    # 稟議書一覧を開くためのメニューを表示、役職で表示異なる  
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

#-------------------ここからアカウントメニューの機能-----------------------------------

@app.route("/show_account")
def show_account():
    if "user" in session:
        return render_template("main3.html", auth=session["auth"])    # アカウントのメニューを表示,authによって表示異なる
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/show_delete_account")
def show_delete_account():
    if "user" in session:
        name = request.args.get("name")
        result = db.select_account(name)           # DBからアカウント一覧を取得する(名前の部分一致OR全部)
        if(result != "failure"):
            return render_template("account_kanri.html", result=result, error="")    # アカウントの一覧を表示(削除するアカウント)  
        else:
            return redirect(url_for("top_page", error="sqlエラー"))
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/delete_account")
def delete_accout():
    if "user" in session:
        result = request.args.get("result")
        render_template("", result=result)  # アカウント削除確認画面を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/delete_account_complete")
def delete_account_complete():
    if "user" in session:
        mail = request.args.get("mail")
        result = db.delete_account(mail)
        if(result != "failure"):
            return render_template("")    # アカウント削除完了画面を表示する
        else:
            return render_template("", error="SQLエラー")  # エラー付きでメニューを表示    
    else:    
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示


@app.route("/show_update_account")
def show_update_account():
    if "user" in session:
        name = request.args.get("name")
        result = db.select_account(name)      # DBからアカウント一覧を取得する(名前の部分一致OR全部)
        if(result != "failure"):
            return render_template("", result=result) # アカウントの一覧を表示(変更するアカウント)
        else:
            return render_template("", result="", error="sqlエラー")
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_account", methods=["POST"])
def update_accout():
    if "user" in session():
        result = request.form.get("result")
        return render_template("", result=result)  # 選択したアカウントを変更するページを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_account_complete")    # アカウントのアップデート
def update_account_complete():
    if "user" in session():
        id = request.args.ger("id")
        name = request.args.get("name")
        mail = request.args.get("mail")
        position = request.args.get("position")
        superier_mail = request.args.get("superier_mail")
        department = request.args.get("department")
        error = request.args.get("error")
        result = db.accout_update(id, name, mail, position, superier_mail, department)  # resultにfailureかsuccessが返ってくる
        if(result != "failure"):
            return render_template("")  # アカウント情報の変更完了画面を表示する
        else:
            return render_template("", error="更新失敗") # エラー付きアカウントメニュー画面を表示する 
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示


@app.route("/my_account")
def my_account():
    if "user" in session:  
        return render_template("main4.html")    # 「アカウント情報」を押したときに表示される自分のアカウント情報のページ
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_pw")
def update_pw():
    if "user" in session:
        return render_template("", error="")   # 「パスワードの変更」を押したときに表示するパスワード変更ページ
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_pw2", methods=["POST"])
def update_pw2():
    if "user" in session:
        pw = request.form.get("pw")
        if(db.select_pw(session["user"], pw)):      # 前のパスワードがあっているか確認する(TrueかFalseが返ってくる)
            return render_template("")            # 次のページを表示
        else:
            return render_template("", error="パスワードが違います")  #  errorを表示して今のページを表示    
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_pw_complete", methods=["POST"])
def update_pw_complete():
    if "user" in session:
        pw = request.form.get("pw")         # 1回目のパスワード入力
        confirm_pw = request.form.get("pw") # 2回目のパスワード入力
        if(pw == confirm_pw):
            result = db.update_pw(session["id"], pw)         # DBのパスワードを更新する
            if(result != "failure"):
                return render_template("")      # パスワード変更完了画面を表示
            else:
                return render_template("", error="sqlエラー") # 同じ画面をエラー付きで表示
        else:
            return render_template("", error="同じパスワードが入力されていません")  # 同じ画面をエラー付きで表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

#------------------------ここから稟議書一覧メニューの機能--------------------------------------

@app.route("/my_document")  # 自分の申請一覧を表示する
def my_document():
    if "user" in session:
        status = request.args.get("status") # 検索する内容を取ってくる
        result = db.select_my_document(session["id"], status)
        if(result != "failure"):
            return render_template("", result=result)
        else:
            return render_template("", error="SQLエラー") # エラー付きでメニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/subordinate_document")   # 部下の申請一覧を表示する
def subordinate_document():
    if "user" in session:
        doc_name = request.args.get("doc_name") # 検索する内容を取ってくる
        result = db.select_subordinate_document(session["mail"], doc_name)
        if(result != "failure"):
            return render_template("", result=result)
        else:
            return render_template("", error="SQLエラー")  # エラー付きでメニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/show_approval")  # 自分に対してきた申請一覧を表示する
def show_approval():
    if "user" in session:
        doc_name = request.args.get("doc_name") # 検索する内容を取ってくる
        result = db.show_approval(session["mail"], doc_name)
        if(result != "failure"):
            return render_template("", result=result)
        else:
            return render_template("", error="SQLエラー")  # エラー付きでメニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/comment_edit")  # 部下の申請一覧と自分に対してきた申請一覧のコメントをクリックした時の処理
def comment_edit():
    if "user" in session:
        result = request.args.get("result")  # 一覧表示するときに使用した値を持ってくる
        return render_template("", result=result)   # コメント編集するための稟議書を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/comment_save")  # コメントを編集して保存を押したとき
def comment_save():
    if "user" in session:
        result = request.args.get("result")
        comment = request.args.get("comment")
        return render_template("", result=result, comment=comment)  # コメント編集確認画面を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/comment_confirm") # コメント編集確認画面の保存を押したとき
def comment_confirm():
    if "user" in session:
        result = request.args.get("result")
        comment = request.args.get("comment")
        # result = db.comment_edit(稟議書ID,コメント)  # 編集したコメントをアップデートする
        if(result != "failure"):
            return render_template("")  #  コメント編集完了画面を表示する
        else:
            return render_template("", error="SQLエラー")  # エラー付きで稟議書メニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/look_document")    # 部下の申請一覧から確認を押したとき
def look_document():
    if "user" in session:
        result = request.args.get("result")
        return render_template("", result=result)  # 選択した稟議書を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/superier_approval")  # 自分に対しての申請一覧の編集を押したとき
def superier_approval():
    if "user" in session:
        result = request.args.get("result")
        return render_template("", result=result)   # 承認か否決する画面を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/superier_approval_complete")  # 承認か否決を押す画面で承認を押したとき
def superier_approval_complete():
    if "user" in session:
        return render_template("")   # 承認完了画面を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示
    
@app.route("/superier_rejection_complete")  # 承認か否決を押す画面で否決を押したとき
def superier_rejection_complete():
    if "user" in session:
        return render_template("")   # 否決完了画面を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示


#------------稟議書作成--------------
@app.route("/create_document") # 「作成」を押したときに新しい稟議書を表示する
def create_document():
    if "user" in session:
        return render_template("")   # 稟議書を表示
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/insert_document")  # 作成する
def insert_document():
    if "user" in session:
        result = "success"
        # いろいろgetしてくる
        result = db.insert_document() # 稟議書をインサートするdb処理　failureかsuccessが返ってくる
        if(result != "failure"):
            return redirect(url_for("approval", )) # 稟議書を申請する画面に飛ばすURLにとばす(232行目)
        else:
            return render_template("", error="保存に失敗しました。")  # メニューにエラー付きで飛ばす
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/approval")
def approval():
    if "user" in session:
        # いろいろgetしてくる
        return render_template("", )   # 稟議書を申請する画面に飛ばす
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/approval_complete")
def approval_complete():
    if "user" in session:
        # 稟議書情報をgetしてくる
        result = "success"
        superier_mail = db.select_superier_mail(session["id"])  # dbから上司のメールアドレスをとってくる
        if(superier_mail != "failure"):
            result = db.approval()  # approval_documentテーブルの承認者IDを更新してapprovalテーブルをインサートする
            if(result != "failure"):
                mail_input.send_mail(superier_mail)   # 申請したと報告するメールを上司に送る
                return render_template("")   # 申請完了ページを表示する
            else:
                return render_template("", error="申請に失敗しました") # エラー付きでメニューを表示する
        else:
            return render_template("", error="申請に失敗しました") # エラー付きでメニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示


@app.route("/logout")
def logout():
    session.pop("user")
    session.pop("mail")
    session.pop("auth")
    # session.pop("position")
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(debug=True)
