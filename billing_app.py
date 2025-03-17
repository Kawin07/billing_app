import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout) #type: ignore
from PySide6.QtGui import QIntValidator #type: ignore
import mysql.connector #type: ignore


class BillingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Billing Application')
        self.setGeometry(300, 300, 500, 400)
        self.initUI()
        self.connect_to_database()

    def initUI(self):
        layout = QVBoxLayout()

        # Customer Name Input
        self.customer_name = QLineEdit(self)
        self.customer_name.setPlaceholderText('Customer Name')
        layout.addWidget(self.customer_name)

        # Customer Contact Input
        self.customer_contact = QLineEdit(self)
        self.customer_contact.setPlaceholderText('Customer Contact (Only Numbers)')
        self.customer_contact.setValidator(QIntValidator())
        layout.addWidget(self.customer_contact)

        # Bill Amount Input
        self.bill_amount = QLineEdit(self)
        self.bill_amount.setPlaceholderText('Bill Amount')
        self.bill_amount.setValidator(QIntValidator())
        layout.addWidget(self.bill_amount)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton('Save Bill', self)
        self.save_button.clicked.connect(self.save_bill)
        button_layout.addWidget(self.save_button)

        self.update_button = QPushButton('Update Bill', self)
        self.update_button.clicked.connect(self.update_bill)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton('Delete Bill', self)
        self.delete_button.clicked.connect(self.delete_bill)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        self.show_button = QPushButton('Show All Bills', self)
        self.show_button.clicked.connect(self.show_bills)
        layout.addWidget(self.show_button)

        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.refresh_table)
        layout.addWidget(self.refresh_button)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

    def connect_to_database(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Kawin@2005',
                database='billingdb'
            )
            self.cursor = self.conn.cursor()
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    name VARCHAR(255),
                                    contact VARCHAR(15)
                                  )''')

            self.cursor.execute('''CREATE TABLE IF NOT EXISTS bills (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    customer_id INT,
                                    bill_amount FLOAT,
                                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                                  )''')
            self.conn.commit()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Database Error', str(e))

    def refresh_table(self):
        self.show_bills()

    def save_bill(self):
        customer_name = self.customer_name.text()
        customer_contact = self.customer_contact.text()
        bill_amount = self.bill_amount.text()

        if not customer_name or not customer_contact or not bill_amount:
            QMessageBox.warning(self, 'Input Error', 'Please enter all details.')
            return

        try:
            self.cursor.execute('SELECT id FROM customers WHERE contact = %s', (customer_contact,))
            customer = self.cursor.fetchone()

            if customer:
                customer_id = customer[0]
            else:
                self.cursor.execute('INSERT INTO customers (name, contact) VALUES (%s, %s)', (customer_name, customer_contact))
                self.conn.commit()
                customer_id = self.cursor.lastrowid

            self.cursor.execute('INSERT INTO bills (customer_id, bill_amount) VALUES (%s, %s)', (customer_id, float(bill_amount)))
            self.conn.commit()
            QMessageBox.information(self, 'Success', 'Bill saved successfully!')

            self.customer_name.clear()
            self.customer_contact.clear()
            self.bill_amount.clear()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Database Error', str(e))

    def show_bills(self):
        try:
            self.cursor.execute('''SELECT bills.id, customers.name, customers.contact, bills.bill_amount 
                                   FROM bills 
                                   JOIN customers ON bills.customer_id = customers.id''')
            rows = self.cursor.fetchall()

            self.table.setRowCount(len(rows))
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(['ID', 'Customer Name', 'Contact', 'Bill Amount'])

            for row_num, row_data in enumerate(rows):
                for col_num, data in enumerate(row_data):
                    self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Database Error', str(e))

    def update_bill(self):
        try:
            current_row = self.table.currentRow()
            if current_row == -1:
                QMessageBox.warning(self, 'Selection Error', 'Please select a bill to update.')
                return

            bill_id = int(self.table.item(current_row, 0).text())
            new_amount = self.bill_amount.text()

            if not new_amount:
                QMessageBox.warning(self, 'Input Error', 'Please enter a valid bill amount.')
                return

            self.cursor.execute('UPDATE bills SET bill_amount = %s WHERE id = %s', (float(new_amount), bill_id))
            self.conn.commit()
            QMessageBox.information(self, 'Success', 'Bill updated successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Update Error', str(e))

    def delete_bill(self):
        try:
            current_row = self.table.currentRow()
            if current_row == -1:
                QMessageBox.warning(self, 'Selection Error', 'Please select a bill to delete.')
                return

            bill_id = int(self.table.item(current_row, 0).text())

            self.cursor.execute('DELETE FROM bills WHERE id = %s', (bill_id,))
            self.conn.commit()
            QMessageBox.information(self, 'Success', 'Bill deleted successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Delete Error', str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BillingApp()
    window.show()
    sys.exit(app.exec())
