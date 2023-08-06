#
# mkbackup/windows.py
#
# windows code


import os, sys, time, locale
import _winreg

import archiver


default_encoding=locale.getdefaultlocale()[1]
console_encoding=sys.stderr.encoding


#======================================================================
#
# Event Viewer  logging
#
#======================================================================
import win32evtlog
import win32evtlogutil
import winerror
import win32con
import pywintypes

evt_dict={
        win32con.EVENTLOG_AUDIT_FAILURE:'AUDIT_FAILURE',
        win32con.EVENTLOG_AUDIT_SUCCESS:'AUDIT_SUCCESS',
        win32con.EVENTLOG_INFORMATION_TYPE:'INF',
        win32con.EVENTLOG_WARNING_TYPE:'WAR',
        win32con.EVENTLOG_ERROR_TYPE:'ERR'
        }

# ---------------------------------------------------------------------
def is_volumeid(path):
    return path[:11].lower()=='\\\\?\\volume{'

# ---------------------------------------------------------------------
def FormatEv(ev_obj, logtype):
    computer=str(ev_obj.ComputerName)
    # cat=str(ev_obj.EventCategory)
    level=str(ev_obj.EventType )
    record=str(ev_obj.RecordNumber)
    evt_id=str(winerror.HRESULT_CODE(ev_obj.EventID))
    evt_type=evt_dict.get(ev_obj.EventType, 'UNK')
    msg=win32evtlogutil.SafeFormatMessage(ev_obj, logtype)
    epoch=int(ev_obj.TimeGenerated)
    msg=u'=== eventid=%d eventtype=%s epoch=%d time="%s" ===\r\n%s' % ( ev_obj.EventID, evt_type, epoch, time.ctime(epoch), msg)
    #print ev_obj.EventID, evt_type, int(ev_obj.TimeGenerated), level, msg.encode('UTF-8')
    return msg 

# ---------------------------------------------------------------------
def ReadEvLog(logtype, source, log, start, end=None):
    # If any event is not 'INFO' => return 'ERR'
    # If the last event is not an 'INFO' => return 'WAR' (in fact when not event are present)
    # Else return 'OK'
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
    try:
        hand=win32evtlog.OpenEventLog(None, logtype) # None for localhost
    except pywintypes.error, e:
        log.error('EventLog error %r', e)
        return 'ERR', u'EventLog error %r' % (e, )
    else:
        cont, output, status=True, u'', ''
        while cont:
            events=win32evtlog.ReadEventLog(hand,flags,0)
            for ev_obj in events:
                if str(ev_obj.SourceName)!=source:
                    continue
                if int(ev_obj.TimeGenerated)<start:
                    cont=False
                    break
                if ev_obj.EventType!=win32con.EVENTLOG_INFORMATION_TYPE:
                    status='ERR'
    
                if ev_obj.EventID==8019 and ev_obj.EventType==win32con.EVENTLOG_INFORMATION_TYPE and status!='ERR':
                    status='OK'
                        
                if output:
                    output=FormatEv(ev_obj, logtype)+u'\r\n'+output
                else:
                    output=FormatEv(ev_obj, logtype)
    
            cont=cont and events
        win32evtlog.CloseEventLog(hand)
        
    if status=='':
        status='ERR'

    return status, output

# ---------------------------------------------------------------------
def WindowsErrorDecode(exception, encoding=default_encoding):
    """convert WindowsError or OSError exception into unicode string, 
    some message can contains non ascii chars in non US windows version"""
    
    # if isinstance(exception, (WindowsError, OSError))

    st=str(exception)
    try:
        return st.decode(encoding)
    except UnicodeDecodeError:
        return st.decode('ascii', 'replace')

# ---------------------------------------------------------------------------
def windows_list_dir(target_dir, log, encoding=default_encoding):
    try:
        dir_out, total_size=archiver._list_dir(target_dir, log) 
    except Exception, e:
        log.error('listing target directory: %s', WindowsErrorDecode(e, encoding))
        dir_out='error listing directory "%s": %s\r\n' % (target_dir, WindowsErrorDecode(e, encoding))
        total_size=0
        
    return dir_out, total_size


# =====================================================================
class Registry:

    sub_key="SOFTWARE\\MagiKSys\\MKSBackup\\%s"

    def __init__(self, master_key):
        self.home_key=self.sub_key % (master_key, )
        self.reg=None
        try:
            self.reg=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.home_key, 0, _winreg.KEY_READ|_winreg.KEY_WRITE)
        except EnvironmentError:
            self.reg=_winreg.CreateKey(_winreg.HKEY_LOCAL_MACHINE, self.home_key)
            _winreg.CloseKey(self.reg)
            self.reg=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.home_key, 0, _winreg.KEY_READ|_winreg.KEY_WRITE)
        
    def LoadValues(self, keys=[]):
        values=dict()
        try:
            i=0
            while True:
                k, v, _t=_winreg.EnumValue(self.reg, i)
                i+=1
                if not keys or k in keys:
                    values[k]=v
        except WindowsError:
            pass
        
        return values    
                
    def SaveValues(self, values):
        for k, v in values.iteritems():
            _winreg.SetValueEx(self.reg, k, None, _winreg.REG_SZ, str(v))

    def Close(self):
        if self.reg:
            _winreg.CloseKey(self.reg)

