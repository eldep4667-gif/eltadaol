"""
Professional dark stylesheet for JobHunter
"""


DARK_STYLESHEET = """
/* ═══════════════════════════════════════════════════════════
   BASE APPLICATION STYLES
═══════════════════════════════════════════════════════════ */

QMainWindow, QWidget {
    background-color: #0F172A;
    color: #E2E8F0;
    font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
}

/* ═══════════════════════════════════════════════════════════
   SEARCH PANEL
═══════════════════════════════════════════════════════════ */

#SearchPanel {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #1A1F35,
        stop:1 #0F172A
    );
    border-bottom: 1px solid #1E293B;
}

/* ═══════════════════════════════════════════════════════════
   INPUT FIELDS
═══════════════════════════════════════════════════════════ */

#SearchInput, #FilterInput {
    background: #1E293B;
    color: #E2E8F0;
    border: 1.5px solid #334155;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    selection-background-color: #7C3AED;
}

#SearchInput:focus, #FilterInput:focus {
    border-color: #7C3AED;
    background: #1E2A3B;
    outline: none;
}

#SearchInput:hover, #FilterInput:hover {
    border-color: #475569;
}

/* ═══════════════════════════════════════════════════════════
   COMBO BOXES
═══════════════════════════════════════════════════════════ */

#SearchCombo {
    background: #1E293B;
    color: #E2E8F0;
    border: 1.5px solid #334155;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    min-height: 36px;
}

#SearchCombo:focus {
    border-color: #7C3AED;
}

#SearchCombo::drop-down {
    border: none;
    width: 24px;
}

#SearchCombo::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #94A3B8;
}

QComboBox QAbstractItemView {
    background: #1E293B;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 6px;
    selection-background-color: #7C3AED;
    outline: none;
    padding: 4px;
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════ */

#SearchButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #7C3AED,
        stop:1 #6D28D9
    );
    color: white;
    border: none;
    border-radius: 9px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

#SearchButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B5CF6,
        stop:1 #7C3AED
    );
}

#SearchButton:pressed {
    background: #5B21B6;
    padding-top: 10px;
    padding-bottom: 6px;
}

#SearchButton:disabled {
    background: #334155;
    color: #64748B;
}

#StopButton {
    background: #1E293B;
    color: #F87171;
    border: 1.5px solid #F87171;
    border-radius: 8px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: bold;
}

#StopButton:hover {
    background: #3B1818;
    color: #FCA5A5;
}

#StopButton:disabled {
    color: #475569;
    border-color: #334155;
    background: #1E293B;
}

#ActionButton {
    background: #1E293B;
    color: #3B82F6;
    border: 1.5px solid #3B82F6;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: bold;
}

#ActionButton:hover {
    background: #172554;
    color: #60A5FA;
    border-color: #60A5FA;
}

#FavButton {
    background: #1E293B;
    color: #FFD700;
    border: 1.5px solid #F59E0B;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: bold;
}

#FavButton:hover {
    background: #2D2010;
    color: #FBBF24;
}

#ExportButton {
    background: #1E293B;
    color: #10B981;
    border: 1.5px solid #10B981;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: bold;
}

#ExportButton:hover {
    background: #0D2B1F;
    color: #34D399;
    border-color: #34D399;
}

#RefreshButton {
    background: #1E293B;
    color: #94A3B8;
    border: 1.5px solid #334155;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
}

#RefreshButton:hover {
    background: #243044;
    color: #E2E8F0;
    border-color: #475569;
}

#DangerButton {
    background: #1E293B;
    color: #F87171;
    border: 1.5px solid #EF4444;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
}

#DangerButton:hover {
    background: #2D1010;
    color: #FCA5A5;
}

/* ═══════════════════════════════════════════════════════════
   JOB TABLE
═══════════════════════════════════════════════════════════ */

#TableContainer {
    background: #0F172A;
}

QTableWidget {
    background: #0F172A;
    alternate-background-color: #111827;
    gridline-color: transparent;
    border: none;
    border-radius: 0;
    color: #CBD5E1;
    font-size: 12px;
    selection-background-color: #1E1B4B;
    selection-color: #E2E8F0;
    outline: none;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1E293B;
}

QTableWidget::item:selected {
    background: #1E1B4B;
    color: #E2E8F0;
    border-left: 3px solid #7C3AED;
}

QTableWidget::item:hover {
    background: #172554;
}

QHeaderView::section {
    background: #0F172A;
    color: #64748B;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #7C3AED;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

QHeaderView::section:hover {
    background: #1E293B;
    color: #94A3B8;
}

QHeaderView {
    background: #0F172A;
}

/* ═══════════════════════════════════════════════════════════
   STATUS PANEL
═══════════════════════════════════════════════════════════ */

#StatusPanel {
    background: #0A0F1E;
    border-top: 1px solid #1E293B;
    min-height: 56px;
    max-height: 56px;
}

/* ═══════════════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════════════ */

#SearchProgress {
    background: #1E293B;
    border: none;
    border-radius: 3px;
    height: 6px;
    max-height: 6px;
}

#SearchProgress::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #7C3AED,
        stop:1 #10B981
    );
    border-radius: 3px;
}

/* ═══════════════════════════════════════════════════════════
   SCROLLBARS
═══════════════════════════════════════════════════════════ */

QScrollBar:vertical {
    background: #0F172A;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #0F172A;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #334155;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #475569;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ═══════════════════════════════════════════════════════════
   CHECKBOXES
═══════════════════════════════════════════════════════════ */

QCheckBox {
    color: #94A3B8;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #334155;
    border-radius: 4px;
    background: #1E293B;
}

QCheckBox::indicator:checked {
    background: #7C3AED;
    border-color: #7C3AED;
}

QCheckBox::indicator:hover {
    border-color: #7C3AED;
}

/* ═══════════════════════════════════════════════════════════
   MESSAGE BOXES
═══════════════════════════════════════════════════════════ */

QMessageBox {
    background: #1E293B;
}

QMessageBox QLabel {
    color: #E2E8F0;
}

QMessageBox QPushButton {
    background: #7C3AED;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background: #8B5CF6;
}

/* ═══════════════════════════════════════════════════════════
   TOOLTIPS
═══════════════════════════════════════════════════════════ */

QToolTip {
    background: #1E293B;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
}
"""


def get_badge_style(color: str) -> str:
    """Returns badge stylesheet for work type labels"""
    return f"""
        color: {color};
        background: transparent;
        border: 1px solid {color};
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 10px;
        font-weight: bold;
    """
