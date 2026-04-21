#!/usr/bin/env python3
"""
JobHunter - Data Analysis Job Search Tool
==========================================
Professional desktop application for automated job searching
"""

import sys
import os

# Ensure the project directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont, QFontDatabase
from ui.main_window import MainWindow


def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("JobHunter")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("DataAnalyst Tools")

    # Set application-wide font
    app.setFont(QFont("Segoe UI", 10))

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
