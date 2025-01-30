import sys
from PySide2.QtWidgets import QApplication
from src.ui.plotter import FunctionsSolver
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FunctionsSolver()
    window.show()
    sys.exit(app.exec_())
