from flask import Flask, render_template, redirect, request, url_for
import sqlite3

app = Flask(__name__)

def getExpensesTotal():
    connection = sqlite3.connect('budget.db')
    cursor = connection.cursor()
    try:
        total = cursor.execute('SELECT SUM(value) FROM expenses').fetchone()[0]/2

    except (TypeError):
        total = 0
    
    connection.close()
    return total

def updateExpenses():
    connection = sqlite3.connect('budget.db')
    cursor = connection.cursor()

    try:
        total = cursor.execute('SELECT SUM(value) FROM expenses').fetchone()[0]
        cursor.execute('UPDATE streams SET value = ? WHERE id = ?', (total, 4))
        cursor.execute('UPDATE streams SET deduction = ? WHERE id = ?', (total/2, 4))
        
    except (TypeError):
        cursor.execute('UPDATE streams SET value = ? WHERE id = ?', (0, 4))
        cursor.execute('UPDATE streams SET deduction = ? WHERE id = ?', (0, 4))        

    connection.commit()
    connection.close()
    

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

    transactionType = request.form['transaction-type']
    inputValue = float(request.form['deposit'])

    connection = sqlite3.connect('budget.db')
    cursor = connection.cursor()
    streams = cursor.execute('SELECT * FROM streams').fetchall()
    spendingBal = streams[0][3]
    savingsBal = streams[1][3]
    investmentsBal = streams[2][3]
    spendingValId = 1
    savingsValId = 2
    investmentsValId = 3

    if transactionType == 'withdraw':
        cursor.execute('UPDATE streams SET value = ? WHERE id = ?', (spendingBal-inputValue, spendingValId))

    elif transactionType == 'deposit':
        cursor.execute('UPDATE streams SET value = ? WHERE id = ?', (savingsBal+inputValue, savingsValId))

    else:
        #check if perecentages have been updated

        #error handle if percentages are greater than 100%
        totalExpenses = getExpensesTotal()
        postExpenses = inputValue - totalExpenses
        #expenses will be deducted first then the percentage will be cut
        savingsPercentage = streams[1][2] / 100
        savingsDeduction = postExpenses * savingsPercentage
        investmentsPercentage = streams[2][2] / 100
        investmentsDeduction = postExpenses * investmentsPercentage

        leftover = postExpenses - savingsDeduction - investmentsDeduction
        cursor.execute('UPDATE streams SET value = ? WHERE id = ?', (spendingBal+leftover, spendingValId))
        cursor.execute('UPDATE streams SET value = ? WHERE id = ?', (savingsBal+savingsDeduction, savingsValId))
        cursor.execute('UPDATE streams SET value = ? WHERE id = ?', (investmentsBal+investmentsDeduction, investmentsValId))
    
    connection.commit()
    connection.close()
    return redirect(url_for('index')) 


                
        

    

@app.route('/add', methods=['POST'])
def add_expense():
    name = request.form['name']
    value = request.form['value']
    connection = sqlite3.connect('budget.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO expenses (refid, name, value) VALUES ( ?, ?, ?)', (4, name, value))
    connection.commit()
    connection.close()
    updateExpenses()
    return redirect(url_for('index')) 


@app.route('/submit/<int:id>', methods=['POST'])
def submit(id):
    action = request.form.get('action')
    value = request.form.get('value')
    
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()

    if action == 'update':
        cursor.execute('UPDATE expenses SET value = ? WHERE expense_id = ?', (value, id))
    elif action == 'delete':
        cursor.execute('DELETE FROM expenses WHERE expense_id = ?', (id,))
    conn.commit()
    conn.close()
    updateExpenses()
    return redirect(url_for('index'))


@app.route('/clear', methods=['POST'])
def clear():
    location = request.form['location']

    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    
    if (location == 'savings'):
        cursor.execute('UPDATE streams Set value = ? WHERE id = ?', (0,2))
    else:
        cursor.execute('UPDATE streams Set value = ? WHERE id = ?', (0,3))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index'))



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


    