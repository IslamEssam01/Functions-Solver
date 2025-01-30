from typing import Any,  Callable

from PySide2.QtCore import QEvent, QThreadPool, Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (QColorDialog, QMainWindow,   QWidget, QVBoxLayout, QLabel,
                               QLineEdit, QPushButton, QHBoxLayout)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


from .DraggableContainer import DraggableContainer

from .Runnables import SolverWorker, PlotWorker

from .PlotManager import PlotManager

from ..calc.evaluator.UnknownFunctionError import UnknownFunctionError
from ..calc.lexer.lexer import Lexer
from ..calc.lexer.LexerError import LexerError
from ..calc.parser.ParserError import ParserError

from ..utils.helpers import evaluator_function, parse_expression


class FunctionsSolver(QMainWindow):
    """
    The main application window for solving and plotting functions.
    """

    def __init__(self):
        super().__init__()
        self.initUI()

        self.f1_valid = True
        self.f2_valid = True

        # Initialize worker threads as None
        self.plot_worker = None
        self.solver_worker = None

    def eventFilter(self, watched, event):
        """
        Filters key press events to prevent invalid input in function fields.

        Args:
            watched: The widget being watched.
            event: The event being filtered.

        Returns:
            bool: True if the event should be filtered, False otherwise.
        """
        if event.type() == QEvent.KeyPress and (watched is self.f1_input or watched is self.f2_input):
            if (watched is self.f1_input and not self.f1_valid) or (watched is self.f2_input and not self.f2_valid):
                # Allow navigation and deletion keys even if the input is invalid
                if event.key() in (Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, Qt.Key_Tab) or \
                        event.modifiers() == Qt.ControlModifier:
                    return False
                else:
                    return True
        return super().eventFilter(watched, event)

    def initUI(self):
        """
        Initialize the user interface.
        """
        self.setWindowTitle("Functions Solver")
        self.setMinimumSize(800, 500)

        f1_base_color = "#ff0000"
        f2_base_color = "#0000ff"

        plot_container = QWidget()
        plot_layout = QVBoxLayout(plot_container)
        plot_layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = FigureCanvas(Figure())

        self.plot_manager = PlotManager(
            self.canvas, f1_base_color, f2_base_color)  # Initialize PlotManager
        self.plot_manager.setup_plot()

        plot_layout.addWidget(self.canvas)

        inputs_container = DraggableContainer(plot_container)
        inputs_container.setObjectName("inputs_container")
        inputs_container.setStyleSheet("""
            #inputs_container {
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(0, 0, 0, 0.15);
                border-radius: 8px;
            }
        """)

        inputs_layout = QVBoxLayout(inputs_container)
        inputs_layout.setSpacing(2)
        inputs_layout.setContentsMargins(10, 10, 10, 10)

        f1_layout, self.f1_input, self.f1_error_label, self.f1_color_button = self.create_input_section(
            f1_base_color)
        inputs_layout.addLayout(f1_layout)

        f2_layout, self.f2_input, self.f2_error_label, self.f2_color_button = self.create_input_section(
            f2_base_color)
        inputs_layout.addLayout(f2_layout)

        buttons_container = QWidget()
        buttons_container.setStyleSheet("""
        QPushButton{
            border-radius:6px;
            background-color:#1d4ed8;
            padding-left:8px;
            padding-right:8px;
            padding-top:4px;
            padding-bottom:4px;
            font-size:16px;
            line-height:24px;
            font-weight:600;
            color:#f8fafc;
        }
        QPushButton:hover{
            background-color:#1e40af;
        }
        """)

        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 5, 0, 0)
        buttons_layout.setSpacing(5)
        buttons_layout.setAlignment(Qt.AlignCenter)

        solve_button = QPushButton("Solve and plot")
        solve_button.setObjectName("solve_button")
        solve_button.clicked.connect(self.solve_plot_functions)
        solve_button.setCursor(Qt.PointingHandCursor)

        plot_button = QPushButton("Plot")
        plot_button.setObjectName("plot_button")
        plot_button.clicked.connect(
            lambda: (self.plot_functions(), self.delete_solutions()))
        plot_button.setCursor(Qt.PointingHandCursor)

        buttons_layout.addWidget(solve_button)
        buttons_layout.addWidget(plot_button)
        inputs_layout.addWidget(buttons_container)

        inputs_container.setFixedWidth(320)
        inputs_container.setFixedHeight(inputs_layout.sizeHint().height())
        inputs_container.move(20, 20)

        self.solutions_container = DraggableContainer(plot_container)
        self.solutions_container.hide()
        self.solutions_container.setObjectName("solutions_container")
        self.solutions_container.setStyleSheet("""
            #solutions_container {
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(0, 0, 0, 0.15);
                border-radius: 8px;
                padding: 5px;
            }
        """)
        self.solutions_container.setFixedWidth(300)
        self.solutions_layout = QVBoxLayout(self.solutions_container)
        self.solutions_layout.setSpacing(3)
        self.solutions_layout.setContentsMargins(10, 10, 10, 10)
        self.solutions_layout.setAlignment(Qt.AlignTop)

        self.setCentralWidget(plot_container)

    def validate_function(self, input_label: QLineEdit, error_label: QLabel):
        """
        Validate the function input using the lexer.

        Args:
            input_label (QLineEdit): The input field for the function.
            error_label (QLabel): The label to display validation errors.
        """
        try:
            Lexer(input_label.text().strip())
            error_label.setText("")
            if input_label is self.f1_input:
                self.f1_valid = True
            elif input_label is self.f2_input:
                self.f2_valid = True
        except LexerError as e:
            error_label.setText(e.message)
            if input_label is self.f1_input:
                self.f1_valid = False
            elif input_label is self.f2_input:
                self.f2_valid = False

    def create_input_section(self, default_color: str = "#ff0000"):
        """
        Create an input section for a function.

        Args:
            default_color (str): The default color for the function plot.

        Returns:
            tuple: A tuple containing the layout, input field, error label, and color button.
        """
        section = QVBoxLayout()
        section.setSpacing(0)

        input_container = QHBoxLayout()
        input_container.setSpacing(4)

        color = QColor(default_color)

        color_button = QPushButton()
        color_button.setFixedSize(25, 25)
        color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {color.darker(110).name()};
            }}
        """)
        color_button.setToolTip("Pick Color")
        color_button.clicked.connect(
            lambda: self.show_color_picker(color_button))
        color_button.setFocusPolicy(Qt.NoFocus)
        color_button.setCursor(Qt.PointingHandCursor)

        input_field = QLineEdit()
        input_field.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 2px solid #ccc;
                border-radius: 4px;
                font-size:16px
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        input_field.installEventFilter(self)
        input_field.setPlaceholderText("Enter a function of x (e.g. x^2+3)")

        input_container.addWidget(color_button)
        input_container.addWidget(input_field)

        error_label = QLabel()
        error_label.setStyleSheet("color: red; font-size: 16px;")

        input_field.textChanged.connect(
            lambda: self.validate_function(input_field, error_label))

        section.addLayout(input_container)
        section.addWidget(error_label)
        return section, input_field, error_label, color_button

    def disable_inputs(self):
        """Disable all interactive elements during processing"""
        self.f1_input.setEnabled(False)
        self.f2_input.setEnabled(False)
        self.f1_color_button.setEnabled(False)
        self.f2_color_button.setEnabled(False)
        for button in self.findChildren(QPushButton):
            button.setEnabled(False)

    def enable_inputs(self):
        """Re-enable all interactive elements after processing"""
        self.f1_input.setEnabled(True)
        self.f2_input.setEnabled(True)
        self.f1_color_button.setEnabled(True)
        self.f2_color_button.setEnabled(True)
        for button in self.findChildren(QPushButton):
            button.setEnabled(True)

    def show_color_picker(self, color_button):
        """
        Show a color picker dialog and update the function color.

        Args:
            color_button: The button whose color is being changed.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            color_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: none;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {color.darker(110).name()};
                }}
            """)

            f1_color = self.f1_color_button.palette().button().color().name()
            f2_color = self.f2_color_button.palette().button().color().name()
            self.plot_manager.update_colors(f1_color, f2_color)

    def update_intersection_display(self, intersection_points: list[float], is_same: bool):
        """
        Update the display of intersection points.

        Args:
            intersection_points (list[float]): The list of intersection points.
            is_same (bool): Whether the two functions are the same.
        """
        self.delete_solutions()
        height = 0
        if is_same:
            label = QLabel("The functions are the same.")
            self.solutions_layout.addWidget(label)
            height += label.sizeHint().height()
        else:
            if intersection_points:
                solutions_title = QLabel("Solutions")
                solutions_title.setStyleSheet("""
                    QLabel {
                        font-size: 16px;
                        font-weight: bold;
                        color: #212529;
                    }
                """)
                height += solutions_title.sizeHint().height()
                self.solutions_layout.addWidget(solutions_title)

                f1_str = self.f1_input.text().strip()
                evaluate = evaluator_function(
                    parse_expression(f1_str))

                for x in intersection_points:
                    y = round(evaluate(x), 4)+0
                    x = round(x, 4)
                    label = QLabel(f"x = {x}, y = {y}")
                    label.setStyleSheet("QLabel{font-size:16px;}")
                    height += label.sizeHint().height()
                    self.solutions_layout.addWidget(label)
            else:
                label = QLabel("No intersection points found")
                self.solutions_layout.addWidget(label)
        self.solutions_container.setFixedHeight(
            height+self.solutions_layout.getContentsMargins()[1]+self.solutions_layout.getContentsMargins()[3])
        self.update_solutions_container_position()
        self.solutions_container.show()

    def update_solutions_container_position(self):
        """
        Update the position of the solutions container based on the window size.
        """
        window_width = self.width()
        window_height = self.height()
        container_width = self.solutions_container.width()
        container_height = self.solutions_container.height()
        self.solutions_container.move(
            window_width - container_width - 20, window_height - container_height - 20)

    def delete_solutions(self):
        for i in reversed(range(self.solutions_layout.count())):
            widget = self.solutions_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.solutions_container.hide()

    def plot_functions(self, intersection_points: list[float | int] = []):
        f1_str = self.f1_input.text().strip()
        f2_str = self.f2_input.text().strip()

        if not f1_str:
            self.f1_error_label.setText("Empty Function")
        if not f2_str:
            self.f2_error_label.setText("Empty Function")
        # Get current plot limits
        ax = self.canvas.figure.get_axes()[0]
        current_xlim = list(ax.get_xlim())
        current_ylim = list(ax.get_ylim())

        self.disable_inputs()

        # Create and start plot worker
        self.plot_worker = PlotWorker(
            f1_str, f2_str,
            current_xlim, current_ylim, intersection_points
        )
        self.plot_worker.signals.finished.connect(self.on_plot_complete)
        self.plot_worker.signals.error.connect(self.on_plot_error)
        QThreadPool.globalInstance().start(self.plot_worker)

    def solve_plot_functions(self):
        f1_str = self.f1_input.text().strip()
        f2_str = self.f2_input.text().strip()

        if not f1_str:
            self.f1_error_label.setText("Empty Function")
        if not f2_str:
            self.f2_error_label.setText("Empty Function")

        if not (f1_str and f2_str):
            self.plot_functions()
            return

        self.disable_inputs()

        # Create and start solver worker
        self.solver_worker = SolverWorker(f1_str, f2_str)
        self.solver_worker.signals.finished.connect(self.on_solve_complete)
        QThreadPool.globalInstance().start(self.solver_worker)

    def on_plot_complete(self, result: tuple[dict[str, Any], list[float], Callable[[int | float], int | float]]):
        plot_data, intersection_points, f1_evaluator = result

        self.plot_manager.update_plot(
            plot_data, intersection_points, f1_evaluator)

        self.enable_inputs()
        if self.plot_worker:
            self.plot_worker = None

    def on_plot_error(self, error: tuple[Exception, str]):
        e, input = error
        if input == "f1":
            if isinstance(e, UnknownFunctionError):
                self.f1_error_label.setText(str(e))
            elif isinstance(e, ParserError):
                self.f1_error_label.setText(str("Invalid Expression"))
        elif input == "f2":
            if isinstance(e, UnknownFunctionError):
                self.f2_error_label.setText(str(e))
            elif isinstance(e, ParserError):
                self.f2_error_label.setText(str("Invalid Expression"))

    def on_solve_complete(self, result: tuple[list[float], bool]):
        intersection_points, is_same = result
        self.update_intersection_display(intersection_points, is_same)

        # Start plotting after solving is complete
        self.plot_functions(intersection_points)

        if self.solver_worker:
            self.solver_worker = None
