"""PyQt6 Heads-Up Display (HUD) overlay for Elenchus (ἔλεγχος)."""

from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
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
        """Construct Hyperstudio-inspired dark interface with precision hairline borders."""
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(4, 4, 4, 4)

        # Primary card container (Carbon #080808 with 1px Graphite #212121 hairline border)
        self.card = QFrame()
        self.card.setObjectName("HUDCard")
        self.card.setStyleSheet("""
            QFrame#HUDCard {
                background-color: #080808;
                border: 1px solid #212121;
                border-radius: 8px;
            }
        """)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(18, 16, 18, 16)
        self.card_layout.setSpacing(12)

        # -------------------------------------------------------------
        # 1. Header Bar
        # -------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Pulse Green status indicator LED
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("StatusDot")
        self.status_dot.setStyleSheet("color: #98ff38; font-size: 8px;")
        header_layout.addWidget(self.status_dot)

        self.title_label = QLabel("elenchus")
        self.title_label.setStyleSheet(
            "color: #f3f3f3; font-weight: 500; font-size: 13px; "
            "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; "
            "letter-spacing: -0.01em;"
        )
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Topmost HUD label
        hud_badge = QLabel("TOPMOST HUD")
        hud_badge.setStyleSheet(
            "color: #9c9c9c; font-size: 10px; font-weight: 500; "
            "font-family: 'JetBrains Mono', 'IBM Plex Mono', 'Cascadia Code', monospace; "
            "letter-spacing: 0.05em;"
        )
        header_layout.addWidget(hud_badge)

        # Collapse Button with Lucide minus icon
        self.collapse_btn = QPushButton()
        self.collapse_btn.setIcon(get_icon("minus", color="#9c9c9c", size=12))
        self.collapse_btn.setIconSize(QSize(12, 12))
        self.collapse_btn.setFixedSize(20, 20)
        self.collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #212121;
            }
        """)
        self.collapse_btn.clicked.connect(self._toggle_collapse)
        header_layout.addWidget(self.collapse_btn)

        # Close Button with Lucide X icon
        self.close_btn = QPushButton()
        self.close_btn.setIcon(get_icon("x", color="#9c9c9c", size=12))
        self.close_btn.setIconSize(QSize(12, 12))
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #212121;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)

        self.card_layout.addLayout(header_layout)

        # -------------------------------------------------------------
        # 2. Action Bar & Mode Pill
        # -------------------------------------------------------------
        self.action_bar = QFrame()
        self.action_bar.setObjectName("ActionBar")
        self.action_bar.setStyleSheet("""
            QFrame#ActionBar {
                background-color: #101010;
                border: 1px solid #212121;
                border-radius: 4px;
            }
        """)
        action_bar_layout = QHBoxLayout(self.action_bar)
        action_bar_layout.setContentsMargins(10, 6, 10, 6)
        action_bar_layout.setSpacing(8)

        # Action Trigger (Listen / Stop)
        self.action_btn = QPushButton()
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_idle_button_style()
        self.action_btn.clicked.connect(self._on_action_button_clicked)
        action_bar_layout.addWidget(self.action_btn, 1)

        # Mode toggle pill (Manual Mode / Auto Mode)
        self.mode_btn = QPushButton("Manual Mode" if self.manual_mode else "Auto Mode")
        self.mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_btn.setToolTip("Toggle Manual Push-to-Listen vs Continuous Auto VAD")
        self.mode_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.06);
                color: #9c9c9c;
                border: 1px solid #212121;
                border-radius: 4px;
                padding: 2px 7px;
                font-size: 10px;
                font-family: 'JetBrains Mono', 'IBM Plex Mono', 'Cascadia Code', monospace;
                font-weight: 500;
                letter-spacing: 0.02em;
            }
            QPushButton:hover {
                border-color: #474747;
                color: #f3f3f3;
            }
        """)
        self.mode_btn.clicked.connect(self._toggle_mode)
        action_bar_layout.addWidget(self.mode_btn)

        self.card_layout.addWidget(self.action_bar)

        # Monochart discrete audio activity meter (30 bars)
        self.audio_meter = MonochartMeter(bar_count=30)
        self.card_layout.addWidget(self.audio_meter)

        # -------------------------------------------------------------
        # 3. Collapsible Content Container
        # -------------------------------------------------------------
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        # Hairline divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("border: none; background-color: #212121; max-height: 1px;")
        content_layout.addWidget(divider)

        # Opponent Transcript Section
        opponent_row = QHBoxLayout()
        opponent_row.setSpacing(6)
        opponent_icon = QLabel()
        opponent_icon.setPixmap(get_pixmap("message", color="#9c9c9c", size=12))
        opponent_row.addWidget(opponent_icon)

        opponent_title = QLabel("OPPONENT STATEMENT")
        opponent_title.setStyleSheet(
            "color: #9c9c9c; font-size: 11px; font-weight: 500; "
            "font-family: 'JetBrains Mono', 'IBM Plex Mono', 'Cascadia Code', monospace; "
            "letter-spacing: 0.05em;"
        )
        opponent_row.addWidget(opponent_title)
        opponent_row.addStretch()
        content_layout.addLayout(opponent_row)

        self.transcript_label = QLabel("Awaiting opponent argument...")
        self.transcript_label.setTextFormat(Qt.TextFormat.PlainText)
        self.transcript_label.setWordWrap(True)
        self.transcript_label.setStyleSheet(
            "color: #c1c1c1; font-size: 13px; font-style: italic; line-height: 1.45; padding-left: 2px;"
        )
        content_layout.addWidget(self.transcript_label)

        # Finding & Rebuttal Card Container
        self.rebuttal_card = QFrame()
        self.rebuttal_card.setObjectName("RebuttalCard")
        self.rebuttal_card.setStyleSheet("""
            QFrame#RebuttalCard {
                background-color: #101010;
                border: 1px solid #212121;
                border-radius: 8px;
            }
        """)
        rebuttal_card_layout = QVBoxLayout(self.rebuttal_card)
        rebuttal_card_layout.setContentsMargins(14, 12, 14, 12)
        rebuttal_card_layout.setSpacing(8)

        # Finding Header Row
        finding_row = QHBoxLayout()
        finding_row.setSpacing(8)

        self.flaw_tag = QLabel("FINDING")
        self.flaw_tag.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.06);
            color: #9c9c9c;
            font-size: 10px;
            font-weight: 500;
            font-family: 'JetBrains Mono', 'IBM Plex Mono', 'Cascadia Code', monospace;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #212121;
            letter-spacing: 0.04em;
        """)
        finding_row.addWidget(self.flaw_tag)

        self.flaw_label = QLabel("None detected yet")
        self.flaw_label.setTextFormat(Qt.TextFormat.PlainText)
        self.flaw_label.setStyleSheet("color: #9c9c9c; font-size: 12px; font-weight: 500;")
        self.flaw_label.setWordWrap(True)
        finding_row.addWidget(self.flaw_label, 1)
        rebuttal_card_layout.addLayout(finding_row)

        # Counter Rebuttal text
        self.counter_label = QLabel("Rebuttal will appear here after analysis.")
        self.counter_label.setTextFormat(Qt.TextFormat.PlainText)
        self.counter_label.setWordWrap(True)
        self.counter_label.setStyleSheet(
            "color: #f3f3f3; font-size: 13px; font-weight: 400; line-height: 1.5;"
        )
        rebuttal_card_layout.addWidget(self.counter_label)

        # Footer Meta Row (Status & Latency)
        card_divider = QFrame()
        card_divider.setFrameShape(QFrame.Shape.HLine)
        card_divider.setStyleSheet("border: none; background-color: #212121; max-height: 1px;")
        rebuttal_card_layout.addWidget(card_divider)

        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(0, 2, 0, 0)

        self.status_label = QLabel("Ready")
        self.status_label.setTextFormat(Qt.TextFormat.PlainText)
        self.status_label.setStyleSheet(
            "color: #9c9c9c; font-size: 11px; "
            "font-family: 'JetBrains Mono', 'IBM Plex Mono', 'Cascadia Code', monospace;"
        )
        footer_row.addWidget(self.status_label)
        footer_row.addStretch()

        self.latency_label = QLabel("")
        self.latency_label.setTextFormat(Qt.TextFormat.PlainText)
        self.latency_label.setStyleSheet(
            "color: #9c9c9c; font-size: 11px; "
            "font-family: 'JetBrains Mono', 'IBM Plex Mono', 'Cascadia Code', monospace;"
        )
        footer_row.addWidget(self.latency_label)
        rebuttal_card_layout.addLayout(footer_row)

        content_layout.addWidget(self.rebuttal_card)
        self.card_layout.addWidget(self.content_widget)
        self.outer_layout.addWidget(self.card)

    def _apply_idle_button_style(self) -> None:
        """Apply visual styling for the idle/ready listen button state."""
        self.action_btn.setText("  Listen (Click or Space)")
        self.action_btn.setIcon(get_icon("mic", color="#f3f3f3", size=13))
        self.action_btn.setIconSize(QSize(13, 13))
        self.action_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #f3f3f3;
                border: none;
                font-size: 12px;
                font-weight: 400;
                text-align: left;
                padding: 2px 0px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)

    def _apply_recording_button_style(self) -> None:
        """Apply visual styling for the active recording button state."""
        self.action_btn.setText("  Stop listening")
        self.action_btn.setIcon(get_icon("square", color="#ef4444", size=13))
        self.action_btn.setIconSize(QSize(13, 13))
        self.action_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ef4444;
                border: none;
                font-size: 12px;
                font-weight: 500;
                text-align: left;
                padding: 2px 0px;
            }
            QPushButton:hover {
                color: #f87171;
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
        self.mode_btn.setText("Manual Mode" if self.manual_mode else "Auto Mode")
        self.pipeline.set_mode(self.manual_mode)

        if not self.manual_mode:
            self.action_btn.setText("  Auto detecting speech")
            self.action_btn.setIcon(get_icon("activity", color="#98ff38", size=13))
            self.action_btn.setIconSize(QSize(13, 13))
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #9c9c9c;
                    border: none;
                    font-size: 12px;
                    font-weight: 400;
                    text-align: left;
                    padding: 2px 0px;
                }
                QPushButton:hover {
                    color: #f3f3f3;
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
            self.status_dot.setStyleSheet("color: #98ff38; font-size: 8px;")
        elif level == "busy":
            self.status_dot.setStyleSheet("color: #d97706; font-size: 8px;")
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
        self.latency_label.setText(f"{latency:.1f}s latency")

        is_non_argument = flaw.lower().startswith("none") or "incomplete" in flaw.lower()

        if is_non_argument:
            self.flaw_tag.setText("NOTE")
            self.flaw_tag.setStyleSheet("""
                background-color: rgba(255, 255, 255, 0.06);
                color: #9c9c9c;
                font-size: 10px;
                font-weight: 500;
                font-family: 'JetBrains Mono', 'IBM Plex Mono', 'Cascadia Code', monospace;
                padding: 2px 6px;
                border-radius: 4px;
                border: 1px solid #212121;
                letter-spacing: 0.04em;
            """)
            self.flaw_label.setStyleSheet("color: #9c9c9c; font-size: 12px; font-weight: 500;")
            self.counter_label.setStyleSheet(
                "color: #9c9c9c; font-size: 13px; font-style: italic; line-height: 1.45;"
            )
        else:
            self.flaw_tag.setText("FINDING")
            self.flaw_tag.setStyleSheet("""
                background-color: rgba(239, 68, 68, 0.12);
                color: #ef4444;
                font-size: 10px;
                font-weight: 500;
                font-family: 'JetBrains Mono', 'IBM Plex Mono', 'Cascadia Code', monospace;
                padding: 2px 6px;
                border-radius: 4px;
                border: 1px solid rgba(239, 68, 68, 0.25);
                letter-spacing: 0.04em;
            """)
            self.flaw_label.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: 500;")
            self.counter_label.setStyleSheet(
                "color: #f3f3f3; font-size: 13px; font-weight: 400; line-height: 1.5;"
            )

    def _toggle_collapse(self) -> None:
        """Collapse or expand HUD content."""
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)
        self.action_bar.setVisible(not self.is_collapsed)
        self.audio_meter.setVisible(not self.is_collapsed)
        self.collapse_btn.setIcon(
            get_icon("activity" if self.is_collapsed else "minus", color="#9c9c9c", size=12)
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
