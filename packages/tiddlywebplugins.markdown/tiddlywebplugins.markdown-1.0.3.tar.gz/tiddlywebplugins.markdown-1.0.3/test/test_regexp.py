
import re

freelink = r'^(.*?)(?:^|(?<=[\s|\(]))\[\[(.+?)\]\](.*?)$'
testlink = r'^(.*?)(?:^|(?<=[\s|\(]))\[\[(.+?)\]\](@[0-9a-z][0-9a-z\-]*?[0-9a-z])(?:\b|$)(.*?)$'
spacelink = r'^(.*?)(?:^|(?<=[\s|\(]))\[\[(.+?)\]\](@[0-9a-z][0-9a-z\-]*[0-9a-z])(?:\b|$)(.*?)$'

free_re = re.compile(freelink)
test_re = re.compile(testlink)
space_re = re.compile(spacelink)

regexps = [
    #free_re,
    test_re,
    space_re
]

test_text = [
    'various [[Bugs]] [[foo]]@ti release',
    'various [[Bugs]] ]] release',
    'various [[Bugs]] [[food]] release',
]

def test_the_re():
    for regexp in regexps:
        print regexp.pattern
        for text in test_text:
            print '\t', text
            m = regexp.match(text)
            if m:
                print '\t', m.groups()
            else:
                print 'no match'


