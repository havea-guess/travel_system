from flask import Flask, request, send_from_directory
import os
import pymysql

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 允许访问桌面图片
@app.route('/desktop/<path:filename>')
def serve_desktop(filename):
    return send_from_directory(r"C:\Users\要不你猜猜？\OneDrive\桌面", filename)

# 数据库连接
def get_db():
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="travel_system",
        charset="utf8"
    )
    return db, db.cursor()

# 全局样式
STYLE = """
<style>
    * { margin:0; padding:0; box-sizing:border-box; font-family: "Microsoft YaHei", sans-serif; }
    body { 
         background: #f0f2f5 url('static/picture2.jpg') no-repeat center center / cover;
        padding: 20px; 
    }
    .container { max-width: 1100px; margin: auto; }
    .card { 
        background: rgba(255,255,255,0.95); 
        padding:26px; 
        border-radius:14px; 
        box-shadow:0 4px 15px rgba(0,0,0,0.08); 
        margin-bottom:22px; 
        backdrop-filter: blur(4px);
    }
    h1 { 
        font-size:24px; 
        color:#222; 
        margin-bottom:18px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    table { width:100%; border-collapse: collapse; background:#fff; border-radius:8px; overflow:hidden; }
    th { background:#409eff; color:white; padding:12px; text-align:left; }
    td { padding:11px 12px; border-bottom:1px solid #eee; }
    tr:hover { background:#f9f9f9; }
    a { color:#409eff; text-decoration:none; }
    a:hover { text-decoration: underline; }
    .nav { 
        display:flex; 
        gap:12px; 
        margin-bottom:20px; 
        flex-wrap:wrap; 
        justify-content: center;
    }
    .nav a { 
        background:#409eff; 
        color:white; 
        padding:10px 16px; 
        border-radius:8px; 
        font-weight:bold;
    }
    .nav a:hover { background:#337ecc; text-decoration:none; }
    .banner img {
        width: 100%;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .btn {
        background:#409eff;
        color:white;
        padding:8px 14px;
        border-radius:6px;
        text-decoration:none;
    }
    input, select, textarea {
        width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box;
        font-size:14px;
    }
    textarea {
        resize:none;
        min-height:80px;
    }
</style>
"""

# ---------------- 首页 ----------------
@app.route('/')
def index():
    return STYLE + """
    <div class='container'>
        <div class='card'>
            <div class='banner'>
                
            </div>
            <h1 style="justify-content:center;">🏖️ 旅行社团队管理系统</h1>
            <div class='nav'>
                <a href="/customer">👤 客户管理</a>
                <a href="/line">🗺️ 线路管理</a>
                <a href="/guide">🧑‍✈️ 导游管理</a>
                <a href="/group">🚍 团队管理</a>
                <a href="/order">🧾 订单管理</a>
                <a href="/fee">💰 费用管理</a>
            </div>
        </div>
    </div>
    """

# ---------------- 客户列表 ----------------
@app.route('/customer')
def customer_list():
    kw = request.args.get("kw", "")
    db, cur = get_db()

    if kw:
        sql = "SELECT * FROM customer WHERE name LIKE %s OR phone LIKE %s"
        cur.execute(sql, (f"%{kw}%", f"%{kw}%"))
    else:
        cur.execute("SELECT * FROM customer")

    rows = cur.fetchall()
    db.close()

    html = STYLE + f"""
    <div class='container'>
        <div class='card'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <h2>👤 客户管理</h2>
                <a href='/customer/add' class='btn' style='background:#28a745'>➕ 添加客户</a>
            </div>

            <form method='get' style='margin:15px 0;'>
                <input type='text' name='kw' placeholder='搜索姓名/电话' value='{kw}' style='padding:8px;width:280px;'>
                <button class='btn' style='background:#17a2b8'>搜索</button>
            </form>

            <table>
                <tr style='background:#409eff;color:white;'>
                    <td>ID</td><td>姓名</td><td>电话</td><td>身份证</td><td>紧急联系人</td><td>旅游偏好</td><td>操作</td>
                </tr>
    """
    for r in rows:
        html += f"""
        <tr>
            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td>{r[4]}</td>
            <td>{r[5]}</td>
            <td>
                <a href='/customer/edit/{r[0]}' style='color:#007bff'>修改</a>
                <a href='/customer/delete/{r[0]}' style='color:#dc3545;margin-left:8px;' onclick='return confirm(\"确定删除？\")'>删除</a>
            </td>
        </tr>
        """
    html += """
            </table>
            <br>
            <a href='/'>← 返回首页</a>
        </div>
    </div>
    """
    return html

# ===================== 添加客户 =====================
@app.route('/customer/add', methods=['GET', 'POST'])
def customer_add():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        id_card = request.form['id_card']
        emergency = request.form['emergency']
        travel_preference = request.form['travel_preference']

        db, cur = get_db()
        cur.execute("SELECT * FROM customer WHERE id_card=%s", (id_card,))
        if cur.fetchone():
            db.close()
            return "<script>alert('该身份证已存在！');history.back();</script>"

        sql = """
        INSERT INTO customer (name, phone, id_card, emergency, travel_preference)
        VALUES (%s,%s,%s,%s,%s)
        """
        cur.execute(sql, (name, phone, id_card, emergency, travel_preference))
        db.commit()
        db.close()
        return "<script>alert('添加成功！ID已自动分配');location.href='/customer';</script>"

    return STYLE + """
    <div class='container'>
        <div class='card' style="max-width: 450px; margin: 30px auto;">
            <h2 style="text-align: center; margin-bottom: 25px; color: #333;">➕ 添加客户</h2>
            <form method='post'>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">姓名</label>
                    <input type='text' name='name' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">电话</label>
                    <input type='text' name='phone' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">身份证号</label>
                    <input type='text' name='id_card' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">紧急联系人</label>
                    <input type='text' name='emergency'>
                </div>
                <div style="margin-bottom: 25px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">旅游偏好</label>
                    <input type='text' name='travel_preference'>
                </div>
                <button class='btn' style='background:#28a745; width: 100%; padding: 10px; font-size: 16px; border: none; border-radius: 6px; cursor: pointer;'>保存</button>
            </form>
            <br>
            <a href='/customer' style="display: inline-block; text-align: center; width: 100%; color: #409eff; text-decoration: none;">← 返回客户列表</a>
        </div>
    </div>
    """

# ===================== 修改客户 =====================
@app.route('/customer/edit/<int:cid>', methods=['GET', 'POST'])
def customer_edit(cid):
    db, cur = get_db()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        id_card = request.form['id_card']
        emergency = request.form['emergency']
        travel_preference = request.form['travel_preference']

        sql = """
        UPDATE customer
        SET name=%s, phone=%s, id_card=%s, emergency=%s, travel_preference=%s
        WHERE customer_id=%s
        """
        cur.execute(sql, (name, phone, id_card, emergency, travel_preference, cid))
        db.commit()
        db.close()
        return "<script>alert('修改成功');location.href='/customer';</script>"

    cur.execute("SELECT * FROM customer WHERE customer_id=%s", (cid,))
    row = cur.fetchone()
    db.close()

    return STYLE + f"""
    <div class='container'>
        <div class='card'>
            <h2>✏️ 修改客户</h2>
            <form method='post'>
                <p>姓名：<input type='text' name='name' value='{row[1]}' required></p>
                <p>电话：<input type='text' name='phone' value='{row[2]}' required></p>
                <p>身份证：<input type='text' name='id_card' value='{row[3]}' required></p>
                <p>紧急联系人：<input type='text' name='emergency' value='{row[4]}'></p>
                <p>旅游偏好：<input type='text' name='travel_preference' value='{row[5]}'></p>
                <button class='btn' style='background:#ffc107;color:black'>保存</button>
            </form>
            <br>
            <a href='/customer'>返回</a>
        </div>
    </div>
    """

# ===================== 删除客户 =====================
@app.route('/customer/delete/<int:cid>')
def customer_delete(cid):
    db, cur = get_db()
    cur.execute("DELETE FROM customer WHERE customer_id=%s", (cid,))
    db.commit()
    db.close()
    return "<script>alert('删除成功');location.href='/customer';</script>"

# ---------------- 线路管理（含简介） ----------------
@app.route('/line')
def line_list():
    db, cur = get_db()
    cur.execute("SELECT * FROM tour_line")
    data = cur.fetchall()
    db.close()

    html = STYLE + """
    <div class='container'>
        <div class='card'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <h1>🗺️ 线路列表</h1>
                <a href='/line/add' class='btn' style='background:#28a745'>➕ 添加线路</a>
            </div>
            <table>
                <tr><th>ID</th><th>目的地</th><th>天数</th><th>景点</th><th>成人价</th><th>儿童价</th><th>状态</th><th>简介</th><th>操作</th></tr>
    """
    for row in data:
        intro = row[7] if row[7] else "无简介"
        html += f"""
        <tr>
            <td>{row[0]}</td>
            <td><a href='/line/detail/{row[0]}'>{row[1]}</a></td>
            <td>{row[2]}</td>
            <td>{row[3]}</td>
            <td>{row[4]}</td>
            <td>{row[5]}</td>
            <td>{row[6]}</td>
            <td style="max-width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{intro}</td>
            <td>
                <a href='/line/edit/{row[0]}' style='color:#007bff'>修改</a>
                <a href='/line/delete/{row[0]}' style='color:#dc3545;margin-left:8px;' onclick='return confirm(\"确定删除？\")'>删除</a>
            </td>
        </tr>
        """
    html += """
            </table>
            <br>
            <a href='/'>← 返回首页</a>
        </div>
    </div>
    """
    return html

# ---------------- 线路详情页（含简介，已修复） ----------------
@app.route('/line/detail/<int:lid>')
def line_detail(lid):
    db, cur = get_db()
    cur.execute("SELECT * FROM tour_line WHERE line_id=%s", (lid,))
    row = cur.fetchone()
    db.close()

    if not row:
        return "<script>alert('线路不存在！');location.href='/line';</script>"

    status_color = {"正常":"green","暂停":"orange","下架":"red"}.get(row[6], "gray")
    intro = row[7] if row[7] else "暂无线路简介"

    html = STYLE + f"""
    <div class='container'>
        <div class='card'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;'>
                <h1>🗺️ 线路详情：{row[1]}</h1>
                <div>
                    <a href='/line/edit/{row[0]}' class='btn' style='background:#ffc107;color:black;margin-right:8px;'>✏️ 修改</a>
                    <a href='/line' class='btn'>← 返回列表</a>
                </div>
            </div>

            <table style="width:100%;max-width:600px;">
                <tr>
                    <th style="width:150px;background:#f5fafe;color:#333;">线路ID</th>
                    <td>{row[0]}</td>
                </tr>
                <tr>
                    <th style="background:#f5fafe;color:#333;">目的地</th>
                    <td>{row[1]}</td>
                </tr>
                <tr>
                    <th style="background:#f5fafe;color:#333;">行程天数</th>
                    <td>{row[2]} 天</td>
                </tr>
                <tr>
                    <th style="background:#f5fafe;color:#333;">景点</th>
                    <td>{row[3]}</td>
                </tr>
                <tr>
                    <th style="background:#f5fafe;color:#333;">成人价格</th>
                    <td>¥{row[4]}</td>
                </tr>
                <tr>
                    <th style="background:#f5fafe;color:#333;">儿童价格</th>
                    <td>¥{row[5]}</td>
                </tr>
                <tr>
                    <th style="background:#f5fafe;color:#333;">状态</th>
                    <td><span style="color:{status_color};font-weight:bold;">{row[6]}</span></td>
                </tr>
                <tr>
                    <th style="background:#f5fafe;color:#333;">线路简介</th>
                    <td style="white-space:pre-wrap;">{intro}</td>
                </tr>
            </table>

            <div style="margin-top:30px;">
                <a href='/line/edit/{row[0]}' class='btn' style='background:#ffc107;color:black;margin-right:10px;'>✏️ 修改线路</a>
                <a href='/line' class='btn'>← 返回线路列表</a>
            </div>
        </div>
    </div>
    """
    return html

# 添加线路（含简介）
@app.route('/line/add', methods=['GET', 'POST'])
def line_add():
    if request.method == 'POST':
        destination = request.form['destination']
        days = request.form['days']
        spots = request.form['spots']
        price_adult = request.form['price_adult']
        price_child = request.form['price_child']
        status = request.form['status']
        intro = request.form['intro']

        db, cur = get_db()
        sql = """
        INSERT INTO tour_line (destination, days, spots, price_adult, price_child, status, intro)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """
        cur.execute(sql, (destination, days, spots, price_adult, price_child, status, intro))
        db.commit()
        db.close()
        return "<script>alert('添加成功！');location.href='/line';</script>"

    return STYLE + """
    <div class='container'>
        <div class='card' style="max-width: 550px; margin: 30px auto;">
            <h2 style="text-align: center; margin-bottom: 25px; color: #333;">➕ 添加线路</h2>
            <form method='post'>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">目的地（如：北京3日游）</label>
                    <input type='text' name='destination' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">天数</label>
                    <input type='number' name='days' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">景点（顿号分隔）</label>
                    <input type='text' name='spots' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">成人价（元）</label>
                    <input type='number' name='price_adult' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">儿童价（元）</label>
                    <input type='number' name='price_child' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">状态</label>
                    <select name='status'>
                        <option value='正常'>正常</option>
                        <option value='暂停'>暂停</option>
                        <option value='下架'>下架</option>
                    </select>
                </div>
                <div style="margin-bottom: 25px;">
                    <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">线路简介</label>
                    <textarea name='intro' rows="5" placeholder="填写线路特色、行程亮点等"></textarea>
                </div>
                <button class='btn' style='background:#28a745; width:100%;'>保存</button>
            </form>
            <br>
            <a href='/line' style="display:block;text-align:center;">← 返回线路列表</a>
        </div>
    </div>
    """

# 修改线路（含简介）
@app.route('/line/edit/<int:lid>', methods=['GET', 'POST'])
def line_edit(lid):
    db, cur = get_db()
    if request.method == 'POST':
        destination = request.form['destination']
        days = request.form['days']
        spots = request.form['spots']
        price_adult = request.form['price_adult']
        price_child = request.form['price_child']
        status = request.form['status']
        intro = request.form['intro']

        sql = """
        UPDATE tour_line
        SET destination=%s, days=%s, spots=%s, price_adult=%s, price_child=%s, status=%s, intro=%s
        WHERE line_id=%s
        """
        cur.execute(sql, (destination, days, spots, price_adult, price_child, status, intro, lid))
        db.commit()
        db.close()
        return "<script>alert('修改成功');location.href='/line';</script>"

    cur.execute("SELECT * FROM tour_line WHERE line_id=%s", (lid,))
    row = cur.fetchone()
    db.close()

    return STYLE + f"""
    <div class='container'>
        <div class='card' style="max-width: 550px; margin: 30px auto;">
            <h2 style="text-align: center; margin-bottom: 25px; color: #333;">✏️ 修改线路</h2>
            <form method='post'>
                <div style="margin-bottom: 15px;">
                    <label>目的地</label>
                    <input type='text' name='destination' value='{row[1]}' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label>天数</label>
                    <input type='number' name='days' value='{row[2]}' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label>景点</label>
                    <input type='text' name='spots' value='{row[3]}' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label>成人价（元）</label>
                    <input type='number' name='price_adult' value='{row[4]}' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label>儿童价（元）</label>
                    <input type='number' name='price_child' value='{row[5]}' required>
                </div>
                <div style="margin-bottom: 15px;">
                    <label>状态</label>
                    <select name='status'>
                        <option value='正常' {'selected' if row[6]=='正常' else ''}>正常</option>
                        <option value='暂停' {'selected' if row[6]=='暂停' else ''}>暂停</option>
                        <option value='下架' {'selected' if row[6]=='下架' else ''}>下架</option>
                    </select>
                </div>
                <div style="margin-bottom: 25px;">
                    <label>线路简介</label>
                    <textarea name='intro' rows="5">{row[7] or ''}</textarea>
                </div>
                <button class='btn' style='background:#ffc107; color:black; width:100%;'>保存</button>
            </form>
            <br>
            <a href='/line' style="display:block;text-align:center;">← 返回线路列表</a>
        </div>
    </div>
    """

# 删除线路
@app.route('/line/delete/<int:lid>')
def line_delete(lid):
    db, cur = get_db()
    cur.execute("DELETE FROM tour_line WHERE line_id=%s", (lid,))
    db.commit()
    db.close()
    return "<script>alert('删除成功');location.href='/line';</script>"

# ---------------- 导游管理 ----------------
@app.route('/guide')
def guide_list():
    db, cur = get_db()
    cur.execute("SELECT * FROM guide")
    data = cur.fetchall()
    db.close()

    html = STYLE + """
    <div class='container'>
        <div class='card'>
            <h1>🧑‍✈️ 导游列表</h1>
            <table>
                <tr><th>ID</th><th>姓名</th><th>电话</th><th>经验</th><th>带团记录</th></tr>
    """
    for row in data:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
    html += """
            </table>
            <br>
            <a href='/'>← 返回首页</a>
        </div>
    </div>
    """
    return html

# ---------------- 团队管理 ----------------
@app.route('/group')
def group_list():
    db, cur = get_db()
    cur.execute("SELECT * FROM tour_group")
    data = cur.fetchall()
    db.close()

    html = STYLE + """
    <div class='container'>
        <div class='card'>
            <h1>🚍 团队列表</h1>
            <table>
                <tr><th>团ID</th><th>线路ID</th><th>导游ID</th><th>出发</th><th>结束</th><th>最大人数</th><th>状态</th></tr>
    """
    for row in data:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
    html += """
            </table>
            <br>
            <a href='/'>← 返回首页</a>
        </div>
    </div>
    """
    return html

# ---------------- 订单管理 ----------------
@app.route('/order')
def order_list():
    db, cur = get_db()
    cur.execute("SELECT * FROM orders")
    data = cur.fetchall()
    db.close()

    html = STYLE + """
    <div class='container'>
        <div class='card'>
            <h1>🧾 订单列表</h1>
            <table>
                <tr><th>订单ID</th><th>团ID</th><th>客户ID</th><th>状态</th><th>实收</th><th>余款</th><th>总价</th></tr>
    """
    for row in data:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
    html += """
            </table>
            <br>
            <a href='/'>← 返回首页</a>
        </div>
    </div>
    """
    return html

# ---------------- 费用管理 ----------------
@app.route('/fee')
def fee_list():
    db, cur = get_db()
    cur.execute("SELECT * FROM fee")
    data = cur.fetchall()
    db.close()

    html = STYLE + """
    <div class='container'>
        <div class='card'>
            <h1>💰 费用与利润</h1>
            <table>
                <tr><th>ID</th><th>团ID</th><th>收入</th><th>地接费</th><th>导游补贴</th><th>保险费</th><th>利润</th></tr>
    """
    for row in data:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
    html += """
            </table>
            <br>
            <a href='/'>← 返回首页</a>
        </div>
    </div>
    """
    return html

if __name__ == '__main__':
    app.run(debug=True)