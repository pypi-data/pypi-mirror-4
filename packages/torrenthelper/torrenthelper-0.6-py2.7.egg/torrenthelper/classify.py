#
# (c)2009 Arjan Scherpenisse <arjan@scherpenisse.net>
#
# MIT licenced, see LICENSE file for details.
#

""" File grouping and classification. """

from fileutil import *
import re
import actions


class Extensions:
    video = "avi,mov,mkv,wmv,ogm,flv,mp4".split(",")
    audio = "mp3,wav,ogg,flac".split(",")



class TorrentClass:
    name = None

    def __init__(self, sourcefolder, files, name=""):
        self.sourcefolder = sourcefolder
        self.files = files
        self.name = name

    def __str__(self):
        base = "%s: %s, %d files" % (str(self.__class__).split(".")[-1], self.sourcefolder, len(self.files))
        return base

    def getPrefixFolder(self):
        return ""


class TVShowSeason (TorrentClass):
    """
    A folder with episodes of a single tv-show season.
    """

    name = None
    season = None

    regexp = "^.*?([^/]+)(\W+)S(e|eason)?\s*(\d+).*/$"

    @staticmethod
    def classify(files, folder):
        # FIXMEa
        m = re.match(TVShowSeason.regexp, folder, re.I)
        if m:
            season = TVShowSeason(folder, files, TVShow.nameFromMatch(m))
            season.season = int(m.groups()[3])
            return season
        return False

    def __str__(self):
        return TorrentClass.__str__(self) + ": %s season %d" % (self.name, self.season)

    def getPrefixFolder(self):
        return "%s/Season %d/" % (self.name, self.season)


class TVShow (TorrentClass):

    regexp = "^.*?([^/]+)(S(\d+)EP?(\d+)|\D(\d+)x(\d+)).*$"
    dateRegexp = "^.*?([^/]+)(\d\d\d\d).?(\d{2}).?(\d{2}).*$"

    season = None
    episode = None

    @staticmethod
    def classify(files, folder):

        """
        TV-shows classifier.
        """

        if len(files) > 1:
            return False

        # A folder with a single episode
        m = re.match(TVShow.regexp, folder + files[0], re.I)
        if m:
            show = TVShow(folder, files, TVShow.nameFromMatch(m))
            g = m.groups()
            idx = 2
            if g[4]:
                idx = 4
            show.season = int(g[idx])
            show.episode = int(g[idx+1])
            return show
        m = re.match(TVShow.dateRegexp, folder + files[0], re.I)
        if m:
            g = m.groups()
            show = TVShow(folder, files, TVShow.nameFromMatch(m))
            show.season = None
            show.episode = "%04d-%02d-%02d" % (int(g[1]), int(g[2]), int(g[3]))
            return show
        return False

    @staticmethod
    def nameFromMatch(m):
        show = m.groups()[0]
        show = re.sub('[_\.]', ' ', show)
        show = re.sub('\s+', ' ', show)
        show = re.sub('\W+$', '', show)
        return show


    def __str__(self):
        if self.season:
            return TorrentClass.__str__(self) + ": %s %dx%d" % (self.name, self.season, self.episode)
        return TorrentClass.__str__(self) + ": %s %s" % (self.name, self.episode)


    def getPrefixFolder(self):
        if self.season:
            return "%s/Season %d/" % (self.name, self.season)
        return "%s/" % (self.name)



class Movie (TorrentClass):

    @staticmethod
    def classify(files, folder):

        """
        Very lazy Movie classifier. assumes all files in a folder are a
        movie, if one of them is a .avi. Only does not consider 'sample'
        files to be movies.
        """

        if re.match('^.*sample.*$', folder, re.I):
            return False

        if len(files) > 5:
            # too many files in the dir
            return False

        if extensions_any(files, Extensions.video):
            return Movie(folder, files)

        return False

    def getPrefixFolder(self):
        return self.sourcefolder



class MusicAlbum (TorrentClass):

    @staticmethod
    def classify(files, folder):

        """ If most files in a folder are audio, it's an album. """

        if extensions_most(files, Extensions.audio):
            return MusicAlbum(folder, files)

        return False


classifiers = [TVShowSeason.classify, TVShow.classify, MusicAlbum.classify, Movie.classify]

def classify(files, folder = "", result = []):

    """
    Classify a set of files. returns a list of torrent classes, determining
    what the files are.
    """

    res = result[:]
    
    dirs, emptyfiles = basedirs(files)

    for k in dirs:
        res += classify(dirs[k], folder + k)

    miss = []
    if not res:
        r = False
        for c in classifiers:
            r = c(files, folder)
            if r:
                break
        if r:
            res += [r]
        elif len(files)>1:
            # try one-for-one
            for f in files:
                r = False
                for c in classifiers:
                    r = c([f], folder)
                    if r:
                        break
                if r:
                    res += [r]
                else:
                    miss.append((f, folder))
        else:
            miss.append((files[0], folder))
    if miss:
        print miss
    return res
    #print "CHECK: ", folder, files



__all__ = ["classify", "Movie", "MusicAlbum", "TVShow", "TVShowSeason"]

