from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Route to display the main page
@app.route('/')
def index():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)

# Route to handle adding a new expense
@app.route('/add', methods=['POST'])
def add_expense():
    name = request.form['name']
    amount = request.form['amount']
    category = request.form['category']
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (name, amount, category) VALUES (?, ?, ?)', (name, amount, category))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create the database and table if they don't exist
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL
    )
    ''')
    conn.close()

    app.run(debug=True)



