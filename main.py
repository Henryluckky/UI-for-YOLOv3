from PyQt5.QtWidgets import QApplication
import main_window
import sys
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = main_window.MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())