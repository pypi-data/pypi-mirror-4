import pybedtools
import sys
x = pybedtools.example_bedtool('rmsk.hg18.chr21.small.bed')
c = [0]
def TTS(feature, upstream=1000, downstream=1000):
    if feature.strand == '-':
        tts = feature.start
        start = tts - downstream
        stop = tts + upstream
    else:
        tts = feature.stop
        start = tts - upstream
        stop = tts + downstream
    start = max(start, 0)
    c[0] += 1
    print start, c
    sys.stdout.flush()
    feature.start = start
    feature.stop = stop
    return feature

def f(x):
    x.start = 0
    x.stop = 1
    return x

print "using 'f'...",
sys.stdout.flush()
y = x.each(f).saveas()
print "done."
sys.stdout.flush()

print "using 'TTS'...",
sys.stdout.flush()
y = x.each(TTS).saveas()
print 'done'
sys.stdout.flush()
