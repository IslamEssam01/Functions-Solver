import pytest
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QPushButton, QWidget

from .plotter import FunctionsSolver


@pytest.fixture
def app(qtbot):
    window = FunctionsSolver()
    qtbot.addWidget(window)
    window.show()
    return window


def wait_for_plot_update(qtbot, app, expected_lines):
    def check_plot():
        return len(app.canvas.figure.axes[0].lines) == expected_lines
    qtbot.waitUntil(check_plot, timeout=10000)


def wait_for_intersection_points(qtbot, app):
    def check_intersections():
        solutions_container = app.findChild(QWidget, "solutions_container")
        return len([w for w in solutions_container.findChildren(QLabel)
                   if any(x in w.text() for x in ["x =", "No intersection", "same"])]) > 0
    qtbot.waitUntil(check_intersections, timeout=10000)


def test_initial_state(app):
    assert app.f1_valid == True
    assert app.f2_valid == True
    assert app.f1_input.text() == ""
    assert app.f2_input.text() == ""
    assert app.f1_error_label.text() == ""
    assert app.f2_error_label.text() == ""


def test_valid_function_input(app, qtbot):
    qtbot.keyClicks(app.f1_input, "x^2")
    qtbot.keyClicks(app.f2_input, "2*x + 1")

    assert app.f1_valid == True
    assert app.f2_valid == True
    assert app.f1_error_label.text() == ""
    assert app.f2_error_label.text() == ""


def test_invalid_function_input(app, qtbot):
    qtbot.keyClicks(app.f1_input, "x,")
    qtbot.keyClicks(app.f2_input, "xx")

    assert app.f1_valid == False
    assert app.f2_valid == True
    assert app.f1_error_label.text() == "Invalid character"
    assert app.f2_error_label.text() == ""


def test_plot_single_function(app, qtbot):
    qtbot.keyClicks(app.f1_input, "x^2")

    plot_button = app.findChild(QPushButton, "plot_button")
    assert plot_button is not None, "Plot button not found"

    qtbot.mouseClick(plot_button, Qt.LeftButton)
    wait_for_plot_update(qtbot, app, 3)

    fig = app.canvas.figure
    ax = fig.axes[0]
    assert len(ax.lines) == 3  # One function plotted
    assert ax.get_xlim() == (-10, 10)  # Default view
    assert ax.get_ylim() == (-10, 10)  # Default view


def test_plot_two_functions(app, qtbot):
    qtbot.keyClicks(app.f1_input, "x^2")
    qtbot.keyClicks(app.f2_input, "2*x + 1")

    plot_button = app.findChild(QPushButton, "plot_button")
    qtbot.mouseClick(plot_button, Qt.LeftButton)
    wait_for_plot_update(qtbot, app, 4)

    fig = app.canvas.figure
    ax = fig.axes[0]
    assert len(ax.lines) == 4  # Two functions plotted


def test_solve_intersecting_functions(app, qtbot):
    qtbot.keyClicks(app.f1_input, "x^2")
    qtbot.keyClicks(app.f2_input, "2*x + 1")

    solve_button = app.findChild(QPushButton, "solve_button")
    qtbot.mouseClick(solve_button, Qt.LeftButton)
    wait_for_intersection_points(qtbot, app)

    solutions_container = app.findChild(QWidget, "solutions_container")
    intersection_labels = [widget for widget in solutions_container.findChildren(QLabel)
                           if any(x in widget.text() for x in ["x =", "No intersection", "same"])]
    assert len(intersection_labels) == 2  # Should find 2 intersection points


def test_solve_non_intersecting_functions(app, qtbot):
    qtbot.keyClicks(app.f1_input, "x^2")
    qtbot.keyClicks(app.f2_input, "-3")

    solve_button = app.findChild(QPushButton, "solve_button")
    qtbot.mouseClick(solve_button, Qt.LeftButton)
    wait_for_intersection_points(qtbot, app)

    solutions_container = app.findChild(QWidget, "solutions_container")
    intersection_labels = [widget for widget in solutions_container.findChildren(QLabel)
                           if any(x in widget.text() for x in ["x =", "No intersection", "same"])]
    assert len(intersection_labels) == 1  # Should find 1 intersection points
    assert intersection_labels[0].text() == "No intersection points found"


def test_function_input_validation(app, qtbot):
    qtbot.keyClicks(app.f1_input, "x^2")
    qtbot.keyClicks(app.f2_input, "2*x + 1")

    assert app.f1_valid == True
    assert app.f2_valid == True
    assert app.f1_error_label.text() == ""
    assert app.f2_error_label.text() == ""

    for _ in range(3):  # Adjust the range as needed
        qtbot.keyClick(app.f1_input, Qt.Key_Backspace)
    qtbot.keyClicks(app.f1_input, "invalidfunction")
    plot_button = app.findChild(QPushButton, "plot_button")
    assert plot_button is not None, "Plot button not found"

    # Click the plot button
    qtbot.mouseClick(plot_button, Qt.LeftButton)
    wait_for_plot_update(qtbot, app, 3)

    assert app.f1_error_label.text() == "Invalid Expression"
    qtbot.keyClick(app.f1_input, 'a', Qt.ControlModifier)
    qtbot.keyClick(app.f1_input, Qt.Key_Backspace)
    qtbot.keyClicks(app.f1_input, "x^2")
    qtbot.mouseClick(plot_button, Qt.LeftButton)
    wait_for_plot_update(qtbot, app, 4)
    assert app.f1_error_label.text() == ""
