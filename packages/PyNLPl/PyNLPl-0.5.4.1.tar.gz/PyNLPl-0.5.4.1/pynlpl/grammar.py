#---------------------------------------------------------------
# PyNLPl - Grammar
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------


class Grammar(object):
    """Represents a context free grammar (may be probablistic)"""
    
    def __init__(self, probablistic=False):    
        self.rules = []
        self.probablistic = False
        
    def append(self, rule):
        assert isinstance(rule, GrammarRule)
        if rule.prob is None:
            if self.probablistic:
                raise ValueError("Grammar rule has to be probablistic to be appended to this grammar, but no probability specified")        
        self.rules.append(rule)

    def __str__(self):
        lines = []
        for rule in rules:
            lines += str(rules)
        return lines
                        
    def __unicode__(self):
        lines = []
        for rule in rules:
            lines += unicode(rules)
        return lines

    def __len__(self):    
        return len(self.rules)
    
    def __getindex__(self, i):
        return self.rules[i]
    
    def __iter__(self):
        for rule in self.rules:
            yield rule
    
    def isnormalform(self):
        for rule in self:
            if len(rule) > 2:
                return False
        return True
    
    def tonormalform(self):
        #convert to normalform 

class GrammarRule(object):
    """Represent a rule in a (probablistic) context free grammar"""
    
    def __init__(self, symbol, constituents, prob = None, terminal=False):
        self.symbol = symbol
        self.prob = prob
        self.terminal = terminal
        assert isinstance(constituents, list) or isinstance(constituents, tuple)
        self.constituents = constituents
        
    def __len__(self):
        return len(self.constituents)
        
    def isunary():
        return (len(self.constituents) == 1)
    
    def __str__(self):
        s = str(self.symbol) + ' -> ' + ' '.join([str(x) for x in self.constituents])
        if self.terminal:
            s = + ' [TERM]'
        if not (self.prob is None): 
            s = + ' ['+str(self.prob)+']'        
    
    def tonormalform():
        #convert to normal form
        

class CKYParser(object):        
    def __init__(self, grammar):
        assert isinstance(grammar, Grammar)
        self.grammar = grammar

    def parse(self, sentence):    
        
        
