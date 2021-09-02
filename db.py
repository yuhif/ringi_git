import MySQLdb
import hashlib
import random, string

from MySQLdb import connections

def get_connection():
    return MySQLdb.connect(user="root", passwd="jyobi2001", host="localhost", db="Approval_management", charset="utf8")

def entry(name, mail, department_id, position_id, superier_mail, auth):
    randlist = [random.choice(string.ascii_letters + string.digits) for i in range(20)]
    salt = ''.join(randlist)
    randlist = [random.choice(string.ascii_letters + string.digits) for i in range(20)]
    pw = ''.join(randlist)
    b_pw = bytes(pw, "utf-8")
    b_salt = bytes(salt, "utf-8")
    hashed_pw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 100).hex()

    if auth == "null":
        auth = 0

    conn = get_connection()
    cur = conn.cursor()
    sql = "INSERT INTO user VALUES(0, %s, %s, %s, %s, %s, %s, %s, %s);"
    try:
        cur.execute(sql, (mail, name, hashed_pw, department_id, position_id, superier_mail, salt, auth))
        cur.close()
        conn.commit()
        conn.close()
        return pw
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"

def login(mail, pw):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT user_id,mail,password,salt,auth FROM user WHERE mail = %s;" # 役職も
    try:
        cur.execute(sql, (mail, ))
        result = cur.fetchone()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"

    b_pw = bytes(pw, "utf-8")
    b_salt = bytes(result[3], "utf-8")
    hashed_pw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 100).hex()
    if(hashed_pw == result[2]):
        return result # 結果を返す
    else:
        return "failure"
    
def select_account(name):   # アカウントの一覧を取得する
    if(name != "null"):
        name = "%" + name + "%"
        sql = "SELECT * FROM account where name=name;"        # nameを使った部分一致
    else:
        sql = "SELECT * FROM account;" # 引数nameが空の場合のsql
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql,(name, ))
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"

def select_pw(id, pw):      # pw変更する時の処理。前のpwを取得する。
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT pw FROM user where user_id=%s;"
    try:
        cur.execute(sql,(id, ))
        result = cur.fetchone()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    # resultの中のソルトと引数のpwをハッシュしてresultの中のpwと比較する
    # b_pw = bytes(, "utf-8")
    # b_salt = bytes(, "utf-8")
    # hashed_pw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 100).hex()
    # if (True):
    #     return True
    # else:
    #     return False

def update_pw(user_id, pw):
    conn = get_connection()
    cur = conn.cursor()
    sql = "update user set pw=%s;"        # pwのupdate文
    try:
        cur.execute()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.commit()
    conn.close()
    return "success"
    
def accout_update(id, name, mail, position, superier_mail, department):
    conn = get_connection()
    cur = conn.cursor()
    sql = "update user set mail=%s,name=%s,position_id=%s,superior_mail=%s,department_id=%s where user_id=%s;"
    try:
        cur.execute()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.commit()
    conn.close()
    return "success"
    
def select_my_document(user_id, status):
    if status == "null":
        sql = "SELECT * FROM approval_document where user_id=%s;"  # 自分の稟議申請一覧を取ってくるsql(全部)
    else:
        sql = "SELECT * FROM approval_document where status=%s;"  # 自分の稟議申請一覧を取ってくるsql(statusでwhereをつかう)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute()
        result = cur.fetchall()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    return result

def select_subordinate_document(mail, doc_name):
    if doc_name == "null":
        sql = "SELECT * FROM approval_document where superior_id=%s;" # 部下の稟議申請一覧を持ってくるsql（全部）（）内は自分のuser_id
    else:
        sql = "SELECT * FROM approval_document where document_name like '%doc_name%'; " # 部下の稟議申請一覧を持ってくるsql（稟議書名・申請者名の部分一致)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, ())
        result = cur.fetchall()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    return result

def select_show_approval(mail, doc_name):
    if doc_name == "null":
        sql = "SELECT * FROM approval_document where superior_id=%s;" # 自分に対してきた申請一覧を持ってくるsql（全部）()内は自分のuser_id
    else:
        sql = "SELECT * FROM approval_document where document_name='%doc_name%';" # 自分に対してきた申請一覧を持ってくるsql（稟議書名・申請者名の部分一致)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, ())
        result = cur.fetchall()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    return result

def insert_document():   # 新規稟議書のインサート
    conn = get_connection()
    cur = conn.cursor()
    sql = "INSERT into approval_document values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        cur.execute(sql,( ))
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.commit()
    conn.close()
    return "success"

def approval():  # 申請処理
    conn = get_connection()
    cur = conn.cursor()
    sql = "INSERT into approval values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"    # approvalテーブルにインサートするsql
    try:
        cur.execute()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.commit()
    conn.close()
    return "success"

def select_superier_mail(user_id):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT mail FROM account where user_id=%s;"   # 上司のメールアドレスを取ってくるsql
    try:
        cur.execute()
        superier_mail = cur.fetchone()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    return superier_mail

def comment_edit(id, comment):

    conn = get_connection()
    cur = conn.cursor()
    sql = "update approval_document set comment=comment where document_id=%s;"

    pass

