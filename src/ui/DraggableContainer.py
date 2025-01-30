from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget


class DraggableContainer(QWidget):
    def __init__(self, parent=None):
        """
        Initialize the DraggableContainer widget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        # Enable styled backgrounds for custom styling (e.g., via CSS)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.dragging = False
        self.offset = None
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        """
        Handle mouse press events.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """
        Handle mouse move events.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if self.dragging and self.offset:
            new_pos = self.mapToParent(event.pos() - self.offset)

            # Keep the widget within the parent's bounds
            new_pos.setX(
                max(0, min(new_pos.x(), self.parent().width() - self.width())))
            new_pos.setY(
                max(0, min(new_pos.y(), self.parent().height() - self.height())))
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None
            self.setCursor(Qt.OpenHandCursor)
