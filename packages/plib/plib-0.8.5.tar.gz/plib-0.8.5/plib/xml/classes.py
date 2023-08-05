#!/usr/bin/env python
"""
Module CLASSES -- Common XML Classes
Sub-Package XML of Package PLIB -- Python XML and XSLT Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module builds on the custom element class functionality
provided by LXML to provide the following features:

- Attributes of XML nodes appear as instance attributes on
  the Python node class instance, with the data converted
  between the strings in the XML file and the appropriate
  Python data type (given by a class field on the custom
  node class);
- DTD generation is automated once the appropriate class
  fields on each custom node class are filled in.
"""

from lxml import etree

from plib.stdlib.classtools import recursedict, recurselist

from plib.xml import io
from plib.xml.defs import *


# 'Attribute property' functions

def _getprop(propname, form=None):
    if form is not None:
        def _getfunc(self):
            return form(self.get(propname))
    else:
        def _getfunc(self):
            return self.get(propname)
    return _getfunc


def _setprop(propname, form=None):
    if form is not None:
        def _setfunc(self, value):
            self.set(propname, form(value))
    else:
        def _setfunc(self, value):
            self.set(propname, value)
    return _setfunc


def attrib_prop(propname):
    """Make XML attribute propname appear as Python property.
    
    Sets up XML attribute propname as an attribute of the
    Python element instance, so instead of
    
        element.get("propname")
    
    and so on, you can just use
    
        element.propname
    
    and so on. Property values are strings, direct to/from
    the XML attribute. (Use attrib_prop_int or attrib_prop_bool
    to expose properties as Python ints or booleans.)
    
    Note that no error checking is done within this function
    to see if the XML attribute is present or that its value
    can be translated to a Python string or any other type;
    any exceptions thrown as a result of this, or any checking
    of the return values from property access, must be handled
    by the calling program.
    """
    
    return property(
        _getprop(propname),
        _setprop(propname))


def _strint(s):
    if s is None:
        return 0
    else:
        return int(s)


def attrib_prop_int(propname):
    """Make XML attribute propname appear as Python integer.
    
    Sets up XML attribute propname as an integer attribute
    of the Python element instance, so property values appear
    as Python ints instead of strings. Note that we use the
    _strint function above to map None to integer 0 (so that a
    non-existent attribute gives zero value).
    """
    
    return property(
        _getprop(propname, _strint),
        _setprop(propname, str))


def _boolstr(flag):
    if flag is True:
        return "yes"
    elif flag is False:
        return "no"
    else:
        return None


def _strbool(s):
    if s == "yes":
        return True
    elif s == "no":
        return False
    else:
        return None


def attrib_prop_bool(propname):
    """Make XML attribute propname appear as Python bool.
    
    Sets up XML attribute propname as a boolean attribute
    of the Python element instance, so property values appear
    as Python True/False instead of strings "yes" and "no".
    Note that any other strings besides "yes" and "no" will
    appear as None, *not* False.
    """
    
    return property(
        _getprop(propname, _strbool),
        _setprop(propname, _boolstr))


# Dictionary of functions vs. type constants
attrfuncs = {
    ATTR_STR: attrib_prop,
    ATTR_INT: attrib_prop_int,
    ATTR_BOOL: attrib_prop_bool
}


class AttrsMeta(type):
    """Metaclass to automatically add XML 'attribute properties'.
    
    Uses the above attrib_prop functions. Looks in the 'attrs' class
    field for a dict of XML attribute names mapped to property
    types; each name then becomes an attrib_prop of the corresponding
    type. Inspired by the 'autoprop' metaclass in Guido's new-style
    class intro essay.
    
    Note that the dict values may also be 2-tuples containing the
    attribute type and a default value. The default value is not used
    by this class but is used by subclasses below.
    
    Note also that the attribute type entries may be either one of
    the predefined ATTR_XXX constants above or a list of allowed
    string values; the latter are treated as ATTR_STR attributes by
    this class (but again the two cases are differentiated in
    subclasses below).
    """
    
    def __init__(cls, name, bases, namespace):
        super(AttrsMeta, cls).__init__(name, bases, namespace)
        if 'attrs' in cls.__dict__:
            attrs = cls.__dict__['attrs']
            for name, value in attrs.iteritems():
                # Allow for attrs entries to be (type, default) tuples
                if isinstance(value, tuple):
                    attrtype = value[0]
                else:
                    attrtype = value
                # Allow for type entries to be lists of allowed strings;
                # note that since list objects aren't hashable we need
                # the extra first isinstance test to avoid a TypeError
                if not (isinstance(attrtype, int) and 
                        (attrtype in attrfuncs)):
                    
                    attrtype = ATTR_STR
                setattr(cls, name, attrfuncs[attrtype](name))
    
    # Note that instance methods of a metaclass are functionally
    # equivalent to class methods of the class -- but if we define
    # them here we don't have to use the classmethod decorator
    
    def xmlattrs(cls):
        """Return dict of all XML attributes in inheritance tree.
        
        Return a complete dict of all XML attributes for
        this class (including ones inherited from bases--the
        'attrs' attribute of a given class by itself only
        contains the *new* attributes for that class). The
        main intended use case is for DTD generation (see the
        subclasses below).
        """
        
        return recursedict(cls, 'attrs')


class Attrs(object):
    """Mixin class for XML tags with automatic 'attribute properties'.
    
    We want to keep this functionality separate from the subtag
    and root tag functionality below, so this class needs to be a
    mixin, but we can't derive it from etree.ElementBase because we
    can't have multiple inheritance on etree classes. This is why
    we need to use the cooperative super mechanism in all the
    metaclasses in this module.
    """
    
    __metaclass__ = AttrsMeta
    
    attrs = {}


### XML custom element classes with DTD generation. ###

class BaseElement(etree.ElementBase):
    """ Base element class. """
    pass


dtdelement = "<!ELEMENT %s %s>"

dtdattlist = "<!ATTLIST %s\n%s>"

dtdattrs = {
    ATTR_STR: "CDATA",
    ATTR_INT: ("CDATA", 0),
    ATTR_BOOL: (["yes", "no"], False)
}


class TagMeta(AttrsMeta):
    """Metaclass to automatically construct XML tag class fields.
    
    Automatically construct more useful class fields for XML tag classes,
    and to provide DTD generation functionality based on class fields.
    
    The automatic constructions which are performed on class
    initialization are:
    
    -- Automatically add XML 'attribute properties' using
       the above attrib_prop functions. (Inherited from AttrsMeta above.)
    
    -- Automatically check consistency of class fields: if there is
       a substr field, the others should all be blank except end (since
       substr explicitly defines the DTD sub-element string); and if
       the element can contain PCDATA, the separator should be '|'.
    
    The DTD generation functionality is implemented by a number of
    class methods. The core idea is to recursively call the dtdentry
    method starting with the root node; this will end up emitting the
    DTD entries for each element type and its attributes, in reverse
    depth-first tree order (i.e., the leaf nodes get emitted first).
    A list of already emitted element names is used to prevent multiple
    copies of the same element's entry. Various class fields are used
    to determine the content of each element's DTD entry, as noted in
    the method docstrings.
    """
    
    def __init__(cls, name, bases, namespace):
        super(TagMeta, cls).__init__(name, bases, namespace)
        if cls.substr:
            if cls.pcdata:
                cls.pcdata = False
            if cls.subtags:
                cls.subtags = []
            if cls.maybe:
                cls.maybe = []
            if cls.some:
                cls.some = []
            if cls.any:
                cls.any = []
            if cls.sep:
                cls.sep = ""
        if cls.pcdata:
            cls.sep = "|"
    
    def xmlsubtags(cls):
        """Return list of all XML attributes in inheritance tree.
        
        Return a complete list of all XML subtags and their
        tag classes (including ones inherited from bases--the
        'subtags' attribute of a given class by itself only
        contains the immediate subtags of this class, not the
        complete recursive tree of subtags.
        """
        
        return recurselist(cls, 'subtags')
    
    def dtdsubtags(cls):
        """Return list of all DTD subtags in inheritance tree.
        
        Return a complete list of 2-tuples for this tag's subtags
        for DTD generation. The default is for this to be the same
        as the recursive 'subtags' field above, but derived tag
        metaclasses can extend or override this behavior.
        """
        
        return cls.xmlsubtags()
    
    def tagdict_subtags(cls):
        """Return list of all tagdict subtags in inheritance tree.
        
        Return a complete list of 2-tuples for this tag's subtags
        for tag dictionary generation (see build_tagdict below).
        The default is to return the same list of subtags as for
        DTD generation.
        """
        
        return cls.dtdsubtags()
    
    def dtdattr(cls, attrname, attrentry):
        """Return DTD attribute entry format string.
        
        Return the appropriate attribute entry format string
        for attrname, constructed from attrentry information.
        The entry should be either a single value giving the
        type of attribute (ATTR_STR, ATTR_INT, or ATTR_BOOL),
        a single list of valid string attribute values, or a
        2-tuple where the first item is as above and the second
        item is the default value for the attribute.
        """
        
        # Unpack 2-tuple if present
        if isinstance(attrentry, tuple):
            attrtype, attrdefault = attrentry
        else:
            attrtype = attrentry
            attrdefault = None
        
        # If type is one of the predefined constants, look it up
        # (see AttrsMeta.__init__ above for why the isinstance
        # check is needed first)
        if isinstance(attrtype, int) and (attrtype in dtdattrs):
            attrkey = attrtype
            attrvalue = dtdattrs[attrkey]
            if isinstance(attrvalue, tuple):
                if attrdefault is None:
                    attrtype, attrdefault = attrvalue
                else:
                    attrtype = attrvalue[0]
            else:
                attrtype = attrvalue
        else:
            attrkey = ATTR_STR
        
        # If type is list of allowed strings, unpack and format
        if isinstance(attrtype, list):
            attrtypestr = "".join(["(", "|".join(attrtype), ")"])
            if attrdefault is None:
                attrdefault = attrtype[0]
        else:
            attrtypestr = attrtype
        
        # Fill in proper default for string attributes if needed
        if (attrkey == ATTR_STR) and not isinstance(attrdefault, basestring):
            if attrdefault:
                attrdefault = "#REQUIRED"
            else:
                attrdefault = "#IMPLIED"
        
        # Fill in proper default for boolean attributes if needed
        if (attrkey == ATTR_BOOL) and not isinstance(attrdefault, basestring):
            if attrdefault:
                attrdefault = "yes"
            else:
                attrdefault = "no"
        
        # Format string default if it's not a generic
        if not (isinstance(attrdefault, basestring) and
                attrdefault.startswith("#")):
            
            attrdefault = '"%s"' % attrdefault
        
        # Return the formatted attribute entry string
        return '  %s %s %s' % (attrname, attrtypestr, attrdefault)
    
    def attlist(cls):
        """Return the DTD attribute list for this tag.
        """
        
        return "\n".join([cls.dtdattr(attrname, attrentry) \
            for attrname, attrentry in cls.xmlattrs().iteritems()])
    
    def dtdsubtag(cls, tagname):
        """Return the appropriate subtag string for tagname.
        
        Uses the maybe, some, and any class fields to determine if
        a suffix should be added to the tag name.
        """
        
        if tagname in recurselist(cls, 'any'):
            return "%s*" % tagname
        if tagname in recurselist(cls, 'maybe'):
            return "%s?" % tagname
        if tagname in recurselist(cls, 'some'):
            return "%s+" % tagname
        return tagname
    
    def subtaglist(cls):
        """Return the DTD subtag list for this tag.
        
        May return other appropriate string values for other types
        of content.
        
        Note that the substr class field, if non-empty, overrides all
        other ways of specifying the element content. The pcdata class
        field determines if character data is acceptable as well as
        subtags, and the dtdsubtags class method (see above) is
        called to get the list of allowed sub-elements.
        """
        
        if cls.substr:
            return (cls.substr, cls.end)
        if cls.pcdata:
            pre = ["#PCDATA"]
        else:
            pre = []
        subtags = cls.dtdsubtags()
        if subtags:
            return (cls.sep.join(pre + [cls.dtdsubtag(tagname)
                for tagname, _ in subtags]), cls.end)
        if pre:
            return (pre[0], "")
        return "EMPTY"
    
    def dtdentry(cls, tagname, done):
        """Return a string containing the DTD entry for this tag.
        
        Recursively includes subtag entries before this tag's
        ELEMENT and ATTLIST entries. The done parameter is
        used to track already emitted tag names so they are
        not emitted again.
        """
        
        done.append(tagname)
        subentries = []
        for key, value in cls.dtdsubtags():
            # Can't use a list comprehension here because the
            # done list may be mutated during recursive calls
            # to this function
            if key not in done:
                subentries.append(value.dtdentry(key, done))
        attlist = cls.attlist()
        if attlist != "":
            attrentries = [dtdattlist % (tagname, attlist)]
        else:
            attrentries = []
        subtaglist = cls.subtaglist()
        if subtaglist != "EMPTY":
            subtaglist = "(%s)%s" % subtaglist
        element = [dtdelement % (tagname, subtaglist)]
        return "\n".join(subentries + element + attrentries + [""])
    
    # Convenience methods
    
    def _extend(cls, attrname, seq):
        if not (attrname in cls.__dict__):
            setattr(cls, attrname, [])
        getattr(cls, attrname).extend(seq)


class Tag(BaseElement):
    """Base class for deriving 'automated' custom element classes.
    """
    
    __metaclass__ = TagMeta
    
    # Note: you can set the substr field to SUBSTR_ANY to allow
    # any type of content in the element
    
    attrs = {}
    subtags = []
    maybe = []
    some = []
    any = []
    sep = ","
    substr = ""
    end = ""
    pcdata = False
    
    # Convenience methods
    
    def xnode(self, expr):
        """Quick way to get the node instead of a list when there's just one.
        """
        return self.xpath(expr)[0]
    
    def subelement(self, tagname):
        """Quick way to create a sub-element and add it to the tree.
        """
        self.append(self.makeelement(tagname))
        return self[-1]


class RootMeta(TagMeta):
    """Metaclass to add class methods for DTD generation.
    
    The DTD for the entire XML file of which the tag class is
    the root node is returned as a string by the dtdgen method.
    """
    
    def dtdheader(cls):
        return '<!-- %s (XML 1.0 DTD) -->\n' % cls.rootname.upper()
    
    def dtdstart(cls):
        #return '<!DOCTYPE %s [\n' % cls.rootname
        return ""
    
    def dtdimports(cls):
        return ""
    
    def dtdend(cls):
        #return '] >\n'
        return ""
    
    def dtdgen(cls):
        """Automatic DTD generation method.
        
        Automatically generate a DTD for the XML file for
        which this is a root node. Return the DTD as a string.
        """
        
        return "\n".join([cls.dtdheader(), cls.dtdstart(), cls.dtdimports(),
            cls.dtdentry(cls.rootname, []), cls.dtdend()])


class RootTag(Tag):
    """Base class for custom element classes for XML root nodes.
    
    The rootname class field, if it is not null, is used
    to determine the node name of the root node; this
    is used both by the tagdict and for DTD generation.
    """
    
    __metaclass__ = RootMeta
    
    rootname = ""


def build_tagdict(klass, tagdict):
    for subname, k in klass.tagdict_subtags():
        # Prevent infinite recursion if there are circular
        # references between subtag classes
        recurse = k not in tagdict.values()
        tagdict.update({subname: k})
        if recurse:
            build_tagdict(k, tagdict)


class TreeMeta(type):
    """Metaclass for XML tree encapsulation.
    
    Generates the tagdict by walking the tree of tags from
    the root node class. The tagdict is used for parsing
    to enable custom element classes. The make_dtd class
    method is also provided to save the DTD to a filename.
    """
    
    def __init__(cls, name, bases, namespace):
        super(TreeMeta, cls).__init__(name, bases, namespace)
        klass = cls.rootclass
        if (klass is not None) and klass.rootname:
            tagdict = {klass.rootname: klass}
            build_tagdict(klass, tagdict)
            cls.tagdict = tagdict
    
    def make_dtd(cls, filename):
        klass = cls.rootclass
        if klass is not None:
            io._writefilename(filename, klass.dtdgen())


class Tree(object):
    """Base class encapsulating XML tree
    
    Includes parsing, serialization, and dtd generation.
    """
    
    __metaclass__ = TreeMeta
    
    rootclass = None
    tagdict = {}
    strip = None
    val = None
    decl = None
    doctype = None
    encoding = None
    indent = None
    
    def __init__(self):
        self.tree = None
        self.root = None
        self.lookup = self.tagdict
    
    def _set_tree(self, fn, arg):
        """Set the XML tree and root node using the given parse function.
        
        Use our lookup (defaults to our tagdict) and whitespace stripping.
        """
        
        self.tree = fn(arg, look=self.lookup, strip=self.strip, val=self.val)
        self.root = self.tree.getroot()
    
    def parse(self, s):
        """Load XML tree from string.
        """
        self._set_tree(io.parseString, s)
    
    def load_from(self, filename):
        """Load XML tree from filename.
        """
        self._set_tree(io.parseFile, filename)
    
    def serialize(self):
        """Serialize XML tree to string with given encoding and indentation.
        """
        return io.toString(self.tree,
            self.encoding, self.indent, self.decl, self.doctype)
    
    def save_to(self, filename):
        """Save XML tree to filename with given encoding and indentation.
        """
        io._writefilename(filename, self.serialize())
