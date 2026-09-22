from typing import Any

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLineEdit
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QEvent
import sys, os, subprocess

if __name__ != "__main__":
    class DevConsole(QDialog):
        def __init__(self, parent, cmd):
            super().__init__(parent)
            self.setWindowTitle("Dev Console")
            self.resize(900, 600)
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.cmd = cmd
            self.buffer = []

            self.output = QTextEdit()
            self.output.setReadOnly(True)

            self.input = QLineEdit()
            self.input.setPlaceholderText("Type command...")
            self.input.returnPressed.connect(self.exec)
            self.input.installEventFilter(self)

            layout = QVBoxLayout()
            layout.addWidget(self.output)
            layout.addWidget(self.input)
            self.setLayout(layout)

            QShortcut(QKeySequence("F5"), self).activated.connect(self.hide)

            self._original_stdout = sys.stdout
            self._original_stderr = sys.stderr
            
            sys.stdout = self
            sys.stderr = self

            self.history = [] 
            self.history_index = -1
        
        def eventFilter(self, obj, event):
            if obj == self.input and event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Up:
                    if self.history and self.history_index > 0:
                        self.history_index -= 1
                        self.input.setText(self.history[self.history_index])
                    elif self.history and self.history_index == -1:
                        self.history_index = len(self.history) - 1
                        self.input.setText(self.history[self.history_index])
                    return True
                elif event.key() == Qt.Key.Key_Down:
                    if 0 <= self.history_index < len(self.history) - 1:
                        self.history_index += 1
                        self.input.setText(self.history[self.history_index])
                    elif self.history_index == len(self.history) - 1:
                        self.history_index = len(self.history)
                        self.input.clear()
                    return True
            return super().eventFilter(obj, event)
        
        def write(self, text):
            self.buffer.append(text)
            self._original_stdout.write(text)
            self.flush()

        def flush(self):
            self.output.insertPlainText("".join(self.buffer))
            self.buffer = []
            self._original_stdout.flush()
        
        def exec(self):
            cmd = self.input.text()
            cmd = str(cmd)
            if cmd.strip():
                if not self.history or self.history[-1] != cmd:
                    self.history.append(cmd)
                self.history_index = len(self.history)
            fcmd = cmd.lower()
            if fcmd.startswith("exec"):
                try:
                    exec(cmd[4:].strip(), globals())
                except Exception as e:
                    self.output.append(f"Execution error: <{e}>\n")
                finally:
                    self.input.clear()
                    return
            if fcmd.startswith("eval"):
                try:
                    self.output.append(f"-> {str(eval(cmd[4:].strip()))}\n")
                except Exception as e:
                    self.output.append(f"Eval error: <{e}>\n")
                finally:
                    self.input.clear()
                    return
            
            if fcmd.startswith("install"):
                path = cmd[7:].strip()
                if not os.path.exists(path):
                    if os.path.exists(f"{path}.py"):
                        path = f"{path}.py"
                    else:
                        self.output.append(f"Invalid path as <{path}>\n")
                        self.input.clear()
                        return
                self.output.append(f"Installation <{path}>\n")
                try:
                    with open(path, "r", encoding="UTF-8") as f:
                        code = f.read()
                    exec(code, globals())
                    self.input.clear()
                    return
                except Exception as e:
                    self.output.append(f"<{e}>\n")
                    self.input.clear()
                    return
                
            if fcmd.startswith("spawn"):
                path = cmd[5:].strip()
                if not os.path.exists(path):
                    if os.path.exists(f"{path}.py"):
                        path = f"{path}.py"
                    else:
                        self.output.append(f"Invalid path as <{path}>\n")
                        self.input.clear()
                        return
                self.output.append(f"Initializing <{path}>\n")
                try:
                    result = subprocess.run(
                        [sys.executable, path],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    self.output.append(f"{result.stdout}\n")
                except subprocess.CalledProcessError as e:
                    self.output.append(f"Execution error: <{e}>\n")
                self.input.clear()
                return
                
            if self.cmd is None:
                self.output.append(f"Unknown command as <{cmd}>\n")
                self.input.clear()
                return
            try:
                self.cmd(cmd)
            except Exception as e:
                self.output.append(f"Unknown error as <{e}>\n")
            self.input.clear()
        
        def closeEvent(self, event):
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            super().closeEvent(event)

    def init(parent_window, cmd=None) -> DevConsole:
        try:
            console = DevConsole(parent_window, cmd)

            QShortcut(QKeySequence("F5"), parent_window).activated.connect(
                lambda: console.show() if console.isHidden() else console.hide())
            return console
        except Exception as e:
            print(e, file=sys.stderr)

    def show(parent_window, cmd=None):
        console = DevConsole(parent_window, cmd)
        console.show()
        return console