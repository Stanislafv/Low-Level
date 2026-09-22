from typing import Any

import sys as _sys
import os as _os
from datetime import date
from subprocess import run as _run
from time import strftime
from atexit import register as _atexitregister
import warnings as _warn
import hashlib
import shutil
import ctypes
import json

def _process_exists(pid):
    pid = int(pid)
    if _sys.platform == "win32":
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32
        PROCESS_QUERY_INFORMATION = 0x0400
        h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
        if h_process == 0:
            return False
        exit_code = wintypes.DWORD()
        kernel32.GetExitCodeProcess(h_process, ctypes.byref(exit_code))
        kernel32.CloseHandle(h_process)
        return exit_code.value == 259      
    else:
        try:
            _os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False
        except OSError:
            return False

class TYPE: pass
class DEBUG(TYPE): pass
class SYSTEM(TYPE): pass
class INFO(TYPE): pass
class WARNING(TYPE): pass
class ERROR(TYPE): pass
class EXIT(TYPE): pass
class START(TYPE): pass
class SEPARATOR(TYPE): pass
class PLUGINLOADER(TYPE): pass
class FileLaunchError(RuntimeError):
    def __init__(self, m="File already launched"):
        super().__init__(m)

def lprint(*args, start="", end="\n", sep=" ", type:str|TYPE = INFO, set_error=False): 
        txt = sep.join(str(a) for a in args)
        dct = {INFO: "[INFO]", WARNING: "[WARNING]", ERROR: "[ERROR]", EXIT: "[EXIT]", START: "[START]", DEBUG: "[DEBUG]", SYSTEM: "[SYSTEM]", PLUGINLOADER: "[PluginLoader]"}
        if type in dct:
            ftype = dct[type]
        else:
            ftype = f"[{type}]"
        if type == ERROR or set_error:
            global _exit_code
            _exit_code = 1
            _sys._ExitCode = 1
        if type != SEPARATOR:
                if len(txt.split("\n")) > 1:
                    print(f"{start}{ftype+'\n   >'}{txt.replace("\n", "\n   >")}", end=end)
                else:
                    print(f"{start}{ftype} {txt}", end=end)
        else:
            print("\n")

_exit_code:Any = 0

class ModError(RuntimeError):
    def __init__(self, m):
        super().__init__(m)

_original_exit = _sys.exit

if _sys.platform == "win32":
    base = _os.environ["APPDATA"]
elif _sys.platform == "darwin":
    base = _os.path.expanduser("~/Library/Application Support")
else:
    base = _os.path.expanduser("~/.local/share")

class AppDir:
    def __init__(self, name=None, version=None, path=None, tee=False, log=True, config=True, cache=True, temp=True, plugins=True):
        self._path_hash = hashlib.sha256(_os.path.abspath(_sys.argv[0]).encode()).hexdigest()[:16]
        if name is None:
            self._file_name = _os.path.splitext(_os.path.basename(_sys.argv[0]))[0]
            self._file_name = f"{self._file_name}({self._path_hash})"
        else:
            self._file_name=name
        if path is not None:
            self.file_path = path
        else:
            self.file_path = _os.path.join(base, "Various", self._file_name)
        self.log_path = _os.path.join(self.file_path, "log.txt")
        self.cache_path = _os.path.join(self.file_path, "cache")
        self.temp_path = _os.path.join(self.file_path, "temp")
        self.mods_path = _os.path.join(self.file_path, "mods")
        self.version_path = _os.path.join(self.file_path, "version.txt")
        self.lock_path = _os.path.join(self.temp_path, "lock")
        _os.makedirs(self.file_path, exist_ok=True)
        _os.makedirs(self.mods_path, exist_ok=True)
        self._one = False
        if version is not None:
            with open(self.version_path, "w", encoding="UTF-8") as f:
                f.write(version)
            self._version = version
        else:
            try:
                with open(self.version_path, "r", encoding="UTF-8") as f:
                    version = f.read()
                self._version = version
            except FileNotFoundError:
                self._version = ""
                with open(self.version_path, "w", encoding="UTF-8") as f: pass

        if log:
            self.log = Log(self.log_path, self.temp_path, self._version, tee=tee)
        if config:
            self.config = Config(self.file_path)
        if cache:
            self.cache = Storage(self.cache_path)
        if temp:
            self.temp = Storage(self.temp_path)
        if plugins:
            self.plugins = PluginLoader(self.mods_path, log=self.log)
    
    def view(self):
        if _sys.platform == "win32":
            _os.startfile(self.file_path)
        else:
            _run(["xdg-open", self.file_path])
    
    def read(self, name, type="r"):
        with open(_os.path.join(self.file_path, str(name)), type, 
                encoding=None if 'b' in type else 'UTF-8') as f:
            return f.read()
    
    def list(self) -> list:
        return _os.listdir(self.file_path)
    
    def mkdir(self, name):
        return Storage(_os.path.join(self.file_path, str(name)))
        
    def write(self, name, txt="", type="w"):
        with open(_os.path.join(self.file_path, str(name)), type, 
                encoding=None if 'b' in type else 'UTF-8') as f:
            f.write(str(txt))
    
    def delete(self, name):
        _os.remove(_os.path.join(self.file_path, str(name)))
    
    def clear(self, name):
        open(_os.path.join(self.file_path, str(name)), "w").close()
    
    def destroy(self):
        shutil.rmtree(self.file_path)
    
    def path(self, name=None):
        if name is None:
            return self.file_path
        return _os.path.join(self.file_path, str(name))

    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self, value):
        with open(self.version_path, "w", encoding="UTF-8") as f:
            f.write(str(value))
        self._version = value
    
    @property
    def onelaunch(self):
        return self._one
    
    @onelaunch.setter
    def onelaunch(self, value):
        if value:
            if _os.path.exists(self.lock_path):
                with open(self.lock_path, "r") as f:
                    old_pid = f.read().strip()
                if _process_exists(old_pid):
                    raise FileLaunchError()
                else:
                    _os.remove(self.lock_path)
            with open(self.lock_path, "w") as f:
                f.write(str(_os.getpid()))
        else:
            if _os.path.exists(self.lock_path):
                _os.remove(self.lock_path)
        self._one = value

class StderrLogger:
    def __init__(self, log_instance):
        self.log = log_instance
        self._stderr = _sys.__stderr__
        self._in_write = False
    
    def write(self, text):
        if self._in_write:
            self._stderr.write(text)
            return
        if text.strip():
            self._in_write = True
            try:
                self.log.write(text.rstrip("\n"), type=ERROR, end="\n")
            except Exception:
                self._stderr.write(text)
            finally:
                self._in_write = False
    
    def flush(self):
        self._stderr.flush()
    
class Log:
    def __init__(self, path, tempfolder=None, version="", tee=False, max_lines = 10000):
        self.tempfolder = tempfolder
        self.version = version
        self.file_path = path
        self.max_lines = max_lines
        self._logged_exit = False
        self._hooks = {
            DEBUG: [],
            SYSTEM: [],
            INFO: [],
            WARNING: [],
            ERROR: [],
            EXIT: [],
            START: [],
            SEPARATOR: [],
            PLUGINLOADER: []
        }
        _os.makedirs(_os.path.dirname(self.file_path), exist_ok=True)

        _warn.showwarning = self._warning_handler
        _sys.exit = self._custom_exit
        _sys.stderr = StderrLogger(self)
        _atexitregister(self._log_exit)
        self.tee = tee

        if not _os.path.exists(self.file_path):
            open(self.file_path, "x").close()
        with open(self.file_path, 'r', encoding='UTF-8') as f:
            lines = f.readlines()
            
        if len(lines) > self.max_lines+1:
            with open(self.file_path, 'w', encoding='UTF-8') as f:
                f.write(f"[{date.today().strftime("%Y-%m-%d")} | {strftime("%H:%M:%S")}] >>> [SYSTEM] File was truncated to {self.max_lines} lines\n")
                f.writelines(lines[-self.max_lines:])
                  
        last_start = -1
        last_exit = -1
        for i, line in enumerate(lines):
            if '[START]' in line:
                last_start = i
            if '[EXIT]' in line or '[SEPARATOR]' in line:
                last_exit = i
            
        if last_start > last_exit:
            self.write(type=SEPARATOR)
            self.write(version, type=START)
            self.write("The previous launch failed", type=WARNING)
        else:
            self.write(version, type=START)

    def dump(self, **kwargs):
        for k, v in kwargs.items():
            self.write(f"{k} = {repr(v)}", type=DEBUG)
    
    def on(self, type, func):
        self._hooks[type].append(func)
        if type == START:
            try:
                func(self.version)
            except TypeError:
                func()

    def off(self, level, callback):
        if callback in self._hooks[level]:
            self._hooks[level].remove(callback)

    def _log_exit(self):
        if self._logged_exit:
            return
        self._logged_exit = True
        if self.tempfolder is not None:
            if _os.path.exists(self.tempfolder):
                if len(_os.listdir(self.tempfolder)) > 0:
                    if _os.path.exists(_os.path.join(self.tempfolder, "lock")):
                        if len(_os.listdir(self.tempfolder)) > 1:
                            self.write(f"Deleted {len(_os.listdir(self.tempfolder))-1} files from temp folder", type=SYSTEM)
                        _os.remove(_os.path.join(self.tempfolder, "lock"))
                    else:
                        self.write(f"Deleted {len(_os.listdir(self.tempfolder))} files from temp folder", type=SYSTEM)
                    shutil.rmtree(self.tempfolder)
                    _os.makedirs(self.tempfolder, exist_ok=True)

        if self.tee:
            print(f"[EXIT] {_exit_code}")
        self.write(_exit_code, type=EXIT)
        self.write(type=SEPARATOR)

    def write(self, *args, start="", end="\n", sep=" ", type:str|TYPE = INFO, set_error=False): 
        txt = sep.join(str(a) for a in args)
        dct = {INFO: "[INFO]", WARNING: "[WARNING]", ERROR: "[ERROR]", EXIT: "[EXIT]", START: "[START]", DEBUG: "[DEBUG]", SYSTEM: "[SYSTEM]", PLUGINLOADER: "[PluginLoader]"}
        if type in dct:
            ftype = dct[type]
        else:
            ftype = f"[{type}]"
        if type == ERROR or set_error:
            global _exit_code
            _exit_code = 1
            _sys._ExitCode = 1
        with open(self.file_path, "a+", encoding="UTF-8") as f:
            if type != SEPARATOR:
                if len(txt.split("\n")) > 1:
                    f.write(f'[{date.today().strftime("%Y-%m-%d")} | {strftime("%H:%M:%S")}] >>> {start}{ftype+"\n                    >>> "}{txt.replace("\n", "\n                    >>> ")}{end}')
                    if self.tee and type is not SEPARATOR and type is not EXIT:
                        print(f"{start}{ftype+'\n   >'}{txt.replace("\n", "\n   >")}", end=end)
                else:
                    f.write(f'[{date.today().strftime("%Y-%m-%d")} | {strftime("%H:%M:%S")}] >>> {start}{ftype} {txt}{end}')
                    if self.tee and type is not SEPARATOR and type is not EXIT:
                        print(f"{start}{ftype} {txt}", end=end)
            else:
                f.write("\n")
            f.flush()

        for callback in self._hooks.get(type, []):
            try:
                try:
                    callback(txt)
                except TypeError:
                    callback()
            except Exception:
                pass
    
    def read(self) -> str:
        with open(self.file_path, "r", encoding="UTF-8") as f:
            return f.read()

    def clear(self):
        with open(self.file_path, "w", encoding="UTF-8") as f: pass
        self.write("CLEARED", type=SYSTEM)

    def _custom_exit(self, code=None):
        global _exit_code
        if code is not None:
            _exit_code = code
        _original_exit(code)

    def view(self):
        if _sys.platform == "win32":
            _os.startfile(self.file_path)
        else:
            _run(["xdg-open", self.file_path])

    def _warning_handler(self, message, category, filename, lineno, file=None, line=None):
        warning_text = _warn.formatwarning(message, category, filename, lineno, line)
        warning_text = warning_text.rstrip("\n")
        self.write(warning_text, type=WARNING)
        print(warning_text, file=_sys.stderr)

class Storage:
    def __init__(self, path):
        self.file_path = path
        _os.makedirs(self.file_path, exist_ok=True)
    
    def read(self, name, type="r"):
        if type == "json":
            with open(_os.path.join(self.file_path, str(name)), "r", encoding='UTF-8') as f:
                return json.load(f)
        with open(_os.path.join(self.file_path, str(name)), type, encoding=None if 'b' in type else 'UTF-8') as f:
            return f.read()
    
    def list(self) -> list:
        return _os.listdir(self.file_path)
    
    def mkdir(self, name):
        return Storage(_os.path.join(self.file_path, str(name)))
        
    def write(self, name, txt="", type="w"):
        load = False
        if type == "json":
            type = "w"
            load = True
        with open(_os.path.join(self.file_path, str(name)), type, 
                encoding=None if 'b' in type else 'UTF-8') as f:
            if load:
                json.dump(txt, f, indent=4, ensure_ascii=False)
                return
            f.write(str(txt))
    
    def delete(self, name):
        _os.remove(_os.path.join(self.file_path, str(name)))
    
    def clear(self, name):
        open(_os.path.join(self.file_path, str(name)), "w").close()
    
    def destroy(self):
        shutil.rmtree(self.file_path)
    
    def path(self, name=None):
        if name is None:
            return self.file_path
        return _os.path.join(self.file_path, str(name))
    
    def exists(self, name=None):
        if name is None:
            return _os.path.exists(self.file_path)
        return _os.path.exists(_os.path.join(self.file_path, str(name)))
    
    def view(self):
        if _sys.platform == "win32":
            _os.startfile(self.file_path)
        else:
            _run(["xdg-open", self.file_path])

class Config:
    def __init__(self, path, name="config"):
        self._path = path
        self.file_path = _os.path.join(self._path, name)+".json"
        try:
            open(self.file_path, "x").close()
        except FileExistsError: pass
    
    def write(self, dct, type="w"):
        if "a" in type:
            with open(self.file_path, "r", encoding="UTF-8") as f:
                try:
                    dct1 = json.load(f)
                except json.decoder.JSONDecodeError: dct1={}
            with open(self.file_path, "w", encoding="UTF-8") as f:
                json.dump(dct1|dct, f, indent=4, ensure_ascii=False)
        elif "w" in type:
            with open(self.file_path, "w", encoding="UTF-8") as f:
                if dct is None:
                    return
                json.dump(dct, f, indent=4, ensure_ascii=False)
        else:
            raise TypeError(f"Type {type} is not valid")
    
    def read(self):
        with open(self.file_path, "r", encoding="UTF-8") as f:
            return json.load(f)
    
    def get(self, key, standart=None):
        with open(self.file_path, "r", encoding="UTF-8") as f:
            try:
                return json.load(f)[key]
            except (KeyError, TypeError):
                return standart
    
    def clear(self):
        open(self.file_path, "w").close()
    
    def __getitem__(self, key):
        with open(self.file_path, "r", encoding="UTF-8") as f:
            return json.load(f)[key]

    def __setitem__(self, key, value):
        data = {}
        if _os.path.getsize(self.file_path) > 0:
            with open(self.file_path, "r", encoding="UTF-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass
        data[key] = value
        with open(self.file_path, "w", encoding="UTF-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def path(self):
        return self.file_path
    
    def view(self):
        if _sys.platform == "win32":
            _os.startfile(self.file_path)
        else:
            _run(["xdg-open", self.file_path])

class PluginLoader:
    def __init__(self, mods_path, log=None):
        self.mods_path = mods_path
        self.mods = {}
        self.log = log
        _os.makedirs(_os.path.dirname(self.mods_path), exist_ok=True)
    
    def init(self):
        for file in _os.listdir(self.mods_path):
            try:
                if file.endswith(".py"):
                    name = file[:-3]
                    self.load(name)
            except Exception as e:
                if self.log is not None:
                    if self.log.tee:
                        self.log.write(f"Failed to load <{file}>: {e}", type=PLUGINLOADER)
                        return
                print(f"[PluginLoader] Failed to load <{file}>: {e}")
    
    def load(self, name):
        file = _os.path.join(self.mods_path, name)
        if not _os.path.exists(file):
            if _os.path.exists(f"{file}.py"):
                file = f"{file}.py"
            else:
                raise ModError(f"<{file}> does not exist")
        with open(file, "r", encoding="UTF-8") as f:
            code = f.read()
        try:
            mod_globals = {}
            exec(code, mod_globals)
            self.mods[name] = mod_globals
            
            if self.log is not None:
                if self.log.tee:
                    self.log.write(f"Loaded <{name}.py>", type=PLUGINLOADER)
                    return True
            print(f"[PluginLoader] Loaded <{name}.py>")
            return True
        except Exception as e:
            if self.log is not None:
                if self.log.tee:
                    self.log.write(f"Failed to load <{name}>: {e}", type=PLUGINLOADER)
                    return False
            print(f"[PluginLoader] Failed to load <{name}>: {e}")
            return False

    def call(self, hook_name, *args):
        for name, mod in self.mods.items():
            if hook_name in mod: 
                try:
                    mod[hook_name](*args)
                except Exception as e:
                    if self.log is not None:
                        if self.log.tee:
                            self.log.write(f"Error in <{name}.{hook_name}> as {e}", type=PLUGINLOADER)
                            return
                    print(f"[PluginLoader] Error in <{name}.{hook_name}> as {e}")