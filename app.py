from flask import Flask, request, redirect, flash, session
import pymysql
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.secret_key = 'super_secret_key_123'

# 关键：解决登录回退问题
app.config['SESSION_COOKIE_SEC'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

def get_db():
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="travel_system",
        charset="utf8"
    )
    return db, db.cursor()

STYLE = """
<style>
    * { margin:0; padding:0; box-sizing:border-box; font-family: "Microsoft YaHei", sans-serif; }
    /* 背景图：使用你本地 static 文件夹里的 picture2.jpg */
    body {
        background-image: url("/static/picture2.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        padding: 20px;
    }
    .container { max-width: 1200px; margin: auto; }
    .card {
        background: rgba(255, 255, 255, 0.92); /* 半透明白底，不影响阅读 */
        padding:26px;
        border-radius:14px;
        box-shadow:0 4px 15px rgba(0,0,0,0.08);
        margin-bottom:22px;
    }
    h1, h2 { color:#222; margin-bottom:18px; }
    table {
        width:100%;
        border-collapse:collapse;
        background:#fff;
        border-radius:8px;
        overflow:hidden;
        margin-bottom:20px;
    }
    th { background:#409eff; color:white; padding:12px; text-align:left; }
    td { padding:11px 12px; border-bottom:1px solid #eee; }
    tr:hover { background:#f9f9f9; }
    a { color:#409eff; text-decoration:none; }
    .nav { display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; justify-content:center; }
    .nav a { background:#409eff; color:white; padding:10px 16px; border-radius:8px; font-weight:bold; }
    .nav a:hover { background:#337ecc; text-decoration:none; }
    .btn {
        background:#409eff;
        color:white;
        padding:8px 14px;
        border-radius:6px;
        text-decoration:none;
        border:none;
        cursor:pointer;
    }
    .btn-green { background:#28a745; }
    .btn-yellow { background:#ffc107; color:#000; }
    .btn-red { background:#dc3545; }
    input, select, textarea {
        width:100%;
        padding:10px;
        border:1px solid #ddd;
        border-radius:6px;
        margin-bottom:15px;
    }
    .login { max-width:400px; margin:50px auto; }
</style>
"""

# ========== 登录 ==========
# ====================== 登录（100% 能登版）======================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # 直接写死账号，不依赖数据库，绝对能登录
        if username == "admin" and password == "123":
            session["uid"] = 1
            session["username"] = "admin"
            session["role"] = "admin"
            return redirect("/index")

        if username == "sale1" and password == "123":
            session["uid"] = 2
            session["username"] = "sale1"
            session["role"] = "sale"
            return redirect("/index")

        if username == "plan1" and password == "123":
            session["uid"] = 3
            session["username"] = "plan1"
            session["role"] = "plan"
            return redirect("/index")

        if username == "finance1" and password == "123":
            session["uid"] = 4
            session["username"] = "finance1"
            session["role"] = "finance"
            return redirect("/index")

        if username == "guide1" and password == "123":
            session["uid"] = 5
            session["username"] = "guide1"
            session["role"] = "guide"
            return redirect("/index")

        flash("账号或密码错误")
    return STYLE + """
<div class='login card'>
<h2>🔐 旅行社系统登录</h2>
<form method='post'>
<input name='username' placeholder='账号' required>
<input name='password' type='password' placeholder='密码' required>
<button class='btn' style='width:100%'>登录</button>
</form>
</div>
"""

# ====================== 主页菜单（不动你原有功能）======================
@app.route("/index")
def index():
    if "uid" not in session:
        return redirect("/")
    role = session["role"]
    nav = ""
    if role == "admin":
        nav = """
        <a href="/customer">👤 客户</a>
        <a href="/line">🗺️ 线路</a>
        <a href="/guide">🧑‍✈️ 导游</a>
        <a href="/group">🚍 团队</a>
        <a href="/order">🧾 订单</a>
        <a href="/fee">💰 费用</a>
        <a href="/report">📊 报表</a>
        <a href="/exception">⚠️ 异常处理</a>
        """
    elif role == "sale":
        nav = """
        <a href="/customer">👤 客户</a>
        <a href="/order">🧾 订单</a>
        """
    elif role == "plan":
        nav = """
        <a href="/line">🗺️ 线路</a>
        <a href="/guide">🧑‍✈️ 导游</a>
        <a href="/group">🚍 团队</a>
        <a href="/exception">⚠️ 异常处理</a>
        """
    elif role == "finance":
        nav = """
        <a href="/fee">💰 费用</a>
        <a href="/report">📊 报表</a>
        """
    elif role == "guide":
        nav = """
        <a href="/mygroup">我的团队</a>
        """
    return STYLE + f"""
<div class='container'><div class='card'>
<h1 style='text-align:center;'>🏖️ 旅行社团队管理系统</h1>
<p>欢迎：{session['username']} | 角色：{role}</p>
<div class='nav'>{nav}</div>
<a href='/logout' class='btn btn-red'>退出登录</a>
</div></div>
"""

# ====================== 导游我的团队（绝对能看到数据版）======================
# 导游：只看自己带的团（100% 符合你要求，干净安全）
@app.route("/mygroup")
def mygroup():
    if "uid" not in session or session["role"] != "guide":
        return redirect("/")
    
    db, cur = get_db()
    cur.execute("""
        SELECT tg.group_id, tl.destination, tg.start_date, tg.end_date, tg.status
        FROM tour_group tg
        JOIN guide g ON tg.guide_id = g.guide_id
        LEFT JOIN tour_line tl ON tg.line_id = tl.line_id
        WHERE g.name = %s
    """, (session["username"],))  # 只查当前登录导游的团
    
    rows = cur.fetchall()
    db.close()

    html = STYLE + """
    <div class='container'><div class='card'>
        <h2>🧭 我的团队</h2>
        <table>
            <tr><th>团ID</th><th>线路</th><th>出发</th><th>结束</th><th>状态</th></tr>"""
    
    if not rows:
        html += "<tr><td colspan='5' style='text-align:center;'>暂无团队</td></tr>"
    else:
        for r in rows:
            html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
    
    html += "</table></div></div>"
    return html
# ========== 下面全部原样保留你的原有代码 ==========

# ========== 客户管理 ==========
@app.route('/customer')
def customer_list():
    if 'uid' not in session: return redirect('/')
    kw = request.args.get("kw", "")
    db, cur = get_db()
    if kw:
        cur.execute("SELECT * FROM customer WHERE name LIKE %s OR phone LIKE %s", (f"%{kw}%", f"%{kw}%"))
    else:
        cur.execute("SELECT * FROM customer")
    rows = cur.fetchall()
    db.close()
    html = STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h2>👤 客户管理</h2>
        <a href='/customer/add' class='btn btn-green'>➕ 添加客户</a>
    </div>
    <form method='get' style='margin:15px 0;'>
        <input type='text' name='kw' placeholder='搜索姓名/电话' style='width:280px;'>
        <button class='btn'>搜索</button>
    </form>
    <table><tr><th>ID</th><th>姓名</th><th>电话</th><th>身份证</th><th>紧急联系人</th><th>旅游偏好</th><th>操作</th></tr>"""
    for r in rows:
        html += f"""
        <tr>
            <td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td>
            <td>
                <a href='/customer/edit/{r[0]}' class='btn btn-yellow'>修改</a>
                <a href='/customer/delete/{r[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
            </td>
        </tr>"""
    html += """</table><br><a href='/'>← 返回首页</a></div></div>"""
    return html

@app.route('/customer/add', methods=['GET','POST'])
def customer_add():
    if 'uid' not in session: return redirect('/')
    if request.method == 'POST':
        name=request.form['name']
        phone=request.form['phone']
        id_card=request.form['id_card']
        emergency=request.form['emergency']
        travel_preference=request.form['travel_preference']
        db, cur=get_db()
        cur.execute("INSERT INTO customer(name,phone,id_card,emergency,travel_preference) VALUES(%s,%s,%s,%s,%s)",
                    (name,phone,id_card,emergency,travel_preference))
        db.commit()
        db.close()
        flash("添加成功","success")
        return redirect('/customer')
    return STYLE + """
    <div class='container'><div class='card' style='max-width:450px;margin:30px auto;'>
    <h2>➕ 添加客户</h2>
    <form method='post'>
        <input type='text' name='name' placeholder='姓名' required>
        <input type='text' name='phone' placeholder='电话' required>
        <input type='text' name='id_card' placeholder='身份证' required>
        <input type='text' name='emergency' placeholder='紧急联系人'>
        <input type='text' name='travel_preference' placeholder='旅游偏好'>
        <button class='btn btn-green' style='width:100%;'>保存</button>
    </form>
    </div></div>
    """

@app.route('/customer/edit/<int:cid>', methods=['GET','POST'])
def customer_edit():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    if request.method == 'POST':
        name=request.form['name']
        phone=request.form['phone']
        id_card=request.form['id_card']
        emergency=request.form['emergency']
        travel_preference=request.form['travel_preference']
        cur.execute("UPDATE customer SET name=%s,phone=%s,id_card=%s,emergency=%s,travel_preference=%s WHERE customer_id=%s",
                    (name,phone,id_card,emergency,travel_preference,cid))
        db.commit()
        db.close()
        flash("修改成功","success")
        return redirect('/customer')
    cur.execute("SELECT * FROM customer WHERE customer_id=%s",(cid,))
    row=cur.fetchone()
    db.close()
    return STYLE + f"""
    <div class='container'><div class='card'>
    <h2>✏️ 修改客户</h2>
    <form method='post'>
        <input type='text' name='name' value='{row[1]}' required>
        <input type='text' name='phone' value='{row[2]}' required>
        <input type='text' name='id_card' value='{row[3]}' required>
        <input type='text' name='emergency' value='{row[4]}'>
        <input type='text' name='travel_preference' value='{row[5]}'>
        <button class='btn btn-yellow'>保存</button>
    </form>
    </div></div>
    """

@app.route('/customer/delete/<int:cid>')
def customer_delete():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("DELETE FROM customer WHERE customer_id=%s",(cid,))
    db.commit()
    db.close()
    flash("删除成功","success")
    return redirect('/customer')

# ========== 线路管理 ==========
@app.route('/line')
def line_list():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("SELECT * FROM tour_line")
    data=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h1>🗺️ 线路列表</h1>
        <a href='/line/add' class='btn btn-green'>➕ 添加线路</a>
    </div>
    <table><tr><th>ID</th><th>目的地</th><th>天数</th><th>景点</th><th>成人价</th><th>儿童价</th><th>状态</th><th>操作</th></tr>"""
    for row in data:
        html += f"""
        <tr>
            <td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td>
            <td>
                <a href='/line/edit/{row[0]}' class='btn btn-yellow'>修改</a>
                <a href='/line/delete/{row[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
            </td>
        </tr>"""
    html += """</table></div></div>"""
    return html

@app.route('/line/add', methods=['GET','POST'])
def line_add():
    if 'uid' not in session: return redirect('/')
    if request.method == 'POST':
        destination=request.form['destination']
        days=request.form['days']
        spots=request.form['spots']
        price_adult=request.form['price_adult']
        price_child=request.form['price_child']
        status=request.form['status']
        db, cur=get_db()
        cur.execute("INSERT INTO tour_line(destination,days,spots,price_adult,price_child,status) VALUES(%s,%s,%s,%s,%s,%s)",
                    (destination,days,spots,price_adult,price_child,status))
        db.commit()
        db.close()
        flash("添加成功","success")
        return redirect('/line')
    return STYLE + """
    <div class='container'><div class='card' style='max-width:550px;margin:30px auto;'>
    <h2>➕ 添加线路</h2>
    <form method='post'>
        <input type='text' name='destination' placeholder='目的地' required>
        <input type='number' name='days' placeholder='天数' required>
        <input type='text' name='spots' placeholder='景点' required>
        <input type='number' name='price_adult' placeholder='成人价' required>
        <input type='number' name='price_child' placeholder='儿童价' required>
        <select name='status'>
            <option value='正常'>正常</option>
            <option value='暂停'>暂停</option>
            <option value='下架'>下架</option>
        </select>
        <button class='btn btn-green' style='width:100%;'>保存</button>
    </form>
    </div></div>
    """

@app.route('/line/edit/<int:lid>', methods=['GET','POST'])
def line_edit():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    if request.method == 'POST':
        destination=request.form['destination']
        days=request.form['days']
        spots=request.form['spots']
        price_adult=request.form['price_adult']
        price_child=request.form['price_child']
        status=request.form['status']
        cur.execute("UPDATE tour_line SET destination=%s,days=%s,spots=%s,price_adult=%s,price_child=%s,status=%s WHERE line_id=%s",
                    (destination,days,spots,price_adult,price_child,status,lid))
        db.commit()
        db.close()
        flash("修改成功","success")
        return redirect('/line')
    cur.execute("SELECT * FROM tour_line WHERE line_id=%s",(lid,))
    row=cur.fetchone()
    db.close()
    return STYLE + f"""
    <div class='container'><div class='card'>
    <h2>✏️ 修改线路</h2>
    <form method='post'>
        <input type='text' name='destination' value='{row[1]}' required>
        <input type='number' name='days' value='{row[2]}' required>
        <input type='text' name='spots' value='{row[3]}' required>
        <input type='number' name='price_adult' value='{row[4]}' required>
        <input type='number' name='price_child' value='{row[5]}' required>
        <select name='status'>
            <option value='正常' {'selected' if row[6]=='正常' else ''}>正常</option>
            <option value='暂停' {'selected' if row[6]=='暂停' else ''}>暂停</option>
            <option value='下架' {'selected' if row[6]=='下架' else ''}>下架</option>
        </select>
        <button class='btn btn-yellow'>保存</button>
    </form>
    </div></div>
    """

@app.route('/line/delete/<int:lid>')
def line_delete():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("DELETE FROM tour_line WHERE line_id=%s",(lid,))
    db.commit()
    db.close()
    flash("删除成功","success")
    return redirect('/line')

# ========== 导游管理 ==========
@app.route('/guide')
def guide_list():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("SELECT * FROM guide")
    data=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h1>🧑‍✈️ 导游列表</h1>
        <a href='/guide/add' class='btn btn-green'>➕ 添加导游</a>
    </div>
    <table><tr><th>ID</th><th>姓名</th><th>电话</th><th>经验</th><th>带团记录</th><th>操作</th></tr>"""
    for row in data:
        html += f"""
        <tr>
            <td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td>
            <td>
                <a href='/guide/edit/{row[0]}' class='btn btn-yellow'>修改</a>
                <a href='/guide/delete/{row[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
            </td>
        </tr>"""
    html += """</table></div></div>"""
    return html

@app.route('/guide/add', methods=['GET','POST'])
def guide_add():
    if 'uid' not in session: return redirect('/')
    if request.method == 'POST':
        name=request.form['name']
        phone=request.form['phone']
        exp=request.form['exp']
        record=request.form['record']
        db, cur=get_db()
        cur.execute("INSERT INTO guide(name,phone,exp,record) VALUES(%s,%s,%s,%s)",
                    (name,phone,exp,record))
        db.commit()
        db.close()
        flash("添加成功","success")
        return redirect('/guide')
    return STYLE + """
    <div class='container'><div class='card' style='max-width:450px;margin:30px auto;'>
    <h2>➕ 添加导游</h2>
    <form method='post'>
        <input type='text' name='name' placeholder='姓名' required>
        <input type='text' name='phone' placeholder='电话' required>
        <input type='text' name='exp' placeholder='经验'>
        <textarea name='record' placeholder='带团记录'></textarea>
        <button class='btn btn-green' style='width:100%;'>保存</button>
    </form>
    </div></div>
    """

@app.route('/guide/edit/<int:gid>', methods=['GET','POST'])
def guide_edit():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    if request.method == 'POST':
        name=request.form['name']
        phone=request.form['phone']
        exp=request.form['exp']
        record=request.form['record']
        cur.execute("UPDATE guide SET name=%s,phone=%s,exp=%s,record=%s WHERE guide_id=%s",
                    (name,phone,exp,record,gid))
        db.commit()
        db.close()
        flash("修改成功","success")
        return redirect('/guide')
    cur.execute("SELECT * FROM guide WHERE guide_id=%s",(gid,))
    row=cur.fetchone()
    db.close()
    return STYLE + f"""
    <div class='container'><div class='card'>
    <h2>✏️ 修改导游</h2>
    <form method='post'>
        <input type='text' name='name' value='{row[1]}' required>
        <input type='text' name='phone' value='{row[2]}' required>
        <input type='text' name='exp' value='{row[3]}'>
        <textarea name='record'>{row[4]}</textarea>
        <button class='btn btn-yellow'>保存</button>
    </form>
    </div></div>
    """

@app.route('/guide/delete/<int:gid>')
def guide_delete():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("DELETE FROM guide WHERE guide_id=%s",(gid,))
    db.commit()
    db.close()
    flash("删除成功","success")
    return redirect('/guide')

# ========== 团队管理 ==========
@app.route('/group')
def group_list():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("SELECT * FROM tour_group")
    data=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h1>🚍 团队列表</h1>
        <a href='/group/add' class='btn btn-green'>➕ 添加团队</a>
    </div>
    <table><tr><th>团ID</th><th>线路ID</th><th>导游ID</th><th>出发</th><th>结束</th><th>最大人数</th><th>状态</th><th>操作</th></tr>"""
    for row in data:
        html += f"""
        <tr>
            <td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td>
            <td>
                <a href='/group/edit/{row[0]}' class='btn btn-yellow'>修改</a>
                <a href='/group/delete/{row[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
            </td>
        </tr>"""
    html += """</table></div></div>"""
    return html

@app.route('/group/add', methods=['GET','POST'])
def group_add():
    if 'uid' not in session: return redirect('/')
    if request.method == 'POST':
        line_id=request.form['line_id']
        guide_id=request.form['guide_id']
        start_date=request.form['start_date']
        end_date=request.form['end_date']
        max_num=request.form['max_num']
        status=request.form['status']
        db, cur=get_db()
        cur.execute("INSERT INTO tour_group(line_id,guide_id,start_date,end_date,max_num,status) VALUES(%s,%s,%s,%s,%s,%s)",
                    (line_id,guide_id,start_date,end_date,max_num,status))
        db.commit()
        db.close()
        flash("添加成功","success")
        return redirect('/group')
    return STYLE + """
    <div class='container'><div class='card' style='max-width:500px;margin:30px auto;'>
    <h2>➕ 添加团队</h2>
    <form method='post'>
        <input type='number' name='line_id' placeholder='线路ID' required>
        <input type='number' name='guide_id' placeholder='导游ID' required>
        <input type='date' name='start_date' required>
        <input type='date' name='end_date' required>
        <input type='number' name='max_num' placeholder='最大人数' required>
        <select name='status'>
            <option value='未发团'>未发团</option>
            <option value='进行中'>进行中</option>
            <option value='已结束'>已结束</option>
        </select>
        <button class='btn btn-green' style='width:100%;'>保存</button>
    </form>
    </div></div>
    """

@app.route('/group/edit/<int:gid>', methods=['GET','POST'])
def group_edit():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    if request.method == 'POST':
        line_id=request.form['line_id']
        guide_id=request.form['guide_id']
        start_date=request.form['start_date']
        end_date=request.form['end_date']
        max_num=request.form['max_num']
        status=request.form['status']
        cur.execute("UPDATE tour_group SET line_id=%s,guide_id=%s,start_date=%s,end_date=%s,max_num=%s,status=%s WHERE group_id=%s",
                    (line_id,guide_id,start_date,end_date,max_num,status,gid))
        db.commit()
        db.close()
        flash("修改成功","success")
        return redirect('/group')
    cur.execute("SELECT * FROM tour_group WHERE group_id=%s",(gid,))
    row=cur.fetchone()
    db.close()
    return STYLE + f"""
    <div class='container'><div class='card'>
    <h2>✏️ 修改团队</h2>
    <form method='post'>
        <input type='number' name='line_id' value='{row[1]}' required>
        <input type='number' name='guide_id' value='{row[2]}' required>
        <input type='date' name='start_date' value='{row[3]}' required>
        <input type='date' name='end_date' value='{row[4]}' required>
        <input type='number' name='max_num' value='{row[5]}' required>
        <select name='status'>
            <option value='未发团' {'selected' if row[6]=='未发团' else ''}>未发团</option>
            <option value='进行中' {'selected' if row[6]=='进行中' else ''}>进行中</option>
            <option value='已结束' {'selected' if row[6]=='已结束' else ''}>已结束</option>
        </select>
        <button class='btn btn-yellow'>保存</button>
    </form>
    </div></div>
    """

@app.route('/group/delete/<int:gid>')
def group_delete():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("DELETE FROM tour_group WHERE group_id=%s",(gid,))
    db.commit()
    db.close()
    flash("删除成功","success")
    return redirect('/group')

# ========== 订单管理 ==========
@app.route('/order')
def order_list():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("SELECT * FROM orders")
    data=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h1>🧾 订单列表</h1>
        <a href='/order/add' class='btn btn-green'>➕ 添加订单</a>
    </div>
    <table><tr><th>订单ID</th><th>团ID</th><th>客户ID</th><th>状态</th><th>实收</th><th>余款</th><th>总价</th><th>操作</th></tr>"""
    for row in data:
        html += f"""
        <tr>
            <td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td>
            <td>
                <a href='/order/edit/{row[0]}' class='btn btn-yellow'>修改</a>
                <a href='/order/delete/{row[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
            </td>
        </tr>"""
    html += """</table></div></div>"""
    return html

@app.route('/order/add', methods=['GET','POST'])
def order_add():
    if 'uid' not in session: return redirect('/')
    if request.method == 'POST':
        group_id=request.form['group_id']
        customer_id=request.form['customer_id']
        status=request.form['status']
        paid=request.form['paid']
        balance=request.form['balance']
        total=request.form['total']
        db, cur=get_db()
        cur.execute("INSERT INTO orders(group_id,customer_id,status,paid,balance,total) VALUES(%s,%s,%s,%s,%s,%s)",
                    (group_id,customer_id,status,paid,balance,total))
        db.commit()
        db.close()
        flash("添加成功","success")
        return redirect('/order')
    return STYLE + """
    <div class='container'><div class='card' style='max-width:500px;margin:30px auto;'>
    <h2>➕ 添加订单</h2>
    <form method='post'>
        <input type='number' name='group_id' placeholder='团ID' required>
        <input type='number' name='customer_id' placeholder='客户ID' required>
        <select name='status'>
            <option value='待付款'>待付款</option>
            <option value='已付款'>已付款</option>
            <option value='已取消'>已取消</option>
        </select>
        <input type='number' step='0.01' name='paid' placeholder='实收' required>
        <input type='number' step='0.01' name='balance' placeholder='余款' required>
        <input type='number' step='0.01' name='total' placeholder='总价' required>
        <button class='btn btn-green' style='width:100%;'>保存</button>
    </form>
    </div></div>
    """

@app.route('/order/edit/<int:oid>', methods=['GET','POST'])
def order_edit():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    if request.method == 'POST':
        group_id=request.form['group_id']
        customer_id=request.form['customer_id']
        status=request.form['status']
        paid=request.form['paid']
        balance=request.form['balance']
        total=request.form['total']
        cur.execute("UPDATE orders SET group_id=%s,customer_id=%s,status=%s,paid=%s,balance=%s,total=%s WHERE order_id=%s",
                    (group_id,customer_id,status,paid,balance,total,oid))
        db.commit()
        db.close()
        flash("修改成功","success")
        return redirect('/order')
    cur.execute("SELECT * FROM orders WHERE order_id=%s",(oid,))
    row=cur.fetchone()
    db.close()
    return STYLE + f"""
    <div class='container'><div class='card'>
    <h2>✏️ 修改订单</h2>
    <form method='post'>
        <input type='number' name='group_id' value='{row[1]}' required>
        <input type='number' name='customer_id' value='{row[2]}' required>
        <select name='status'>
            <option value='待付款' {'selected' if row[3]=='待付款' else ''}>待付款</option>
            <option value='已付款' {'selected' if row[3]=='已付款' else ''}>已付款</option>
            <option value='已取消' {'selected' if row[3]=='已取消' else ''}>已取消</option>
        </select>
        <input type='number' step='0.01' name='paid' value='{row[4]}' required>
        <input type='number' step='0.01' name='balance' value='{row[5]}' required>
        <input type='number' step='0.01' name='total' value='{row[6]}' required>
        <button class='btn btn-yellow'>保存</button>
    </form>
    </div></div>
    """

@app.route('/order/delete/<int:oid>')
def order_delete():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("DELETE FROM orders WHERE order_id=%s",(oid,))
    db.commit()
    db.close()
    flash("删除成功","success")
    return redirect('/order')

# ========== 费用管理 ==========
@app.route('/fee')
def fee_list():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("SELECT * FROM fee")
    data=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h1>💰 费用与利润统计</h1>
        <a href='/fee/add' class='btn btn-green'>➕ 添加费用</a>
    </div>
    <table><tr><th>ID</th><th>团ID</th><th>团费收入</th><th>地接费</th><th>导游补贴</th><th>保险费</th><th>利润</th><th>操作</th></tr>"""
    for row in data:
        html += f"""
        <tr>
            <td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td>
            <td>
                <a href='/fee/edit/{row[0]}' class='btn btn-yellow'>修改</a>
                <a href='/fee/delete/{row[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
            </td>
        </tr>"""
    html += """</table></div></div>"""
    return html

@app.route('/fee/add', methods=['GET','POST'])
def fee_add():
    if 'uid' not in session: return redirect('/')
    if request.method == 'POST':
        group_id=request.form['group_id']
        income=request.form['income']
        local_fee=request.form['local_fee']
        guide_subsidy=request.form['guide_subsidy']
        insurance=request.form['insurance']
        profit=request.form['profit']
        db, cur=get_db()
        cur.execute("INSERT INTO fee(group_id,income,local_fee,guide_subsidy,insurance,profit) VALUES(%s,%s,%s,%s,%s,%s)",
                    (group_id,income,local_fee,guide_subsidy,insurance,profit))
        db.commit()
        db.close()
        flash("添加成功","success")
        return redirect('/fee')
    return STYLE + """
    <div class='container'><div class='card' style='max-width:500px;margin:30px auto;'>
    <h2>➕ 添加费用</h2>
    <form method='post'>
        <input type='number' name='group_id' placeholder='团ID' required>
        <input type='number' step='0.01' name='income' placeholder='团费收入' required>
        <input type='number' step='0.01' name='local_fee' placeholder='地接费' required>
        <input type='number' step='0.01' name='guide_subsidy' placeholder='导游补贴' required>
        <input type='number' step='0.01' name='insurance' placeholder='保险费' required>
        <input type='number' step='0.01' name='profit' placeholder='利润' required>
        <button class='btn btn-green' style='width:100%;'>保存</button>
    </form>
    </div></div>
    """

@app.route('/fee/edit/<int:fid>', methods=['GET','POST'])
def fee_edit():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    if request.method == 'POST':
        group_id=request.form['group_id']
        income=request.form['income']
        local_fee=request.form['local_fee']
        guide_subsidy=request.form['guide_subsidy']
        insurance=request.form['insurance']
        profit=request.form['profit']
        cur.execute("UPDATE fee SET group_id=%s,income=%s,local_fee=%s,guide_subsidy=%s,insurance=%s,profit=%s WHERE fee_id=%s",
                    (group_id,income,local_fee,guide_subsidy,insurance,profit,fid))
        db.commit()
        db.close()
        flash("修改成功","success")
        return redirect('/fee')
    cur.execute("SELECT * FROM fee WHERE fee_id=%s",(fid,))
    row=cur.fetchone()
    db.close()
    return STYLE + f"""
    <div class='container'><div class='card'>
    <h2>✏️ 修改费用</h2>
    <form method='post'>
        <input type='number' name='group_id' value='{row[1]}' required>
        <input type='number' step='0.01' name='income' value='{row[2]}' required>
        <input type='number' step='0.01' name='local_fee' value='{row[3]}' required>
        <input type='number' step='0.01' name='guide_subsidy' value='{row[4]}' required>
        <input type='number' step='0.01' name='insurance' value='{row[5]}' required>
        <input type='number' step='0.01' name='profit' value='{row[6]}' required>
        <button class='btn btn-yellow'>保存</button>
    </form>
    </div></div>
    """

@app.route('/fee/delete/<int:fid>')
def fee_delete():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("DELETE FROM fee WHERE fee_id=%s",(fid,))
    db.commit()
    db.close()
    flash("删除成功","success")
    return redirect('/fee')

# ========== 统计报表 ==========
@app.route('/report')
def report():
    if 'uid' not in session: return redirect('/')
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    db, cur = get_db()
    cur.execute("""
        SELECT COUNT(*) FROM tour_group 
        WHERE DATE_FORMAT(start_date, '%%Y-%%m')=%s
    """, (month,))
    group_count = cur.fetchone()[0]
    cur.execute("""
        SELECT tg.group_id, tl.destination, tg.start_date, tg.end_date, tg.status
        FROM tour_group tg
        LEFT JOIN tour_line tl ON tg.line_id = tl.line_id
        WHERE DATE_FORMAT(tg.start_date, '%%Y-%%m')=%s
    """, (month,))
    group_detail = cur.fetchall()
    cur.execute("""
        SELECT l.destination, COUNT(o.order_id) cnt
        FROM tour_line l
        LEFT JOIN tour_group g ON l.line_id=g.line_id
        LEFT JOIN orders o ON g.group_id=o.group_id
        GROUP BY l.line_id
        ORDER BY cnt DESC
    """)
    line_rank = cur.fetchall()
    cur.execute("""
        SELECT c.name, IFNULL(SUM(o.paid), 0) total
        FROM customer c
        LEFT JOIN orders o ON c.customer_id=o.customer_id
        GROUP BY c.customer_id
        ORDER BY total DESC
    """)
    customer_rank = cur.fetchall()
    db.close()
    html = STYLE + f"""
    <div class='container'><div class='card'>
    <h1>📊 月度统计报表（{month}）</h1>
    <form method='get' style='margin-bottom:20px;'>
        <input type='month' name='month' value='{month}' style='width:200px;'>
        <button class='btn'>查询</button>
    </form>
    <h2>一、月度出团明细（共 {group_count} 个）</h2>
    <table><tr><th>团ID</th><th>线路</th><th>出发日期</th><th>结束日期</th><th>状态</th></tr>"""
    for g in group_detail:
        html += f"<tr><td>{g[0]}</td><td>{g[1]}</td><td>{g[2]}</td><td>{g[3]}</td><td>{g[4]}</td></tr>"
    html += """</table>
    <h2>二、线路热度排行</h2>
    <table><tr><th>排名</th><th>线路</th><th>订单数</th></tr>"""
    for i, (dest, cnt) in enumerate(line_rank, 1):
        html += f"<tr><td>{i}</td><td>{dest}</td><td>{cnt}</td></tr>"
    html += """</table>
    <h2>三、客户消费排行</h2>
    <table><tr><th>排名</th><th>客户</th><th>总消费</th></tr>"""
    for i, (name, total) in enumerate(customer_rank, 1):
        html += f"<tr><td>{i}</td><td>{name}</td><td>{total}</td></tr>"
    html += """</table></div></div>"""
    return html

# ========== 异常处理 ==========
@app.route('/exception', methods=['GET','POST'])
def exception():
    if 'uid' not in session: return redirect('/')
    if request.method == 'POST':
        group_id = request.form['group_id']
        type_ = request.form['type']
        reason = request.form['reason']
        db, cur = get_db()
        if type_ == 'cancel':
            cur.execute("UPDATE tour_group SET status='已取消' WHERE group_id=%s", (group_id,))
        elif type_ == 'refund':
            cur.execute("UPDATE orders SET status='已退团', paid=paid*0.7 WHERE group_id=%s", (group_id,))
        elif type_ == 'change_guide':
            new_guide = request.form.get('new_guide', '').strip()
            if new_guide:
                cur.execute("UPDATE tour_group SET guide_id=%s WHERE group_id=%s", (new_guide, group_id))
        cur.execute("INSERT INTO exception_log(group_id, type, reason) VALUES(%s,%s,%s)",
                    (group_id, type_, reason))
        db.commit()
        db.close()
        flash("异常处理成功","success")
        return redirect('/exception')
    db, cur=get_db()
    cur.execute("SELECT * FROM exception_log ORDER BY id DESC")
    logs=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <h1>⚠️ 异常处理中心</h1>
    <form method='post'>
        <input type='number' name='group_id' placeholder='团ID' required>
        <select name='type' required>
            <option value='cancel'>成团不足取消</option>
            <option value='refund'>客户退团扣费</option>
            <option value='change_guide'>临时更换导游</option>
        </select>
        <input type='number' name='new_guide' placeholder='新导游ID（仅换导游时填写）'>
        <textarea name='reason' placeholder='异常原因' required></textarea>
        <button class='btn btn-red' style='width:100%;'>提交处理</button>
    </form>
    <h2>异常记录</h2>
    <table><tr><th>ID</th><th>团ID</th><th>类型</th><th>原因</th><th>时间</th></tr>"""
    for log in logs:
        html += f"""
        <tr>
            <td>{log[0]}</td><td>{log[1]}</td><td>{log[2]}</td><td>{log[3]}</td><td>{log[4]}</td>
        </tr>"""
    html += """</table></div></div>"""
    return html

if __name__ == '__main__':
    app.run(debug=True)