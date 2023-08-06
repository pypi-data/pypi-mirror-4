# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import subprocess
import sys
import threading

from .utils import *

class FilePlayer(object):
    def __init__(self, cfg):
        self.cfg = cfg

    def play_file(self, fn):
        if fn.startswith(u'-'):
            fn = u'./' + fn
        cmd = [self.cfg['exe']] + self.cfg['fileOpts'] + [fn]
        proc = subprocess.Popen(cmd)
        self._proc = proc
        proc.wait()

    def check(self):
        try:
            cmd = [self.cfg['exe']] + [self.cfg['checkOpts']]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.communicate()
        except OSError:
            return False
        return p.returncode == 0

    def terminate(self):
        p = self._proc
        if p:
            p.terminate()

class IncrementalPlayer(FilePlayer):
    def __init__(self, cfg):
        assert 'incrementalOpts' in cfg
        super(IncrementalPlayer, self).__init__(cfg)

    def play_incremental(self, block_queue):
        cmd = [self.cfg['exe']] + self.cfg['incrementalOpts']
        self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        pos = 0
        while True:
            block_queue.get()
        # TODO feed



def _find_player(fn, players=None):
    """ players is either an array of executable names or None (auto-detect) """
    SUPPORTED = [
        {
            'exe': 'mplayer',
            'incrementalOpts': ['-'],
            'fileOpts': ['-really-quiet'],
            'checkOpts': ['-help']
        },
        {
            'exe': 'vlc',
            'incrementalOpts': ['-'],
            'fileOpts': [],
            'checkOpts': ['--version']
        },
        {
            'exe': 'xdg-open',
            'fileOpts': [],
            'checkOpts': ['--version'],
        }
    ]
    if sys.platform == 'darwin': # open has entirely different semantics on Linux
        SUPPORTED.append({
            'exe': 'open',
            'fileOpts': [],
            'checkOpts': ['--version']
        })
    if players:
        configs = []
        for p in playerp:
            try:
                cfg = next(p for p in SUPPORTED if p['exe'] == p)
            except StopIteration:
                # Unsupported player, construct defaults
                cfg = {
                    'exe': p,
                    'fileOpts': [],
                    'checkOpts': ['--help'],
                }
            configs.append(cfg)
    else:
        configs = SUPPORTED

    for c in configs:
        klass = IncrementalPlayer if 'incrementalOpts' in c else FilePlayer
        player = klass(c)
        if player.check():
            return player

    raise OSError(u'Cannot find a suitable player program. Use --player to specify one')    

class BlockQueue(compat_Queue):
    def __init__(self, filename):
        super(BlockQueue, self).__init__()
        self._filename = filename

    def put(progress):
        if progress['filename'] == self._filename:
            super(BlockQueue, self).put(progress)


QUIT_SIGNAL = object()

class PlayerManager(threading.Thread):
    def __init__(self, fd, players_spec=None, playbuffer='finished'):
        super(PlayerManager, self).__init__()
        self._fd = fd
        assert playbuffer == 'finished' or isinstance(playbuffer, int)
        self._players_spec = players_spec
        self._playbuffer = playbuffer

        self._to_play = compat_Queue()
        self._notified = set() # All the files we have already 
        self._block_queue = None

    def __enter__(self):
        self.start()

    def __exit__(self):
        self.quit()

    def quit(self):
        self._to_play.put(QUIT_SIGNAL)

    def start(self):
        self._player = _find_player(_players_spec)
        self._fd.add_progress_hook(self._progress_hook)
        super(PlayerManager, self).start()

    def run(self):
        supports_incremental = hasattr('play_incremental', self._player)
        played = set()
        while True:
            progress = self._to_play.get()
            if progress is QUIT_SIGNAL:
                self._player.terminate()
                break
            fn = progress['filename']
            if fn in played:
                continue
            played.add(fn)
            if progress['status'] == 'finished':
                self._player.play_file(fn)
            elif progress['status'] == '__player_start':
                assert supports_incremental
                self._block_queue = BlockQueue(fn, progress['file_handle'])
                self._player.play_incremental(progress, self._block_queue)
                self._block_queue = None

    
    def _progress_hook(self, progress):
        if progress['status'] == 'finished':
            self._notified.add(progress['filename'])
            self._to_play.put(progress)
        if (self._playbuffer != 'finished' and 
            progress['status'] == 'downloading' and
            progress.get('downloaded_bytes', 0) >= self._playbuffer and
            hasattr('play_incremental', self._player)
        ):
            if progress['filename'] not in notified:
                self._notified.add(progress['filename'])
                fh = TODO_dup_fh
                vp = {
                    'bytes_downloaded': progress['bytes_downloaded'],
                    'filename': progress['filename'],
                    'file_handle': fh,
                }
            bq = self._block_queue
            if bq:
                bq.put(progress)

