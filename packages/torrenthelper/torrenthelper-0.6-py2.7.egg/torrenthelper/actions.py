#
# (c)2009 Arjan Scherpenisse <arjan@scherpenisse.net>
#
# MIT licenced, see LICENSE file for details.
#

""" File/folder actions based on file classifications """

import os
from lxml.etree import parse, Element, SubElement, tostring


class Action:

    verbose = True
    pretend = True
    
    def __init__(self, files):
        self.files  = files

    def _assurefolder(self, folder):
        if os.path.exists(folder):
            return
        if self.verbose:
            print "Make dir:", folder
        if self.pretend:
            return
        os.makedirs(folder)
        
    def process (self):
        raise NotImplementedError()


class CopyAction (Action):

    def __init__(self, origin, files, target):
        Action.__init__(self, files)
        self.origin = origin
        self.target = target

    def process (self):

        target = self.target
        self._assurefolder(target)

        dirs = set([os.path.dirname(f) for f in self.files])
        dirfiles = {}
        #for d in dirs:
        #    self._assurefolder(target + d)
        #    dirfiles[target+d] = []
        dirfiles[target] = []
        
        for f in self.files:
            t = target+os.path.basename(f)
            if os.path.exists(t):
                if self.verbose:
                    print "%s already exists." % (t)
                continue
            dirfiles[target].append(self.origin+f)

        for d in dirfiles:
            if not dirfiles[d]:
                continue
            for f in dirfiles[d]:
                if self.verbose:
                    print "Hard link %s -->\n  %s" % (f, os.path.join(d, os.path.basename(f)))
                if self.pretend:
                    continue
                os.link(f, os.path.join(d, os.path.basename(f)))


class UpdateRSSAction (Action):

    def __init__(self, rssfile, files):
        Action.__init__(self, files)
        self.rssfile = rssfile

    def process (self):

        if not os.path.exists(self.rssfile):
            print "** RSS file %s does not exist!" % self.rssfile
            return

        if self.verbose:
            print "Updating RSS file %s with %d entries" % (self.rssfile, len(self.files))
            
        if self.pretend:
            return
        
        tree = parse(open(self.rssfile, 'r'))
        rss = tree.getroot()

        channel = rss[0]

        item_idx = 0
        for node in channel:
            if node.tag == "item":
                break
            item_idx += 1

        for filename in self.files:
            name = os.path.basename(filename)
            
            url = "file://" + filename

            data = {"title": name, "description": filename, "link": url}
            item = Element("item")
            for k in data:
                c = SubElement(item, k)
                c.text = data[k]

            enc = SubElement(item, "enclosure")
            enc.attrib["url"] = url
            enc.attrib["type"] = "movie"

            channel.insert(item_idx, item)

        tree.write(open(self.rssfile, 'w'))


class UpdateXBMCAction (Action):

    def __init__(self, type):
        Action.__init__(self, [])
        self.type = type

    def process (self):
        from xbmc import xbmcclient
        if self.verbose:
            print "Updating XBMC library:", self.type
        if self.pretend:
            return
        client = xbmcclient.XBMCClient()
        client.connect()
        client.send_action("UpdateLibrary(%s)" % self.type)
        client.close()

