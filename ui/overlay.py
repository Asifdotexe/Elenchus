"""PyQt6 Heads-Up Display (HUD) overlay for Elenchus (ἔλεγχος)."""

from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import Config
from core.pipeline import PipelineWorker
from ui.icons import get_icon, get_pixmap
from ui.waveform import MonochartMeter


class ElenchusOverlay(QWidget):
    """Draggable, frameless, minimal HUD overlay displaying Socratic debate refutations."""

    def __init__(self, config: Config, pipeline: PipelineWorker):
        """Initialize the HUD overlay window and widgets.

        :param config: Application configuration instance.
        :param pipeline: Pipeline worker instance providing signals.
        """
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
        """Construct ShadCN-inspired dark interface with Lucide icons and Monochart meters."""
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(12, 12, 12, 12)

        # Primary card container with directional top-down lighting
        self.card = QFrame()
        self.card.setObjectName("HUDCard")
        self.card.setStyleSheet("""
            QFrame#HUDCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #151518, stop:1 #0c0c0e);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
        """)

        # Soft diffused drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 6)
        self.card.setGraphicsEffect(shadow)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(16, 14, 16, 16)
        self.card_layout.setSpacing(12)

        # -------------------------------------------------------------
        # 1. Header Bar
        # -------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("StatusDot")
        self.status_dot.setStyleSheet("color: #10b981; font-size: 8px;")
        header_layout.addWidget(self.status_dot)

        self.title_label = QLabel("elenchus")
        self.title_label.setStyleSheet(
            "color: #fafafa; font-weight: 600; font-size: 13px; "
            "font-family: 'Inter', -apple-system, 'Segoe UI Variable Text', 'Segoe UI', sans-serif; "
            "letter-spacing: -0.01em;"
        )
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Latency badge pill
        self.latency_label = QLabel("")
        self.latency_label.setStyleSheet(
            "color: #71717a; font-size: 10px; font-weight: 500; font-family: monospace; "
            "background-color: rgba(255, 255, 255, 0.04); padding: 2px 6px; border-radius: 4px;"
        )
        header_layout.addWidget(self.latency_label)

        # Mode toggle button with Lucide sliders icon
        self.mode_btn = QPushButton("Manual" if self.manual_mode else "Auto")
        self.mode_btn.setIcon(get_icon("sliders", color="#a1a1aa", size=13))
        self.mode_btn.setIconSize(QSize(13, 13))
        self.mode_btn.setToolTip("Toggle Manual Push-to-Listen vs Continuous Auto VAD")
        self.mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #18181b;
                color: #a1a1aa;
                border: 1px solid #27272a;
                border-radius: 5px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #27272a;
                color: #fafafa;
                border-color: #3f3f46;
            }
        """)
        self.mode_btn.clicked.connect(self._toggle_mode)
        header_layout.addWidget(self.mode_btn)

        # Collapse Button with Lucide minus icon
        self.collapse_btn = QPushButton()
        self.collapse_btn.setIcon(get_icon("minus", color="#71717a", size=13))
        self.collapse_btn.setIconSize(QSize(13, 13))
        self.collapse_btn.setFixedSize(22, 22)
        self.collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27272a;
            }
        """)
        self.collapse_btn.clicked.connect(self._toggle_collapse)
        header_layout.addWidget(self.collapse_btn)

        # Close Button with Lucide X icon
        self.close_btn = QPushButton()
        self.close_btn.setIcon(get_icon("x", color="#71717a", size=13))
        self.close_btn.setIconSize(QSize(13, 13))
        self.close_btn.setFixedSize(22, 22)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27272a;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)

        self.card_layout.addLayout(header_layout)

        # -------------------------------------------------------------
        # 2. Main Action Button & Monochart Audio Level Meter
        # -------------------------------------------------------------
        self.action_btn = QPushButton()
        self.action_btn.setFixedHeight(36)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_idle_button_style()
        self.action_btn.clicked.connect(self._on_action_button_clicked)
        self.card_layout.addWidget(self.action_btn)

        # Monocharts-inspired segmented audio activity meter
        self.audio_meter = MonochartMeter(bar_count=30)
        self.card_layout.addWidget(self.audio_meter)

        # Status row
        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            "color: #71717a; font-size: 11px; "
            "font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;"
        )
        status_row.addWidget(self.status_label)
        status_row.addStretch()

        shortcut_label = QLabel("Space")
        shortcut_label.setStyleSheet(
            "color: #71717a; font-size: 10px; font-weight: 500; font-family: monospace; "
            "background-color: #18181b; border: 1px solid #27272a; border-radius: 3px; padding: 1px 5px;"
        )
        status_row.addWidget(shortcut_label)
        self.card_layout.addLayout(status_row)

        # -------------------------------------------------------------
        # 3. Collapsible Content Container
        # -------------------------------------------------------------
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 4, 0, 0)
        content_layout.setSpacing(12)

        # Subtle 1px ShadCN separator
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(
            "border: none; background-color: rgba(255, 255, 255, 0.07); max-height: 1px;"
        )
        content_layout.addWidget(divider)

        # Opponent Transcript Section
        opponent_row = QHBoxLayout()
        opponent_row.setSpacing(6)
        opponent_icon = QLabel()
        opponent_icon.setPixmap(get_pixmap("message", color="#71717a", size=13))
        opponent_row.addWidget(opponent_icon)

        opponent_title = QLabel("Opponent Statement")
        opponent_title.setStyleSheet("color: #71717a; font-size: 11px; font-weight: 500;")
        opponent_row.addWidget(opponent_title)
        opponent_row.addStretch()
        content_layout.addLayout(opponent_row)

        self.transcript_label = QLabel("Awaiting opponent argument...")
        self.transcript_label.setWordWrap(True)
        self.transcript_label.setStyleSheet(
            "color: #a1a1aa; font-size: 12px; font-style: italic; line-height: 1.45; padding-left: 2px;"
        )
        content_layout.addWidget(self.transcript_label)

        # Finding & Rebuttal Card Container
        self.rebuttal_card = QFrame()
        self.rebuttal_card.setStyleSheet("""
            QFrame {
                background-color: #141417;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
        """)
        rebuttal_card_layout = QVBoxLayout(self.rebuttal_card)
        rebuttal_card_layout.setContentsMargins(14, 12, 14, 14)
        rebuttal_card_layout.setSpacing(8)

        # Finding Header Row
        finding_row = QHBoxLayout()
        finding_row.setSpacing(6)

        self.flaw_tag = QLabel("Finding")
        self.flaw_tag.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.06);
            color: #a1a1aa;
            font-size: 10px;
            font-weight: 500;
            padding: 2px 7px;
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        """)
        finding_row.addWidget(self.flaw_tag)

        self.flaw_label = QLabel("None detected yet")
        self.flaw_label.setStyleSheet("color: #e4e4e7; font-size: 12px; font-weight: 600;")
        self.flaw_label.setWordWrap(True)
        finding_row.addWidget(self.flaw_label, 1)
        rebuttal_card_layout.addLayout(finding_row)

        # Counter Rebuttal text
        self.counter_label = QLabel("Rebuttal will appear here after analysis.")
        self.counter_label.setWordWrap(True)
        self.counter_label.setStyleSheet(
            "color: #fafafa; font-size: 13px; font-weight: 400; line-height: 1.5;"
        )
        rebuttal_card_layout.addWidget(self.counter_label)

        content_layout.addWidget(self.rebuttal_card)
        self.card_layout.addWidget(self.content_widget)
        self.outer_layout.addWidget(self.card)

    def _apply_idle_button_style(self) -> None:
        """Apply visual styling for the idle/ready listen button state."""
        self.action_btn.setText("  Listen")
        self.action_btn.setIcon(get_icon("mic", color="#fafafa", size=14))
        self.action_btn.setIconSize(QSize(14, 14))
        self.action_btn.setStyleSheet("""
            QPushButton {
                background-color: #18181b;
                color: #fafafa;
                border: 1px solid #2e2e34;
                border-radius: 7px;
                font-weight: 500;
                font-size: 12px;
                letter-spacing: 0.1px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #222226;
                border: 1px solid #3f3f46;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #121215;
            }
        """)

    def _apply_recording_button_style(self) -> None:
        """Apply visual styling for the active recording button state."""
        self.action_btn.setText("  Stop listening")
        self.action_btn.setIcon(get_icon("square", color="#fca5a5", size=14))
        self.action_btn.setIconSize(QSize(14, 14))
        self.action_btn.setStyleSheet("""
            QPushButton {
                background-color: #261215;
                color: #fca5a5;
                border: 1px solid #7f1d1d;
                border-radius: 7px;
                font-weight: 500;
                font-size: 12px;
                letter-spacing: 0.1px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #321519;
                border: 1px solid #991b1b;
                color: #fecaca;
            }
            QPushButton:pressed {
                background-color: #1d0e10;
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
        """Handle Listen / Stop action button click."""
        if not self.manual_mode:
            self._toggle_mode()
        self.pipeline.toggle_manual_capture()

    def _on_recording_state_changed(self, is_recording: bool) -> None:
        """Update button text and styling based on recording state.

        :param is_recording: True if audio is actively recording, False otherwise.
        """
        if is_recording:
            self._apply_recording_button_style()
        else:
            self._apply_idle_button_style()

    def _toggle_mode(self) -> None:
        """Toggle between Manual button mode and Auto VAD silence-cut mode."""
        self.manual_mode = not self.manual_mode
        self.mode_btn.setText("Manual" if self.manual_mode else "Auto")
        self.pipeline.set_mode(self.manual_mode)

        if not self.manual_mode:
            self.action_btn.setText("  Auto detecting speech")
            self.action_btn.setIcon(get_icon("activity", color="#10b981", size=14))
            self.action_btn.setIconSize(QSize(14, 14))
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #121215;
                    color: #a1a1aa;
                    border: 1px solid #27272a;
                    border-radius: 7px;
                    font-size: 11px;
                    font-weight: 500;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #18181b;
                    color: #d4d4d8;
                }
            """)
        else:
            self._apply_idle_button_style()

    def _on_status_changed(self, text: str, level: str) -> None:
        """Update status label and dot color.

        :param text: Status description string.
        :param level: Status level indicator ('ok', 'busy', or 'error').
        """
        self.status_label.setText(text)
        if level == "ok":
            self.status_dot.setStyleSheet("color: #10b981; font-size: 8px;")
        elif level == "busy":
            self.status_dot.setStyleSheet("color: #f59e0b; font-size: 8px;")
        elif level == "error":
            self.status_dot.setStyleSheet("color: #ef4444; font-size: 8px;")

    def _on_audio_level(self, rms: float, is_speaking: bool) -> None:
        """Update Monochart segmented audio level meter.

        :param rms: Current audio energy level.
        :param is_speaking: True if speech is actively detected, False otherwise.
        """
        self.audio_meter.set_level(rms, is_speaking)

    def _on_transcript_received(self, text: str) -> None:
        """Display incoming speech transcript.

        :param text: Transcribed speech text from opponent.
        """
        self.transcript_label.setText(f'"{text}"')

    def _on_rebuttal_received(self, flaw: str, counter: str, latency: float) -> None:
        """Display extracted flaw, counter rebuttal, and latency with dynamic styling.

        :param flaw: Detected logical flaw or category label.
        :param counter: Generated counter-argument or explanatory note.
        :param latency: End-to-end processing latency in seconds.
        """
        self.flaw_label.setText(flaw)
        self.counter_label.setText(counter)
        self.latency_label.setText(f"{latency:.1f}s")

        is_non_argument = flaw.lower().startswith("none") or "incomplete" in flaw.lower()

        if is_non_argument:
            self.flaw_tag.setText("Note")
            self.flaw_tag.setStyleSheet("""
                background-color: rgba(255, 255, 255, 0.05);
                color: #71717a;
                font-size: 10px;
                font-weight: 500;
                padding: 2px 7px;
                border-radius: 4px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            """)
            self.flaw_label.setStyleSheet("color: #a1a1aa; font-size: 12px; font-weight: 500;")
            self.counter_label.setStyleSheet(
                "color: #71717a; font-size: 12px; font-style: italic; line-height: 1.45;"
            )
        else:
            self.flaw_tag.setText("Fallacy")
            self.flaw_tag.setStyleSheet("""
                background-color: rgba(239, 68, 68, 0.12);
                color: #f87171;
                font-size: 10px;
                font-weight: 600;
                padding: 2px 7px;
                border-radius: 4px;
                border: 1px solid rgba(239, 68, 68, 0.25);
            """)
            self.flaw_label.setStyleSheet("color: #fafafa; font-size: 12px; font-weight: 600;")
            self.counter_label.setStyleSheet(
                "color: #fafafa; font-size: 13px; font-weight: 400; line-height: 1.5;"
            )

    def _toggle_collapse(self) -> None:
        """Collapse or expand HUD content."""
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)
        self.action_btn.setVisible(not self.is_collapsed)
        self.audio_meter.setVisible(not self.is_collapsed)
        self.collapse_btn.setIcon(
            get_icon("activity" if self.is_collapsed else "minus", color="#71717a", size=13)
        )
        self.adjustSize()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard shortcut events.

        :param event: Key event triggered by user.
        """
        if event.key() == Qt.Key.Key_Space:
            self._on_action_button_clicked()
            event.accept()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Record window position offset when left mouse button is pressed for dragging.

        :param event: Mouse press event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Reposition window during mouse drag operations.

        :param event: Mouse move event.
        """
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def closeEvent(self, event) -> None:
        """Clean shutdown of worker threads and application.

        :param event: Window close event.
        """
        self.pipeline.stop()
        event.accept()
        app = QApplication.instance()
        if app is not None:
            app.quit()
