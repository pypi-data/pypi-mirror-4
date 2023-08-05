#coding=utf-8
import syslog,traceback

DEBUG = False

def _open(log_name):
    '''
    打开日志
    log_name:日志标示
    ret:无返回
    '''
    if DEBUG:
        syslog.openlog(log_name,syslog.LOG_PERROR,syslog.LOG_LOCAL0)
    else:
        syslog.openlog(log_name,0,syslog.LOG_LOCAL0)
    
def _close():
    '''
    关闭日志
    ret:无返回
    '''
    syslog.closelog()

def _err(**kw):
    '''
    记录出错日志
    kw:需要记录的信息
    ret:无返回
    '''
    _log(level = syslog.LOG_ERR,**kw)
    
def _warning(**kw):
    '''
    记录告警日志
    kw:需要记录的信息
    ret:无返回
    '''
    _log(level = syslog.LOG_WARNING,**kw)
        
def _notice(**kw):
    '''
    记录notice日志
    kw:需要记录的信息
    ret:无返回
    '''
    _log(level = syslog.LOG_NOTICE,**kw)
    
def _info(**kw):
    '''
    记录INFO日志
    kw:需要记录的信息
    ret:无返回
    '''
    _log(level = syslog.LOG_INFO,**kw)
    
def _log(**kw):
    '''
    集体记录信息
    kw:需要记录的信息参数
    ret:无返回
    '''
    exc = ''
    level = kw.pop('level',syslog.LOG_WARNING)
    is_err = kw.pop('err',False)
    if level == syslog.LOG_ERR or is_err:exc = traceback.format_exc()
    for k in kw.keys(): 
        val = str(kw.get(k))
        if val and type(val) == unicode:
            val = val.encode('utf-8')
        exc += ' ：' + val  
     
    syslog.syslog(level,exc)
