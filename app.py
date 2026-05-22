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
        background: rgba(255, 255, 255, 0.92);
        padding:26px;
        border-radius:14px;
        box-shadow:0 4px 15px rgba(0,0,0,0.08);
        margin-bottom:22px;
    }
    h1, h2 { color:#22; margin-bottom:18px; }
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
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
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

# 主页菜单
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

# 导游我的团队
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
    """, (session["username"],))
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
    html += "</table><br><a href='/index'>← 返回首页</a></div></div>"
    return html

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
    html += """</table><br><a href='/index'>← 返回首页</a></div></div>"""
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
def customer_edit(cid):
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
def customer_delete(cid):
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("DELETE FROM customer WHERE customer_id=%s",(cid,))
    db.commit()
    db.close()
    flash("删除成功","success")
    return redirect('/customer')

# ========== 线路管理（已统一风格+返回/index） ==========
@app.route('/line')
def line_list():
    if 'uid' not in session:
        return redirect('/')
    db, cur = get_db()
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        cur.execute("SELECT * FROM tour_line WHERE destination LIKE %s", (f'%{keyword}%',))
    else:
        cur.execute("SELECT * FROM tour_line")
    lines = cur.fetchall()
    db.close()
    return STYLE + """
    <div class='container'><div class='card'>
        <div style='display:flex;justify-content:space-between;align-items:center;'>
            <h2>🗺️ 线路管理</h2>
            <a href='/line/add' class='btn btn-green'>➕ 添加线路</a>
        </div>
        <form method='get' style='margin:15px 0;'>
            <input type='text' name='keyword' placeholder='搜索目的地' value='""" + keyword + """' style='width:280px;'>
            <button class='btn'>搜索</button>
        </form>
        <table>
            <tr><th>ID</th><th>目的地</th><th>天数</th><th>景点</th><th>成人价</th><th>儿童价</th><th>状态</th><th>操作</th></tr>""" + "".join([
        f"""
            <tr>
                <td>{line[0]}</td><td>{line[1]}</td><td>{line[2]}</td><td>{line[3]}</td><td>{line[4]}</td><td>{line[5]}</td><td>{line[6]}</td>
                <td>
                    <a href='/line/edit/{line[0]}' class='btn btn-yellow'>修改</a>
                    <a href='/line/delete/{line[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
                </td>
            </tr>""" for line in lines
    ]) + """
        </table>
        <br><a href='/index'>← 返回首页</a>
    </div></div>
    """

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

@app.route('/line/edit/<int:lid>', methods=['GET', 'POST'])
def line_edit(lid):
    if 'uid' not in session:
        return redirect('/')
    db, cur = get_db()
    if request.method == 'POST':
        destination = request.form['destination']
        days = request.form['days']
        spots = request.form['spots']
        price_adult = request.form['price_adult']
        price_child = request.form['price_child']
        status = request.form['status']
        cur.execute(
            "UPDATE tour_line SET destination=%s, days=%s, spots=%s, price_adult=%s, price_child=%s, status=%s WHERE line_id=%s",
            (destination, days, spots, price_adult, price_child, status, lid)
        )
        db.commit()
        db.close()
        flash("修改成功","success")
        return redirect('/line')
    cur.execute("SELECT * FROM tour_line WHERE line_id=%s", (lid,))
    row = cur.fetchone()
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
            <option value='正常' {'selected' if row[6] == '正常' else ''}>正常</option>
            <option value='暂停' {'selected' if row[6] == '暂停' else ''}>暂停</option>
            <option value='下架' {'selected' if row[6] == '下架' else ''}>下架</option>
        </select>
        <button class='btn btn-yellow' style='width:100%;'>保存修改</button>
    </form>
</div></div>
"""

@app.route('/line/delete/<int:lid>')
def line_delete(lid):
    if 'uid' not in session:
        return redirect('/')
    db, cur = get_db()
    
    # 先删除使用了这条线路的所有团队
    cur.execute("DELETE FROM tour_group WHERE line_id=%s", (lid,))
    
    # 再删除线路
    cur.execute("DELETE FROM tour_line WHERE line_id=%s", (lid,))
    
    db.commit()
    db.close()
    flash("线路及关联团队已删除", "success")
    return redirect('/line')

# ========== 导游管理 ==========
@app.route('/guide')
def guide_list():
    if 'uid' not in session: return redirect('/')
    kw = request.args.get("kw", "")
    db, cur=get_db()
    if kw:
        cur.execute("SELECT * FROM guide WHERE name LIKE %s OR phone LIKE %s", (f"%{kw}%", f"%{kw}%"))
    else:
        cur.execute("SELECT * FROM guide")
    data=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h2>🧑‍✈️ 导游管理</h2>
        <a href='/guide/add' class='btn btn-green'>➕ 添加导游</a>
    </div>
    <form method='get' style='margin:15px 0;'>
        <input type='text' name='kw' placeholder='搜索导游姓名/电话' value='""" + kw + """' style='width:280px;'>
        <button class='btn'>搜索</button>
    </form>
    <table><tr><th>ID</th><th>姓名</th><th>电话</th><th>从业经验</th><th>带团履历</th><th>操作</th></tr>"""
    for row in data:
        html += f"""
        <tr>
            <td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td>
            <td>
                <a href='/guide/edit/{row[0]}' class='btn btn-yellow'>修改</a>
                <a href='/guide/delete/{row[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
            </td>
        </tr>"""
    html += """</table><br><a href='/index'>← 返回首页</a></div></div>"""
    return html

@app.route('/guide/add', methods=['GET','POST'])
def guide_add():
    if 'uid' not in session: return redirect('/')
    if request.method == 'POST':
        name=request.form['name']
        phone=request.form['phone']
        experience=request.form['experience']
        team_records=request.form['team_records']
        db, cur=get_db()
        cur.execute("INSERT INTO guide(name, phone, experience, team_records) VALUES(%s, %s, %s, %s)",
                    (name, phone, experience, team_records))
        db.commit()
        db.close()
        flash("添加成功","success")
        return redirect('/guide')
    return STYLE + """
    <div class='container'><div class='card' style='max-width:450px;margin:30px auto;'>
    <h2>➕ 添加导游</h2>
    <form method='post'>
        <input type='text' name='name' placeholder='姓名' required>
        <input type='text' name='phone' placeholder='联系电话' required>
        <input type='text' name='experience' placeholder='从业经验'>
        <textarea name='team_records' placeholder='带团履历'></textarea>
        <button class='btn btn-green' style='width:100%;'>保存提交</button>
    </form>
    </div></div>
    """

@app.route('/guide/edit/<int:gid>', methods=['GET','POST'])
def guide_edit(gid):
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    if request.method == 'POST':
        name=request.form['name']
        phone=request.form['phone']
        experience=request.form['experience']
        team_records=request.form['team_records']
        cur.execute("UPDATE guide SET name=%s, phone=%s, experience=%s, team_records=%s WHERE guide_id=%s",
                    (name, phone, experience, team_records, gid))
        db.commit()
        db.close()
        flash("修改成功","success")
        return redirect('/guide')
    cur.execute("SELECT * FROM guide WHERE guide_id=%s",(gid,))
    row=cur.fetchone()
    db.close()
    return STYLE + f"""
    <div class='container'><div class='card'>
    <h2>✏️ 修改导游信息</h2>
    <form method='post'>
        <input type='text' name='name' value='{row[1]}' required>
        <input type='text' name='phone' value='{row[2]}' required>
        <input type='text' name='experience' value='{row[3]}'>
        <textarea name='team_records'>{row[4]}</textarea>
        <button class='btn btn-yellow'>保存修改</button>
    </form>
    </div></div>
    """

@app.route('/guide/delete/<int:gid>')
def guide_delete(gid):
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("DELETE FROM guide WHERE guide_id=%s",(gid,))
    db.commit()
    db.close()
    flash("删除成功","success")
    return redirect('/guide')

# ========== 团队管理 ==========
@app.route('/group')
@app.route('/group')
def group_list():
    if 'uid' not in session: return redirect('/')

    # ===================== 只加这一段 =====================
    kw = request.args.get("kw", "")
    # ======================================================

    db, cur=get_db()

    # ===================== 只加这一段 =====================
    if kw:
        cur.execute("SELECT * FROM tour_group WHERE group_id LIKE %s OR line_id LIKE %s OR guide_id LIKE %s OR status LIKE %s", (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%"))
    else:
    # ======================================================

        cur.execute("SELECT * FROM tour_group")
    data=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h2>🚍 团队管理</h2>
        <a href='/group/add' class='btn btn-green'>➕ 添加团队</a>
    </div>

    <!-- ==================== 只加这一行搜索框 ==================== -->
    <form method='get' style='margin:15px 0;'>
        <input type='text' name='kw' placeholder='搜索团队' style='width:280px;'>
        <button class='btn'>搜索</button>
    </form>
    <!-- =========================================================== -->

    <table><tr><th>团ID</th><th>线路编号</th><th>导游编号</th><th>出发日期</th><th>结束日期</th><th>最大人数</th><th>团队状态</th><th>操作</th></tr>"""
    for row in data:
        html += f"""
        <tr>
            <td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td>
            <td>
                <a href='/group/edit/{row[0]}' class='btn btn-yellow'>修改</a>
                <a href='/group/delete/{row[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
            </td>
        </tr>"""
    html += """</table><br><a href='/index'>← 返回首页</a></div></div>"""
    return html

@app.route('/group/add', methods=['GET','POST'])
def group_add():
    if 'uid' not in session:
        return redirect('/')
    db, cur = get_db()
    # 先获取所有可用的线路和导游ID，给下拉框用
    cur.execute("SELECT line_id FROM tour_line")
    lines = cur.fetchall()
    cur.execute("SELECT guide_id FROM guide")
    guides = cur.fetchall()
    if request.method == 'POST':
        line_id = request.form['line_id']
        guide_id = request.form['guide_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        max_num = request.form['max_num']
        status = request.form['status']
        
        # 关键校验：检查ID是否存在
        cur.execute("SELECT * FROM tour_line WHERE line_id=%s", (line_id,))
        if not cur.fetchone():
            flash("线路ID不存在，请先添加线路！", "danger")
            return redirect('/group/add')
        cur.execute("SELECT * FROM guide WHERE guide_id=%s", (guide_id,))
        if not cur.fetchone():
            flash("导游ID不存在，请先添加导游！", "danger")
            return redirect('/group/add')
        
        cur.execute("""
            INSERT INTO tour_group(line_id, guide_id, start_date, end_date, max_num, status)
            VALUES(%s, %s, %s, %s, %s, %s)
        """, (line_id, guide_id, start_date, end_date, max_num, status))
        db.commit()
        db.close()
        flash("团队添加成功！", "success")
        return redirect('/group')
    
    # 给下拉框生成选项
    line_options = "".join([f"<option value='{l[0]}'>{l[0]}</option>" for l in lines])
    guide_options = "".join([f"<option value='{g[0]}'>{g[0]}</option>" for g in guides])
    
    return STYLE + f"""
    <div class='container'><div class='card' style='max-width:500px;margin:30px auto;'>
    <h2>➕ 添加旅游团队</h2>
    <form method='post'>
        <select name='line_id' required>
            <option value=''>请选择线路ID</option>
            {line_options}
        </select>
        <select name='guide_id' required>
            <option value=''>请选择导游ID</option>
            {guide_options}
        </select>
        <input type='date' name='start_date' required>
        <input type='date' name='end_date' required>
        <input type='number' name='max_num' placeholder='团队最大人数' required>
        <select name='status'>
            <option value='未发团'>未发团</option>
            <option value='进行中'>进行中</option>
            <option value='已结束'>已结束</option>
        </select>
        <button class='btn btn-green' style='width:100%;'>保存提交</button>
    </form>
    </div></div>
    """

@app.route('/group/edit/<int:gid>', methods=['GET','POST'])
def group_edit(gid):
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
    <h2>✏️ 修改团队信息</h2>
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
        <button class='btn btn-yellow'>保存修改</button>
    </form>
    </div></div>
    """

@app.route('/group/delete/<int:gid>')
def group_delete(gid):
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
    kw = request.args.get("kw", "")
    db, cur=get_db()
    if kw:
        cur.execute("SELECT * FROM orders WHERE group_id LIKE %s OR customer_id LIKE %s", (f"%{kw}%", f"%{kw}%"))
    else:
        cur.execute("SELECT * FROM orders")
    data=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h2>🧾 订单管理</h2>
        <a href='/order/add' class='btn btn-green'>➕ 添加订单</a>
    </div>
    <form method='get' style='margin:15px 0;'>
        <input type='text' name='kw' placeholder='搜索团ID/客户ID' value='""" + kw + """' style='width:280px;'>
        <button class='btn'>搜索</button>
    </form>
    <table><tr><th>订单ID</th><th>团ID</th><th>客户ID</th><th>订单状态</th><th>已收金额</th><th>剩余尾款</th><th>订单总价</th><th>操作</th></tr>"""
    for row in data:
        if row[3] == 0:
            status_text = "待付款"
        elif row[3] == 1:
            status_text = "已付款"
        else:
            status_text = "已取消"
        html += f"""
        <tr>
            <td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{status_text}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td>
            <td>
                <a href='/order/edit/{row[0]}' class='btn btn-yellow'>修改</a>
                <a href='/order/delete/{row[0]}' class='btn btn-red' onclick='return confirm("确定删除？")'>删除</a>
            </td>
        </tr>"""
    html += """</table><br><a href='/index'>← 返回首页</a></div></div>"""
    return html

@app.route('/order/add', methods=['GET','POST'])
def order_add():
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("SELECT customer_id, name FROM customer")
    customers = cur.fetchall()
    cur.execute("SELECT group_id FROM tour_group")
    groups = cur.fetchall()
    db.close()
    if request.method == 'POST':
        group_id=request.form['group_id']
        customer_id=request.form['customer_id']
        order_status=request.form['order_status']
        received_amount=request.form['received_amount']
        balance=request.form['balance']
        total_price=request.form['total_price']
        db, cur=get_db()
        cur.execute("""
            INSERT INTO orders(group_id, customer_id, order_status, received_amount, balance, total_price)
            VALUES(%s, %s, %s, %s, %s, %s)
        """, (group_id, customer_id, order_status, received_amount, balance, total_price))
        db.commit()
        db.close()
        flash("添加成功","success")
        return redirect('/order')
    customer_options = "".join([f"<option value='{cid}'>{cid} - {name}</option>" for cid, name in customers])
    group_options = "".join([f"<option value='{gid}'>{gid}</option>" for gid, in groups])
    return STYLE + f"""
    <div class='container'><div class='card' style='max-width:500px;margin:30px auto;'>
    <h2>➕ 新增旅游订单</h2>
    <form method='post'>
        <select name='group_id' required>
            <option value=''>请选择团队</option>
            {group_options}
        </select>
        <select name='customer_id' required>
            <option value=''>请选择客户</option>
            {customer_options}
        </select>
        <select name='order_status'>
            <option value='0'>待付款</option>
            <option value='1'>已付款</option>
            <option value='2'>已取消</option>
        </select>
        <input type='number' step='0.01' name='received_amount' placeholder='已收金额' required>
        <input type='number' step='0.01' name='balance' placeholder='剩余尾款' required>
        <input type='number' step='0.01' name='total_price' placeholder='订单总金额' required>
        <button class='btn btn-green' style='width:100%;'>保存提交</button>
    </form>
    </div></div>
    """

@app.route('/order/edit/<int:oid>', methods=['GET','POST'])
def order_edit(oid):
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("SELECT customer_id, name FROM customer")
    customers = cur.fetchall()
    cur.execute("SELECT group_id FROM tour_group")
    groups = cur.fetchall()
    db.close()
    if request.method == 'POST':
        group_id=request.form['group_id']
        customer_id=request.form['customer_id']
        order_status=request.form['order_status']
        received_amount=request.form['received_amount']
        balance=request.form['balance']
        db, cur = get_db()
        total_price=request.form['total_price']
        cur.execute("""
            UPDATE orders SET group_id=%s, customer_id=%s, order_status=%s, received_amount=%s, balance=%s, total_price=%s
            WHERE order_id=%s
        """, (group_id, customer_id, order_status, received_amount, balance, total_price, oid))
        db.commit()
        db.close()
        flash("修改成功","success")
        return redirect('/order')
    cur.execute("SELECT * FROM orders WHERE order_id=%s",(oid,))
    row=cur.fetchone()
    db.close()
    customer_options = "".join([f"<option value='{cid}' {'selected' if cid == row[2] else ''}>{cid} - {name}</option>" for cid, name in customers])
    group_options = "".join([f"<option value='{gid[0]}' {'selected' if gid[0] == row[1] else ''}>{gid[0]}</option>" for gid, in groups])
    return STYLE + f"""
    <div class='container'><div class='card'>
    <h2>✏️ 修改订单信息</h2>
    <form method='post'>
        <select name='group_id' required>
            {group_options}
        </select>
        <select name='customer_id' required>
            {customer_options}
        </select>
        <select name='order_status'>
            <option value='0' {'selected' if row[3]==0 else ''}>待付款</option>
            <option value='1' {'selected' if row[3]==1 else ''}>已付款</option>
            <option value='2' {'selected' if row[3]==2 else ''}>已取消</option>
        </select>
        <input type='number' step='0.01' name='received_amount' value='{row[4]}' required>
        <input type='number' step='0.01' name='balance' value='{row[5]}' required>
        <input type='number' step='0.01' name='total_price' value='{row[6]}' required>
        <button class='btn btn-yellow'>保存修改</button>
    </form>
    </div></div>
    """

@app.route('/fee/add', methods=['GET','POST'])
def fee_add():
    if 'uid' not in session:
        return redirect('/')
    if request.method == 'POST':
        group_id = request.form['group_id']
        income = request.form['income']
        land_fee = request.form['land_fee']
        guide_subsidy = request.form['guide_subsidy']
        insurance_fee = request.form['insurance_fee']
        profit = request.form['profit']
        db, cur = get_db()
        cur.execute("""
            INSERT INTO fee(group_id, income, land_fee, guide_subsidy, insurance_fee, profit)
            VALUES(%s,%s,%s,%s,%s,%s)
        """, (group_id, income, land_fee, guide_subsidy, insurance_fee, profit))
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
        <input type='number' step='0.01' name='land_fee' placeholder='地接费' required>
        <input type='number' step='0.01' name='guide_subsidy' placeholder='导游补贴' required>
        <input type='number' step='0.01' name='insurance_fee' placeholder='保险费' required>
        <input type='number' step='0.01' name='profit' placeholder='利润' required>
        <button class='btn btn-green' style='width:100%;'>保存</button>
    </form>
    </div></div>
    """

@app.route('/order/delete/<int:oid>')
def order_delete(oid):
    if 'uid' not in session: return redirect('/')
    db, cur=get_db()
    cur.execute("DELETE FROM orders WHERE order_id=%s",(oid,))
    db.commit()
    db.close()
    flash("删除成功","success")
    return redirect('/order')

# ========== 费用管理 ==========
# ========== 费用管理（已100%修好） ==========
@app.route('/fee')
def fee_list():
    if 'uid' not in session: return redirect('/')
    db, cur = get_db()
    cur.execute("SELECT * FROM fee")
    data=cur.fetchall()
    db.close()
    html=STYLE + """
    <div class='container'><div class='card'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <h2>💰 费用与利润统计</h2>
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
    html += """</table><br><a href='/index'>← 返回首页</a></div></div>"""
    return html


@app.route('/fee/edit/<int:fid>', methods=['GET','POST'])
def fee_edit(fid):
     
     if 'uid' not in session: 
         return redirect('/')
     
     db, cur = get_db()

     if request.method == 'POST':
        group_id = request.form['group_id']
        income = request.form['income']
        land_fee = request.form['land_fee']
        guide_subsidy = request.form['guide_subsidy']
        insurance_fee = request.form['insurance_fee']
        profit = request.form['profit']
        cur.execute("UPDATE fee SET group_id=%s, income=%s, land_fee=%s, guide_subsidy=%s, insurance_fee=%s, profit=%s WHERE fee_id=%s", (group_id, income, land_fee, guide_subsidy, insurance_fee, profit, fid))
        db.commit()
        db.close()
        flash("修改成功", "success")
        return redirect('/fee')
     
     
     cur.execute("SELECT * FROM fee WHERE fee_id=%s", (fid,))
     row = cur.fetchone()
     db.close()
     return STYLE + f"""
    <div class='container'><div class='card'>
    <h2>✏️ 修改费用</h2>
    <form method='post'>
        <input type='number' name='group_id' value='{row[1]}' required>
        <input type='number' step='0.01' name='income' value='{row[2]}' required>
        <input type='number' step='0.01' name='land_fee' value='{row[3]}' required>
        <input type='number' step='0.01' name='guide_subsidy' value='{row[4]}' required>
        <input type='number' step='0.01' name='insurance_fee' value='{row[5]}' required>
        <input type='number' step='0.01' name='profit' value='{row[6]}' required>
        <button class='btn btn-yellow'>保存</button>
    </form>
    </div></div>
    """

@app.route('/fee/delete/<int:fid>')
def fee_delete(fid):
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
    html += """</table><br><a href='/index'>← 返回首页</a></div></div>"""
    return html

# ========== 异常处理 ==========
# ========== 异常处理（完整版：状态 + 标记已处理 + 筛选） ==========
@app.route('/exception', methods=['GET','POST'])
def exception():
    if 'uid' not in session:
        return redirect('/')

    # ==============================================
    # 1. 提交异常（原来的功能）
    # ==============================================
    if request.method == 'POST':
        group_id = request.form['group_id']
        type_ = request.form['type']
        reason = request.form['reason']
        new_guide = request.form.get('new_guide', '').strip()

        db, cur = get_db()

        if type_ == 'cancel':
            cur.execute("UPDATE tour_group SET status='已取消' WHERE group_id=%s", (group_id,))
        elif type_ == 'refund':
            cur.execute("UPDATE orders SET order_status='已退团', received_amount=received_amount*0.7 WHERE group_id=%s", (group_id,))
        elif type_ == 'change_guide' and new_guide:
            cur.execute("UPDATE tour_group SET guide_id=%s WHERE group_id=%s", (new_guide, group_id))

        # 插入日志，默认未处理
        cur.execute("""
            INSERT INTO exception_log(group_id, type, reason, status)
            VALUES(%s, %s, %s, '未处理')
        """, (group_id, type_, reason))

        db.commit()
        db.close()
        flash("异常提交成功", "success")
        return redirect('/exception')

    # ==============================================
    # 2. 标记为已处理（按钮功能）
    # ==============================================
    if request.args.get('mark_done'):
        log_id = request.args.get('mark_done')
        db, cur = get_db()
        cur.execute("UPDATE exception_log SET status='已处理' WHERE id=%s", (log_id,))
        db.commit()
        db.close()
        flash("已标记为已处理 ✅", "success")
        return redirect('/exception')

    # ==============================================
    # 3. 筛选功能（全部 / 未处理 / 已处理）
    # ==============================================
    filter_status = request.args.get('filter', 'all')

    db, cur = get_db()
    if filter_status == '未处理':
        cur.execute("SELECT * FROM exception_log WHERE status='未处理' ORDER BY id DESC")
    elif filter_status == '已处理':
        cur.execute("SELECT * FROM exception_log WHERE status='已处理' ORDER BY id DESC")
    else:
        cur.execute("SELECT * FROM exception_log ORDER BY id DESC")

    logs = cur.fetchall()
    db.close()

    # ==============================================
    # 页面输出
    # ==============================================
    html = STYLE + """
    <div class='container'><div class='card'>
    <h1>⚠️ 异常处理中心</h1>

    <!-- 筛选菜单 -->
    <div style="margin:15px 0; display:flex; gap:10px;">
        <a href="/exception?filter=all" class="btn">全部</a>
        <a href="/exception?filter=未处理" class="btn btn-yellow">未处理</a>
        <a href="/exception?filter=已处理" class="btn btn-green">已处理</a>
    </div>

    <!-- 提交表单 -->
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
    <table>
        <tr>
            <th>ID</th>
            <th>团ID</th>
            <th>类型</th>
            <th>原因</th>
            <th>时间</th>
            <th>状态</th>
            <th>操作</th>
        </tr>"""

    for log in logs:
        log_id = log[0]
        group_id = log[1]
        type_name = log[2]
        reason = log[3]
        create_time = log[5] if len(log) >= 6 else ""
        status = log[4] if len(log) >= 5 else "未处理"

        # 状态颜色
        if status == "已处理":
            status_html = f"<span style='color:green; font-weight:bold;'>{status}</span>"
            btn_html = ""  # 已处理 → 不显示按钮
        else:
            status_html = f"<span style='color:red; font-weight:bold;'>{status}</span>"
            btn_html = f'''
                <a href="/exception?mark_done={log_id}" 
                    class="btn btn-green"
                    onclick="return confirm('确定标记为已处理？')">
                    标记已处理
                </a>
            '''

        html += f"""
        <tr>
            <td>{log_id}</td>
            <td>{group_id}</td>
            <td>{type_name}</td>
            <td>{reason}</td>
            <td>{create_time}</td>
            <td>{status_html}</td>
            <td>{btn_html}</td>
        </tr>"""

    html += """
    </table>
    <br>
    <a href='/index'>← 返回首页</a>
    </div></div>
    """
    return html

# 退出登录
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)