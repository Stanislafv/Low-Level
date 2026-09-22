try:
    import pymsgbox
except Exception:
    raise Exception("Install pymsgbox")

try:
    import traceback
    import os, applib
    import testing
    from base.MusicPlayer import MusicPlayer
    from base.folders import folder

    from ui.MainWindow import MainWindow

    from base.font import application
except Exception:
    pymsgbox.alert(f"Critical StartError:\n{traceback.format_exc()}", "C1", icon=pymsgbox.STOP)
    __import__("os").abort()

def main()->int:
    try:
        failed, critical = testing.start(testing.Mode.SMOKE)

        if critical:
            folder.log.write("\n".join(critical), type="StartError", set_error=True)
            pymsgbox.alert(f"Critical StartError:\n{"\n".join(critical)}", "C2", icon=pymsgbox.STOP)
            return 1
        
        if failed:
            folder.log.write("\n".join(failed), type="StartError", set_error=True)
            if pymsgbox.confirm(f"Failed {len(failed)} tests:\n{"\n".join(failed)}\nLaunch the game?", "C3", icon=pymsgbox.WARNING) != pymsgbox.OK_TEXT:
                return 1

        if not failed and not critical:
            folder.log.write("All systems online", type="StartInfo")

        folder.plugins.init()

        folder.plugins.call("pre_start", application)

        window = MainWindow()
        window.showFullScreen()

        folder.plugins.call("start", window)

        MusicPlayer.start()
    except Exception as e:
        folder.log.write(traceback.format_exc(), type="StartError", set_error=True)
        if "window" in locals():
            if window is not None:
                window.close()

        pymsgbox.alert(f"Critical StartError: {e}", "C(global)", icon=pymsgbox.STOP)
        return 1
    
    return application.exec()

if __name__ == "__main__":
    os._exit(max(main(), applib._exit_code))