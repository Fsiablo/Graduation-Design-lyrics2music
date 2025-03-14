import random

from flask import Flask,render_template,send_file,flash
from flask import redirect
from flask import url_for
from flask import request
from model.check_login import is_existed,exist_user,is_null
from model.check_regist import add_user
from music_gen import music_gen
from midi2wav import mid2wav
import time
app = Flask(__name__)
app.secret_key = '123456'
mucis_src=''
@app.route('/')
def index():
    return redirect(url_for('user_login'))

@app.route('/user_login',methods=['GET','POST'])
def user_login():
    if request.method=='POST':  # 注册发送的请求为POST请求
        username = request.form['username']
        password = request.form['password']
        if is_null(username,password):
            login_massage = "温馨提示：账号和密码是必填"
            return render_template('login.html', message=login_massage)
        elif is_existed(username, password):
            return redirect(url_for('index_'))
        elif exist_user(username):
            login_massage = "温馨提示：密码错误，请输入正确密码"
            return render_template('login.html', message=login_massage)
        else:
            login_massage = "温馨提示：不存在该用户，请先注册"
            return render_template('login.html', message=login_massage)
    return render_template('login.html')

@app.route("/register",methods=["GET", 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if is_null(username,password):
            login_massage = "温馨提示：账号和密码是必填"
            return render_template('register.html', message=login_massage)
        elif exist_user(username):
            login_massage = "温馨提示：用户已存在，请直接登录"
            return render_template('register.html', message=login_massage)
        else:
            add_user(request.form['username'], request.form['password'] )
            return render_template('index.html', username=username)
    return render_template('register.html')
@app.route("/index_",methods=["GET","POST"])
def index_():
    global mucis_src
    seed=0
    src=''
    if request.method=='POST':
        lyrics=request.form['lyrics']
        action=request.form['button']
        seed=request.form['seed']
        if seed=='':
            seed=0
        if action=='提交':
            last_gen=lyrics
            with open('tmp','w') as f:
                f.write(last_gen)
            if not lyrics:
                return render_template('index.html', seed=seed, src=src)
            flash("Generating.....")
            start_time = time.time()
            music_gen(lyrics,seed=seed)
            src=mid2wav()
            mucis_src=src
            end_time = time.time()
            print(end_time-start_time)
            flash("完成！")
        if action=='换一首':
            if lyrics!='':
                music_gen(lyrics, seed=seed)
            else:
                with open('tmp','r') as f:
                    last_gen=f.read()
                if not last_gen:
                    return render_template('index.html', seed=seed, src=src)
                music_gen(last_gen, seed=seed)
            seed = random.randint(0, 10000)
            flash("Generating.....")
            src=mid2wav()
            mucis_src=src
            flash("完成")
        if action=='下载歌曲':
            try:
                return send_file (mucis_src, as_attachment=True)
            except:
                return render_template('index.html', seed=seed, src=src)
        if action=='下载曲谱':
            try:
                return send_file('static/music/out.xml', as_attachment=True)
            except:
                return render_template('index.html', seed=seed, src=src)
    return render_template('index.html', seed=seed,src=src)
if __name__=="__main__":
    app.run(debug=True)


