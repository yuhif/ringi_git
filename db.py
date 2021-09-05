import MySQLdb
import hashlib
import random, string

from MySQLdb import connections

def get_connection():
    return MySQLdb.connect(user="root", passwd="jyobi2001", host="localhost", db="Approval_management", charset="utf8")

def entry(name, mail, department_id, position_id, superior_mail, auth):
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
        cur.execute(sql, (mail, name, hashed_pw, department_id, position_id, superior_mail, salt, auth))
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
    sql = "SELECT user_id,mail,password,salt,auth,position_id,superior_mail FROM user WHERE mail = %s;" # 役職も
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
    if(name == "null" or name == None):
        sql = "SELECT * FROM user;"        # nameを使った部分一致
    else:
        name = "%" + name + "%"
        sql = "SELECT * FROM user where name=%s;" # 引数nameが空の場合のsql
    conn = get_connection()
    cur = conn.cursor()
    try:
        if name == "null" or name == None:
            cur.execute(sql, )
        else:
            cur.execute(sql, (name, ))
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
    sql = "SELECT password,salt FROM user where user_id=%s;"
    try:
        cur.execute(sql,(id, ))
        result = cur.fetchone()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return False
    cur.close()
    conn.close()
    # resultの中のソルトと引数のpwをハッシュしてresultの中のpwと比較する
    b_pw = bytes(pw, "utf-8")
    b_salt = bytes(result[1], "utf-8")
    hashed_pw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 100).hex()
    
    if (hashed_pw == result[0]):
        return True
    else:
        return False


def update_pw(user_id, pw):
    conn = get_connection()
    cur = conn.cursor()
    salt_sql = "SELECT salt FROM user WHERE user_id = %s;"
    sql = "update user set password=%s WHERE user_id = %s;"        # pwのupdate文
    try:
        cur.execute(salt_sql,(user_id, ))
        salt = cur.fetchone()
        b_pw = bytes(pw, "utf-8")
        b_salt = bytes(salt[0], "utf-8")
        hashed_pw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 100).hex()

        cur.execute(sql,(hashed_pw, user_id))
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.commit()
    conn.close()
    return "success"
    
def accout_update(id, name, mail, position, superior_mail, department):
    conn = get_connection()
    cur = conn.cursor()
    sql = "update user set mail=%s,name=%s,position_id=%s,superior_mail=%s,department_id=%s where user_id=%s;"
    try:
        cur.execute(sql, (mail, name, position, superior_mail, department, id))
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.commit()
    conn.close()
    return "success"
    
def select_my_document(user_id, status):
    if status == "null" or status == None:
        sql = """SELECT document_id,approval_document.user_id,document_name,application_date,contents,quaritity,
        price,total_payment,reason,comment,result,authorizer_id,preferred_day,user.name 
        FROM approval_document JOIN user ON approval_document.user_id = user.user_id where approval_document.user_id=%s;"""  # 自分の稟議申請一覧を取ってくるsql(全部)
    else:
        sql = """SELECT document_id,approval_document.user_id,document_name,application_date,contents,quaritity,
        price,total_payment,reason,comment,result,authorizer_id,preferred_day,user.name 
        FROM approval_document JOIN user ON approval_document.user_id = user.user_id where result=%s and approval_document.user_id=%s;"""  # 自分の稟議申請一覧を取ってくるsql(statusでwhereをつかう)
    conn = get_connection()
    cur = conn.cursor()
    try:
        if status == None or status == "null":
            cur.execute(sql, (user_id, ))
        else:
            cur.execute(sql, (status, user_id))
        result = cur.fetchall()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    return result

def select_subordinate_document(id, doc_name):
    if doc_name == "null" or doc_name == None:
        sql = """SELECT document_id,approval_document.user_id,document_name,application_date,contents,quaritity,
        price,total_payment,reason,comment,result,authorizer_id,preferred_day,user.name 
        FROM approval_document JOIN user ON approval_document.user_id = user.user_id 
        WHERE document_id IN (SELECT document_id FROM approval WHERE user_id = %s);"""   # 部下の稟議申請一覧を持ってくるsql（全部）（）内は自分のuser_id
    else:
        doc_name = "%" + doc_name + "%"
        sql = """SELECT document_id,approval_document.user_id,document_name,application_date,contents,quaritity,
        price,total_payment,reason,comment,result,authorizer_id,preferred_day,user.name 
        FROM approval_document JOIN user ON approval_document.user_id = user.user_id 
        where (document_name like %s OR user.name like %s) AND document_id IN (SELECT document_id FROM approval WHERE user_id = %s);""" # 部下の稟議申請一覧を持ってくるsql（稟議書名・申請者名の部分一致)
    conn = get_connection()
    cur = conn.cursor()
    try:
        if doc_name == "null" or doc_name == None:
            cur.execute(sql, (id, ))
        else:
            cur.execute(sql, (doc_name, doc_name, id))
        result = cur.fetchall()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    return result

def select_show_approval(id, doc_name):
    if doc_name == "null" or doc_name == None:
        sql = """SELECT document_id,approval_document.user_id,document_name,application_date,contents,quaritity,
        price,total_payment,reason,comment,result,authorizer_id,preferred_day,user.name 
        FROM approval_document JOIN user ON approval_document.user_id = user.user_id 
        WHERE authorizer_id = %s;""" # 自分に対してきた申請一覧を持ってくるsql（全部）()内は自分のuser_id
    else:
        doc_name = "%" + doc_name + "%"
        sql = """SELECT document_id,approval_document.user_id,document_name,application_date,contents,quaritity,
        price,total_payment,reason,comment,result,authorizer_id,preferred_day,user.name 
        FROM approval_document JOIN user ON approval_document.user_id = user.user_id 
        WHERE (document_name LIKE %s OR user.name LIKE %s) AND authorizer_id = %s;""" # 自分に対してきた申請一覧を持ってくるsql（稟議書名・申請者名の部分一致)
    conn = get_connection()
    cur = conn.cursor()
    try:
        if doc_name == "null" or doc_name == None:
            cur.execute(sql, (id,))
        else:
            cur.execute(sql, (doc_name, doc_name, id, ))
        result = cur.fetchall()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    return result

def insert_document(id, doc_name, contents, quaritity, price, total_payment, reason, comment, preferred_day):   # 新規稟議書のインサート
    conn = get_connection()
    cur = conn.cursor()
    sql = """INSERT into approval_document(user_id, document_name,application_date,contents,
    quaritity,price,total_payment,reason,comment,result,authorizer_id,preferred_day) 
    value(%s,%s,null,%s,%s,%s,%s,%s,%s,3,0,%s) """
    try:
        cur.execute(sql,( ))
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.commit()
    conn.close()
    return "success"

def application(superior_id, document_id):  # 申請処理
    conn = get_connection()
    cur = conn.cursor()
    sql = "INSERT into approval(user_id,document_id) value(%s,%s)"    # approvalテーブルにインサートするsql
    try:
        cur.execute()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.commit()
    conn.close()
    return "success"

def approval_prepare(superior_mail):
    conn = get_connection()
    cur = conn.cursor()
    sql = ""

def select_superior_id(mail):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT user_id FROM user where mail=%s;"   # 上司のidを取ってくるsql
    try:
        cur.execute(sql, (mail, ))
        superier_id = cur.fetchone()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    return superier_id

def select_document_id_first(user_id):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT document_id FROM approval_document WHERE user_id = %s ORDER BY application_date DESC LIMIT 1;"
    try:
        cur.execute(sql, (user_id, ))
        document_id = cur.fetchone()
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"
    cur.close()
    conn.close()
    return document_id[0]

def comment_edit(id, comment):
    conn = get_connection()
    cur = conn.cursor()
    sql = "update approval_document set comment=%s where document_id=%s;"
    try:
        cur.execute(sql, (comment, id, ))
        cur.close()
        conn.commit()
        conn.close()
        return "success"
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"

def delete_account(mail):
    conn = get_connection()
    cur = conn.cursor()
    sql = "DELETE FROM user WHERE mail = %s"
    try:
        cur.execute(sql, (mail, ))
        cur.close()
        conn.commit()
        conn.close()
        return "success"
    except Exception as e:
        print("SQLの実行に失敗", e)
        return "failure"

