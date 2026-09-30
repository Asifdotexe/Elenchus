"""Minimalist monochrome audio activity meter inspired by Monocharts."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget


class MonochartMeter(QWidget):
    """Monochrome segmented audio level visualizer displaying discrete dynamic micro-bars."""

    def __init__(self, parent: QWidget | None = None, bar_count: int = 28):
        """Initialize the monochart meter with bar geometry.

        :param parent: Optional parent QWidget.
        :param bar_count: Total number of discrete vertical bars to render.
        """
        super().__init__(parent)
        self.bar_count = bar_count
        self.level: float = 0.0  # Normalized 0.0 - 1.0
        self.is_speaking: bool = False
        self.setFixedHeight(12)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_level(self, rms: float, is_speaking: bool) -> None:
        """Update live audio energy level and trigger repaint.

        :param rms: Raw Root Mean Square audio energy float.
        :param is_speaking: Flag indicating if speech threshold is currently exceeded.
        """
        # Scale RMS 0.0 - 0.08 to normalized 0.0 - 1.0
        normalized = min(1.0, max(0.0, rms / 0.07))
        # Smooth attack and decay
        self.level = max(normalized, self.level * 0.75 + normalized * 0.25)

        self.is_speaking = is_speaking
        self.update()

    def paintEvent(self, event) -> None:
        """Render discrete monochrome micro-bars with antialiasing.

        :param event: Qt paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0:
            painter.end()
            return

        total_gap = (self.bar_count - 1) * 2
        bar_width = max(2.0, (width - total_gap) / float(self.bar_count))
        active_count = int(round(self.level * self.bar_count))

        inactive_color = QColor(39, 39, 42, 160)  # Zinc 800 subtle
        if self.is_speaking:
            active_color = QColor(16, 185, 129, 230)  # Crisp emerald
        else:
            active_color = QColor(212, 212, 216, 200)  # Monochrome zinc-300

        for i in range(self.bar_count):
            x = i * (bar_width + 2.0)
            is_active = i < active_count

            # Modulate bar height slightly for organic spectrum appearance
            scale = 0.5 + 0.5 * (1.0 - abs(i - self.bar_count * 0.4) / (self.bar_count * 0.6))
            bar_height = max(3.0, height * scale if is_active else 3.0)
            y = (height - bar_height) / 2.0

            color = active_color if is_active else inactive_color
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_height), 1.0, 1.0)

        painter.end()
