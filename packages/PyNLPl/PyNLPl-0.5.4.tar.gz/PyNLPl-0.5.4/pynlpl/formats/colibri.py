#-*- coding:utf-8 -*-


class NGram(object):
    def __init__(self, l):
        if isinstance(l, str) or instance(l, unicode):
            self.data = tuple(l.split(' '))
        elif isinstance(l, tuple):
            self.data = l
        else:
            self.data = tuple(l)
    
    def __len__(self):
        return len(self.data)


class SkipGram(NGram):
