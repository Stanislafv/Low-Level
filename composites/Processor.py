from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6 import QtCore

from base.font import Font
from base.cursors import Cursor
from base.functions import try_int, save
from base.MusicPlayer import MusicPlayer

from composites.MemoryBlock import MemoryBlock

from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtCore import QRegularExpression

from ui.Menu import Menu

commands = ["MOV", "ADD", "PUSH", "JMP", "OUT"]

class Highlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []
        
        cmd_format = QTextCharFormat()
        cmd_format.setForeground(QColor("#569CD6"))

        register_format = QTextCharFormat()
        register_format.setForeground(QColor("#4EC9B0"))

        pattern = QRegularExpression(r"\bR[0-7]\b")
        self.rules.append((pattern, register_format))

        pattern = QRegularExpression(r"\bIP\b")
        self.rules.append((pattern, register_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))

        pattern = QRegularExpression("\[[^\"]*\]")
        self.rules.append((pattern, string_format))

        for cmd in commands:
            pattern = QRegularExpression(rf"\b{cmd}\b")
            self.rules.append((pattern, cmd_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
                
        pattern = QRegularExpression("//[^\n]*")
        self.rules.append((pattern, comment_format))

    @save
    def highlightBlock(self, text):
        for pattern, format in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(
                    match.capturedStart(), 
                    match.capturedLength(), 
                    format                  
                )

class ProcessorEditor(Menu):
    def __init__(self, processor:Processor):
        super().__init__(processor.w)
        self.processor = processor

        self.setAutoFillBackground(True)

        layout = QtWidgets.QVBoxLayout(self)

        self.editor = QtWidgets.QPlainTextEdit()
        self.editor.setPlainText(processor.code)
        self.editor.setFont(Font.Bold)
        self.editor.textChanged.connect(self.save)

        self.editor_highlighter = Highlighter(self.editor.document()) 
        
        layout.addWidget(self.editor)

        self.console = QtWidgets.QTextEdit()
        self.console.setReadOnly(True)  
        self.console.setFont(Font.Bold)
        self.console.setMaximumHeight(self.parent().height()//4)
        layout.addWidget(self.console)
        
        run_btn = QtWidgets.QPushButton("Start")
        run_btn.setFont(Font.Bold)
        run_btn.clicked.connect(self.processor.parsing)
        layout.addWidget(run_btn)

        stop_btn = QtWidgets.QPushButton("Stop")
        stop_btn.setFont(Font.Bold)
        stop_btn.clicked.connect(self.processor.stop)
        layout.addWidget(stop_btn)
        
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setFont(Font.Bold)
        close_btn.clicked.connect(self.Back)
        layout.addWidget(close_btn)

        self.move(0, 0)

        self.setFixedSize(QtCore.QSize(self.parent().width(), self.parent().height()))

        self.hide()

    def save(self):
        self.processor.code = self.editor.toPlainText()

class Processor(MemoryBlock):
    def __init__(self, *args, **kwargs):
        self._time_after = 0
        self.active_line = 0
        self.speed = 0.05
        self.active = False
        self.code = ""

        self.registers = {"R0": 0, "R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 0, "R6": 0, "R7": 0, "IP": 1}

        self.split_code = []
        self.ends = []

        self.marks = {}

        super().__init__(*args, **kwargs)

        self.editor = ProcessorEditor(self)

    def on_click(self):
        MusicPlayer.play("click_2")
        self.editor.Show()

    def parsing_line(self, line:str):
        line = line.strip()
        match line.split(" "):
            case ["OUT", *args]:
                self.editor.console.append(" ".join(args))
        
            case ["MOV", value, name]:
                if name not in self.registers:
                    self.editor.console.append(f"Unknown register as {name}")
                    self.stop()
                            
                self.registers[name] = value

            case ["JMP", mark]:
                if mark in self.marks:
                    self.active_line = self.marks[mark]
                else:
                    try:
                        self.active_line = int(mark)-1
                    except ValueError:
                        self.editor.console.append(f"Mark {mark} not exists")

            case ["PUSH", name]:
                try:
                    value = int(name)
                except ValueError:
                    value = self.marks[name]
                self.ends.append(value)

            case _:
                if line.startswith(":"):
                    return
                self.editor.console.append(f"Segmentation fault at {self.active_line+1} line")
                self.stop()

    @save
    def parsing(self, *args):
        code = self.code.replace(";", "\n")
        self.split_code = code.split("\n")
        self.active_line = 0
        self.active = True

        for num, line in enumerate(self.split_code):
            if line.startswith(":"):
                self.marks[line[1:]] = num

    def stop(self):
        self.code = ""
        self.active_line = 0
        self._time_after = 0
        
        self.registers = {"R0": 0, "R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 0, "R6": 0, "R7": 0, "IP": 1}
        
        self.split_code = []
        self.ends = []
        
        self.marks = {}
        self.active = False

    @save
    def update(self, tick, dt):
        if not self.active:
            return
        self._time_after += dt
        while self._time_after > self.speed:
            self._time_after -= self.speed

            if len(self.split_code) == self.active_line:
                self.stop()
                break

            try:
                line = self.split_code[self.active_line].rstrip()
            except IndexError:
                self.stop()
                break

            if not line or line.startswith('//') or line.endswith(":"): 
                self._time_after += self.speed
                self.active_line += 1
                continue

            for part in line.split('[')[1:]: 
                result = part.split(']')[0]
                if result in self.registers:
                    line = line.replace(f"[{result}]", str(self.registers[result]))
                else:
                    self.editor.console.append(f"Register <{result}> not exists")
                    return

            self.parsing_line(line)

            print(self.active_line)

            self.active_line+=1
            self.registers["IP"] = self.active_line+1
