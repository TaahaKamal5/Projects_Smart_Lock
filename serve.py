from flask import Flask, Response, request, render_template
from flask import redirect, url_for, session, flash
from savedData import *
import json

app = Flask(__name__)
app.secret_key = "SECRET"

@app.route('/')
def home():
    return render_template("index.html", logged_in='logged_in' in session)


# @app.route('/home')
# def home():
#     #items = get_devices()
#     return render_template("home.html")


@app.route('/macs')
def template_macs():
    if 'logged_in' in session:
        items = get_all_WhiteList()
        return render_template("tabled.html", items=items)
    else:
        return redirect(url_for('home'))


@app.route('/insert', methods=['POST'])
def insert():
    error = None
    if request.method == 'POST' and 'logged_in' in session:
        if valid_insert(request.form['name'], request.form['mac']):
            insert_mac_name(request.form['name'], request.form['mac'])
            return "Success!"
        else:
            return "nah"
    else:
        return redirect(url_for('home'))


@app.route('/insert', methods=['GET'])
def insert_form():
    if 'logged_in' in session:
        return render_template("input.html")
    else:
        return redirect(url_for('home'))

@app.route('/devices', methods=['GET'])
def devices():
    """
    This returns a list of device, mac address keypairs
    """
    if request.method == 'GET' and 'logged_in' in session:
        return json.dumps(get_devices())
    else:
        return redirect(url_for('home'))


@app.route('/devices/delete', methods=['POST'])
def delete():
    """
    This deletes the specified name
    """
    if request.method == 'POST' and 'logged_in' in session:
        if request.form['name']:
            delete_name(request.form['name'])
            return "Deleted based on name"
        elif request.form['mac']:
            delete_name(request.form['mac'])
            return "Deleted based on html"
    else:
        return redirect(url_for('home'))


@app.route('/devices/delete', methods=['GET'])
def delete_form():
    """
    This deletes the specified name
    """
    if 'logged_in' in session:
        return render_template("delete.html")


@app.route('/new', methods=['POST', 'GET'])
def new():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        saved.addUser(username, password)
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Try again'
        else:
            session['logged_in'] = True
            flash('Logged in!')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out')
    return redirect(url_for('home'))


def delete_name(name):
    """
    This function will delete based on the name
    """

    conn = connect()
    c = conn.cursor()

    c.execute("""DELETE FROM devices 
                 WHERE name = ?""", (name, ))

    conn.commit()
    conn.close()


def get_devices():
    """
    This function returns all the devices name's and their mac addresses
    currently in the devices table

    Returns:
        str[]: A list of all devices in the table
    """
    devices = []

    conn = connect()
    c = conn.cursor()

    for row in c.execute("""SELECT * FROM devices"""):
        devices.append((row[1], row[2]))

    conn.close()

    return devices


def valid_insert(name, mac):
    """
    This function determines if the name and mac address of a device are safe to
    be inserted into the db. Pretty basic right now

    Args:
        name (str): the name of the device
        mac  (str): the mac address of the device

    Returns:
        bool: True for valid/safe to insert, false for not
    """
    if type(name) == str and len(name) < 100:
        if type(mac) == str and len(mac) < 100:
            return True
    return False


def connect():
    """
    This function returns a connection to the databse

    Returns:
        sqlite3.Connection: connection to db
    """

    return sql.connect('test.db')


def create_db():
    """
    This function creates a table called devices
    """

    conn = connect()
    c = conn.cursor()

    c.execute("""CREATE TABLE devices 
                 (id INTEGER PRIMARY KEY, name varchar(25), mac varchar(30))"""
              )

    conn.commit()
    conn.close()


def main():
    conn = connect()
    c = conn.cursor()

    #create_db()


def insert_mac_name(name, mac):
    """
    This function inserts the name and mac address of a device into the devices
    table of the db

    Args:
        name (str): the name of the device
        mac  (str): the mac address of the device
    """

    conn = connect()
    c = conn.cursor()

    c.execute("""INSERT INTO devices (name, mac) VALUES (?, ?)""", (name, mac))

    conn.commit()
    conn.close()


def get_macs():
    """
    This function returns all the mac addresses inside the table devices

    Returns:
        str[]: A list of all mac addresses inside the table devices
    """
    macs = []

    conn = connect()
    c = conn.cursor()

    for row in c.execute("""SELECT mac FROM devices"""):
        macs.append(row[0])

    conn.close()

    return macs


def db_scanned_macs():
    """
    This function returns the database values of the current devices connected to
    the network
    """

    return_list = []

    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM scanned")

    for i in c.fetchall():
        return_list.append(i[0])

    return return_list


def match_macs(mac):
    """
    This function returns if the argument is in the table devices
    
    Args:
        mac(str): A mac address

    Returns:
        bool: if mac
    """

    return mac in get_macs()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    """
    main()
    print(get_macs())
    print(match_macs("eyeyeyey"))
    print(match_macs("eyeyeyea"))
    print(db_scanned_macs())
    """
