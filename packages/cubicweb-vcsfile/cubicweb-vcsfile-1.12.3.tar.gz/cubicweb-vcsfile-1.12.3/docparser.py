# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from logilab.mtconverter import xml_escape
from logilab.mtconverter.transform import Transform

class Diff2HTMLTransform(Transform):
    """note: this transform use CSS classes which can be obtained using:
    formatter.get_style_defs()
    """
    inputs = 'text/x-diff',
    output = 'text/annotated-html'
    name = 'Diff2HTMLTransform'

    def __init__(self, ipcb=None):
        # insert point callback
        self._ipcb = ipcb

    def _convert(self, trdata):
        cw = trdata.appobject._cw
        trdata.__counter = 0
        cw.add_css('cubes.vcsfile.css')
        output = []
        w = output.append
        cbs = {'+++': self.new_file,
               '---': self.old_file,
               'diff': self.start_file,
               '@@': self.start_chunk,
               }
        w(u'<div class="text/x-diff">\n')
        w(u'<div class="diffComment">\n')
        self._done_cb = self.stop_comment
        self._continue_cb = self.comment_line
        lines = trdata.decode().split('\n')
        if lines[-1] == '':
            del lines[-1]
        for line in lines:
            try:
                cb = cbs[line.split(' ', 1)[0]]
            except KeyError:
                if self._continue_cb is not None:
                    self._continue_cb(trdata, w, line)
            else:
                if self._done_cb is not None:
                    self._done_cb(trdata, w)
                    self._done_cb = None
                self._continue_cb = None
                cb(trdata, w, line)
        if self._done_cb is not None:
            self._done_cb(trdata, w)
        w(u'</div>\n')
        return ''.join(output)

    def diff_line(self, trdata, w, line):
        cssclass = {'-': 'diffOldLine',
                    '+': 'diffNewLine',
                    ' ': 'diffLine',
                    '\\': 'diffOldLine'}[line[0]]
        trdata.__counter += 1
        w(u'<span class="lineCount">%s</span> ' % trdata.__counter)
        if line.strip():
            w(u'<span class="%s">%s</span>\n' % (cssclass, xml_escape(line)))
        else:
            w('\n')

    def comment_line(self, trdata, w, line):
        w(xml_escape(line) + '<br/>')

    def new_file(self, trdata, w, line):
        #w(u'<span class="diffFile">%s</span>\n' % xml_escape(line))
        pass

    def old_file(self, trdata, w, line):
        pass

    def start_file(self, trdata, w, line):
        w(u'<div class="diffCmd">%s</div>\n' % xml_escape(line))

    def start_chunk(self, trdata, w, line):
        w(u'<div class="diffChunk">\n')
        w(u'<span class="diffChunkTitle">%s</span>\n' % xml_escape(line))
        w(u'<pre class="diff">\n')
        self._done_cb = self.stop_chunk
        self._continue_cb = self.diff_line

    def inc_counter(self, trdata):
        try:
            trdata.insert_points_count += 1
            ipid = trdata.insert_points_count
        except AttributeError:
            ipid = trdata.insert_points_count = 1
        return ipid

    def stop_chunk(self, trdata, w):
        w(u'</pre>\n')
        ipid = self.inc_counter(trdata)
        if self._ipcb is not None:
            self._ipcb(ipid, trdata, w)
        w(u'</div>\n')

    def stop_comment(self, trdata, w):
        ipid = self.inc_counter(trdata)
        if self._ipcb is not None:
            self._ipcb(ipid, trdata, w)
        w(u'</div>\n')
