# -*- coding: utf-8 -*-
import re


class Replacement(object):
    """ Store some lovely information allowing us to change
        this to that, that to this, or whatever strange combinations
        you can find in-between.
    """

    def __init__(self,
                 this,
                 that,
                 matcher=None,
                 lbuffer=None,
                 rbuffer=None,
                 ending=None):
        self.this = this
        self.that = that
        self.matcher = matcher or r"(?:(?:\s|\t)*|;)({proper}){ending}".format(
            proper=this,
            # A positive look ahead can catch many little problems.
            ending="(?=" + ending + ")" if ending is not None else ""
        )
        if lbuffer is not None or rbuffer is not None:
            # One should always prepend and append the proper buffer character.
            self.that = "{0}{1}{2}".format(
                lbuffer if lbuffer is not None else "",
                that,
                rbuffer if rbuffer is not None else ""
            )
        self.ending = ending if ending is not None else ""

    def __repr___(self):
        return "<Replacement '{0}' to '{1}'>".format(
            self.this,
            self.that
        )


class Spiffing(object):
    """ This class is only present to allow our older friends to
        catch up to the latest spiffing.Monocle class usage.

        **DEPRECATED** use spiffing.Monocle instead
    """

    def __init__(self, css):
        """ One must simply supply a string of spiffingly written CSS,
            and access it in full via the instance.american variable.

            **DEPRECATED** Use spiffing.Monocle(css) instead
        """
        self.monocle = Monocle(css)

    @property
    def american(self):
        """ This just sends our developer friends the information our
            spiffing monocle provides.

            **DEPRECATED** Use spiffing.Monocle(css).american instead.
        """
        return self.monocle.american

class Monocle(object):
    """ Do you want to convert your butchered American English CSS to
        "proper" CSS? Of course you do, old chap! What a silly question.
        Do you want to send it right back the other way? Do we indeed.
    """

    english_to_american = [
        Replacement("colour", "color"),
        Replacement("grey", "gray", matcher=r"\s*(grey)\s*", lbuffer=" ", rbuffer=" "),
        Replacement("!please", "!important", matcher=r"(!please)(?=;)", ending=""),
        Replacement("centre", "center", lbuffer=" "),
        Replacement("plump", "bold", ending="", lbuffer=" "),
        Replacement("photograph", "image"),
        Replacement("capitalise", "capitalize", lbuffer=" ")
    ]

    american_to_english = [
        Replacement("color", "colour"),
        Replacement("gray", "grey", matcher=r"\s*(gray)\s*", lbuffer=" ", rbuffer=" "),
        Replacement("!important", "!please", matcher=r"(!important)(?=;)", ending=""),
        Replacement("center", "centre", lbuffer=" "),
        Replacement("bold", "plump", ending="", lbuffer=" "),
        Replacement("image", "photograph"),
        Replacement("capitalize", "capitalise", lbuffer=" ")
    ]

    def __init__(self, css):
        self.css = css

    @property
    def english(self):
        """ Convert the lesser state-side version of CSS we're working
            with into a piece of art, readable by proper developers.
        """
        return self._sub(self.css, Monocle.american_to_english)

    @property
    def american(self):
        """ Butcher our proper CSS into one which the lesser capitalist
            American swine can successfully read.
        """
        return self._sub(self.css, Monocle.english_to_american)

    def _sub(self, css, reps):
        """ Run through a list of Replacement objects,
            subbing each into the string we're given.
        """
        for r in reps:
            css = re.sub(r.matcher, r.that + r.ending, css, flags=re.I)
        return css