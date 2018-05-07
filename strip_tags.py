# -*- coding: utf-8-*-
def strip_tags(html):
    import re
    dr = re.compile(r'<[^>.*]+>', re.S)
    dd = dr.sub('', html)
    dd = re.sub(r'500\)this.width=500\' align=\'center\' hspace=10 vspace=10 alt=', ' ', dd)
    dd = re.sub(r'500\)this.width=500\' align=\'center\' hspace=10 vspace=10  rel=\'nofollow\'/>', '', dd)
    dd = re.sub(r'500\)this.width=500\'align=\'center\'hspace=10vspace=10rel=\'nofollow\'/>', ' ', dd)
    dd = re.sub(r'500\)this.', ' ', dd)
    dd = re.sub(r'500\)this.width=500\' align=\'center\' hspace=10 vspace=10>', ' ', dd)
    # dd = re.sub(r'.......................................................................................', ' ', dd)
    # dd = re.sub(r'................................................................................', ' ', dd)
    # dd = re.sub(r'.....................................................................................', ' ', dd)
    # dd = re.sub(r'...............................................................................', ' ', dd)
    return dd