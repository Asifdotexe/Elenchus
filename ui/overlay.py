"""PyQt6 Heads-Up Display (HUD) overlay for aenf."""

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QColor
from PyQt6.QtWidgets import (
    QApplication,
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
        self.manual_mode = config.manual_mode

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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _build_ui(self) -> None:
        """Construct dark glassmorphic card interface."""
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(12, 12, 12, 12)

        # Glass container frame
        self.card = QFrame()
        self.card.setObjectName("HUDCard")
        self.card.setStyleSheet("""
            QFrame#HUDCard {
                background-color: rgba(18, 18, 24, 0.93);
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 12px;
            }
        """)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 6)
        self.card.setGraphicsEffect(shadow)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(16, 12, 16, 14)
        self.card_layout.setSpacing(10)

        # 1. Header Bar
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("StatusDot")
        self.status_dot.setStyleSheet("color: #00FFA3; font-size: 11px;")
        header_layout.addWidget(self.status_dot)

        title_label = QLabel("aenf // HUD")
        title_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px; font-family: 'Segoe UI', sans-serif; letter-spacing: 0.5px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Mode switch button (Manual vs Auto VAD)
        self.mode_btn = QPushButton("Manual" if self.manual_mode else "Auto VAD")
        self.mode_btn.setToolTip("Click to toggle Manual Button vs Auto Silence-detection")
        self.mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                color: #A0A0C0;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 4px;
                padding: 2px 7px;
                font-size: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.18);
                color: #FFFFFF;
            }
        """)
        self.mode_btn.clicked.connect(self._toggle_mode)
        header_layout.addWidget(self.mode_btn)

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

        # 2. Main Action Button (Wake / Listen / Cut & Analyze)
        self.action_btn = QPushButton("🎙️  Start Listening")
        self.action_btn.setFixedHeight(34)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_idle_button_style()
        self.action_btn.clicked.connect(self._on_action_button_clicked)
        self.card_layout.addWidget(self.action_btn)

        # Status text below action button
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #888899; font-size: 11px; font-family: 'Segoe UI', sans-serif;")
        self.card_layout.addWidget(self.status_label)

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

        # 3. Collapsible Content Container
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

        self.transcript_label = QLabel("Press 'Start Listening' to capture opponent...")
        self.transcript_label.setWordWrap(True)
        self.transcript_label.setStyleSheet("color: #C0C0D4; font-size: 12px; font-style: italic; line-height: 1.4;")
        content_layout.addWidget(self.transcript_label)

        # Flaw Badge Section
        flaw_container = QHBoxLayout()
        flaw_container.setSpacing(6)
        self.flaw_tag = QLabel("FLAW")
        self.flaw_tag.setStyleSheet("""
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
        flaw_container.addWidget(self.flaw_tag)
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

    def _apply_idle_button_style(self) -> None:
        """Style button for idle/ready state."""
        self.action_btn.setText("🎙️  Start Listening (Space)")
        self.action_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 255, 163, 0.15), stop:1 rgba(0, 229, 255, 0.15));
                color: #00FFA3;
                border: 1px solid rgba(0, 255, 163, 0.35);
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 255, 163, 0.28), stop:1 rgba(0, 229, 255, 0.28));
                border: 1px solid #00FFA3;
                color: #FFFFFF;
            }
        """)

    def _apply_recording_button_style(self) -> None:
        """Style button for active recording state."""
        self.action_btn.setText("⏹️  Stop & Analyze Now")
        self.action_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255, 92, 92, 0.30), stop:1 rgba(255, 140, 66, 0.30));
                color: #FFFFFF;
                border: 1px solid #FF5C5C;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255, 92, 92, 0.45), stop:1 rgba(255, 140, 66, 0.45));
                border: 1px solid #FFA0A0;
            }
        """)

    def _connect_signals(self) -> None:
        """Hook pipeline signals to GUI slots."""
        self.pipeline.status_changed.connect(self._on_status_changed)
        self.pipeline.audio_level.connect(self._on_audio_level)
        self.pipeline.transcript_received.connect(self._on_transcript_received)
        self.pipeline.rebuttal_received.connect(self._on_rebuttal_received)
        self.pipeline.recording_state_changed.connect(self._on_recording_state_changed)

    def _on_action_button_clicked(self) -> None:
        """Handle Listen / Stop button press."""
        if not self.manual_mode:
            # If in Auto mode, clicking switches to manual and triggers listen
            self._toggle_mode()
        self.pipeline.toggle_manual_capture()

    def _on_recording_state_changed(self, is_recording: bool) -> None:
        """Update button text and styling based on recording state."""
        if is_recording:
            self._apply_recording_button_style()
        else:
            self._apply_idle_button_style()

    def _toggle_mode(self) -> None:
        """Toggle between Manual button mode and Auto VAD silence-cut mode."""
        self.manual_mode = not self.manual_mode
        self.mode_btn.setText("Manual" if self.manual_mode else "Auto VAD")
        self.pipeline.set_mode(self.manual_mode)

        if not self.manual_mode:
            self.action_btn.setText("Auto VAD Mode (Listening)")
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.04);
                    color: #707088;
                    border: 1px dashed rgba(255, 255, 255, 0.15);
                    border-radius: 6px;
                    font-size: 11px;
                }
            """)
        else:
            self._apply_idle_button_style()

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
        """Display extracted flaw, counter rebuttal, and latency with dynamic styling."""
        self.flaw_label.setText(flaw)
        self.counter_label.setText(counter)
        self.latency_label.setText(f"⚡ {latency:.1f}s")

        is_non_argument = flaw.lower().startswith("none") or "incomplete" in flaw.lower()

        if is_non_argument:
            self.flaw_tag.setText("INFO")
            self.flaw_tag.setStyleSheet("""
                background-color: rgba(121, 134, 203, 0.20);
                color: #9FA8DA;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
            """)
            self.flaw_label.setStyleSheet("color: #B0BEC5; font-size: 12px; font-weight: 500;")
            self.counter_label.setStyleSheet("""
                color: #B0BEC5;
                font-size: 12px;
                font-style: italic;
                line-height: 1.4;
                background-color: rgba(255, 255, 255, 0.04);
                padding: 8px 10px;
                border-radius: 6px;
                border-left: 3px solid #78909C;
            """)
        else:
            self.flaw_tag.setText("FLAW")
            self.flaw_tag.setStyleSheet("""
                background-color: rgba(255, 92, 92, 0.20);
                color: #FF7070;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
            """)
            self.flaw_label.setStyleSheet("color: #FFA726; font-size: 12px; font-weight: bold;")
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

    def _toggle_collapse(self) -> None:
        """Collapse or expand HUD content."""
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)
        self.action_btn.setVisible(not self.is_collapsed)
        self.collapse_btn.setText("+" if self.is_collapsed else "—")
        self.adjustSize()

    # Keyboard shortcut (Space toggles listening)
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space:
            self._on_action_button_clicked()
            event.accept()
        else:
            super().keyPressEvent(event)

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
        """Clean shutdown of worker threads and application."""
        self.pipeline.stop()
        event.accept()
        app = QApplication.instance()
        if app is not None:
            app.quit()

