# cdef extern from "xercesc/util/XercesDefs.hpp" namespace "xercesc":
#     ctypedef unsigned int XMLCh

# cdef extern from "xercesc/dom/DOM.hpp" namespace "xercesc":
#     cdef cppclass DOMElement:
#        XMLCh* getTagName()
