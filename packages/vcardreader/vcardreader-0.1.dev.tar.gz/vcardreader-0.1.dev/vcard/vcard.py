#!/usr/bin/env python

"""
Extract useful information from a VCARD file.


"""

import time
import argparse
import collections

def __passOne(handle):
    """
    Do the initial parsing of a VCARD file, mainly glueing lines togeter and
    placing it in a list.

    @arg handle: Open readable handle to a VCARD file.
    @type handle: stream

    @returns: List of VCARD lines.
    @rtype: list
    """
    vCardList = []
    line = handle.readline()

    while line:
        thisLine = line[:-1]
        line = handle.readline()

        while line.startswith(' '):
            thisLine += line[1:-1]
            line = handle.readline()
        #while

        vCardList.append(thisLine)
    #while

    return vCardList
#__passOne

def __passTwo(vCardList):
    """
    Convert a list of VCARD lines into a nested dictionary.

    @arg vCardList: List of VCARD lines.
    @type vCardList: list

    @returns: Nested dictionary containing the VCARD information.
    @rtype: dict
    """
    vCard = collections.defaultdict(list)

    while vCardList:
        line = vCardList.pop(0)
        data = line.split(':', 1)

        if ';' in data[0]:
            l = data[0].split(';')

            vCard[l[0]].append(collections.defaultdict(list, dict(map(lambda x:
                x.split('='), l[1:]) + [["VALUE", data[1]]])))
        #if
        elif data[0] == "BEGIN":
            vCard[data[1]].append(__passTwo(vCardList))
        elif data[0] == "END":
            return vCard
        else:
            vCard[data[0]].append({"VALUE": data[1]})
    #while

    return vCard
#__passTwo

def parseCard(handle):
    """
    Parse the VCARD file and place the content in a nested dictionary.

    @arg handle: Open readable handle to a VCARD file.
    @type handle: stream

    @returns: Nested dictionary containing the VCARD information.
    @rtype: dict
    """
    return __passTwo(__passOne(handle))
#parseCard

def printCard(vCard, step=2, indent=0):
    """
    Pretty print VCARD data.

    @arg vCard: Nested dictionary containing the VCARD information.
    @type vCard: dict
    @arg step: Number of spaces for each indent.
    @type step: int
    @arg indent: Indent level.
    @type indent: int
    """
    for i in vCard:
        if type(vCard[i]) == list:
            print "%s%s {" % (' ' * indent, i)
            for j in vCard[i]:
                if type(j) == collections.defaultdict:
                    print "%s[" % (' ' * (indent + step))
                    printCard(j, indent=indent + 2 * step)
                    print "%s]" % (' ' * (indent + step))
                #if
                else:
                    print "%s%s" %(' ' * (indent + step), j)
            print "%s}" % (' ' * indent)
        else:
            print "%s%s : %s" %(' ' * indent, i, vCard[i])
    #for
#printCard

def parseTime(timeStr):
    """
    Convert a VCARD formatted time string into a time object.

    @arg timeStr: VCARD formatted time string.
    @type timeStr: str

    @returns:
    @rtype: object
    """
    return time.strptime(timeStr, "%Y%m%dT%H%M%S")
#parseDate

def replaceAll(text, d):
    """
    Replace all occurrences of keys of {d} in {text} with the value in {d}.

    @arg text: A piece of text.
    @type text: str
    @arg d: Dictionary containing strings and their replacement.
    @type d: dict

    @returns: Modified text.
    @rtype: str
    """
    for i in d:
        text = text.replace(i, d[i])

    return text
#replaceAll

def vcard(handle):
    """
    Extract useful information from a VCARD file.

    @arg handle: Open readable handle to a VCARD file.
    @type handle: stream
    """
    descriptionReplace = {"\\n": "\n", "\\,": ","}
    vCard = parseCard(handle)

    event = vCard["VCALENDAR"][0]["VEVENT"][0]

    print "Organiser: %s" % event["ORGANIZER"][0]["CN"]
    print "Attendees:"
    for i in event["ATTENDEE"]:
        print "  %s" % i["CN"]
    print "Summary: %s" % event["SUMMARY"][0]["VALUE"]

    print "When: %s-%s" % (time.strftime("%a %d %b %Y %H:%M",
        parseTime(event["DTSTART"][0]["VALUE"])), time.strftime("%H:%M",
        parseTime(event["DTEND"][0]["VALUE"])))

    print "Location: %s" % event["LOCATION"][0]["VALUE"]
    print "Description:\n" 
    if event["DESCRIPTION"]:
        print replaceAll(event["DESCRIPTION"][0]["VALUE"], descriptionReplace)
    else:
        print replaceAll(event["VALARM"][0]["DESCRIPTION"][0]["VALUE"],
            descriptionReplace)
#vcard

def main():
    """
    Main entry point.
    """
    usage = __doc__.split("\n\n\n")
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage[0], epilog=usage[1])

    parser.add_argument("input", metavar="INPUT", type=argparse.FileType("r"))

    arguments = parser.parse_args()

    try:
        vcard(arguments.input)
    except ValueError, error:
        parser.error(error)
#main

if __name__ == "__main__":
    main()
