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
    mail = request.form.get("textmail")
    pw = request.form.get("textpw")
    if(pw != None):
        result = db.login(mail, pw)
        if(result != "failure"):
            session["user"] = result[0]  # user_idを入れる
            session["mail"] = result[1]
            session["position"] = result[5]
            session["auth"] = result[4]
            session["superior_mail"] = result[6]
            session["name"] = result[7]
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for("top_page"))              #  トップページにリダイレクト 
        else:
            return redirect(url_for("login_page", error="パスワードかメールアドレスが違います。")) #失敗したとき
    else:
        return redirect(url_for("login_page", error="パスワードかメールアドレスが違います。"))

@app.route("/top") # トップページ
def top_page():
    error = request.args.get("error")
    if "user" in session:
        return render_template("main.html")
    else:
        return redirect(url_for("login_page", error="パスワードかメールアドレスが違います。")) #失敗したとき


@app.route("/author_entry_page") #　管理者が登録するためのURL
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
    if position != "1":
        superior_mail = request.form.get("superier_mail")
    else:
        superior_mail = ""
    department = request.form.get("department")
    auth = request.form.get("auth")
    return render_template("account_confirm.html", name=name, mail=mail, position=position, superior_mail=superior_mail, department=department, auth=auth)

@app.route("/entry_complete", methods=["POST"]) # アカウント登録完了画面の表示とDB更新とメール送信
def entry_complete():
    name = request.form.get("name")
    mail = request.form.get("mail")
    position = request.form.get("position")
    superior_mail = request.form.get("superior_mail")
    department = request.form.get("department")
    auth = request.form.get("auth")
    result = db.entry(name, mail, department, position, superior_mail, auth)
    if (result != "failure"):
        result = mail_sample.send_mail(mail, result)  # [result]にパスワードが入ってるから引数にしてメール処理に渡す
        return render_template("result.html", auth=auth)  # アカウント登録完了画面を表示する
    else:
        if(auth == "1"):
            return redirect(url_for("login_page", error="アカウント登録に失敗")) # 失敗した時ログインページにエラー付きで飛ぶ
        else:
            return redirect(url_for("show_account", error="アカウント登録失敗"))

@app.route("/show_document")
def show_document():
    if "user" in session:
        error = request.args.get("error")
        return render_template("main2.html", position=session["position"], error=error)    # 稟議書一覧を開くためのメニューを表示、役職で表示異なる  
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

#-------------------ここからアカウントメニューの機能-----------------------------------

@app.route("/show_account")
def show_account():
    if "user" in session:
        error = request.args.get("error")
        info = request.args.get("info")
        return render_template("main3.html", auth=session["auth"], error=error, info=info)    # アカウントのメニューを表示,authによって表示異なる
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/show_delete_account")
def show_delete_account():
    if "user" in session:
        name = request.args.get("name")
        result = db.select_account(name)           # DBからアカウント一覧を取得する(名前の部分一致OR全部)
        if(result != "failure"):
            return render_template("control.html", result=result, error="")    # アカウントの一覧を表示(削除するアカウント)  
        else:
            return redirect(url_for("top_page", error="sqlエラー"))
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user" in session:
        mail = request.form.get("mail")
        name = request.form.get("name")
        position = request.form.get("position")
        superior_mail = request.form.get("superior_mail")
        department = request.form.get("department")
        return render_template("account_delete.html", mail=mail, name=name, position=position, superior_mail=superior_mail, department=department)  # アカウント削除確認画面を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/delete_account_complete", methods=["POST"])
def delete_account_complete():
    if "user" in session:
        mail = request.form.get("mail")
        result = db.delete_account(mail)
        if(result != "failure"):
            return render_template("delete_result.html")    # アカウント削除完了画面を表示する
        else:
            return redirect(url_for("show_account", error="SQLエラー"))  # エラー付きでメニューを表示    
    else:    
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示


@app.route("/show_update_account")
def show_update_account():
    if "user" in session:
        name = request.args.get("name")
        result = db.select_account(name)     # DBからアカウント一覧を取得する(名前の部分一致OR全部)
        if(result != "failure"):
            return render_template("control_change.html", result=result) # アカウントの一覧を表示(変更するアカウント)
        else:
            return redirect(url_for("show_account", result="", error="sqlエラー"))
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_account", methods=["POST"])
def update_account():
    if "user" in session:
        id = request.form.get("id")
        mail = request.form.get("mail")
        name = request.form.get("name")
        position = request.form.get("position")
        superior_mail = request.form.get("superior_mail")
        department = request.form.get("department")
        return render_template("account_change.html",id=id, name=name, mail=mail, position=position, superior_mail=superior_mail, department=department)  # 選択したアカウントを変更するページを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_account_complete", methods=["POST"])    # アカウントのアップデート
def update_account_complete():
    if "user" in session:
        id = request.form.get("id")
        name = request.form.get("name")
        mail = request.form.get("mail")
        position = request.form.get("position")
        superior_mail = request.form.get("superior_mail")
        department = request.form.get("department")
        print(department)
        error = request.form.get("error")
        result = db.account_update(id, name, mail, position, superior_mail, department)  # resultにfailureかsuccessが返ってくる
        if(result != "failure"):
            return render_template("change_result.html")  # アカウント情報の変更完了画面を表示する
        else:
            return redirect(url_for("show_account", error="更新失敗")) # エラー付きアカウントメニュー画面を表示する 
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示


@app.route("/my_account")
def my_account():
    if "user" in session:
        error = request.args.get("error")
        return render_template("main4.html", name=session["name"], mail=session["mail"], superior_mail=session["superior_mail"], position=session["position"], error=error)    # 「アカウント情報」を押したときに表示される自分のアカウント情報のページ
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_pw")
def update_pw():
    if "user" in session:
        error = request.args.get("error")
        return render_template("main5.html", error=error)   # 「パスワードの変更」を押したときに表示するパスワード変更ページ
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_pw2", methods=["POST"])
def update_pw2():
    if "user" in session:
        pw = request.form.get("pw3")
        if(pw != ""):
            if(db.select_pw(session["user"], pw)):      # 前のパスワードがあっているか確認する(TrueかFalseが返ってくる)
                return render_template("main6.html")            # 次のページを表示
            else:
                return redirect(url_for("update_pw", error="パスワードが違います"))  #  errorを表示して今のページを表示    
        else:
            return redirect(url_for("update_pw", error="パスワードが違います"))
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/update_pw_complete", methods=["POST"])
def update_pw_complete():
    if "user" in session:
        pw = request.form.get("pw5")       # 1回目のパスワード入力
        confirm_pw = request.form.get("pw7") # 2回目のパスワード入力
        if(pw == confirm_pw and pw != ""):
            print(pw)
            result = db.update_pw(session["user"], pw)         # DBのパスワードを更新する
            if(result != "failure"):
                return render_template("main7.html")      # パスワード変更完了画面を表示
            else:
                return redirect(url_for("update_pw", error="sqlエラー")) # 同じ画面をエラー付きで表示
        else:
            return redirect(url_for("update_pw", error="同じパスワードが入力されていません"))  # 同じ画面をエラー付きで表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

#------------------------ここから稟議書一覧メニューの機能--------------------------------------

@app.route("/my_document")  # 自分の申請一覧を表示する
def my_document():
    if "user" in session:
        status = request.args.get("status") # 検索する内容を取ってくる
        result = db.select_my_document(session["user"], status)
        if(result != "failure"):
            return render_template("my_ringi_search.html", result=result)
        else:
            return redirect(url_for("show_document", error="SQLエラー")) # エラー付きでメニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/subordinate_document")   # 部下の申請一覧を表示する
def subordinate_document():
    if "user" in session:
        doc_name = request.args.get("doc_name") # 検索する内容を取ってくる
        result = db.select_subordinate_document(session["user"], doc_name)
        if(result != "failure"):
            return render_template("subordinate_ringi_search.html", result=result, my_id=session["user"])
        else:
            return redirect(url_for("show_document", error="SQLエラー"))  # エラー付きでメニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/show_approval")  # 自分に対してきた申請一覧を表示する
def show_approval():
    if "user" in session:
        doc_name = request.args.get("doc_name") # 検索する内容を取ってくる
        print(doc_name)
        result = db.select_show_approval(session["user"], doc_name)
        if(result != "failure"):
            return render_template("approval_ringi_search.html", result=result)
        else:
            return redirect(url_for("show_document", error="SQLエラー"))  # エラー付きでメニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/comment_edit")  # 部下の申請一覧と自分に対してきた申請一覧のコメントをクリックした時の処理
def comment_edit():
    if "user" in session:
        num = request.args.get("number")          # 一覧表示するときに使用した値を持ってくる
        document_id = request.args.get("doc_id")
        doc_name = request.args.get("doc_name")
        contents = request.args.get("contents")
        quaritity = request.args.get("quaritity")
        price = request.args.get("price")
        total_payment = request.args.get("total_payment")
        reason = request.args.get("reason")
        comment = request.args.get("comment")
        result = request.args.get("result")
        preferred_day = request.args.get("preferred_day")    
        return render_template("ringi5.html", num=num, name=session["name"], document_id=document_id, doc_name=doc_name, contents=contents, quaritity=quaritity, price=price, total_payment=total_payment, reason=reason, comment=comment, result=result, preferred_day=preferred_day)   # コメント編集するための稟議書を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/comment_save")  # コメントを編集して保存を押したとき
def comment_save():
    if "user" in session:
        num = request.args.get("number")          # 一覧表示するときに使用した値を持ってくる
        document_id = request.args.get("document_id")
        doc_name = request.args.get("doc_name")
        contents = request.args.get("contents")
        quaritity = request.args.get("quaritity")
        price = request.args.get("price")
        total_payment = request.args.get("total_payment")
        reason = request.args.get("reason")
        comment = request.args.get("comment")
        result = request.args.get("result")
        preferred_day = request.args.get("preferred_day")    
        return render_template("ringi6.html", num=num, name=session["name"], document_id=document_id, doc_name=doc_name, contents=contents, quaritity=quaritity, price=price, total_payment=total_payment, reason=reason, comment=comment, result=result, preferred_day=preferred_day)   # コメント編集を確認するための稟議書を表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/comment_confirm") # コメント編集確認画面の保存を押したとき
def comment_confirm():
    if "user" in session:
        document_id = request.args.get("doc_id")
        comment = request.args.get("comment")
        result = db.comment_edit(document_id, comment)  # 編集したコメントをアップデートする
        if(result != "failure"):
            return render_template("comment_edit_result.html")  #  コメント編集完了画面を表示する
        else:
            return redirect(url_for("show_document", error="SQLエラー"))  # エラー付きで稟議書メニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

# @app.route("/look_document")    # 部下の申請一覧から確認を押したとき
# def look_document():
#     if "user" in session:
#         result = request.args.get("result")
#         return render_template("", result=result)  # 選択した稟議書を表示する
#     else:
#         return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/superior_approval")  # 自分に対しての申請一覧の編集を押したとき
def superior_approval():
    if "user" in session:
        num = request.args.get("num")
        document_id = request.args.get("document_id")
        doc_name = request.args.get("doc_name")
        contents = request.args.get("contents")
        quaritity = request.args.get("quaritity")
        price = request.args.get("price")
        total_payment = request.args.get("total_payment")
        reason = request.args.get("reason")
        comment = request.args.get("comment")
        result = request.args.get("result")
        preferred_day = request.args.get("preferred_day")    
        return render_template("ringi4.html", num=num, name=session["name"], document_id=document_id, doc_name=doc_name, contents=contents, quaritity=quaritity, price=price, total_payment=total_payment, reason=reason, comment=comment, result=result, preferred_day=preferred_day)   # 承認するための画面を表示
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/superior_approval_complete")  # 承認か否決を押す画面で承認を押したとき
def superior_approval_complete():
    if "user" in session:
        doc_id = request.args.get("document_id")
        if session["superior_mail"] != "null" and session["superior_mail"] != "":
            superior_id = db.select_superior_id(session["superior_mail"])
            result = db.approval(doc_id, superior_id[0], session["user"])    
        else:
            result = db.president_approval(doc_id, session["user"])  # 社長の承認
        if result != "failure":
            return render_template("approval_result.html")   # 承認完了画面を表示する
        else:
            return redirect(url_for('show_document', error="SQLエラー")) # エラーでメニュー表示
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示
    
@app.route("/superior_rejection_complete")  # 承認か否決を押す画面で否決を押したとき
def superior_rejection_complete():
    if "user" in session:
        document_id = request.args.get("document_id")
        result = db.rejection(document_id, session["user"])
        if result != "failure":
            return render_template("reject_result.html")   # 否決完了画面を表示する
        else:
            return redirect(url_for("show_document", error="SQLエラー"))
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示


#------------稟議書作成--------------
@app.route("/create_document") # 「作成」を押したときに新しい稟議書を表示する
def create_document():
    if "user" in session:
        return render_template("ringi1.html", textmanager=session["name"])   # 稟議書を表示
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/insert_document")  # 作成する
def insert_document():
    if "user" in session:
        doc_name = request.args.get("doc_name")
        contents = request.args.get("contents")
        quaritity = request.args.get("quaritity")
        price = request.args.get("price")
        total_payment = request.args.get("total_payment")
        reason = request.args.get("reason")
        comment = "null"
        preferred_day = request.args.get("preferred_day")
        result1 = db.insert_document(session["user"], doc_name, contents, quaritity, price, total_payment, reason, comment, preferred_day) # 稟議書をインサートするdb処理　failureかsuccessが返ってくる
        document_id = db.select_document_id_first(session["user"])
        if(result1 != "failure"):
            return redirect(url_for("application",document_id=document_id, doc_name=doc_name, contents=contents, quaritity=quaritity, price=price, total_payment=total_payment, reason=reason, comment=comment, preferred_day=preferred_day)) # 稟議書を申請する画面に飛ばすURLにとばす
        else:
            return redirect(url_for("show_document", error="保存に失敗しました。"))  # メニューにエラー付きで飛ばす
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/save_document")
def save_document():
    if "user" in session:
        doc_id = request.args.get("doc_id")
        doc_name = request.args.get("doc_name")
        contents = request.args.get("contents")
        quaritity = request.args.get("quaritity")
        price = request.args.get("price")
        total_payment = request.args.get("total_payment")
        reason = request.args.get("reason")
        preferred_day = request.args.get("preferred_day")
        return render_template("ringi_save.html", name=session["name"], document_id=doc_id, doc_name=doc_name, contents=contents, quaritity=quaritity, price=price, total_payment=total_payment, reason=reason, preferred_day=preferred_day)    
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示


@app.route("/save_document_complete")
def save_document_complete():
    if "user" in session:
        doc_id = request.args.get("doc_id")
        doc_name = request.args.get("doc_name")
        contents = request.args.get("contents")
        quaritity = request.args.get("quaritity")
        price = request.args.get("price")
        total_payment = request.args.get("total_payment")
        reason = request.args.get("reason")
        preferred_day = request.args.get("preferred_day")
        result1 = db.update_document(doc_id, doc_name, contents, quaritity, price, total_payment, reason, preferred_day) # 稟議書をインサートするdb処理　failureかsuccessが返ってくる
        if(result1 != "failure"):
            return redirect(url_for("application",document_id=doc_id, doc_name=doc_name, contents=contents, quaritity=quaritity, price=price, total_payment=total_payment, reason=reason, preferred_day=preferred_day)) # 稟議書を申請する画面に飛ばすURLにとばす
        else:
            return redirect(url_for("show_document", error="保存に失敗しました。"))  # メニューにエラー付きで飛ばす
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示


@app.route("/application")
def application():
    if "user" in session:
        document_id = request.args.get("document_id")
        doc_name = request.args.get("doc_name")
        contents = request.args.get("contents")
        quaritity = request.args.get("quaritity")
        price = request.args.get("price")
        total_payment = request.args.get("total_payment")
        reason = request.args.get("reason")
        comment = request.args.get("comment")
        result = request.args.get("result")
        preferred_day = request.args.get("preferred_day")    
        return render_template("ringi3.html",name=session["name"], document_id=document_id, doc_name=doc_name, contents=contents, quaritity=quaritity, price=price, total_payment=total_payment, reason=reason, comment=comment, result=result, preferred_day=preferred_day)   # 稟議書を申請する画面に飛ばす
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/application_complete")
def application_complete():
    if "user" in session:
        document_id = request.args.get("document_id")
        result = request.args.get("result") 
        superior_id = db.select_superior_id(session["superior_mail"])
        if(superior_id != "failure"):
            result = db.application(superior_id[0], document_id)  # approval_documentテーブルの承認者IDを更新してapprovalテーブルをインサートする
        else:
            return redirect(url_for("show_document", error="SQLエラー")) 
        if(result != "failure"):
            mail_input.send_mail(session["superior_mail"])   # 申請したと報告するメールを上司に送る
            return render_template("application_result.html")   # 申請完了ページを表示する
        else:
            return redirect(url_for("show_document", error="申請に失敗しました")) # エラー付きでメニューを表示する
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/show_approval_document")
def show_approval_document():
    if "user" in session:
        num = request.args.get("number") 
        document_id = request.args.get("document_id")
        doc_name = request.args.get("doc_name")
        contents = request.args.get("contents")
        quaritity = request.args.get("quaritity")
        price = request.args.get("price")
        total_payment = request.args.get("total_payment")
        reason = request.args.get("reason")
        comment = request.args.get("comment")
        result = request.args.get("result")
        preferred_day = request.args.get("preferred_day")    
        return render_template("ringi2.html", num=num, name=session["name"], document_id=document_id, doc_name=doc_name, contents=contents, quaritity=quaritity, price=price, total_payment=total_payment, reason=reason, comment=comment, result=result, preferred_day=preferred_day)   # 稟議書確認画面表示
    else:
        return redirect(url_for("login_page", error="セッションが切れました"))  # セッション切れでログイン画面表示

@app.route("/logout")
def logout():
    session.pop("user")
    session.pop("mail")
    session.pop("auth")
    session.pop("position")
    session.pop("superior_mail")
    session.pop("name")
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(debug=True)
