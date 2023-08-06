# -*- coding: utf-8 -*-
#
# presentation.py
#
# Copyright (C) 2012, 2013 Steve Canny scanny@cisco.com
#
# This module is part of python-pptx and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
API classes for dealing with presentations and other objects one typically
encounters as an end-user of the PowerPoint user interface.
"""

import hashlib

try:
    from PIL import Image as PIL_Image
except ImportError:
    import Image as PIL_Image

import os
import posixpath
import weakref

import pptx.packaging
import pptx.spec as spec
import pptx.util as util

from pptx.constants import MSO
from pptx.exceptions import InvalidPackageError
from pptx.oxml import (
    _Element, _SubElement, oxml_fromstring, oxml_tostring, _get_or_add, qn)

from pptx.spec import namespaces
from pptx.spec import (
    CT_PRESENTATION, CT_SLIDE, CT_SLIDELAYOUT, CT_SLIDEMASTER, CT_SLIDESHOW,
    CT_TEMPLATE)
from pptx.spec import (
    RT_IMAGE, RT_OFFICEDOCUMENT, RT_SLIDE, RT_SLIDELAYOUT, RT_SLIDEMASTER)
from pptx.spec import (
    PH_TYPE_BODY, PH_TYPE_CTRTITLE, PH_TYPE_DT, PH_TYPE_FTR, PH_TYPE_OBJ,
    PH_TYPE_SLDNUM, PH_TYPE_SUBTITLE, PH_TYPE_TITLE, PH_ORIENT_HORZ,
    PH_ORIENT_VERT, PH_SZ_FULL)
from pptx.spec import slide_ph_basenames

from pptx.util import Px

import logging
log = logging.getLogger('pptx.presentation')
log.setLevel(logging.DEBUG)
# log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                              '%(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

# default namespace map for use in lxml calls
_nsmap = namespaces('a', 'r', 'p')


def _child(element, child_tagname, nsmap=None):
    """
    Return direct child of *element* having *child_tagname* or :class:`None`
    if no such child element is present.
    """
    # use default nsmap if not specified
    if nsmap is None:
        nsmap = _nsmap
    xpath = './%s' % child_tagname
    matching_children = element.xpath(xpath, namespaces=nsmap)
    return matching_children[0] if len(matching_children) else None


def _to_unicode(text):
    """
    Return *text* as a unicode string.

    *text* can be a 7-bit ASCII string, a UTF-8 encoded 8-bit string, or
    unicode. String values are converted to unicode assuming UTF-8 encoding.
    Unicode values are returned unchanged.
    """
    # both str and unicode inherit from basestring
    if not isinstance(text, basestring):
        tmpl = 'expected UTF-8 encoded string or unicode, got %s value %s'
        raise TypeError(tmpl % (type(text), text))
    # return unicode strings unchanged
    if isinstance(text, unicode):
        return text
    # otherwise assume UTF-8 encoding, which also works for ASCII
    return unicode(text, 'utf-8')


# ============================================================================
# Package
# ============================================================================

class Package(object):
    """
    Return an instance of |Package| loaded from *file*, where *file* can be a
    path (a string) or a file-like object. If *file* is a path, it can be
    either a path to a PowerPoint `.pptx` file or a path to a directory
    containing an expanded presentation file, as would result from unzipping
    a `.pptx` file. If *file* is |None|, the default presentation template is
    loaded.
    """
    # track instances as weakrefs so .containing() can be computed
    __instances = []

    def __init__(self, file=None):
        super(Package, self).__init__()
        self.__presentation = None
        self.__relationships = _RelationshipCollection()
        self.__images = ImageCollection()
        self.__instances.append(weakref.ref(self))
        if file is None:
            file = self.__default_pptx_path
        self.__open(file)

    @classmethod
    def containing(cls, part):
        """Return package instance that contains *part*"""
        for pkg in cls.instances():
            if part in pkg._parts:
                return pkg
        raise KeyError("No package contains part %r" % part)

    @classmethod
    def instances(cls):
        """Return tuple of Package instances that have been created"""
        # clean garbage collected pkgs out of __instances
        cls.__instances[:] = [wkref for wkref in cls.__instances
                              if wkref() is not None]
        # return instance references in a tuple
        pkgs = [wkref() for wkref in cls.__instances]
        return tuple(pkgs)

    @property
    def presentation(self):
        """
        Reference to the :class:`Presentation` instance contained in this
        package.
        """
        return self.__presentation

    def save(self, file):
        """
        Save this package to *file*, where *file* can be either a path to a
        file (a string) or a file-like object.
        """
        pkgng_pkg = pptx.packaging.Package().marshal(self)
        pkgng_pkg.save(file)

    @property
    def _images(self):
        return self.__images

    @property
    def _relationships(self):
        return self.__relationships

    def __load(self, pkgrels):
        """
        Load all the model-side parts and relationships from the on-disk
        package by loading package-level relationship parts and propagating
        the load down the relationship graph.
        """
        # keep track of which parts are already loaded
        part_dict = {}

        # discard any previously loaded relationships
        self.__relationships = _RelationshipCollection()

        # add model-side rel for each pkg-side one, and load target parts
        for pkgrel in pkgrels:
            # unpack working values for part to be loaded
            reltype = pkgrel.reltype
            pkgpart = pkgrel.target
            partname = pkgpart.partname
            content_type = pkgpart.content_type
            # log.debug("%s -- %s", reltype, partname)

            # create target part
            part = Part(reltype, content_type)
            part_dict[partname] = part
            part._load(pkgpart, part_dict)

            # create model-side package relationship
            model_rel = _Relationship(pkgrel.rId, reltype, part)
            self.__relationships._additem(model_rel)

        # gather references to image parts into __images
        self.__images = ImageCollection()
        image_parts = [part for part in self._parts
                       if part.__class__.__name__ == 'Image']
        for image in image_parts:
            self.__images._loadpart(image)

    def __open(self, file):
        """
        Load presentation contained in *file* into this package.
        """
        pkg = pptx.packaging.Package().open(file)
        self.__load(pkg.relationships)
        # unmarshal relationships selectively for now
        for rel in self.__relationships:
            if rel._reltype == RT_OFFICEDOCUMENT:
                self.__presentation = rel._target

    @property
    def __default_pptx_path(self):
        """
        The path of the default presentation, used when no path is specified
        on construction.
        """
        thisdir = os.path.split(__file__)[0]
        return os.path.join(thisdir, 'templates', 'default.pptx')

    @property
    def _parts(self):
        """
        Return a list containing a reference to each of the parts in this
        package.
        """
        return [part for part in Package.__walkparts(self.__relationships)]

    @staticmethod
    def __walkparts(rels, parts=None):
        """
        Recursive function, walk relationships to iterate over all parts in
        this package. Leave out *parts* parameter in call to visit all parts.
        """
        # initial call can leave out parts parameter as a signal to initialize
        if parts is None:
            parts = []
        # log.debug("in __walkparts(), len(parts)==%d", len(parts))
        for rel in rels:
            # log.debug("rel.target.partname==%s", rel.target.partname)
            part = rel._target
            # only visit each part once (graph is cyclic)
            if part in parts:
                continue
            parts.append(part)
            yield part
            for part in Package.__walkparts(part._relationships, parts):
                yield part


# ============================================================================
# Base classes
# ============================================================================

class Collection(object):
    """
    Base class for collection classes. May also be used for part collections
    that don't yet have any custom methods.

    Has the following characteristics.:

    * Container (implements __contains__)
    * Iterable (delegates __iter__ to :class:`list`)
    * Sized (implements __len__)
    * Sequence (delegates __getitem__ to :class:`list`)
    """
    def __init__(self):
        # log.debug('Collection.__init__() called')
        super(Collection, self).__init__()
        self.__values = []

    @property
    def _values(self):
        """Return read-only reference to collection values (list)."""
        return self.__values

    def __contains__(self, item):  # __iter__ would do this job by itself
        """Supports 'in' operator (e.g. 'x in collection')."""
        return (item in self.__values)

    def __getitem__(self, key):
        """Provides indexed access, (e.g. 'collection[0]')."""
        return self.__values.__getitem__(key)

    def __iter__(self):
        """Supports iteration (e.g. 'for x in collection: pass')."""
        return self.__values.__iter__()

    def __len__(self):
        """Supports len() function (e.g. 'len(collection) == 1')."""
        return len(self.__values)

    def index(self, item):
        """Supports index method (e.g. '[1, 2, 3].index(2) == 1')."""
        return self.__values.index(item)


class Observable(object):
    """
    Simple observer pattern mixin. Limitations:

    * observers get all message types from subject (Observable), subscription
      is on subject basis, not subject + event_type.

    * notifications are oriented toward "value has been updated", which seems
      like only one possible event, could also be something like "load has
      completed" or "preparing to load".
    """
    def __init__(self):
        super(Observable, self).__init__()
        self._observers = []

    def _notify_observers(self, name, value):
        # value = getattr(self, name)
        for observer in self._observers:
            observer.notify(self, name, value)

    def add_observer(self, observer):
        """
        Begin notifying *observer* of events. *observer* must implement method
        ``notify(observed, name, new_value)``
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove *observer* from notification list."""
        assert observer in self._observers, "remove_observer called for"\
                                            "unsubscribed object"
        self._observers.remove(observer)


# ============================================================================
# Relationships
# ============================================================================

class _RelationshipCollection(Collection):
    """
    Sequence of relationships maintained in rId order. Maintaining the
    relationships in sorted order makes the .rels files both repeatable and
    more readable, which is very helpful for debugging.
    :class:`RelationshipCollection` has an attribute *_reltype_ordering* which
    is a sequence (tuple) of reltypes. If *_reltype_ordering* contains one or
    more reltype, the collection is maintained in reltype + partname.idx
    order and relationship ids (rIds) are renumbered to match that sequence
    and any numbering gaps are filled in.
    """
    def __init__(self):
        super(_RelationshipCollection, self).__init__()
        self.__reltype_ordering = ()

    def _additem(self, relationship):
        """
        Insert *relationship* into the appropriate position in this ordered
        collection.
        """
        rIds = [rel._rId for rel in self._values]
        if relationship._rId in rIds:
            tmpl = "cannot add relationship with duplicate rId '%s'"
            raise ValueError(tmpl % relationship._rId)
        self._values.append(relationship)
        self.__resequence()
        # register as observer of partname changes
        relationship._target.add_observer(self)

    @property
    def _next_rId(self):
        """
        Next available rId in collection, starting from 'rId1' and making use
        of any gaps in numbering, e.g. 'rId2' for rIds ['rId1', 'rId3'].
        """
        tmpl = 'rId%d'
        next_rId_num = 1
        for relationship in self._values:
            if relationship._num > next_rId_num:
                return tmpl % next_rId_num
            next_rId_num += 1
        return tmpl % next_rId_num

    @property
    def _reltype_ordering(self):
        """
        Tuple of relationship types, e.g. ``(RT_SLIDE, RT_SLIDELAYOUT)``. If
        present, relationships of those types are grouped, and those groups
        are ordered in the same sequence they appear in the tuple. In
        addition, relationships of the same type are sequenced in order of
        partname number (e.g. 16 for /ppt/slides/slide16.xml). If empty, the
        collection is maintained in existing rId order; rIds are not
        renumbered and any gaps in numbering are left to remain. Specifying
        this value for a collection with members causes it to be immediately
        reordered. The ordering is maintained as relationships are added or
        removed, renumbering rIds whenever necessary to also maintain the
        sequence in rId order.
        """
        return self.__reltype_ordering

    @_reltype_ordering.setter
    def _reltype_ordering(self, ordering):
        self.__reltype_ordering = tuple(ordering)
        self.__resequence()

    def rels_of_reltype(self, reltype):
        """
        Return a :class:`list` containing the subset of relationships in this
        collection of type *reltype*. The returned list is ordered by rId.
        Returns an empty list if there are no relationships of type *reltype*
        in the collection.
        """
        return [rel for rel in self._values if rel._reltype == reltype]

    def notify(self, subject, name, value):
        """RelationshipCollection implements the Observer interface"""
        if isinstance(subject, BasePart):
            if name == 'partname':
                self.__resequence()

    def __resequence(self):
        """
        Sort relationships and renumber if necessary to maintain values in rId
        order.
        """
        if self.__reltype_ordering:
            def reltype_key(rel):
                reltype = rel._reltype
                if reltype in self.__reltype_ordering:
                    return self.__reltype_ordering.index(reltype)
                return len(self.__reltype_ordering)

            def partname_idx_key(rel):
                partname = util.Partname(rel._target.partname)
                if partname.idx is None:
                    return 0
                return partname.idx
            self._values.sort(key=lambda rel: partname_idx_key(rel))
            self._values.sort(key=lambda rel: reltype_key(rel))
            # renumber consistent with new sort order
            for idx, relationship in enumerate(self._values):
                relationship._rId = 'rId%d' % (idx+1)
        else:
            self._values.sort(key=lambda rel: rel._num)


class _Relationship(object):
    """
    Relationship to a part from a package or part. *rId* must be unique in any
    |_RelationshipCollection| this relationship is added to; use
    :attr:`_RelationshipCollection._next_rId` to get a unique rId.
    """
    def __init__(self, rId, reltype, target):
        super(_Relationship, self).__init__()
        # can't get _num right if rId is non-standard form
        assert rId.startswith('rId'), "rId in non-standard form: '%s'" % rId
        self.__rId = rId
        self.__reltype = reltype
        self.__target = target

    @property
    def _rId(self):
        """
        Relationship id for this relationship. Must be of the form
        ``rId[1-9][0-9]*``.
        """
        return self.__rId

    @property
    def _reltype(self):
        """
        Relationship type URI for this relationship. Corresponds roughly to
        the part type of the target part.
        """
        return self.__reltype

    @property
    def _target(self):
        """
        Target part of this relationship. Relationships are directed, from a
        source and a target. The target is always a part.
        """
        return self.__target

    @property
    def _num(self):
        """
        The numeric portion of the rId of this |_Relationship|, expressed as
        an :class:`int`. For example, :attr:`_num` for a relationship with an
        rId of ``'rId12'`` would be ``12``.
        """
        try:
            num = int(self.__rId[3:])
        except ValueError:
            num = 9999
        return num

    @_rId.setter
    def _rId(self, value):
        self.__rId = value


# ============================================================================
# Parts
# ============================================================================

class PartCollection(Collection):
    """
    Sequence of parts. Sensitive to partname index when ordering parts added
    via _loadpart(), e.g. ``/ppt/slide/slide2.xml`` appears before
    ``/ppt/slide/slide10.xml`` rather than after it as it does in a
    lexicographical sort.
    """
    def __init__(self):
        super(PartCollection, self).__init__()

    def _loadpart(self, part):
        """
        Insert a new part loaded from a package, such that list remains
        sorted in logical partname order (e.g. slide10.xml comes after
        slide9.xml).
        """
        new_partidx = util.Partname(part.partname).idx
        for idx, seq_part in enumerate(self._values):
            partidx = util.Partname(seq_part.partname).idx
            if partidx > new_partidx:
                self._values.insert(idx, part)
                return
        self._values.append(part)


class ImageCollection(PartCollection):
    """
    Immutable sequence of images, typically belonging to an instance of
    :class:`Package`. An image part containing a particular image blob appears
    only once in an instance, regardless of how many times it is referenced by
    a pic shape in a slide.
    """
    def __init__(self):
        super(ImageCollection, self).__init__()

    def add_image(self, file):
        """
        Return image part containing the image in *file*, which is either a
        path to an image file or a file-like object containing an image. If an
        image instance containing this same image already exists, that
        instance is returned. If it does not yet exist, a new one is created.
        """
        # use Image constructor to validate and characterize image file
        image = Image(file)
        # return matching image if found
        for existing_image in self._values:
            if existing_image._sha1 == image._sha1:
                return existing_image
        # otherwise add it to collection and return new image
        self._values.append(image)
        self.__rename_images()
        return image

    def __rename_images(self):
        """
        Assign partnames like ``/ppt/media/image9.png`` to all images in the
        collection. The name portion is always ``image``. The number part
        forms a continuous sequence starting at 1 (e.g. 1, 2, 3, ...). The
        extension is preserved during renaming.
        """
        for idx, image in enumerate(self._values):
            image.partname = '/ppt/media/image%d%s' % (idx+1, image.ext)


class Part(object):
    """
    Part factory. Returns an instance of the appropriate custom part type for
    part types that have them, BasePart otherwise.
    """
    def __new__(cls, reltype, content_type):
        """
        *reltype* is the relationship type, e.g. ``RT_SLIDE``, corresponding
        to the type of part to be created. For at least one part type, in
        particular the presentation part type, *content_type* is also required
        in order to fully specify the part to be created.
        """
        # log.debug("Creating Part for %s", reltype)
        if reltype == RT_OFFICEDOCUMENT:
            if content_type in (CT_PRESENTATION, CT_TEMPLATE, CT_SLIDESHOW):
                return Presentation()
            else:
                tmpl = "Not a presentation content type, got '%s'"
                raise InvalidPackageError(tmpl % content_type)
        elif reltype == RT_SLIDE:
            return Slide()
        elif reltype == RT_SLIDELAYOUT:
            return SlideLayout()
        elif reltype == RT_SLIDEMASTER:
            return SlideMaster()
        elif reltype == RT_IMAGE:
            return Image()
        return BasePart()


class BasePart(Observable):
    """
    Base class for presentation model parts. Provides common code to all parts
    and is the class we instantiate for parts we don't unmarshal or manipulate
    yet.

    .. attribute:: _element

       ElementTree element for XML parts. ``None`` for binary parts.

    .. attribute:: _load_blob

       Contents of part as a byte string extracted from the package file. May
       be set to ``None`` by subclasses that override ._blob after content is
       unmarshaled, to free up memory.

    .. attribute:: _relationships

       :class:`RelationshipCollection` instance containing the relationships
       for this part.

    """
    def __init__(self, content_type=None):
        """
        Needs content_type parameter so newly created parts (not loaded from
        package) can register their content type.
        """
        super(BasePart, self).__init__()
        self.__content_type = content_type
        self.__partname = None
        self._element = None
        self._load_blob = None
        self._relationships = _RelationshipCollection()

    @property
    def _blob(self):
        """
        Default is to return unchanged _load_blob. Dynamic parts will
        override. Raises :class:`ValueError` if _load_blob is None.
        """
        if self.partname.endswith('.xml'):
            assert self._element is not None, 'BasePart._blob is undefined '\
                'for xml parts when part.__element is None'
            xml = oxml_tostring(self._element, encoding='UTF-8',
                                pretty_print=True, standalone=True)
            return xml
        # default for binary parts is to return _load_blob unchanged
        assert self._load_blob, "BasePart._blob called on part with no "\
            "_load_blob; perhaps _blob not overridden by sub-class?"
        return self._load_blob

    @property
    def _content_type(self):
        """
        Content type of this part, e.g.
        'application/vnd.openxmlformats-officedocument.theme+xml'.
        """
        if self.__content_type is None:
            msg = "BasePart._content_type accessed before assigned"
            raise ValueError(msg)
        return self.__content_type

    @_content_type.setter
    def _content_type(self, content_type):
        self.__content_type = content_type

    @property
    def partname(self):
        """Part name of this part, e.g. '/ppt/slides/slide1.xml'."""
        assert self.__partname, "BasePart.partname referenced before assigned"
        return self.__partname

    @partname.setter
    def partname(self, partname):
        self.__partname = partname
        self._notify_observers('partname', self.__partname)

    def _add_relationship(self, reltype, target_part):
        """
        Return new relationship of *reltype* to *target_part* after adding it
        to the relationship collection of this part.
        """
        rId = self._relationships._next_rId
        rel = _Relationship(rId, reltype, target_part)
        self._relationships._additem(rel)
        return rel

    def _load(self, pkgpart, part_dict):
        """
        Load part and relationships from package part, and propagate load
        process down the relationship graph. *pkgpart* is an instance of
        :class:`pptx.packaging.Part` containing the part contents read from
        the on-disk package. *part_dict* is a dictionary of already-loaded
        parts, keyed by partname.
        """
        # log.debug("loading part %s", pkgpart.partname)

        # # set attributes from package part
        self.__content_type = pkgpart.content_type
        self.__partname = pkgpart.partname
        if pkgpart.partname.endswith('.xml'):
            self._element = oxml_fromstring(pkgpart.blob)
        else:
            self._load_blob = pkgpart.blob

        # discard any previously loaded relationships
        self._relationships = _RelationshipCollection()

        # load relationships and propagate load for related parts
        for pkgrel in pkgpart.relationships:
            # unpack working values for part to be loaded
            reltype = pkgrel.reltype
            target_pkgpart = pkgrel.target
            partname = target_pkgpart.partname
            content_type = target_pkgpart.content_type

            # create target part
            if partname in part_dict:
                part = part_dict[partname]
            else:
                part = Part(reltype, content_type)
                part_dict[partname] = part
                part._load(target_pkgpart, part_dict)

            # create model-side package relationship
            model_rel = _Relationship(pkgrel.rId, reltype, part)
            self._relationships._additem(model_rel)
        return self


class Presentation(BasePart):
    """
    Top level class in object model, represents the contents of the /ppt
    directory of a .pptx file.
    """
    def __init__(self):
        super(Presentation, self).__init__()
        self.__slidemasters = PartCollection()
        self.__slides = SlideCollection(self)

    @property
    def slidemasters(self):
        """
        List of :class:`SlideMaster` objects belonging to this presentation.
        """
        return tuple(self.__slidemasters)

    @property
    def slides(self):
        """
        :class:`SlideCollection` object containing the slides in this
        presentation.
        """
        return self.__slides

    @property
    def _blob(self):
        """
        Rewrite sldId elements in sldIdLst before handing over to super for
        transformation of _element into a blob.
        """
        self.__rewrite_sldIdLst()
        # # at least the following needs to be added before using
        # # _reltype_ordering again for Presentation
        # self.__rewrite_notesMasterIdLst()
        # self.__rewrite_handoutMasterIdLst()
        # self.__rewrite_sldMasterIdLst()
        return super(Presentation, self)._blob

    def _load(self, pkgpart, part_dict):
        """
        Load presentation from package part.
        """
        # call parent to do generic aspects of load
        super(Presentation, self)._load(pkgpart, part_dict)

        # side effect of setting reltype ordering is that rId values can be
        # changed (renumbered during resequencing), so must complete rewrites
        # of all four IdLst elements (notesMasterIdLst, etc.) internal to
        # presentation.xml to reflect any possible changes. Not sure if good
        # order in the .rels files is worth the trouble just yet, so
        # commenting this out for now.

        # # set reltype ordering so rels file ordering is readable
        # self._relationships._reltype_ordering = (RT_SLIDEMASTER,
        #     RT_NOTESMASTER, RT_HANDOUTMASTER, RT_SLIDE, RT_PRESPROPS,
        #     RT_VIEWPROPS, RT_TABLESTYLES, RT_THEME)

        # selectively unmarshal relationships for now
        for rel in self._relationships:
            # log.debug("Presentation Relationship %s", rel._reltype)
            if rel._reltype == RT_SLIDEMASTER:
                self.__slidemasters._loadpart(rel._target)
            elif rel._reltype == RT_SLIDE:
                self.__slides._loadpart(rel._target)
        return self

    def __rewrite_sldIdLst(self):
        """
        Rewrite the ``<p:sldIdLst>`` element in ``<p:presentation>`` to
        reflect current ordering of slide relationships and possible
        renumbering of ``rId`` values.
        """
        sldIdLst = _child(self._element, 'p:sldIdLst', _nsmap)
        if sldIdLst is None:
            sldIdLst = self.__add_sldIdLst()
        sldIdLst.clear()
        sld_rels = self._relationships.rels_of_reltype(RT_SLIDE)
        for idx, rel in enumerate(sld_rels):
            sldId = _Element('p:sldId', _nsmap)
            sldIdLst.append(sldId)
            sldId.set('id', str(256+idx))
            sldId.set(qn('r:id'), rel._rId)

    def __add_sldIdLst(self):
        """
        Add a <p:sldIdLst> element to <p:presentation> in the right sequence
        among its siblings.
        """
        sldIdLst = _child(self._element, 'p:sldIdLst', _nsmap)
        assert sldIdLst is None, '__add_sldIdLst() called where '\
                                 '<p:sldIdLst> already exists'
        sldIdLst = _Element('p:sldIdLst', _nsmap)
        # insert new sldIdLst element in right sequence
        sldSz = _child(self._element, 'p:sldSz', _nsmap)
        if sldSz is not None:
            sldSz.addprevious(sldIdLst)
        else:
            notesSz = _child(self._element, 'p:notesSz', _nsmap)
            notesSz.addprevious(sldIdLst)
        return sldIdLst


class Image(BasePart):
    """
    Return new Image part instance. *file* may be |None|, a path to a file (a
    string), or a file-like object. If *file* is |None|, no image is loaded
    and :meth:`_load` must be called before using the instance. Otherwise, the
    file referenced or contained in *file* is loaded. Corresponds to package
    files ppt/media/image[1-9][0-9]*.*.
    """
    def __init__(self, file=None):
        super(Image, self).__init__()
        self.__ext = None
        if file is not None:
            self.__load_image_from_file(file)

    @property
    def ext(self):
        """Return file extension for this image"""
        assert self.__ext, "Image.__ext referenced before assigned"
        return self.__ext

    @property
    def _sha1(self):
        """Return SHA1 hash digest for image"""
        return hashlib.sha1(self._blob).hexdigest()

    @property
    def _blob(self):
        """
        For an image, _blob is always _load_blob, image file content is not
        manipulated.
        """
        return self._load_blob

    def _load(self, pkgpart, part_dict):
        """Handle aspects of loading that are particular to image parts."""
        # call parent to do generic aspects of load
        super(Image, self)._load(pkgpart, part_dict)
        # set file extension
        self.__ext = posixpath.splitext(pkgpart.partname)[1]
        # return self-reference to allow generative calling
        return self

    @staticmethod
    def __image_ext_content_type(ext):
        """Return the content type corresponding to filename extension *ext*"""
        if ext not in spec.default_content_types:
            tmpl = "unsupported image file extension '%s'"
            raise TypeError(tmpl % (ext))
        content_type = spec.default_content_types[ext]
        if not content_type.startswith('image/'):
            tmpl = "'%s' is not an image content type; ext '%s'"
            raise TypeError(tmpl % (content_type, ext))
        return content_type

    @staticmethod
    def __ext_from_image_stream(stream):
        """
        Return the filename extension appropriate to the image file contained
        in *stream*.
        """
        ext_map = {'GIF': '.gif', 'JPEG': '.jpg', 'PNG': '.png',
                   'TIFF': '.tiff', 'WMF': '.wmf'}
        stream.seek(0)
        format = PIL_Image.open(stream).format
        if format not in ext_map:
            tmpl = "unsupported image format, expected one of: %s, got '%s'"
            raise ValueError(tmpl % (ext_map.keys(), format))
        return ext_map[format]

    def __load_image_from_file(self, file):
        """
        Load image from *file*, which is either a path to an image file or a
        file-like object.
        """
        if isinstance(file, basestring):  # file is a path
            path = file
            self.__ext = os.path.splitext(path)[1]
            self._content_type = self.__image_ext_content_type(self.__ext)
            with open(path, 'rb') as f:
                self._load_blob = f.read()
        else:  # assume file is a file-like object
            self.__ext = self.__ext_from_image_stream(file)
            self._content_type = self.__image_ext_content_type(self.__ext)
            file.seek(0)
            self._load_blob = file.read()


# ============================================================================
# Slide Parts
# ============================================================================

class SlideCollection(PartCollection):
    """
    Immutable sequence of slides belonging to an instance of |Presentation|,
    with methods for manipulating the slides in the presentation.
    """
    def __init__(self, presentation):
        super(SlideCollection, self).__init__()
        self.__presentation = presentation

    def add_slide(self, slidelayout):
        """Add a new slide that inherits layout from *slidelayout*."""
        # 1. construct new slide
        slide = Slide(slidelayout)
        # 2. add it to this collection
        self._values.append(slide)
        # 3. assign its partname
        self.__rename_slides()
        # 4. add presentation->slide relationship
        self.__presentation._add_relationship(RT_SLIDE, slide)
        # 5. return reference to new slide
        return slide

    def __rename_slides(self):
        """
        Assign partnames like ``/ppt/slides/slide9.xml`` to all slides in the
        collection. The name portion is always ``slide``. The number part
        forms a continuous sequence starting at 1 (e.g. 1, 2, 3, ...). The
        extension is always ``.xml``.
        """
        for idx, slide in enumerate(self._values):
            slide.partname = '/ppt/slides/slide%d.xml' % (idx+1)


class BaseSlide(BasePart):
    """
    Base class for slide parts, e.g. slide, slideLayout, slideMaster,
    notesSlide, notesMaster, and handoutMaster.
    """
    def __init__(self, content_type=None):
        """
        Needs content_type parameter so newly created parts (not loaded from
        package) can register their content type.
        """
        super(BaseSlide, self).__init__(content_type)
        self._shapes = None

    @property
    def name(self):
        """Internal name of this slide-like object."""
        cSld = self._element.cSld
        return cSld.get('name', default='')

    @property
    def shapes(self):
        """Collection of shape objects belonging to this slide."""
        assert self._shapes is not None, ("BaseSlide.shapes referenced "
                                          "before assigned")
        return self._shapes

    def _load(self, pkgpart, part_dict):
        """Handle aspects of loading that are general to slide types."""
        # call parent to do generic aspects of load
        super(BaseSlide, self)._load(pkgpart, part_dict)
        # unmarshal shapes
        self._shapes = ShapeCollection(self._element.cSld.spTree, self)
        # return self-reference to allow generative calling
        return self


class Slide(BaseSlide):
    """
    Slide part. Corresponds to package files ppt/slides/slide[1-9][0-9]*.xml.
    """
    def __init__(self, slidelayout=None):
        super(Slide, self).__init__(CT_SLIDE)
        self.__slidelayout = slidelayout
        self._element = self.__minimal_element
        self._shapes = ShapeCollection(self._element.cSld.spTree, self)
        # if slidelayout, this is a slide being added, not one being loaded
        if slidelayout:
            self._shapes._clone_layout_placeholders(slidelayout)
            # add relationship to slideLayout part
            self._add_relationship(RT_SLIDELAYOUT, slidelayout)

    @property
    def slidelayout(self):
        """
        :class:`SlideLayout` object this slide inherits appearance from.
        """
        return self.__slidelayout

    def _load(self, pkgpart, part_dict):
        """
        Load slide from package part.
        """
        # call parent to do generic aspects of load
        super(Slide, self)._load(pkgpart, part_dict)
        # selectively unmarshal relationships for now
        for rel in self._relationships:
            # log.debug("SlideMaster Relationship %s", rel._reltype)
            if rel._reltype == RT_SLIDELAYOUT:
                self.__slidelayout = rel._target
        return self

    @property
    def __minimal_element(self):
        """
        Return element containing the minimal XML for a slide, based on what
        is required by the XMLSchema.
        """
        sld = _Element('p:sld', _nsmap)
        _SubElement(sld, 'p:cSld', _nsmap)
        _SubElement(sld.cSld, 'p:spTree', _nsmap)
        _SubElement(sld.cSld.spTree, 'p:nvGrpSpPr', _nsmap)
        _SubElement(sld.cSld.spTree.nvGrpSpPr, 'p:cNvPr', _nsmap)
        _SubElement(sld.cSld.spTree.nvGrpSpPr, 'p:cNvGrpSpPr', _nsmap)
        _SubElement(sld.cSld.spTree.nvGrpSpPr, 'p:nvPr', _nsmap)
        _SubElement(sld.cSld.spTree, 'p:grpSpPr', _nsmap)
        sld.cSld.spTree.nvGrpSpPr.cNvPr.set('id', '1')
        sld.cSld.spTree.nvGrpSpPr.cNvPr.set('name', '')
        return sld


class SlideLayout(BaseSlide):
    """
    Slide layout part. Corresponds to package files
    ppt/slideLayouts/slideLayout[1-9][0-9]*.xml.
    """
    def __init__(self):
        super(SlideLayout, self).__init__(CT_SLIDELAYOUT)
        self.__slidemaster = None

    @property
    def slidemaster(self):
        """Slide master from which this slide layout inherits properties."""
        assert self.__slidemaster is not None, ("SlideLayout.slidemaster "
                                                "referenced before assigned")
        return self.__slidemaster

    def _load(self, pkgpart, part_dict):
        """
        Load slide layout from package part.
        """
        # call parent to do generic aspects of load
        super(SlideLayout, self)._load(pkgpart, part_dict)

        # selectively unmarshal relationships we need
        for rel in self._relationships:
            # log.debug("SlideLayout Relationship %s", rel._reltype)
            # get slideMaster from which this slideLayout inherits properties
            if rel._reltype == RT_SLIDEMASTER:
                self.__slidemaster = rel._target

        # return self-reference to allow generative calling
        return self


class SlideMaster(BaseSlide):
    """
    Slide master part. Corresponds to package files
    ppt/slideMasters/slideMaster[1-9][0-9]*.xml.
    """
    # TECHNOTE: In the Microsoft API, Master is a general type that all of
    # SlideMaster, SlideLayout (CustomLayout), HandoutMaster, and NotesMaster
    # inherit from. So might look into why that is and consider refactoring
    # the various masters a bit later.

    def __init__(self):
        super(SlideMaster, self).__init__(CT_SLIDEMASTER)
        self.__slidelayouts = PartCollection()

    @property
    def slidelayouts(self):
        """
        Collection of slide layout objects belonging to this slide master.
        """
        return self.__slidelayouts

    def _load(self, pkgpart, part_dict):
        """
        Load slide master from package part.
        """
        # call parent to do generic aspects of load
        super(SlideMaster, self)._load(pkgpart, part_dict)

        # selectively unmarshal relationships for now
        for rel in self._relationships:
            # log.debug("SlideMaster Relationship %s", rel._reltype)
            if rel._reltype == RT_SLIDELAYOUT:
                self.__slidelayouts._loadpart(rel._target)
        return self


# ============================================================================
# Shapes
# ============================================================================

class BaseShape(object):
    """
    Base class for shape objects. Both :class:`Shape` and :class:`Picture`
    inherit from :class:`BaseShape`.
    """
    def __init__(self, shape_element):
        super(BaseShape, self).__init__()
        self._element = shape_element
        # e.g. nvSpPr for shape, nvPicPr for pic, etc.
        self.__nvXxPr = shape_element.xpath('./*[1]', namespaces=_nsmap)[0]

    @property
    def has_textframe(self):
        """
        True if this shape has a txBody element and can contain text.
        """
        return _child(self._element, 'p:txBody') is not None

    @property
    def id(self):
        """
        Id of this shape. Note that ids are constrained to positive integers.
        """
        return int(self.__nvXxPr.cNvPr.get('id'))

    @property
    def is_placeholder(self):
        """
        True if this shape is a placeholder. A shape is a placeholder if it
        has a <p:ph> element.
        """
        return _child(self.__nvXxPr.nvPr, 'p:ph') is not None

    @property
    def name(self):
        """Name of this shape."""
        return self.__nvXxPr.cNvPr.get('name')

    def _set_text(self, text):
        """Replace all text in shape with single run containing *text*"""
        if not self.has_textframe:
            raise TypeError("cannot set text of shape with no text frame")
        self.textframe.text = _to_unicode(text)

    #: Write-only. Assignment to *text* replaces all text currently contained
    #: by the shape, resulting in a text frame containing exactly one
    #: paragraph, itself containing a single run. The assigned value can be a
    #: 7-bit ASCII string, a UTF-8 encoded 8-bit string, or unicode. String
    #: values are converted to unicode assuming UTF-8 encoding.
    text = property(None, _set_text)

    @property
    def textframe(self):
        """
        TextFrame instance for this shape. Raises :class:`ValueError` if shape
        has no text frame. Use :meth:`has_textframe` to check whether a shape
        has a text frame.
        """
        txBody = _child(self._element, 'p:txBody')
        if txBody is None:
            raise ValueError('shape has no text frame')
        return TextFrame(txBody)

    @property
    def _is_title(self):
        """
        True if this shape is a title placeholder.
        """
        ph = _child(self.__nvXxPr.nvPr, 'p:ph')
        if ph is None:
            return False
        # idx defaults to 0 when idx attr is absent
        ph_idx = ph.get('idx', '0')
        # title placeholder is identified by idx of 0
        return ph_idx == '0'


class ShapeCollection(BaseShape, Collection):
    """
    Sequence of shapes. Corresponds to CT_GroupShape in pml schema. Note that
    while spTree in a slide is a group shape, the group shape is recursive in
    that a group shape can include other group shapes within it.
    """
    _NVGRPSPPR = qn('p:nvGrpSpPr')
    _GRPSPPR = qn('p:grpSpPr')
    _SP = qn('p:sp')
    _GRPSP = qn('p:grpSp')
    _GRAPHICFRAME = qn('p:graphicFrame')
    _CXNSP = qn('p:cxnSp')
    _PIC = qn('p:pic')
    _CONTENTPART = qn('p:contentPart')
    _EXTLST = qn('p:extLst')

    def __init__(self, spTree, slide=None):
        # log.debug('ShapeCollect.__init__() called w/element 0x%X', id(spTree))
        super(ShapeCollection, self).__init__(spTree)
        self.__spTree = spTree
        self.__slide = slide
        self.__shapes = self._values
        # unmarshal shapes
        for elm in spTree.iterchildren():
            # log.debug('elm.tag == %s', elm.tag[60:])
            if elm.tag in (self._NVGRPSPPR, self._GRPSPPR, self._EXTLST):
                continue
            elif elm.tag == self._SP:
                shape = Shape(elm)
            elif elm.tag == self._PIC:
                shape = Picture(elm)
            elif elm.tag == self._GRPSP:
                shape = ShapeCollection(elm)
            elif elm.tag == self._CONTENTPART:
                msg = "first time 'contentPart' shape encountered in the "\
                      "wild, please let developer know and send example"
                raise ValueError(msg)
            else:
                shape = BaseShape(elm)
            self.__shapes.append(shape)

    @property
    def placeholders(self):
        """
        Immutable sequence containing the placeholder shapes in this shape
        collection, sorted in *idx* order.
        """
        placeholders =\
            [Placeholder(sp) for sp in self.__shapes if sp.is_placeholder]
        placeholders.sort(key=lambda ph: ph.idx)
        return tuple(placeholders)

    @property
    def title(self):
        """The title shape in collection or None if no title placeholder."""
        for shape in self.__shapes:
            if shape._is_title:
                return shape
        return None

    def add_picture(self, file, left, top, width=None, height=None):
        """
        Add picture shape displaying image in *file*, where *file* can be
        either a path to a file (a string) or a file-like object.
        """
        pkg = Package.containing(self.__slide)
        image = pkg._images.add_image(file)
        rel = self.__slide._add_relationship(RT_IMAGE, image)
        pic = self.__pic(rel._rId, file, left, top, width, height)
        self.__spTree.append(pic)
        picture = Picture(pic)
        self.__shapes.append(picture)
        return picture

    def add_textbox(self, left, top, width, height):
        """
        Add text box shape of specified size at specified position.
        """
        id = self.__next_shape_id
        name = 'TextBox %d' % (id-1)
        sp = self.__sp(id, name, left, top, width, height, is_textbox=True)
        self.__spTree.append(sp)
        shape = Shape(sp)
        self.__shapes.append(shape)
        return shape

    def _clone_layout_placeholders(self, slidelayout):
        """
        Add placeholder shapes based on those in *slidelayout*. Z-order of
        placeholders is preserved. Latent placeholders (date, slide number,
        and footer) are not cloned.
        """
        latent_ph_types = (PH_TYPE_DT, PH_TYPE_SLDNUM, PH_TYPE_FTR)
        for sp in slidelayout.shapes:
            if not sp.is_placeholder:
                continue
            ph = Placeholder(sp)
            if ph.type in latent_ph_types:
                continue
            self.__clone_layout_placeholder(ph)

    def __clone_layout_placeholder(self, layout_ph):
        """
        Add a new placeholder shape based on the slide layout placeholder
        *layout_ph*.
        """
        id = self.__next_shape_id
        ph_type = layout_ph.type
        orient = layout_ph.orient
        shapename = self.__next_ph_name(ph_type, id, orient)

        sp = self.__new_placeholder_sp(layout_ph, id, ph_type, orient,
                                       shapename)
        self.__spTree.append(sp)
        shape = Shape(sp)
        self.__shapes.append(shape)
        return shape

    def __new_placeholder_sp(self, layout_ph, id, ph_type, orient, shapename):
        """
        Assemble a new ``<p:sp>`` element based on the specified parameters.
        """
        # form XML hierarchy
        sp = _Element('p:sp', _nsmap)
        _SubElement(sp, 'p:nvSpPr')
        _SubElement(sp.nvSpPr, 'p:cNvPr')
        sp.nvSpPr.cNvPr.set('id', str(id))
        sp.nvSpPr.cNvPr.set('name', shapename)
        _SubElement(sp.nvSpPr, 'p:cNvSpPr')
        _SubElement(sp.nvSpPr.cNvSpPr, 'a:spLocks')
        sp.nvSpPr.cNvSpPr[qn('a:spLocks')].set('noGrp', '1')

        _SubElement(sp.nvSpPr, 'p:nvPr')
        ph = _SubElement(sp.nvSpPr.nvPr, 'p:ph')
        if ph_type != PH_TYPE_OBJ:
            ph.set('type', ph_type)
        if layout_ph.orient != PH_ORIENT_HORZ:
            ph.set('orient', layout_ph.orient)
        if layout_ph.sz != PH_SZ_FULL:
            ph.set('sz', layout_ph.sz)
        if layout_ph.idx != 0:
            ph.set('idx', str(layout_ph.idx))

        _SubElement(sp, 'p:spPr')

        placeholder_types_that_have_a_text_frame = (
            PH_TYPE_TITLE, PH_TYPE_CTRTITLE, PH_TYPE_SUBTITLE, PH_TYPE_BODY,
            PH_TYPE_OBJ)

        if ph_type in placeholder_types_that_have_a_text_frame:
            _SubElement(sp, 'p:txBody')
            _SubElement(sp.txBody, 'a:bodyPr')
            _SubElement(sp.txBody, 'a:lstStyle')
            _SubElement(sp.txBody, 'a:p')

        return sp

    def __next_ph_name(self, ph_type, id, orient):
        """
        Next unique placeholder name for placeholder shape of type *ph_type*,
        with id number *id* and orientation *orient*. Usually will be standard
        placeholder root name suffixed with id-1, e.g.
        __next_ph_name(PH_TYPE_TBL, 4, 'horz') ==> 'Table Placeholder 3'. The
        number is incremented as necessary to make the name unique within the
        collection. If *orient* is ``'vert'``, the placeholder name is
        prefixed with ``'Vertical '``.
        """
        basename = slide_ph_basenames[ph_type]
        # prefix rootname with 'Vertical ' if orient is 'vert'
        if orient == PH_ORIENT_VERT:
            basename = 'Vertical %s' % basename
        # increment numpart as necessary to make name unique
        numpart = id - 1
        names = self.__spTree.xpath('//p:cNvPr/@name', namespaces=_nsmap)
        while True:
            name = '%s %d' % (basename, numpart)
            if name not in names:
                break
            numpart += 1
        # log.debug("assigned placeholder name '%s'" % name)
        return name

    @property
    def __next_shape_id(self):
        """
        Next available drawing object id number in collection, starting from 1
        and making use of any gaps in numbering. In practice, the minimum id
        is 2 because the spTree element is always assigned id="1".
        """
        cNvPrs = self.__spTree.xpath('//p:cNvPr', namespaces=_nsmap)
        ids = [int(cNvPr.get('id')) for cNvPr in cNvPrs]
        ids.sort()
        # first gap in sequence wins, or falls off the end as max(ids)+1
        next_id = 1
        for id in ids:
            if id > next_id:
                break
            next_id += 1
        return next_id

    def __pic(self, rId, file, x, y, cx=None, cy=None):
        """
        Return minimal ``<p:pic>`` element based on *rId* and *file*. *file* is
        either a path to the file (a string) or a file-like object.
        """
        id = self.__next_shape_id
        shapename = 'Picture %d' % (id-1)
        if isinstance(file, basestring):  # *file* is a path
            filename = os.path.split(file)[1]
        else:
            filename = None
            file.seek(0)

        # set cx and cy from image size if not specified
        cx_px, cy_px = PIL_Image.open(file).size
        cx = cx if cx is not None else Px(cx_px)
        cy = cy if cy is not None else Px(cy_px)

        # assemble XML hierarchy of pic element
        pic = _Element('p:pic', _nsmap)
        _SubElement(pic, 'p:nvPicPr')
        _SubElement(pic.nvPicPr, 'p:cNvPr')
        pic.nvPicPr.cNvPr.set('id', str(id))
        pic.nvPicPr.cNvPr.set('name', shapename)
        if filename:
            pic.nvPicPr.cNvPr.set('descr', filename)
        _SubElement(pic.nvPicPr, 'p:cNvPicPr')
        _SubElement(pic.nvPicPr, 'p:nvPr')

        _SubElement(pic, 'p:blipFill')
        _SubElement(pic.blipFill, 'a:blip')
        pic.blipFill[qn('a:blip')].set(qn('r:embed'), rId)
        _SubElement(pic.blipFill, 'a:stretch')
        _SubElement(pic.blipFill[qn('a:stretch')], 'a:fillRect')
        _SubElement(pic, 'p:spPr')
        _SubElement(pic.spPr, 'a:xfrm')
        _SubElement(pic.spPr[qn('a:xfrm')], 'a:off')
        pic.spPr[qn('a:xfrm')].off.set('x', str(x))
        pic.spPr[qn('a:xfrm')].off.set('y', str(y))
        _SubElement(pic.spPr[qn('a:xfrm')], 'a:ext')
        pic.spPr[qn('a:xfrm')].ext.set('cx', str(cx))
        pic.spPr[qn('a:xfrm')].ext.set('cy', str(cy))
        _SubElement(pic.spPr, 'a:prstGeom')
        pic.spPr[qn('a:prstGeom')].set('prst', 'rect')
        _SubElement(pic.spPr[qn('a:prstGeom')], 'a:avLst')
        return pic

    def __sp(self, sp_id, shapename, x, y, cx, cy, is_textbox=False):
        """Return new ``<p:sp>`` element based on parameters."""
        sp = _Element('p:sp', _nsmap)
        _SubElement(sp, 'p:nvSpPr')
        _SubElement(sp.nvSpPr, 'p:cNvPr')
        sp.nvSpPr.cNvPr.set('id', str(sp_id))
        sp.nvSpPr.cNvPr.set('name', shapename)
        _SubElement(sp.nvSpPr, 'p:cNvSpPr')
        if is_textbox:
            sp.nvSpPr.cNvSpPr.set('txBox', '1')
        _SubElement(sp.nvSpPr, 'p:nvPr')

        _SubElement(sp, 'p:spPr')
        _SubElement(sp.spPr, 'a:xfrm')
        _SubElement(sp.spPr[qn('a:xfrm')], 'a:off')
        sp.spPr[qn('a:xfrm')].off.set('x', str(x))
        sp.spPr[qn('a:xfrm')].off.set('y', str(y))
        _SubElement(sp.spPr[qn('a:xfrm')], 'a:ext')
        sp.spPr[qn('a:xfrm')].ext.set('cx', str(cx))
        sp.spPr[qn('a:xfrm')].ext.set('cy', str(cy))
        _SubElement(sp.spPr, 'a:prstGeom')
        sp.spPr[qn('a:prstGeom')].set('prst', 'rect')
        _SubElement(sp.spPr[qn('a:prstGeom')], 'a:avLst')
        _SubElement(sp.spPr, 'a:noFill')

        _SubElement(sp, 'p:txBody')
        _SubElement(sp.txBody, 'a:bodyPr')
        sp.txBody[qn('a:bodyPr')].set('wrap', 'none')
        _SubElement(sp.txBody[qn('a:bodyPr')], 'a:spAutoFit')
        _SubElement(sp.txBody, 'a:lstStyle')
        _SubElement(sp.txBody, 'a:p')

        return sp


class Placeholder(object):
    """
    Decorator (pattern) class for adding placeholder properties to a shape
    that contains a placeholder element, e.g. ``<p:ph>``.
    """
    def __new__(cls, shape):
        cls = type('PlaceholderDecorator', (Placeholder, shape.__class__), {})
        return object.__new__(cls)

    def __init__(self, shape):
        self.__decorated = shape
        xpath = './*[1]/p:nvPr/p:ph'
        self.__ph = self._element.xpath(xpath, namespaces=_nsmap)[0]

    def __getattr__(self, name):
        """
        Called when *name* is not found in ``self`` or in class tree. In this
        case, delegate attribute lookup to decorated (it's probably in its
        instance namespace).
        """
        return getattr(self.__decorated, name)

    @property
    def type(self):
        """Placeholder type, e.g. PH_TYPE_CTRTITLE"""
        return self.__ph.get('type', PH_TYPE_OBJ)

    @property
    def orient(self):
        """Placeholder 'orient' attribute, e.g. PH_ORIENT_HORZ"""
        return self.__ph.get('orient', PH_ORIENT_HORZ)

    @property
    def sz(self):
        """Placeholder 'sz' attribute, e.g. PH_SZ_FULL"""
        return self.__ph.get('sz', PH_SZ_FULL)

    @property
    def idx(self):
        """Placeholder 'idx' attribute, e.g. '0'"""
        return int(self.__ph.get('idx', 0))


class Picture(BaseShape):
    """
    A picture shape, one that places an image on a slide. Corresponds to the
    ``<p:pic>`` element.
    """
    def __init__(self, pic):
        super(Picture, self).__init__(pic)


class Shape(BaseShape):
    """
    A shape that can appear on a slide. Corresponds to the ``<p:sp>`` element
    that can appear in any of the slide-type parts (slide, slideLayout,
    slideMaster, notesPage, notesMaster, handoutMaster).
    """
    def __init__(self, shape_element):
        super(Shape, self).__init__(shape_element)


# ============================================================================
# Text-related classes
# ============================================================================

class TextFrame(object):
    """
    The part of a shape that contains its text. Not all shapes have a text
    frame. Corresponds to the ``<p:txBody>`` element that can appear as a
    child element of ``<p:sp>``. Not intended to be constructed directly.
    """
    def __init__(self, txBody):
        super(TextFrame, self).__init__()
        self.__txBody = txBody

    @property
    def paragraphs(self):
        """
        Immutable sequence of :class:`Paragraph` instances corresponding to
        the paragraphs in this text frame. A text frame always contains at
        least one paragraph.
        """
        xpath = './a:p'
        p_elms = self.__txBody.xpath(xpath, namespaces=_nsmap)
        paragraphs = []
        for p in p_elms:
            paragraphs.append(Paragraph(p))
        return tuple(paragraphs)

    def _set_text(self, text):
        """Replace all text in text frame with single run containing *text*"""
        self.clear()
        self.paragraphs[0].text = _to_unicode(text)

    #: Write-only. Assignment to *text* replaces all text currently contained
    #: in the text frame with the assigned expression. After assignment, the
    #: text frame contains exactly one paragraph containing a single run
    #: containing all the text. The assigned value can be a 7-bit ASCII
    #: string, a UTF-8 encoded 8-bit string, or unicode. String values are
    #: converted to unicode assuming UTF-8 encoding.
    text = property(None, _set_text)

    def _set_vertical_anchor(self, value):
        """
        Set ``anchor`` attribute of ``<a:bodyPr>`` element
        """
        value_map = {MSO.ANCHOR_TOP: 't', MSO.ANCHOR_MIDDLE: 'ctr',
                     MSO.ANCHOR_BOTTOM: 'b'}
        bodyPr = _get_or_add(self.__txBody, 'a:bodyPr')
        bodyPr.set('anchor', value_map[value])

    #: Write-only. Assignment to *vertical_anchor* sets the vertical
    #: alignment of the text frame to top, middle, or bottom. Valid values are
    #: ``MSO.ANCHOR_TOP``, ``MSO.ANCHOR_MIDDLE``, or ``MSO.ANCHOR_BOTTOM``.
    #: The ``MSO`` name is imported from ``pptx.constants``.
    vertical_anchor = property(None, _set_vertical_anchor)

    def add_paragraph(self):
        """
        Return new |Paragraph| instance appended to the sequence of paragraphs
        contained in this text frame.
        """
        # <a:p> elements are last in txBody, so can simply append new one
        p = _Element('a:p', _nsmap)
        self.__txBody.append(p)
        return Paragraph(p)

    def clear(self):
        """
        Remove all paragraphs except one empty one.
        """
        p_list = self.__txBody.xpath('./a:p', namespaces=_nsmap)
        for p in p_list[1:]:
            self.__txBody.remove(p)
        p = self.paragraphs[0]
        p.clear()


class _Font(object):
    """
    Character properties object, prominent among those properties being font
    size, font name, bold, italic, etc. Corresponds to ``<a:rPr>`` child
    element of a run. Also appears as ``<a:defRPr>`` and ``<a:endParaRPr>``
    in paragraph and ``<a:defRPr>`` in list style elements. Not intended to be
    constructed directly.
    """
    def __init__(self, rPr):
        super(_Font, self).__init__()
        self.__rPr = rPr

    @property
    def bold(self):
        """
        Get or set boolean bold value of |_Font|, e.g.
        ``paragraph.font.bold = True``.
        """
        b = self.__rPr.get('b')
        return True if b in ('true', '1') else False

    @bold.setter
    def bold(self, bool):
        if bool:
            self.__rPr.set('b', '1')
        elif 'b' in self.__rPr.attrib:
            del self.__rPr.attrib['b']

    def _set_size(self, centipoints):
        # handle float centipoints value gracefully
        centipoints = int(centipoints)
        self.__rPr.set('sz', str(centipoints))

    #: Set the font size. In PresentationML, font size is expressed in
    #: hundredths of a point (centipoints). The :class:`pptx.util.Pt` class
    #: allows convenient conversion to centipoints from float or integer point
    #: values, e.g. ``Pt(12.5)``. I'm pretty sure I just made up the word
    #: *centipoint*, but it seems apt :).
    size = property(None, _set_size)


class Paragraph(object):
    """
    Paragraph object. Not intended to be constructed directly.
    """
    def __init__(self, p):
        super(Paragraph, self).__init__()
        self.__p = p

    @property
    def font(self):
        """
        :class:`_Font` object containing default character properties for the
        runs in this paragraph. These character properties override default
        properties inherited from parent objects such as the text frame the
        paragraph is contained in and they may be overridden by character
        properties set at the run level.
        """
        # A _Font instance is created on first access if it doesn't exist.
        # This can cause "litter" <a:pPr> and <a:defRPr> elements to be
        # included in the XML if the _Font element is referred to but not
        # populated with values.
        if not hasattr(self.__p, 'pPr'):
            pPr = _Element('a:pPr', _nsmap)
            self.__p.insert(0, pPr)
        if not hasattr(self.__p.pPr, 'defRPr'):
            _SubElement(self.__p.pPr, 'a:defRPr')
        return _Font(self.__p.pPr.defRPr)

    @property
    def runs(self):
        """
        Immutable sequence of :class:`Run` instances corresponding to the runs
        in this paragraph.
        """
        xpath = './a:r'
        r_elms = self.__p.xpath(xpath, namespaces=_nsmap)
        runs = []
        for r in r_elms:
            runs.append(Run(r))
        return tuple(runs)

    def _set_text(self, text):
        """Replace runs with single run containing *text*"""
        self.clear()
        r = self.add_run()
        r.text = _to_unicode(text)

    #: Write-only. Assignment to *text* replaces all text currently contained
    #: in the paragraph. After assignment, the paragraph containins exactly
    #: one run containing the text value of the assigned expression. The
    #: assigned value can be a 7-bit ASCII string, a UTF-8 encoded 8-bit
    #: string, or unicode. String values are converted to unicode assuming
    #: UTF-8 encoding.
    text = property(None, _set_text)

    def add_run(self):
        """Return a new run appended to the runs in this paragraph."""
        r = _Element('a:r', _nsmap)
        _SubElement(r, 'a:t')
        # work out where to insert it, ahead of a:endParaRPr if there is one
        endParaRPr = _child(self.__p, 'a:endParaRPr')
        if endParaRPr is not None:
            endParaRPr.addprevious(r)
        else:
            self.__p.append(r)
        return Run(r)

    def clear(self):
        """Remove all runs from this paragraph."""
        # retain pPr if present
        pPr = _child(self.__p, 'a:pPr')
        self.__p.clear()
        if pPr is not None:
            self.__p.insert(0, pPr)


class Run(object):
    """
    Text run object. Corresponds to ``<a:r>`` child element in a paragraph.
    """
    def __init__(self, r):
        super(Run, self).__init__()
        self.__r = r

    @property
    def font(self):
        """
        :class:`_Font` object containing run-level character properties for the
        text in this run. Character properties can and perhaps most often are
        inherited from parent objects such as the paragraph and slide layout
        the run is contained in. Only those specifically assigned at the run
        level are contained in the :class:`_Font` object.
        """
        if not hasattr(self.__r, 'rPr'):
            self.__r.insert(0, _Element('a:rPr', _nsmap))
        return _Font(self.__r.rPr)

    @property
    def text(self):
        """
        Read/Write. Text contained in the run. A regular text run is required
        to contain exactly one ``<a:t>`` (text) element. Assignment to *text*
        replaces the text currently contained in the run. The assigned value
        can be a 7-bit ASCII string, a UTF-8 encoded 8-bit string, or unicode.
        String values are converted to unicode assuming UTF-8 encoding.
        """
        return self.__r.t.text

    @text.setter
    def text(self, str):
        """Set the text of this run to *str*."""
        self.__r.t._setText(_to_unicode(str))
