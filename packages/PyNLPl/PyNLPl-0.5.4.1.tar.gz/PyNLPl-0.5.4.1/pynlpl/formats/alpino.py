#! /usr/bin/env python
# -*- coding: utf8 -*-

import folia
import lxml.etree

class AlpinoNode(object):
    

class AlpinoTree(object):
    def __init__(self, filename = None, id = None, annotator = 'alpino', annotatortype = folia.AnnotatorType.AUTO):
        if filename:
            parsexml(filename)
        
        if not id:
            id = id=os.path.basename(filename.replace('.xml',''))
        self.foliadoc = folia.Document(id=id)
        self.foliadoc.declare(folia.AnnotationType.POS, "cgn", annotator=annotator, annotatortype=annotatortype)
        self.foliadoc.declare(folia.AnnotationType.SYNTAX, "alpino-syntax", annotator=annotator, annotatortype=annotatortype)
        self.foliadoc.declare(folia.AnnotationType.DEPENDENCY, "alpino-dependency", annotator=annotator, annotatortype=annotatortype)
        self.foliatext = self.foliadoc.append(folia.Text)
         
        
    def parsexml(self, filename):
        tree = lxml.etree.parse(filename)
        node = tree.getroot()
        foliasentence = self.foliatext.append(folia.Sentence)
        syntaxlayer = foliasentence.append(folia.SyntaxLayer)
        dependencylayer = foliasentence.append(folia.DependencyLayer)
        
        if node.tag == "alpino_ds":
            for e in node:
                if e.tag == 'node':
                    self.parsenode(e):
                elif e.tag == 'sentence':
                    foliasentence.settext(e.value)
        else:
            raise Exception("No Alpino XML file: " + filename)
        
    def parsenode(self, node):
        for subnode in node:
            if subnode.tag == 'node':
                self.parsenode(e)
                
                
        
