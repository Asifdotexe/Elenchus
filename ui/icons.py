"""Lucide icon vector renderer for PyQt6 matching ShadCN design system."""

from PyQt6.QtCore import QByteArray
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

LUCIDE_SVGS = {
    "mic": (
        '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>'
        '<path d="M19 10v2a7 7 0 0 1-14 0v-2"/>'
        '<line x1="12" x2="12" y1="19" y2="22"/>'
    ),
    "square": '<rect width="14" height="14" x="5" y="5" rx="2"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/>',
    "sliders": (
        '<line x1="4" x2="4" y1="21" y2="14"/>'
        '<line x1="4" x2="4" y1="10" y2="3"/>'
        '<line x1="12" x2="12" y1="21" y2="12"/>'
        '<line x1="12" x2="12" y1="8" y2="3"/>'
        '<line x1="20" x2="20" y1="21" y2="16"/>'
        '<line x1="20" x2="20" y1="12" y2="3"/>'
        '<line x1="2" x2="6" y1="14" y2="14"/>'
        '<line x1="10" x2="14" y1="8" y2="8"/>'
        '<line x1="18" x2="22" y1="16" y2="16"/>'
    ),
    "minus": '<path d="M5 12h14"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
}


def get_pixmap(
    name: str, color: str = "#a1a1aa", size: int = 16, stroke_width: float = 2.0
) -> QPixmap:
    """Render a Lucide icon into a transparent QPixmap.

    :param name: Name of the Lucide icon.
    :param color: Stroke color hex string.
    :param size: Dimension in pixels for width and height.
    :param stroke_width: Width of icon stroke lines.
    :return: Rendered QPixmap instance.
    """
    if name not in LUCIDE_SVGS:
        return QPixmap()
    inner = LUCIDE_SVGS[name]
    svg_str = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )
    renderer = QSvgRenderer(QByteArray(svg_str.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def get_icon(name: str, color: str = "#a1a1aa", size: int = 16, stroke_width: float = 2.0) -> QIcon:
    """Render a Lucide icon into a QIcon.

    :param name: Name of the Lucide icon.
    :param color: Stroke color hex string.
    :param size: Dimension in pixels for width and height.
    :param stroke_width: Width of icon stroke lines.
    :return: Rendered QIcon instance.
    """
    if name not in LUCIDE_SVGS:
        return QIcon()
    return QIcon(get_pixmap(name, color=color, size=size, stroke_width=stroke_width))
