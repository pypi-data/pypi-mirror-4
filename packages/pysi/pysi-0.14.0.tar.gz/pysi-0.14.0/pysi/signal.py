# -*- coding: utf-8 -*-
'''
Сигналы

    @pysi.signal.connect('sig')
    def my_sig(rq, var):
        rq.context['test'] = var

    @pysi.view('/')
    def index(rq):
        pysi.signal.send('sig', rq, u'сигналит')
        return {'a': 1}
'''

_signals = {}

def connect(signal_name):
    def decorator(func):
        _signals.setdefault(signal_name, []).append(func)
        return func
    return decorator
    
def send(signal_name, *args, **kwargs):
    if signal_name in _signals:
        for func in _signals[signal_name]:
            func(*args, **kwargs)