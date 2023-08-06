from verbose import verbose

#import StringIO
import formatter

import sys
if sys.version_info[0] >= 3:
    import io as StringIO
    #self._pswriter = io.StringIO()
else:
    import StringIO
    #self._pswriter = cStringIO.StringIO()


import re

p_sy = re.compile("Syntax:\s*")
p_ex = re.compile("Example:\s*")

#_trail_comment = r"(\s*(#.*)?)"
_trail_comment = r"(\s?)"
_redirect_file = r"\s*>\s*([\w.]+)"

#p_xpaget = re.compile(r"\$xpaget\s+ds9\s+([\s\w\d\-\+:.{}'\"]*)")
p_xpaget = re.compile(r"\$xpaget\s+ds9\s+(.*)")

p_xpaget_wo_ds9 = re.compile(r"\$xpaget\s+([\s\w\d\-\+:.{}]*)")

p_xpaget_w_redirect = re.compile(r"\$xpaget\s+ds9\s+([\s\w\d\-\+:.{}]*)" \
                                 + _redirect_file)

p_xpaget_mask = re.compile(r"\$xpaget\s+mask\s*([\w\d\-\+:.{}]*)")

#p_xpaset = re.compile(r"\$xpaset\s+-p\s+ds9\s+([\s\w\d\-\+:.{}'\"]*)")
p_xpaset = re.compile(r"\$xpaset\s+-p\s+ds9\s+(.*)")

p_xpaset_wo_ds9 = re.compile(r"\$xpaset\s+([\s\w\d\-\+:.{}]*)(\s*(#.*)?)")

p_xpaset_w_echo = re.compile(r"\$echo\s+(.+)\s+\|\s+xpaset\s+ds9\s+(.*)")

# We use "xpa[sg]et" due to the bug in the xpa.html
p_xpaset_w_cat = re.compile(r"\$cat\s+(.+)\s+\|\s+xpa[sg]et\s+ds9\s+(.*)")


from tokenize import generate_tokens, COMMENT

# comments are detected using tokenize.generate_tokens
def takeout_comment(s):

    g = generate_tokens(StringIO.StringIO(s).readline)
    c = [tokval for toknum, tokval, _, _, _  in g if toknum == COMMENT]
    if c:
        return s.replace(c[0],"").strip(), c[0]
    else:
        return s, ""

def _convert_syntax(l):

    l, c = takeout_comment(l)
    # SET
    if p_xpaset_w_echo.search(l):
        #print l
        r = p_xpaset_w_echo.subn(r"ds9.set('\2', \1)", l)[0]
    elif p_xpaset_w_cat.search(l):
        s = r"r=open('\1').read(); ds9.set('\2', r)"
        r = p_xpaset_w_cat.subn(s, l)[0]
    elif p_xpaset.search(l):
        r = p_xpaset.subn(r"ds9.set('\1')", l)[0]
    elif p_xpaset_wo_ds9.search(l):
        r = p_xpaset_wo_ds9.subn(r"ds9.set('\1')", l)[0]

    # GET
    elif p_xpaget_w_redirect.search(l):
        s = r"r = ds9.get('\1'); open('\2','w').write(r)"
        r = p_xpaget_w_redirect.subn(s, l)[0]
    elif p_xpaget_mask.search(l):
        r = p_xpaget_mask.subn(r"r = ds9.get('mask \1')", l)[0]
    elif p_xpaget.search(l):
        r = p_xpaget.subn(r"r = ds9.get('\1')", l)[0]
    else:
        if l:
            if not l[0] == "#":
                verbose.report("WARNING : failed to convert (%s)" % l,
                               "helpful")
        r = l

    if c:
        r = r + " " + c

    return r


import sys
if sys.version_info[0] < 3:
    #import htmllib
    import HTMLParser
else:
    import html.parser as HTMLParser
from formatter import AS_IS
from html.entities import name2codepoint

class parser(HTMLParser.HTMLParser):
    def __init__(self, **kwargs):

        self.nullwriter = formatter.NullWriter()
        self.fmtr = formatter.AbstractFormatter(self.nullwriter)
        HTMLParser.HTMLParser.__init__(self,  **kwargs)

        self.help_strings = dict()

        self.fmtr.writer = self.nullwriter

        self._current_help = ""
        self.h4 = False

        self.nofill = 0

    def handle_starttag(self, tag, attrs):
        if tag == "h4":
            self.start_h4(attrs)
        elif tag == "a":
            self.start_a(attrs)
        elif tag == "pre":
            self.start_pre(attrs)

    def handle_endtag(self, tag):
        if tag == "h4":
            self.end_h4()
        elif tag == "pre":
            self.end_pre()

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        #print("Named ent:", c)
        self.fmtr.add_flowing_data(c)

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        #print("Num ent  :", c)
        self.fmtr.add_flowing_data(c)

    def handle_data(self, d):
        if self.h4:
            self.h4_title = self.h4_title + d.strip()
        else:
            if self.nofill:
                self.formatter.add_literal_data(d)
            else:
                self.fmtr.add_flowing_data(d)
            #htmllib.HTMLParser.handle_data(self, d)
            #print("#", d)

    # For older version of ds9 (e.g., ds9_v5.6), the xpa.html uses
    # <h4>, but in the later versions (e.g., v6.2), they use <a
    # name="#..">.

    def start_h4(self, attrs):
        self.h4 = True
        self.h4_title = ""

    def end_h4(self):
        #print self.h4_title

        if self.h4_title:
            f = StringIO.StringIO("")
            self.help_strings[self.h4_title] = f
            self.fmtr.writer = formatter.DumbWriter(f, 800)

        self.h4 = False


    def start_a(self, attrs):
        dattrs = dict(attrs)
        print(dattrs)
        if "name" in dattrs:

            h4_title = dattrs["name"]

            f = StringIO.StringIO("")
            self.help_strings[h4_title] = f
            self.fmtr.writer = formatter.DumbWriter(f, 800)

    def start_pre(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_font((AS_IS, AS_IS, AS_IS, 1))
        self.nofill = self.nofill + 1

    def end_pre(self):
        self.formatter.end_paragraph(1)
        self.formatter.pop_font()
        self.nofill = max(0, self.nofill - 1)


    def get_help(self):
        r = dict()

        for k, v in self.help_strings.items():
            s = v.getvalue()
            v.close()

            ## Syntax :
            ss = p_sy.split(s)

            if len(ss) == 1:
                # a special case for "psprint" with only description.
                #print "whats going on?", k, ss
                expl = ss[0].replace("\240", " ")
                syntax = ""
                example = ""

            elif len(ss) == 2:
                expl, _rest = ss
                # replace "nbsp"
                expl = expl.replace("\240", " ")

                ## Example :
                syntax, example = p_ex.split(_rest)

                # replace "nbsp"
                syntax = syntax.replace("\240", " ")
                example = example.replace("\240", " ")


                ex_ = [_convert_syntax(l.strip()) for l in example.split("\n")]
                example = "\n".join(ex_)


            else:
                print("ignoring %s : failed to pars." % k)
                continue

            # fix expl
            filtered_expl = [l for l in expl.split("\n") if l.strip() and l.strip() != k]

            #expl
            r[k] = dict(expl="\n".join(filtered_expl), syntax=syntax, example=example)

            #print h.help_strings["header"].getvalue().replace("\240"," ")
        return r


#open("xpa.html").read()
def parse_xpa_help(s):
    h = parser()

    h.feed(s)
    h.close()
    r = h.get_help()

    return r


def test2():
    t = """
<!DOCTYPE doctype PUBLIC "-//w3c//dtd html 4.0 transitional//en">
<html>
<body link="#0000ff" vlink="#551a8b" alink="#ff0000">
<blockquote>
  <p>The <a href="http://hea-www.harvard.edu/RD/xpa/index.html">XPA </a>
messaging system provides seamless communication between DS9 and other
Unix programs, including X programs, Perl, <a
 href="http://space.mit.edu/cxc/software/slang/modules/xpa/"> S-Lang,</a>
and Tcl/Tk. It also provides an easy way for users to communicate with
DS9 by executing XPA client commands in the shell or by utilizing such
commands in scripts. Because XPA works both at the programming level
and the shell level, it is a powerful tool for unifying any analysis
environment.</p>
  <tt> <a href="#2mass">2mass</a><br>
  <a href="#about">about</a><br>
  <a href="#analysis">analysis</a><br>
  <a href="#array">array</a>
  </tt>
</body>
</html>
"""
    h = parser(strict=False)
    h.feed(t)
    h.close()

    s = open("../tt.html").read()
    h.feed(s)
    h.close()
    print(h.help_strings)

def test1():
    HTMLParser = htmllib.HTMLParser

    class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            print("Encountered a start tag:", tag)
        def handle_endtag(self, tag):
            print("Encountered an end tag :", tag)
        def handle_data(self, data):
            print("Encountered some data  :", data)

    parser = MyHTMLParser(strict=False)
    parser.feed('<html><head><title>Test</title></head>'
                '<body><h1>Parse me!</h1></body></html>')

if __name__ == "__main__":
    s = open("../tt.html").read()
    #r = parse_xpa_help(s)
    #test2()

    h = parser()

    h.feed(s)
    h.close()
    #r = h.get_help()
