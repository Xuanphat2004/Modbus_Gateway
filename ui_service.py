from flask import Flask, request, render_template, redirect
import sqlite3
from database_service import add_mapping, delete_mapping

app = Flask(__name__)

@app.route('/')
def index():
    """Hiển thị form thêm ánh xạ và danh sách ánh xạ hiện tại"""
    conn = sqlite3.connect('modbus_mapping.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tcp_address, rtu_id, rtu_address FROM mapping")
    mappings = cursor.fetchall()
    conn.close()
    return render_template('templates_index.html', mappings=mappings)

@app.route('/add_mapping', methods=['POST'])
def add_mapping_route():
    """Xử lý yêu cầu thêm ánh xạ từ form"""
    tcp_address = int(request.form['tcp_address'])
    rtu_id = int(request.form['rtu_id'])
    rtu_address = int(request.form['rtu_address'])
    add_mapping(tcp_address, rtu_id, rtu_address)
    return redirect('/')

@app.route('/delete_mapping/<int:tcp_address>', methods=['POST'])
def delete_mapping_route(tcp_address):
    """Xử lý yêu cầu xóa ánh xạ dựa trên tcp_address"""
    delete_mapping(tcp_address)
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)