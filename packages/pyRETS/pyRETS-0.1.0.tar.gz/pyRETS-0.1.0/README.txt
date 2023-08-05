======
pyRETS
======

pyRETS is a Pure Python library for accessing RETS Servers to download
Real Estate Listings.

libRETS is a great library but takes to long to setup and manage when you run a
cluster of import workers and it has a tendancy to require newer versions of
packages than are available from RHEL6 without compiling the required packages
from source. And so pyRETS is born from pure python so we can `pip` and `puppet`
our rets library without fear of having to break packages on our servers.

This library is still under development.

Recusing Metadata Example:

    pyrets = pyRETS('serverurl', 'username', 'password')
    if (pyrets.Login()):
        for resource in pyrets.GetMetadata().GetMetadataAsObject().Resource:
            print "Found Resource:", resource.ResourceID
            
            if "Class" in resource:
                for a in resource.Class:
                    print "- Found Class:", a.ClassName
                    if "Field" in a:
                        for b in a.Field:
                            print "  - Found Field:", b.SystemName
            
            if "Object" in resource:
                for c in resource.Object:
                    print "  - Found Object:", c.ObjectType
            
            if "LookupType" in resource:
                for d in resource.LookupType:
                    print "    - Found LookupType:", d.LookupName
                    if "Lookup" in d:
                        for e in d.Lookup:
                            print "      - Found LookupValue:", e.ShortValue,
                                                        ",", e.LongValue

