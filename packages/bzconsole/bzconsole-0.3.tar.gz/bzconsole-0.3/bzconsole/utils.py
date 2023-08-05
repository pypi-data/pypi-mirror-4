import os
import subprocess
import tempfile

def tmpbuffer(editor=None):
    """open an editor and retreive the resulting editted buffer"""
    if not editor:
        editor = os.environ['EDITOR']
    tmpfile = tempfile.mktemp(suffix='.txt')
    cmdline = editor.split()
    cmdline.append(tmpfile)
    edit = subprocess.call(cmdline)
    buffer = file(tmpfile).read().strip()
    os.remove(tmpfile)
    return buffer
