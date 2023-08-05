import os
import datetime
import time

from _pytest.monkeypatch import monkeypatch

def pytest_funcarg__monkeyplus(request):
    result = monkeyplus()
    request.addfinalizer(result.undo)
    return result

class monkeyplus(monkeypatch):
    def patch_osstat(self, path, st_mode=16877, st_ino=742635, st_dev=234881026, st_nlink=51,
            st_uid=501, st_gid=20, st_size=1734, st_atime=1257942648, st_mtime=1257873561, 
            st_ctime=1257873561):
        """ Patches os.stat for `path`.
    
        Patching os.stat can be tricky, because it can mess much more than what you're trying to test.
        Also, it can be cumbersome to do it. This method lets you do it easily. Just specify a path
        for which you want to patch os.stat, and specify the values through **kwargs. The defaults
        here are just some stats (that make sense) to fill up.
    
        Example call: monkeyplus.patch_osstat('foo/bar', st_mtime=42)
        """
        if not hasattr(self, '_patched_osstat'): # first osstat mock, actually install the mock
            self._patched_osstat = {} # path: os.stat_result
            old_osstat = os.stat
            def fake_osstat(path):
                try:
                    return self._patched_osstat[path]
                except KeyError:
                    return old_osstat(path)
            self.setattr(os, 'stat', fake_osstat)
        st_seq = [st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime]
        self._patched_osstat[path] = os.stat_result(st_seq)
    
    def patch_today(self, year, month, day):
        """Patches today's date to date(year, month, day)
        """
        # For the patching to work system wide, time.time() must be patched. However, there is no way
        # to get a time.time() value out of a datetime, so a timedelta must be used
        new_today = datetime.date(year, month, day)
        today = datetime.date.today()
        time_now = time.time()
        delta = today - new_today
        self.setattr(time, 'time', lambda: time_now - (delta.days * 24 * 60 * 60))
    
    def patch_time_ticking(self, force_int_diff=False):
        """Patches time.time() and ensures that it never returns the same value each time it's
        called.
        
        If force_int_diff is True, the minimum difference between time() result is 1.
        """
        if hasattr(self, '_time_before_ticking_patch'):
            # Already patched, do nothing.
            return
        self._last_time_tick = time.time()
        if force_int_diff:
            self._last_time_tick = int(self._last_time_tick)
        self._time_before_ticking_patch = time.time
        
        def fake_time():
            result = self._time_before_ticking_patch()
            if force_int_diff:
                result = int(result)
            if result <= self._last_time_tick:
                result = self._last_time_tick + 1
            self._last_time_tick = result
            return result
        
        self.setattr(time, 'time', fake_time)
