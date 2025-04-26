from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  
    database="phongtro"
)
cursor = db.cursor(dictionary=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    keyword = request.args.get('search', '').strip()

    if request.method == 'POST':
        cursor.execute("SELECT ma_phong FROM phong_tro ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result and result['ma_phong']:
            try:
                last_number = int(result['ma_phong'].split('-')[1])
            except:
                last_number = 0
        else:
            last_number = 0
        new_number = last_number + 1
        ma_phong = f"PT-{str(new_number).zfill(3)}"

        ten_nguoi_thue = request.form['ten_nguoi_thue']
        so_dien_thoai = request.form['so_dien_thoai']
        ngay_bat_dau_thue = request.form['ngay_bat_dau_thue']
        hinh_thuc_thanh_toan = request.form['hinh_thuc_thanh_toan']
        ghi_chu = request.form['ghi_chu']

        if ngay_bat_dau_thue < today:
            return "Ngày bắt đầu thuê không được nhỏ hơn hôm nay!", 400
        if not so_dien_thoai.isdigit() or len(so_dien_thoai) != 10:
            return "Số điện thoại phải gồm đúng 10 chữ số!", 400

        cursor.execute(""" 
            INSERT INTO phong_tro (ma_phong, ten_nguoi_thue, so_dien_thoai, ngay_bat_dau_thue, hinh_thuc_thanh_toan, ghi_chu)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (ma_phong, ten_nguoi_thue, so_dien_thoai, ngay_bat_dau_thue, hinh_thuc_thanh_toan, ghi_chu))
        db.commit()
        return redirect('/')

    if keyword:
        cursor.execute("""
            SELECT * FROM phong_tro
            WHERE ma_phong LIKE %s OR ten_nguoi_thue LIKE %s OR so_dien_thoai LIKE %s
        """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    else:
        cursor.execute("SELECT * FROM phong_tro")

    phong_tros = cursor.fetchall()
    return render_template('index.html', phong_tros=phong_tros, keyword=keyword, today=today)


@app.route('/delete', methods=['POST'])
def delete():
    ids = request.form.getlist('delete_ids')
    if ids:
        format_strings = ','.join(['%s'] * len(ids))
        query = "DELETE FROM phong_tro WHERE id IN (%s)" % format_strings
        cursor.execute(query, tuple(ids))
        db.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
