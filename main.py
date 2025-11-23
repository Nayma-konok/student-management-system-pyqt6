from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication,QVBoxLayout,QWidget,QLabel,QGridLayout,QLineEdit,QPushButton,\
    QMainWindow,QTableWidget,QTableWidgetItem,QDialog,QComboBox, QToolBar,QStatusBar,QMessageBox
from PyQt6.QtGui import QAction,QIcon
import sys
import sqlite3


class DatabaseConnection:
    def __init__(self,database_file="database.db"):
        self.database_file=database_file

    def connect(self):
        connection=sqlite3.connect(self.database_file)
        return connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(500,400)

        file_menu_item=self.menuBar().addMenu("&File")
        help_menu_item=self.menuBar().addMenu("&Help")
        edit_menu_item=self.menuBar().addMenu("&Edit")

        add_student_action=QAction(QIcon("icons/add.png"), "Add Student",self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)


        about_action=QAction("About",self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        edit_action=QAction(QIcon("icons/search.png"),"Search",self)
        edit_menu_item.addAction(edit_action)
        edit_action.triggered.connect(self.search)

        self.table=QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id","Name","Course","Mobile"))
        self.table.verticalHeader().setVisible(False) 
        self.setCentralWidget(self.table)

        #create toolbar and add toolbar elements
        toolbar=QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(edit_action)

        #create statusbar and add statusbar elements
        status_bar=QStatusBar()
        self.setStatusBar(status_bar)

        #delete a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button=QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button=QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        self.statusBar().addWidget(edit_button)
        self.statusBar().addWidget(delete_button)


    def load_data(self):
        connection=DatabaseConnection().connect()
        result= connection.execute("Select * From students")
        self.table.setRowCount(0)
        for row_number,row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number,data in enumerate(row_data):
                self.table.setItem(row_number,column_number,QTableWidgetItem(str(data)))
        connection.close()


    def insert(self):
        dialog=InsertDialog()
        dialog.exec()

    def search(self):
        dialog1=SearchDialog()
        dialog1.exec()

    def edit(self):
        dialog1=EditDialog()
        dialog1.exec()

    def delete(self):
        dialog1=DeleteDialog()
        dialog1.exec()

    def about(self):
        dialog1=AboutDialog()
        dialog1.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content="""
        This was created during the python course
        """
        self.setText(content)
                  
class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout=QVBoxLayout()

        #Get student name from a selected row
        index=main_window.table.currentRow()
        self.student_id = main_window.table.item(index, 0).text()
        student_name=main_window.table.item(index, 1).text()
        student_course = main_window.table.item(index, 2).text()
        mobile_number = main_window.table.item(index, 3).text()

        self.student_name = QLineEdit()
        self.student_name.setText(student_name)
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Physics", "Astronomy"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(student_course)  # set correct course
        layout.addWidget(self.course_name) 

        self.mobile_number = QLineEdit()
        self.mobile_number.setText(mobile_number)
        layout.addWidget(self.mobile_number)

        button = QPushButton("Save Changes")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
       connection=DatabaseConnection().connect()
       cursor=connection.cursor()
       cursor.execute("UPDATE students SET name =?, course= ? , mobile= ? WHERE id =?" , 
                      (self.student_name.text(), 
                       self.course_name.itemText(self.course_name.currentIndex()), 
                       self.mobile_number.text(), 
                       self.student_id ))
       connection.commit()
       cursor.close()
       connection.close()
       main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout=QGridLayout()
        confirmation=QLabel("Do you want to delete?")
        yes=QPushButton("Yes")
        no=QPushButton("No")

        layout.addWidget(confirmation,0,0,1,2)
        layout.addWidget(yes,1,0)
        layout.addWidget(no,1,1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)


    def delete_student(self):
        index=main_window.table.currentRow()
        self.student_id = main_window.table.item(index, 0).text()
        
        connection=sqlite3.connect("database.db")
        cursor=connection.cursor()
        cursor.execute("DELETE From students WHERE id =?" , (self.student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget=QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Deleted Successfully")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout=QVBoxLayout()

        self.student_name=QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name=QComboBox()
        courses=["Biology","Math","Physics","Astronomy"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.mobile_number=QLineEdit()
        self.mobile_number.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile_number)

        button=QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name= self.student_name.text()
        course= self.course_name.itemText(self.course_name.currentIndex())
        mobile= self.mobile_number.text()
        connection=DatabaseConnection().connect()
        cursor=connection.cursor()
        cursor.execute("INSERT INTO students(name,course,mobile) VALUES (?,?,?)",
                       (name,course,mobile))
        
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        
        layout=QVBoxLayout()

        self.student_name=QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        button=QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name= self.student_name.text()
        connection=DatabaseConnection().connect()
        cursor=connection.cursor()
        result=cursor.execute("Select * From students WHERE name = ?" ,(name,))
        rows=list(result)
        print(rows)
        items=main_window.table.findItems(name,Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(),1).setSelected(True)

        cursor.close()
        connection.close()
        main_window.load_data()



app=QApplication(sys.argv)
main_window=MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())