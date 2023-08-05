#!/usr/bin/python

"""
-----------------------------------------------
wordy.py, or "A Million Monkeys Can't be Wrong"
-----------------------------------------------

A generic Lorum Ipsum type generator, outputting random paragraphs of text
for pasting into your content management solution, your page templates or any
other use you can think of (sometimes I run it over and over again to see if
it makes poetry - it never does).

Usage:
``./wordy.py -p N -w /path/to/word/file -o /path/to/output/file``
    Writes N paragraphs of random text to the specified output file using the 
    specified word file as the source.  By default we use /use/share/dict/words,
    but any file with one word per line will do

``-p`` *or* ``--paragraphs``
    Defines the number of paragraphs to be written.  

``-w`` *or* ``--word-file``
    Specified the source word file to use.  If this option is missed
    /usr/share/dict/words is used.

``-o`` *or* ``--out-file``
    Specifies the file to write the output to.  If this option is missed the
    output is written to screen.

Or you can simply run ``./wordy.py N`` and N paragraphs of text will be written
to screen
"""

__author__ = "Andy Theyers <andy@isotoma.com>"
__version__ = "$Revision: 1136 $"[11:-2]
__docformat__ = "restructuredtext"

import random

default_word_file = '/usr/share/dict/words'

class WordSmith:
    
    """ A real million monkeys, this one """

    def __init__(self, wordfile=None):
        if wordfile is None:
            self.wordfile = default_word_file
        else:
            self.wordfile = wordfile
        
    def __call__(self, paras=3, outfile=None):
        paragraphs = []
        for i in range(paras):
            type = random.randint(0,2)
            if type == 0:
                sentences = random.randint(2,4)
            elif type == 1:
                sentences = random.randint(3,6)
            else:
                sentences = random.randint(4,9)
            paragraphs.append(self._getparagraph(sentences))
        return paragraphs
             
    def _getword(self):
        if not hasattr(self, '_words'):
            self._words = open(self.wordfile, 'r').read().split()
            self._words_len = len(self._words)
        return unicode(self._words[random.randint(0, self._words_len -1)], 'latin_1')

    def _getsentence(self):
        length = random.randint(3,15)
        raw = ' '.join([ self._getword() for i in range(length)])
        return raw[0].upper() + raw[1:] + '. '
        
    def _getparagraph(self, sentences):
        return ''.join([ self._getsentence() for i in range(sentences)])

def main():
    import sys
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-w",
                      "--word-file",
                      dest="word_file",
                      help=("Use this file as the word source, instead "
                            "of the default (/usr/share/dict/words)")
                     )
    parser.add_option("-o",
                      "--out-file",
                      dest="outfile",
                      help="Write the output to this file"
                     )
    parser.add_option("-p",
                      "--paragraphs",
                      type="int",
                      dest="paragraphs",
                      help="Defines the number of paragraphs of output"
                     )
    (options, args) = parser.parse_args()
    
    if not options.paragraphs:
        if len(args) == 1 and args[0].isdigit():
            paras = int(args[0])
        else:
            print "This script requires a number of paragraphs:"
            print "  use -p or --paragraphs"
            print ""
            sys.exit()
    else:
        paras = options.paragraphs
        
    if not options.word_file:
        wordfile = default_word_file
    else:
        wordfile = options.word_file
        
    wordsmith = WordSmith(wordfile=wordfile)
    wordsmith(paras=paras, outfile=options.outfile)

if __name__ == '__main__':
    main()
