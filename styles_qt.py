#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Qt Stylesheets - Material Design風スタイル定義
"""



DARK_THEME = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 9pt;
    color: #E0E0E0;
}

/* ラベル */
QLabel {
    color: #E0E0E0;
    background-color: transparent;
}

QLabel[heading="true"] {
    font-size: 10pt;
    font-weight: 600;
    color: #BDBDBD;
}

QLabel[title="true"] {
    font-size: 16pt;
    font-weight: bold;
    color: #FFFFFF;
}

/* ボタン */
QPushButton {
    background-color: #1E88E5;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 9pt;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #1565C0;
}

QPushButton:disabled {
    background-color: #424242;
    color: #757575;
}

QPushButton[primary="true"] {
    background-color: #1E88E5;
    padding: 10px 24px;
    font-size: 10pt;
    font-weight: 600;
}

QPushButton[primary="true"]:hover {
    background-color: #1976D2;
}

QPushButton[secondary="true"] {
    background-color: #424242;
    color: #E0E0E0;
}

QPushButton[secondary="true"]:hover {
    background-color: #616161;
}

QPushButton[secondary="true"]:disabled {
    background-color: #2C2C2C;
    color: #555555;
    border: 1px solid #424242;
}

/* リストウィジェット */
QListWidget {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 8px;
    color: #E0E0E0;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #1565C0;
    color: white;
}

QListWidget::item:hover {
    background-color: #2C2C2C;
}

/* コンボボックス */
QComboBox {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px 12px;
    color: #E0E0E0;
    min-height: 28px;
}

QComboBox:hover {
    border: 1px solid #1E88E5;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #BDBDBD;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 4px;
    selection-background-color: #1565C0;
    selection-color: white;
    padding: 4px;
}

/* ラインエディット */
QLineEdit {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px 12px;
    color: #E0E0E0;
    min-height: 28px;
}

QLineEdit:focus {
    border: 2px solid #1E88E5;
}

QLineEdit:disabled {
    background-color: #2C2C2C;
    color: #757575;
}

/* テキストエディット */
QTextEdit, QPlainTextEdit {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 12px;
    color: #E0E0E0;
}

/* プログレスバー */
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #333333;
    height: 8px;
    text-align: center;
    color: #E0E0E0;
}

QProgressBar::chunk {
    background-color: #1E88E5;
    border-radius: 4px;
}

/* チェックボックス */
QCheckBox {
    color: #E0E0E0;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 12px;
    height: 12px;
    border-radius: 3px;
    border: 2px solid #616161;
    background-color: #1E1E1E;
}

QCheckBox::indicator:checked {
    background-color: #1E88E5;
    border-color: #1E88E5;
}

/* フレーム */
QFrame[card="true"] {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 20px;
}

QFrame[dropzone="true"] {
    background-color: #2C2C2C;
    border: 2px dashed #616161;
    border-radius: 8px;
}

QFrame[dropzone="true"]:hover {
    background-color: #1A237E;
    border-color: #1E88E5;
}

/* スクロールバー */
QScrollBar:vertical {
    background-color: #2C2C2C;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #616161;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #757575;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* メニューバー */
QMenuBar {
    background-color: #1E1E1E;
    border-bottom: 1px solid #333333;
    padding: 4px;
}

QMenuBar::item {
    padding: 8px 12px;
    background-color: transparent;
    color: #E0E0E0;
}

QMenuBar::item:selected {
    background-color: #2C2C2C;
    border-radius: 4px;
}

QMenu {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 20px;
    border-radius: 4px;
    color: #E0E0E0;
}

QMenu::item:selected {
    background-color: #1565C0;
    color: white;
}
"""
