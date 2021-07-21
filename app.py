from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template("index.html")

@app.route('/')
def account_page():
    return render_template("account1.html")

@app.route('/')
def account2_page():
    return render_template("account2.html")

@app.route('/')
def account_change():
    return render_template("account_change.html")

@app.route('/')
def change_result():
    return render_template("change_result.html")

@app.route('/')
def menu_page():
    return render_template("menu.html")

@app.route('/')
def kanrisha_page():
    return render_template("kanrisha_account.html")





if __name__ == "__main__":
    app.run(debug=True) 
