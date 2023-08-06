# -*- coding: utf-8 -*-
import re


class Replacement(object):
    def __init__(self,
                 english,
                 american,
                 matcher=None,
                 lbuffer=None,
                 rbuffer=None,
                 ending=None):
        self.english = english
        self.american = american
        self.matcher = matcher or r"(?:(?:\s|\t)*|;)({proper}){ending}".format(
            proper=english,
            # A positive look ahead can catch many little problems.
            ending="(?=" + ending + ")" if ending is not None else ""
        )
        if lbuffer is not None or rbuffer is not None:
            # One should always prepend and append the proper buffer character.
            self.american = "{0}{1}{2}".format(
                lbuffer if lbuffer is not None else "",
                american,
                rbuffer if rbuffer is not None else ""
            )
        self.ending = ending if ending is not None else ""

    def __repr___(self):
        return "<Replacement '{0}' to '{1}'>".format(
            self.english,
            self.american
        )


class Spiffing(object):
    """ One should never leave home without a method of sending information
        to our State-side friends, should we? No, quite not!
        This class allows one to translate "proper CSS" to the CSS required
        by our American brethren's Browsers.
    """

    """ A list of translations, showing the processor which words from
        the Queen's English we should butcher, allowing our State-side friends
        to read our otherwise perfect style-sheet.

        The list should be comprised of Replacement objects.
    """
    replacements = [
        Replacement("colour", "color"),
        Replacement("grey", "gray", matcher=r"\s*(grey)\s*", lbuffer=" ", rbuffer=" "),
        Replacement("!please", "!important", matcher=r"(!please)(?=;)", ending=""),
        Replacement("transparency", "opacity", matcher="(transparency)(?=:)"),
        Replacement("centre", "center", lbuffer=" "),
        Replacement("plump", "bold", ending="", lbuffer=" "),
        Replacement("photograph", "image"),
        Replacement("capitalise", "capitalize", lbuffer=" ")
    ]

    def __init__(self, css):
        """ One must simply supply a string of spiffingly written CSS,
            and access it in full via the instance.american variable.
        """
        self.css = css

    @property
    def american(self):
        """ This method simply runs through all available translations, and
            applies them to the CSS, creating CSS readable by our State-side
            chums.
        """
        pro = self.css
        for r in Spiffing.replacements:
            pro = re.sub(r.matcher, r.american + r.ending, pro, flags=re.I)
        return pro
