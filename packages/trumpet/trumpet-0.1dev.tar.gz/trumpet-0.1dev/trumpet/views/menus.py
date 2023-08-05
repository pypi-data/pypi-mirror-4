import sys
i = sys.version_info
if i[0] > 2 or i[1] > 6:
    from collections import OrderedDict
else:
    from leaflet.OrderedDict import OrderedDict
    
from formencode.htmlgen import html, Element

class Table(Element):
    def __init__(self, **kw):
        Element.__init__(self, 'table', {})

class UL(Element):
    def __init__(self, **kw):
        Element.__init__(self, 'ul', {})

class Nav(Element):
    def __init__(self, **kw):
        Element.__init__(self, 'nav', {})
class Div(Element):    
    def __init__(self, **kw):
        Element.__init__(self, 'div', {})

class BaseMenu(UL):
    def __init__(self, header='BaseMenu', **args):
        UL.__init__(self, **args)
        UL.set(self, 'class', 'left-menu')
        #UL.set(self, 'class', 'nav-list')
        self.list = self
        self.append(self.list)
        self._menu = {}
        self.set_header(header)
        self.top_entry = None
        self.bottom_entry = None
        
    def set_header(self, header=None):
        if header is not None:
            self._header = header
        while len(self.getchildren()):
            self.remove(self.getchildren()[0])
        self.list.append(html.li(self._header, class_="left-menu-header"))

    def append_new_entry(self, name, page):
        atts = {}
        if 'class' in self.attrib:
            atts['class'] = self.attrib['class']
        self._menu[name] = html.a(name, href=page)
        li = html.li(self._menu[name])
        self.list.append(li)

    def set_new_entries(self, entries, header=None):
        self.set_header(header)
        if self.top_entry:
            self.append_new_entry(*self.top_entry)
        for name, page in entries:
            self.append_new_entry(name, page)
        if self.bottom_entry:
            self.append_new_entry(*self.bottom_entry)

    def output(self):
        return unicode(self)


"""
    <ul>
      <li class="has-dropdown"><a href="#">extra</a>
	<ul class="dropdown">
          <li><a href="#">Link 1</a></li>
          <li><a href="#">Link 2</a></li>
          <li><a href="#">Link 3</a></li>
	</ul>
      </li>
    </ul>
    <ul class="right">
      <li class="has-dropdown"><a href="#">Link 3</a>
	<ul class="dropdown">
          <li><a href="#">Link 1</a></li>
          <li><a href="#">Link 2</a></li>
          <li><a href="#">Link 3</a></li>
	</ul>
      </li>
    </ul>
  </nav>
"""
class TopBar(object):
    def __init__(self, title):
        self.title = title
        self.entries = OrderedDict()

    def render(self):
        data = '<nav class="top-bar"><ul>\n'
        template = '<li><a href="%s" class="active"><span>%s</span></a></li>\n'
        for name, page in self.entries.items():
            data += template % (page, name)
        data += '</ul></nav>\n'
        return data


class TopTabs(OrderedDict):
    def html_output(self):
        data = '<nav class="top-bar"><ul>\n'
        template = '<li><a href="%s" class="active"><span>%s</span></a></li>\n'
        for name, page in self.items():
            data += template % (page, name)
        data += '</ul></nav>\n'
        return data


