
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
    h = Parser(strict=False)
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

    h = Parser()

    h.feed(s)
    h.close()
    r = h.get_help()
