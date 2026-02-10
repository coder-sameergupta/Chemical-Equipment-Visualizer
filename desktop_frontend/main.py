import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, 
                             QListWidget, QMessageBox, QTabWidget, QHeaderView, QLineEdit, QDialog, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from api_client import APIClient

# Theme Colors
DARK_THEME = """
    QMainWindow, QDialog, QWidget { background-color: #000000; color: #f8fafc; }
    QLabel { color: #f8fafc; }
    QLineEdit { background-color: #111; color: white; border: 1px solid #333; padding: 5px; border-radius: 4px; }
    QPushButton { background-color: #38bdf8; color: #000; border: none; padding: 8px; border-radius: 4px; font-weight: bold; }
    QPushButton:hover { background-color: #0ea5e9; }
    QTableWidget { background-color: #111; color: white; gridline-color: #333; }
    QHeaderView::section { background-color: #222; color: white; padding: 4px; }
    QTabWidget::pane { border: 1px solid #333; }
    QTabBar::tab { background: #111; color: #94a3b8; padding: 8px; }
    QTabBar::tab:selected { background: #38bdf8; color: #000; }
"""

LIGHT_THEME = """
    QMainWindow, QDialog, QWidget { background-color: #f0f9ff; color: #0f172a; }
    QLabel { color: #0f172a; }
    QLineEdit { background-color: white; color: #0f172a; border: 1px solid #cbd5e1; padding: 5px; border-radius: 4px; }
    QPushButton { background-color: #0ea5e9; color: white; border: none; padding: 8px; border-radius: 4px; font-weight: bold; }
    QPushButton:hover { background-color: #0284c7; }
    QTableWidget { background-color: white; color: #0f172a; gridline-color: #cbd5e1; }
    QHeaderView::section { background-color: #e2e8f0; color: #0f172a; padding: 4px; }
    QTabWidget::pane { border: 1px solid #cbd5e1; }
    QTabBar::tab { background: #e2e8f0; color: #64748b; padding: 8px; }
    QTabBar::tab:selected { background: #0ea5e9; color: white; }
"""

class RegisterDialog(QDialog):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("Sign Up")
        self.setFixedSize(300, 200)
        
        layout = QFormLayout()
        self.username = QLineEdit()
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        
        layout.addRow("Username:", self.username)
        layout.addRow("Email:", self.email)
        layout.addRow("Password:", self.password)
        
        self.register_btn = QPushButton("Create Account")
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)

    def handle_register(self):
        username = self.username.text()
        email = self.email.text()
        password = self.password.text()
        
        if not username or not email or not password:
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        if self.client.register(username, email, password):
            QMessageBox.information(self, "Success", "Registration successful! Please login.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Registration failed. Try again.")

class ForgotPasswordDialog(QDialog):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("Forgot Password")
        self.setFixedSize(300, 120)
        
        layout = QFormLayout()
        self.email = QLineEdit()
        layout.addRow("Email:", self.email)
        
        self.reset_btn = QPushButton("Send Reset Link")
        self.reset_btn.clicked.connect(self.handle_reset)
        layout.addWidget(self.reset_btn)
        
        self.setLayout(layout)

    def handle_reset(self):
        email = self.email.text()
        if not email:
            QMessageBox.warning(self, "Error", "Email is required")
            return

        if self.client.reset_password_request(email):
            QMessageBox.information(self, "Success", "Password reset link sent! Check backend console.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to send reset request.")

class LoginDialog(QDialog):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("Login")
        self.setFixedSize(320, 250)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Username:", self.username)
        form_layout.addRow("Password:", self.password)
        layout.addLayout(form_layout)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        # Additional Options
        options_layout = QHBoxLayout()
        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setStyleSheet("background: transparent; color: #38bdf8; border: 1px solid #38bdf8;") 
        self.signup_btn.clicked.connect(self.open_register)
        
        self.forgot_btn = QPushButton("Forgot Password?")
        self.forgot_btn.setStyleSheet("background: transparent; color: #94a3b8; border: none;")
        self.forgot_btn.clicked.connect(self.open_forgot_password)
        
        options_layout.addWidget(self.signup_btn)
        options_layout.addWidget(self.forgot_btn)
        layout.addLayout(options_layout)
        
        self.setLayout(layout)

    def handle_login(self):
        username = self.username.text()
        password = self.password.text()
        
        if self.client.login(username, password):
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

    def open_register(self):
        dialog = RegisterDialog(self.client)
        dialog.exec_()

    def open_forgot_password(self):
        dialog = ForgotPasswordDialog(self.client)
        dialog.exec_()

class DashboardTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()
        self.refresh_history()

    def init_ui(self):
        layout = QHBoxLayout()

        # Sidebar (History)
        self.sidebar_layout = QVBoxLayout()
        self.refresh_btn = QPushButton("Refresh History")
        self.refresh_btn.clicked.connect(self.refresh_history)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_selected_upload)
        
        self.sidebar_layout.addWidget(QLabel("<b>Recent Uploads</b>"))
        self.sidebar_layout.addWidget(self.history_list)
        self.sidebar_layout.addWidget(self.refresh_btn)
        
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(self.sidebar_layout)
        sidebar_widget.setFixedWidth(200)

        # Main Area
        main_layout = QVBoxLayout()
        self.stats_label = QLabel("Select an upload from history to view data.")
        self.stats_label.setStyleSheet("font-size: 14px; padding: 10px;")
        
        self.figure = plt.figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        
        self.table = QTableWidget()

        # Download Button
        self.download_btn = QPushButton("Download Report (PDF)")
        self.download_btn.setStyleSheet("background-color: #8b5cf6; color: white; font-weight: bold; padding: 10px;")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.download_report)
        
        main_layout.addWidget(self.stats_label)
        main_layout.addWidget(self.download_btn)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.table)
        
        layout.addWidget(sidebar_widget)
        layout.addLayout(main_layout, stretch=1)
        self.setLayout(layout)

    def refresh_history(self):
        history = self.client.get_history()
        self.history_list.clear()
        for item in history:
            self.history_list.addItem(f"#{item['id']} ({item['uploaded_at'][:10]})")
            self.history_list.item(self.history_list.count()-1).setData(Qt.UserRole, item['id'])

    def load_selected_upload(self, item):
        self.current_upload_id = item.data(Qt.UserRole)
        summary = self.client.get_summary(self.current_upload_id)
        data = self.client.get_data(self.current_upload_id)
        
        if summary:
            avgs = summary['averages']
            self.stats_label.setText(
                f"<b>Upload #{self.current_upload_id}</b> | Total: {summary['total_count']} | "
                f"Avg Flow: {avgs['avg_flowrate']:.2f} | "
                f"Pressure: {avgs['avg_pressure']:.2f} | "
                f"Temp: {avgs['avg_temperature']:.2f}"
            )
            self.update_charts(summary, data)
            self.download_btn.setEnabled(True)
        
        if data:
            self.update_table(data)

    def download_report(self):
        if not hasattr(self, 'current_upload_id'):
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"report_{self.current_upload_id}.pdf", "PDF Files (*.pdf)")
        if path:
            if self.client.download_report(self.current_upload_id, path):
                QMessageBox.information(self, "Success", f"Report saved to {path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to download report.")

    def update_charts(self, summary, data):
        self.figure.clear()
        
        # Line Chart
        ax1 = self.figure.add_subplot(121)
        names = [d['equipment_name'] for d in data]
        ax1.plot(names, [d['flowrate'] for d in data], label='Flow')
        ax1.plot(names, [d['pressure'] for d in data], label='Pressure')
        ax1.legend()
        ax1.set_title("Parameters")
        ax1.tick_params(axis='x', rotation=45)
        
        # Bar Chart
        ax2 = self.figure.add_subplot(122)
        types = [d['equipment_type'] for d in summary['type_distribution']]
        counts = [d['count'] for d in summary['type_distribution']]
        ax2.bar(types, counts, color='teal')
        ax2.set_title("Distribution")
        
        self.figure.tight_layout()
        self.canvas.draw()

    def update_table(self, data):
        self.table.setRowCount(len(data))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Name', 'Type', 'Flow', 'Press', 'Temp'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for i, row in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(row['equipment_name'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row['equipment_type'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row['flowrate'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row['pressure'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(row['temperature'])))

class UploadTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Upload CSV Data")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        self.status = QLabel("Ready to upload")
        self.status.setAlignment(Qt.AlignCenter)
        
        btn = QPushButton("Select CSV File")
        btn.setFixedSize(200, 50)
        btn.setStyleSheet("font-size: 14px; background-color: #3b82f6; color: white; border-radius: 5px;")
        btn.clicked.connect(self.upload_file)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.status)
        layout.addStretch()
        self.setLayout(layout)

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV Files (*.csv)')
        if fname:
            self.status.setText("Uploading...")
            res = self.client.upload_file(fname)
            if res:
                self.status.setText(f"Success! Upload ID: {res['id']}")
                QMessageBox.information(self, "Success", "File uploaded successfully!")
            else:
                self.status.setText("Upload Failed")

class UsersTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Username', 'Email', 'Is Staff'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        refresh_btn = QPushButton("Refresh User List")
        refresh_btn.clicked.connect(self.load_users)
        
        layout.addWidget(QLabel("<b>Registered Users</b>"))
        layout.addWidget(self.table)
        layout.addWidget(refresh_btn)
        self.setLayout(layout)
        
        self.load_users()

    def load_users(self):
        users = self.client.get_users()
        self.table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.table.setItem(i, 0, QTableWidgetItem(str(u['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(u['username']))
            self.table.setItem(i, 2, QTableWidgetItem(u['email']))
            self.table.setItem(i, 3, QTableWidgetItem("Yes" if u['is_staff'] else "No"))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = APIClient()
        self.dark_mode = True # Default to Dark Mode
        
        # Apply initial theme
        self.apply_theme()
        
        # Show Login Dialog first
        if not self.show_login():
            sys.exit(0)

        self.init_ui()

    def show_login(self):
        dialog = LoginDialog(self.client)
        dialog.setStyleSheet(DARK_THEME if self.dark_mode else LIGHT_THEME) # Apply theme to dialog too
        return dialog.exec_() == QDialog.Accepted

    def init_ui(self):
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.setGeometry(100, 100, 1000, 700)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(DashboardTab(self.client), "📊 Dashboard")
        self.tabs.addTab(UploadTab(self.client), "📤 Upload")
        self.tabs.addTab(UsersTab(self.client), "👥 Users")
        
        # Header / Toolbar
        container = QWidget()
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        header.addWidget(QLabel("Logged in as User"))
        
        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.setFixedSize(120, 30)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(80, 30)
        logout_btn.setStyleSheet("background-color: #ef4444; color: white;")
        logout_btn.clicked.connect(self.logout)
        
        header.addStretch()
        header.addWidget(self.theme_btn)
        header.addWidget(logout_btn)
        
        layout.addLayout(header)
        layout.addWidget(self.tabs)
        container.setLayout(layout)
        
        self.setCentralWidget(container)
        self.apply_theme() # Re-apply theme to affect new widgets

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        app = QApplication.instance()
        if self.dark_mode:
            app.setStyleSheet(DARK_THEME)
        else:
            app.setStyleSheet(LIGHT_THEME)

    def logout(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
