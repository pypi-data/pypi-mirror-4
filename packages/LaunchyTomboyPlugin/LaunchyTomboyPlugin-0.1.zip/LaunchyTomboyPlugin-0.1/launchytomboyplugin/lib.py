import glob
from os import environ as ose
import os.path as osp
import subprocess
import sys
import xml.etree.cElementTree as et

BASE_DIR = osp.dirname(__file__)
ICON_DIR = osp.join(BASE_DIR, 'icons')
TOMBOY_ICON_PATH = osp.join(ICON_DIR, 'tomboy.png')
NEWNOTE_ICON_PATH = osp.join(ICON_DIR, 'notebook-new.png')

class TomboyLib(object):
    def __init__(self):
        self.name = "Tomboy"
        self.icon = TOMBOY_ICON_PATH
        self.new_note_icon = NEWNOTE_ICON_PATH

    def debug(self, *msg):
        if ose.get('LAUNCHY_TOMBOY_DEBUG'):
            sys.stdout.write('TOMBOY - ' + ' '.join(map(str, msg)) + '\n')

    def error(self, *msg):
        sys.stderr.write('TOMBOY - ' + ' '.join(map(str, msg)) + '\n')

    @property
    def tomboy_notes_dir(self):
        if ose.get('TOMBOY_PATH'):
            return ose.get('TOMBOY_PATH')
        return osp.join(ose.get('APPDATA'), 'Tomboy', 'notes')

    @property
    def tomboy_exe_path(self):
        tp_path = ose.get('TOMBOY_PROGRAM_PATH')
        if not tp_path:
            pf_path = ose.get('ProgramFiles(x86)')
            if not pf_path:
                pf_path = ose.get('ProgramFiles')
            if not pf_path:
                self.error('Can\'t get tomboy path environment variables: '
                           '"TOMBOY_PROGRAM_PATH", "ProgramFiles(x86)", or "ProgramFiles"')
            tp_path = osp.join(pf_path, 'Tomboy', 'Tomboy.exe')
        if not osp.isfile(tp_path):
            self.error('Tomboy.exe not found at', tp_path, '.  Set TOMBOY_PROGRAM_PATH environment variable and restart Launchy.')
        return tp_path

    @property
    def note_paths(self):
        glob_pattern = osp.join(self.tomboy_notes_dir, '*.note')
        return glob.glob(glob_pattern)

    @property
    def note_titles(self):
        for fpath in self.note_paths:
            root = et.parse(fpath).getroot()
            title = root.find('{http://beatniksoftware.com/tomboy}title')
            if title is not None:
                yield title.text

    def launch_note(self, note_title):
        self.tomboy_exec('--open-note', note_title)

    def new_note(self):
        self.tomboy_exec('--new-note')

    def search_notes(self):
        self.tomboy_exec()

    def debug_info(self):
        self.debug('Name:', self.name)
        self.debug('Icon dir:', self.icon)
        self.debug('Tomboy exe path:', self.tomboy_exe_path)
        self.debug('Notes dir:', self.tomboy_notes_dir)
        self.debug( 'Note count:', len(self.note_paths))
        for title in self.note_titles:
            self.debug('First note:', title)
            break

    def debug_actions(self):
        for title in self.note_titles:
            self.launch_note(title)
            break
        self.new_note()

    def tomboy_exec(self, *tomboyargs):
        args = [self.tomboy_exe_path]
        args.extend(tomboyargs)
        self.debug('executing tomboy', args)
        proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            )
        stdout, stderr = proc.communicate()
        self.debug('cmd return code: ', proc.returncode)
        self.debug('cmd stdout: ', stdout)
        self.debug('cmd stderr: ', stderr)

if __name__ == '__main__':
    ose['LAUNCHY_TOMBOY_DEBUG'] = '1'
    tbl = TomboyLib()
    tbl.debug_info()
    tbl.debug_actions()
