'''Emulate Brython's browser.html module for offline rendering'''

class _Node:
    def __init__(self, tag, content, **kwargs):
        self.tag = tag
        self.content = [] if content is None else [content]
        self.attrs = kwargs
    def __le__(self, item):
        self.content.append(item)
    def __str__(self):
        style = self.attrs.get('style')
        if isinstance(style, dict):
            self.attrs['style'] = ''.join('%s:%s;'%(k, v) for k, v in style.items())
        open_tag = '%s%s' % (
            self.tag,
            ''.join(' %s=%r'%(k, v) for k, v in self.attrs.items()),
            )
        if not self.content:
            if self.tag == 'div':
                return '<%s></div>' % open_tag
            return '<%s />' % open_tag
        return '<%s>%s</%s>' % (
            open_tag,
            ''.join(str(x) for x in self.content),
            self.tag,
            )

class Html:
    def __getattr__(self, attr):
        def f(content=None, **kwargs):
            return _Node(attr.lower(), content, **kwargs)
        return f

html = Html()
