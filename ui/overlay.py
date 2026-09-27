"""PyQt6 Heads-Up Display (HUD) overlay for aenf."""

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QFrame,
    QGraphicsDropShadowEffect,
)

from config import Config
from core.pipeline import PipelineWorker


class AenfOverlay(QWidget):
    """Draggable, frameless, translucent HUD overlay displaying live debate rebuttals."""

    def __init__(self, config: Config, pipeline: PipelineWorker):
        super().__init__()
        self.config = config
        self.pipeline = pipeline
        self.drag_position = QPoint()
        self.is_collapsed = False

        self._setup_window_properties()
        self._build_ui()
        self._connect_signals()

    def _setup_window_properties(self) -> None:
        """Configure frameless, always-on-top, translucent window flags."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(self.config.window_width)
        self.setWindowOpacity(self.config.opacity)

    def _build_ui(self) -> None:
        """Construct dark glassmorphic card interface."""
        # Main outer layout
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(12, 12, 12, 12)

        # Glass container frame
        self.card = QFrame()
        self.card.setObjectName("HUDCard")
        self.card.setStyleSheet("""
            QFrame#HUDCard {
                background-color: rgba(18, 18, 24, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 12px;
            }
        """)

        # Drop shadow for floating depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 6)
        self.card.setGraphicsEffect(shadow)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(16, 12, 16, 14)
        self.card_layout.setSpacing(10)

        # 1. Header Bar (Drag handle, Title, Status, Controls)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Status indicator dot
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("StatusDot")
        self.status_dot.setStyleSheet("color: #00FFA3; font-size: 11px;")
        header_layout.addWidget(self.status_dot)

        # Brand Title
        title_label = QLabel("aenf // HUD")
        title_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px; font-family: 'Segoe UI', sans-serif; letter-spacing: 0.5px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Status text
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #888899; font-size: 11px; font-family: 'Segoe UI', sans-serif;")
        header_layout.addWidget(self.status_label)

        # Latency badge
        self.latency_label = QLabel("")
        self.latency_label.setStyleSheet("color: #7986CB; font-size: 11px; font-weight: bold;")
        header_layout.addWidget(self.latency_label)

        # Minimize / Collapse Button
        self.collapse_btn = QPushButton("—")
        self.collapse_btn.setFixedSize(22, 22)
        self.collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                color: #B0B0C0;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.18);
                color: #FFFFFF;
            }
        """)
        self.collapse_btn.clicked.connect(self._toggle_collapse)
        header_layout.addWidget(self.collapse_btn)

        # Close Button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(22, 22)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 75, 75, 0.15);
                color: #FF7070;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 75, 75, 0.35);
                color: #FFFFFF;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)

        self.card_layout.addLayout(header_layout)

        # Audio VU / activity bar
        self.audio_bar = QProgressBar()
        self.audio_bar.setFixedHeight(3)
        self.audio_bar.setRange(0, 100)
        self.audio_bar.setValue(0)
        self.audio_bar.setTextVisible(False)
        self.audio_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.06);
                border: none;
                border-radius: 1px;
            }
            QProgressBar::chunk {
                background-color: #00FFA3;
                border-radius: 1px;
            }
        """)
        self.card_layout.addWidget(self.audio_bar)

        # 2. Collapsible Content Container
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 4, 0, 0)
        content_layout.setSpacing(8)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("border: none; background-color: rgba(255, 255, 255, 0.08); max-height: 1px;")
        content_layout.addWidget(divider)

        # Opponent Transcript Section
        transcript_header = QLabel("OPPONENT")
        transcript_header.setStyleSheet("color: #707088; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        content_layout.addWidget(transcript_header)

        self.transcript_label = QLabel("Awaiting speech...")
        self.transcript_label.setWordWrap(True)
        self.transcript_label.setStyleSheet("color: #C0C0D4; font-size: 12px; font-style: italic; line-height: 1.4;")
        content_layout.addWidget(self.transcript_label)

        # Flaw Badge Section
        flaw_container = QHBoxLayout()
        flaw_container.setSpacing(6)
        flaw_tag = QLabel("FLAW")
        flaw_tag.setStyleSheet("""
            background-color: rgba(255, 92, 92, 0.20);
            color: #FF7070;
            font-size: 10px;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
        """)
        self.flaw_label = QLabel("None detected yet")
        self.flaw_label.setStyleSheet("color: #FFA726; font-size: 12px; font-weight: bold;")
        self.flaw_label.setWordWrap(True)
        flaw_container.addWidget(flaw_tag)
        flaw_container.addWidget(self.flaw_label, 1)
        content_layout.addLayout(flaw_container)

        # Counter Rebuttal Section
        counter_header = QLabel("REBUTTAL")
        counter_header.setStyleSheet("color: #707088; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        content_layout.addWidget(counter_header)

        self.counter_label = QLabel("Listening for arguments...")
        self.counter_label.setWordWrap(True)
        self.counter_label.setStyleSheet("""
            color: #00FFA3;
            font-size: 13px;
            font-weight: 500;
            line-height: 1.4;
            background-color: rgba(0, 255, 163, 0.05);
            padding: 8px 10px;
            border-radius: 6px;
            border-left: 3px solid #00FFA3;
        """)
        content_layout.addWidget(self.counter_label)

        self.card_layout.addWidget(self.content_widget)
        self.outer_layout.addWidget(self.card)

    def _connect_signals(self) -> None:
        """Hook pipeline signals to GUI slots."""
        self.pipeline.status_changed.connect(self._on_status_changed)
        self.pipeline.audio_level.connect(self._on_audio_level)
        self.pipeline.transcript_received.connect(self._on_transcript_received)
        self.pipeline.rebuttal_received.connect(self._on_rebuttal_received)

    def _on_status_changed(self, text: str, level: str) -> None:
        """Update status label and dot color."""
        self.status_label.setText(text)
        if level == "ok":
            self.status_dot.setStyleSheet("color: #00FFA3; font-size: 11px;")
        elif level == "busy":
            self.status_dot.setStyleSheet("color: #FFA726; font-size: 11px;")
        elif level == "error":
            self.status_dot.setStyleSheet("color: #FF5C5C; font-size: 11px;")

    def _on_audio_level(self, rms: float, is_speaking: bool) -> None:
        """Update VU meter progress bar."""
        # Scale RMS typical range (0.0 to 0.1) into 0-100%
        val = min(100, int((rms / 0.08) * 100))
        self.audio_bar.setValue(val)
        if is_speaking:
            self.audio_bar.setStyleSheet("""
                QProgressBar { background-color: rgba(255, 255, 255, 0.06); border: none; border-radius: 1px; }
                QProgressBar::chunk { background-color: #00E5FF; border-radius: 1px; }
            """)
        else:
            self.audio_bar.setStyleSheet("""
                QProgressBar { background-color: rgba(255, 255, 255, 0.06); border: none; border-radius: 1px; }
                QProgressBar::chunk { background-color: #00FFA3; border-radius: 1px; }
            """)

    def _on_transcript_received(self, text: str) -> None:
        """Display incoming speech transcript."""
        self.transcript_label.setText(f'"{text}"')

    def _on_rebuttal_received(self, flaw: str, counter: str, latency: float) -> None:
        """Display extracted flaw, counter rebuttal, and latency."""
        self.flaw_label.setText(flaw)
        self.counter_label.setText(counter)
        self.latency_label.setText(f"⚡ {latency:.1f}s")

    def _toggle_collapse(self) -> None:
        """Collapse or expand HUD content."""
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)
        self.collapse_btn.setText("+" if self.is_collapsed else "—")
        self.adjustSize()

    # Window drag events
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def closeEvent(self, event) -> None:
        """Clean shutdown of worker threads."""
        self.pipeline.stop()
        event.accept()
