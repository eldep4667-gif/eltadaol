"""
Main application window - Professional dark UI for JobHunter
"""

import os
import sys
import csv
import json
import webbrowser
import logging
from datetime import datetime
from typing import List, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar, QStatusBar,
    QFrame, QSplitter, QCheckBox, QMessageBox, QFileDialog,
    QAbstractItemView, QToolBar, QApplication, QScrollArea,
    QGroupBox, QSpinBox, QTextEdit, QDialog
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QThread, Signal, QSize, QRect, QPoint
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
    QBrush, QPen, QLinearGradient, QAction, QFontMetrics,
    QCursor, QKeySequence
)

from core.models import Job, JOB_TITLES, WORK_TYPES, EXPERIENCE_LEVELS
from core.search_manager import SearchWorker
from ui.styles import DARK_STYLESHEET, get_badge_style

logger = logging.getLogger(__name__)


class JobTable(QTableWidget):
    """Custom job table with enhanced styling"""
    
    COLUMNS = [
        ("★", 35),
        ("Job Title", 220),
        ("Company", 160),
        ("Location", 130),
        ("Work Type", 100),
        ("Salary", 120),
        ("Source", 90),
        ("Posted", 90),
        ("Apply", 80),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_table()
        self._jobs: List[Job] = []
        self._favorites: set = set()
    
    def _setup_table(self):
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels([c[0] for c in self.COLUMNS])
        
        header = self.horizontalHeader()
        for i, (_, width) in enumerate(self.COLUMNS):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            self.setColumnWidth(i, width)
        
        # Last column (Apply) stretches
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)
        
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Row height
        self.verticalHeader().setDefaultSectionSize(44)
        
        # Double click to open
        self.cellDoubleClicked.connect(self._on_double_click)
    
    def _on_double_click(self, row, col):
        """Open apply URL on double click"""
        if row < len(self._jobs):
            job = self._jobs[row]
            if job.apply_url and job.apply_url != "N/A":
                webbrowser.open(job.apply_url)
    
    def add_jobs(self, jobs: List[Job]):
        """Add new jobs to the table"""
        for job in jobs:
            self._jobs.append(job)
            self._add_row(job)
    
    def _add_row(self, job: Job):
        row = self.rowCount()
        self.insertRow(row)
        
        # Favorite star
        fav_item = QTableWidgetItem("★" if job.is_favorite else "☆")
        fav_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        fav_item.setForeground(QColor("#FFD700") if job.is_favorite else QColor("#555"))
        self.setItem(row, 0, fav_item)
        
        # Title (with truncation)
        title_item = QTableWidgetItem(job.title)
        title_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_item.setForeground(QColor("#E2E8F0"))
        self.setItem(row, 1, title_item)
        
        # Company
        company_item = QTableWidgetItem(job.company)
        company_item.setForeground(QColor("#94A3B8"))
        self.setItem(row, 2, company_item)
        
        # Location
        loc_item = QTableWidgetItem(job.location)
        loc_item.setForeground(QColor("#64748B"))
        self.setItem(row, 3, loc_item)
        
        # Work type badge
        wt_item = QTableWidgetItem(job.work_type)
        wt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        color = self._get_type_color(job.work_type)
        wt_item.setForeground(QColor(color))
        wt_item.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.setItem(row, 4, wt_item)
        
        # Salary
        salary_item = QTableWidgetItem(job.salary)
        salary_item.setForeground(QColor("#10B981"))
        self.setItem(row, 5, salary_item)
        
        # Source
        src_item = QTableWidgetItem(job.source)
        src_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        src_item.setForeground(QColor("#7C3AED"))
        src_item.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.setItem(row, 6, src_item)
        
        # Date
        date_item = QTableWidgetItem(job.date_posted)
        date_item.setForeground(QColor("#64748B"))
        self.setItem(row, 7, date_item)
        
        # Apply button hint
        apply_item = QTableWidgetItem("🔗 Apply")
        apply_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_item.setForeground(QColor("#3B82F6"))
        apply_item.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.setItem(row, 8, apply_item)
    
    def _get_type_color(self, work_type: str) -> str:
        colors = {
            "Remote": "#10B981",
            "Full Time": "#3B82F6",
            "Part Time": "#F59E0B",
            "Hybrid": "#8B5CF6",
            "Internship": "#EC4899",
            "Contract": "#F97316",
            "Freelance": "#06B6D4",
        }
        for key, color in colors.items():
            if key.lower() in work_type.lower():
                return color
        return "#94A3B8"
    
    def get_selected_job(self) -> Optional[Job]:
        """Get currently selected job"""
        rows = self.selectedIndexes()
        if rows:
            row = rows[0].row()
            if row < len(self._jobs):
                return self._jobs[row]
        return None
    
    def toggle_favorite(self):
        """Toggle favorite for selected row"""
        job = self.get_selected_job()
        if job:
            job.is_favorite = not job.is_favorite
            rows = self.selectedIndexes()
            if rows:
                row = rows[0].row()
                fav_item = self.item(row, 0)
                if fav_item:
                    fav_item.setText("★" if job.is_favorite else "☆")
                    fav_item.setForeground(
                        QColor("#FFD700") if job.is_favorite else QColor("#555")
                    )
    
    def filter_jobs(self, text: str = "", remote_only: bool = False):
        """Filter visible rows"""
        text_lower = text.lower()
        for row in range(self.rowCount()):
            if row >= len(self._jobs):
                break
            job = self._jobs[row]
            
            # Text filter
            text_match = (
                not text or
                text_lower in job.title.lower() or
                text_lower in job.company.lower() or
                text_lower in job.location.lower()
            )
            
            # Remote filter
            remote_match = not remote_only or "remote" in job.work_type.lower()
            
            self.setRowHidden(row, not (text_match and remote_match))
    
    def get_all_jobs(self) -> List[Job]:
        return self._jobs.copy()
    
    def get_favorites(self) -> List[Job]:
        return [j for j in self._jobs if j.is_favorite]
    
    def clear_all(self):
        self.setRowCount(0)
        self._jobs.clear()


class AnimatedButton(QPushButton):
    """Button with hover animation"""
    
    def __init__(self, text, icon_char="", parent=None, style_class="primary"):
        super().__init__(parent)
        self._style_class = style_class
        full_text = f"{icon_char}  {text}" if icon_char else text
        self.setText(full_text)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(38)


class SearchPanel(QFrame):
    """Top search controls panel"""
    
    search_requested = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SearchPanel")
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Title row
        title_row = QHBoxLayout()
        logo = QLabel("⚡ JobHunter")
        logo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        logo.setStyleSheet("color: #7C3AED; letter-spacing: 1px;")
        
        subtitle = QLabel("Data Analysis Job Search Engine")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #64748B; margin-top: 4px;")
        
        title_col = QVBoxLayout()
        title_col.addWidget(logo)
        title_col.addWidget(subtitle)
        title_col.setSpacing(0)
        
        title_row.addLayout(title_col)
        title_row.addStretch()
        
        # Search stats badge
        self.stats_label = QLabel("جاهز للبحث")
        self.stats_label.setStyleSheet("""
            color: #94A3B8;
            background: #1E293B;
            border-radius: 12px;
            padding: 4px 12px;
            font-size: 11px;
        """)
        title_row.addWidget(self.stats_label)
        layout.addLayout(title_row)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #1E293B;")
        layout.addWidget(sep)
        
        # Controls grid
        controls = QGridLayout()
        controls.setSpacing(10)
        controls.setColumnStretch(0, 2)
        controls.setColumnStretch(1, 1)
        controls.setColumnStretch(2, 1)
        controls.setColumnStretch(3, 1)
        controls.setColumnStretch(4, 1)
        
        # Row 1: Location, Salary, Experience, Work Type, Search
        loc_label = QLabel("📍 الدولة / المدينة")
        loc_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        controls.addWidget(loc_label, 0, 0)
        
        sal_label = QLabel("💰 الراتب (اختياري)")
        sal_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        controls.addWidget(sal_label, 0, 1)
        
        exp_label = QLabel("🎯 مستوى الخبرة")
        exp_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        controls.addWidget(exp_label, 0, 2)
        
        type_label = QLabel("🏢 نوع الوظيفة")
        type_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        controls.addWidget(type_label, 0, 3)
        
        # Inputs Row 2
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Cairo, Egypt / Remote...")
        self.location_input.setObjectName("SearchInput")
        controls.addWidget(self.location_input, 1, 0)
        
        self.salary_input = QLineEdit()
        self.salary_input.setPlaceholderText("e.g. 5000+ USD")
        self.salary_input.setObjectName("SearchInput")
        controls.addWidget(self.salary_input, 1, 1)
        
        self.exp_combo = QComboBox()
        self.exp_combo.addItems(EXPERIENCE_LEVELS)
        self.exp_combo.setObjectName("SearchCombo")
        controls.addWidget(self.exp_combo, 1, 2)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(WORK_TYPES)
        self.type_combo.setObjectName("SearchCombo")
        controls.addWidget(self.type_combo, 1, 3)
        
        self.search_btn = AnimatedButton("بحث الآن", "🔍")
        self.search_btn.setObjectName("SearchButton")
        self.search_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.search_btn.setMinimumHeight(42)
        self.search_btn.clicked.connect(self._on_search)
        controls.addWidget(self.search_btn, 1, 4)
        
        layout.addLayout(controls)
        
        # Row 2: Keywords & Filters
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)
        
        kw_label = QLabel("🔎")
        kw_label.setStyleSheet("color: #94A3B8;")
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("فلترة النتائج... (اسم شركة، مدينة، مهارة)")
        self.keyword_input.setObjectName("FilterInput")
        self.keyword_input.textChanged.connect(self._on_filter_changed)
        
        self.remote_check = QCheckBox("🌐 Remote فقط")
        self.remote_check.setStyleSheet("color: #10B981; font-weight: bold;")
        self.remote_check.stateChanged.connect(self._on_filter_changed)
        
        self.stop_btn = AnimatedButton("إيقاف", "⏹")
        self.stop_btn.setObjectName("StopButton")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumWidth(100)
        
        filter_row.addWidget(kw_label)
        filter_row.addWidget(self.keyword_input, 3)
        filter_row.addWidget(self.remote_check)
        filter_row.addWidget(self.stop_btn)
        
        layout.addLayout(filter_row)
    
    def _on_search(self):
        params = {
            "location": self.location_input.text().strip(),
            "salary": self.salary_input.text().strip(),
            "experience": self.exp_combo.currentText(),
            "work_type": self.type_combo.currentText().replace("All Types", ""),
        }
        self.search_requested.emit(params)
    
    def _on_filter_changed(self):
        """Emit filter signal - handled by main window"""
        pass
    
    def set_searching(self, is_searching: bool):
        self.search_btn.setEnabled(not is_searching)
        self.stop_btn.setEnabled(is_searching)
        if is_searching:
            self.search_btn.setText("🔄  جاري البحث...")
        else:
            self.search_btn.setText("🔍  بحث الآن")
    
    def update_stats(self, count: int):
        self.stats_label.setText(f"✓ {count} وظيفة")


class StatusPanel(QFrame):
    """Bottom status and action panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusPanel")
        self._build_ui()
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)
        
        # Left: Status info
        self.job_count_label = QLabel("0 وظيفة")
        self.job_count_label.setStyleSheet(
            "color: #7C3AED; font-weight: bold; font-size: 13px;"
        )
        
        self.status_label = QLabel("في انتظار البحث...")
        self.status_label.setStyleSheet("color: #64748B; font-size: 11px;")
        
        info_col = QVBoxLayout()
        info_col.addWidget(self.job_count_label)
        info_col.addWidget(self.status_label)
        info_col.setSpacing(2)
        
        layout.addLayout(info_col)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("SearchProgress")
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(6)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        # Action buttons
        self.open_btn = AnimatedButton("فتح الرابط", "🌐")
        self.open_btn.setObjectName("ActionButton")
        self.open_btn.setToolTip("فتح رابط التقديم في المتصفح (أو انقر مرتين على الصف)")
        
        self.fav_btn = AnimatedButton("المفضلة", "★")
        self.fav_btn.setObjectName("FavButton")
        self.fav_btn.setToolTip("إضافة/إزالة من المفضلة")
        
        self.csv_btn = AnimatedButton("CSV", "📄")
        self.csv_btn.setObjectName("ExportButton")
        
        self.excel_btn = AnimatedButton("Excel", "📊")
        self.excel_btn.setObjectName("ExportButton")
        
        self.refresh_btn = AnimatedButton("تحديث", "🔄")
        self.refresh_btn.setObjectName("RefreshButton")
        
        self.clear_btn = AnimatedButton("مسح", "🗑")
        self.clear_btn.setObjectName("DangerButton")
        
        for btn in [self.open_btn, self.fav_btn, self.csv_btn,
                    self.excel_btn, self.refresh_btn, self.clear_btn]:
            btn.setMinimumHeight(36)
            layout.addWidget(btn)
    
    def set_status(self, text: str):
        self.status_label.setText(text)
    
    def set_count(self, count: int):
        self.job_count_label.setText(f"✦ {count} وظيفة")
    
    def set_loading(self, loading: bool):
        self.progress_bar.setVisible(loading)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self._jobs: List[Job] = []
        self._worker: Optional[SearchWorker] = None
        self._new_jobs_count = 0
        
        self.setWindowTitle("⚡ JobHunter — Data Analysis Jobs")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 850)
        
        self._apply_styles()
        self._build_ui()
        self._connect_signals()
        self._setup_notification_timer()
        
        # Center window
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
    
    def _apply_styles(self):
        from ui.styles import DARK_STYLESHEET
        self.setStyleSheet(DARK_STYLESHEET)
    
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search panel (top)
        self.search_panel = SearchPanel()
        main_layout.addWidget(self.search_panel)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background: #1E293B; max-height: 1px;")
        main_layout.addWidget(divider)
        
        # Job table (center) 
        table_container = QWidget()
        table_container.setObjectName("TableContainer")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(12, 12, 12, 8)
        table_layout.setSpacing(6)
        
        # Table header
        table_header = QHBoxLayout()
        tbl_title = QLabel("نتائج البحث")
        tbl_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        tbl_title.setStyleSheet("color: #E2E8F0;")
        
        self.new_badge = QLabel("  ✦ جديد  ")
        self.new_badge.setStyleSheet("""
            background: #7C3AED;
            color: white;
            border-radius: 8px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: bold;
        """)
        self.new_badge.setVisible(False)
        
        sort_label = QLabel("انقر مرتين على وظيفة لفتح رابط التقديم")
        sort_label.setStyleSheet("color: #475569; font-size: 10px;")
        
        table_header.addWidget(tbl_title)
        table_header.addWidget(self.new_badge)
        table_header.addStretch()
        table_header.addWidget(sort_label)
        table_layout.addLayout(table_header)
        
        self.job_table = JobTable()
        table_layout.addWidget(self.job_table)
        
        main_layout.addWidget(table_container, 1)
        
        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setStyleSheet("background: #1E293B; max-height: 1px;")
        main_layout.addWidget(divider2)
        
        # Status panel (bottom)
        self.status_panel = StatusPanel()
        main_layout.addWidget(self.status_panel)
    
    def _connect_signals(self):
        # Search panel
        self.search_panel.search_requested.connect(self._start_search)
        self.search_panel.keyword_input.textChanged.connect(self._apply_filters)
        self.search_panel.remote_check.stateChanged.connect(self._apply_filters)
        self.search_panel.stop_btn.clicked.connect(self._stop_search)
        
        # Status panel buttons
        self.status_panel.open_btn.clicked.connect(self._open_selected_job)
        self.status_panel.fav_btn.clicked.connect(self._toggle_favorite)
        self.status_panel.csv_btn.clicked.connect(self._save_csv)
        self.status_panel.excel_btn.clicked.connect(self._save_excel)
        self.status_panel.refresh_btn.clicked.connect(self._refresh_search)
        self.status_panel.clear_btn.clicked.connect(self._clear_results)
    
    def _setup_notification_timer(self):
        """Flash new badge when jobs are found"""
        self._badge_timer = QTimer()
        self._badge_timer.timeout.connect(self._flash_badge)
        self._badge_flash_count = 0
    
    def _flash_badge(self):
        self._badge_flash_count += 1
        visible = self.new_badge.isVisible()
        self.new_badge.setVisible(not visible)
        if self._badge_flash_count >= 8:
            self._badge_timer.stop()
            self.new_badge.setVisible(False)
            self._badge_flash_count = 0
    
    def _start_search(self, params: dict):
        """Start the job search"""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
        
        self.search_panel.set_searching(True)
        self.status_panel.set_loading(True)
        self.status_panel.set_status("🔍 جاري البحث في جميع المواقع...")
        
        self._new_jobs_count = 0
        
        self._worker = SearchWorker(params)
        self._worker.jobs_found.connect(self._on_jobs_found)
        self._worker.progress_update.connect(self._on_progress)
        self._worker.search_complete.connect(self._on_search_complete)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()
    
    def _stop_search(self):
        if self._worker:
            self._worker.stop()
        self.search_panel.set_searching(False)
        self.status_panel.set_loading(False)
        self.status_panel.set_status("⏹ تم إيقاف البحث")
    
    def _on_jobs_found(self, jobs: List[Job]):
        """Called when new jobs are found"""
        self.job_table.add_jobs(jobs)
        total = self.job_table.rowCount()
        self.status_panel.set_count(total)
        self.search_panel.update_stats(total)
        
        self._new_jobs_count += len(jobs)
        
        # Show notification badge
        if self._new_jobs_count > 0:
            self.new_badge.setText(f"  ✦ +{self._new_jobs_count} جديد  ")
            self.new_badge.setVisible(True)
            if not self._badge_timer.isActive():
                self._badge_flash_count = 0
                self._badge_timer.start(400)
        
        # Apply current filters
        self._apply_filters()
    
    def _on_progress(self, message: str):
        self.status_panel.set_status(message)
    
    def _on_search_complete(self, total: int):
        self.search_panel.set_searching(False)
        self.status_panel.set_loading(False)
        self.status_panel.set_status(f"✅ اكتمل البحث — {total} وظيفة فريدة")
        self.status_panel.set_count(total)
    
    def _on_error(self, error: str):
        self.search_panel.set_searching(False)
        self.status_panel.set_loading(False)
        self.status_panel.set_status(f"⚠ خطأ: {error}")
    
    def _apply_filters(self):
        keyword = self.search_panel.keyword_input.text()
        remote_only = self.search_panel.remote_check.isChecked()
        self.job_table.filter_jobs(keyword, remote_only)
    
    def _open_selected_job(self):
        job = self.job_table.get_selected_job()
        if job and job.apply_url:
            webbrowser.open(job.apply_url)
        else:
            QMessageBox.information(self, "تنبيه", "الرجاء اختيار وظيفة أولاً")
    
    def _toggle_favorite(self):
        self.job_table.toggle_favorite()
    
    def _refresh_search(self):
        """Re-run last search"""
        params = {
            "location": self.search_panel.location_input.text().strip(),
            "salary": self.search_panel.salary_input.text().strip(),
            "experience": self.search_panel.exp_combo.currentText(),
            "work_type": self.search_panel.type_combo.currentText().replace("All Types", ""),
        }
        self._start_search(params)
    
    def _clear_results(self):
        reply = QMessageBox.question(
            self, "تأكيد", "هل تريد مسح جميع النتائج؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.job_table.clear_all()
            self.status_panel.set_count(0)
            self.status_panel.set_status("تم مسح النتائج")
            self.search_panel.update_stats(0)
    
    def _save_csv(self):
        """Export to CSV"""
        jobs = self.job_table.get_all_jobs()
        if not jobs:
            QMessageBox.warning(self, "تنبيه", "لا توجد وظائف للتصدير")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "حفظ CSV",
            f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Job Title", "Company", "Location", "Work Type",
                        "Salary", "Source", "Date Posted", "Apply URL"
                    ])
                    for job in jobs:
                        writer.writerow([
                            job.title, job.company, job.location, job.work_type,
                            job.salary, job.source, job.date_posted, job.apply_url
                        ])
                
                QMessageBox.information(self, "✅ تم", f"تم الحفظ:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل الحفظ:\n{e}")
    
    def _save_excel(self):
        """Export to Excel"""
        try:
            import pandas as pd
        except ImportError:
            QMessageBox.critical(self, "خطأ", "يرجى تثبيت pandas:\npip install pandas openpyxl")
            return
        
        jobs = self.job_table.get_all_jobs()
        if not jobs:
            QMessageBox.warning(self, "تنبيه", "لا توجد وظائف للتصدير")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "حفظ Excel",
            f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if filename:
            try:
                data = [{
                    "Job Title": j.title,
                    "Company": j.company,
                    "Location": j.location,
                    "Work Type": j.work_type,
                    "Salary": j.salary,
                    "Source": j.source,
                    "Date Posted": j.date_posted,
                    "Apply URL": j.apply_url,
                    "Favorite": "★" if j.is_favorite else "",
                } for j in jobs]
                
                df = pd.DataFrame(data)
                
                with pd.ExcelWriter(filename, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Jobs")
                    
                    # Auto-size columns
                    ws = writer.sheets["Jobs"]
                    for col in ws.columns:
                        max_len = max(len(str(cell.value or "")) for cell in col)
                        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
                
                QMessageBox.information(self, "✅ تم", f"تم الحفظ:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل الحفظ:\n{e}")
    
    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(3000)
        event.accept()
