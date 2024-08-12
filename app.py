from flask import Flask, render_template, redirect, request, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    connection = sqlite3.connect('budget.db')
    cursor = connection.cursor()
    streams = cursor.execute('SELECT * FROM streams').fetchall()
    expenses = cursor.execute('SELECT * FROM expenses').fetchall()
    connection.close()
    return render_template('index.html', streams = streams, expenses = expenses)

@app.route('/transaction', methods=['POST'])
def edit_balance():
    wdad


if __name__ == '__main__':
    connection = sqlite3.connect('budget.db')
    cursor = connection.cursor()

    # Create the streams table
    command1 = """
    CREATE TABLE IF NOT EXISTS 
    streams (
        id INTEGER PRIMARY KEY,
        type TEXT,
        deduction REAL,
        value REAL
    )
    """
    cursor.execute(command1)

    # Check if the streams table is empty
    cursor.execute('SELECT COUNT(*) FROM streams')
    count = cursor.fetchone()[0]

    if count == 0:
        # Insert initial rows into the streams table if it's empty
        initial_data = [
            (1, 'wallet', 0, 0),
            (2, 'savings', 0, 0),
            (3, 'investments', 0, 0),
            (4, 'bills', 0, 0)
        ]
        cursor.executemany('INSERT INTO streams (id, type, deduction, value) VALUES (?, ?, ?, ?)', initial_data)

    # Create the expenses table
    command2 = """
    CREATE TABLE IF NOT EXISTS 
    expenses (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        refid INTEGER,
        name TEXT,
        value REAL,
        FOREIGN KEY(refid) REFERENCES streams(id)
    )
    """
    cursor.execute(command2)

    # Commit the transaction
    connection.commit()

    # Close the connection
    connection.close()

    # Run the Flask app
    app.run(debug=True)


    