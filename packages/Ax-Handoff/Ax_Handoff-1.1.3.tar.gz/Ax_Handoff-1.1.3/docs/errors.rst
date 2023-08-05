==============================================================================
Errors & Exceptions
==============================================================================

The ``axonchisel.handoff.error`` module contains all Exceptions raised by 
this package:
    
- ``SerializeError``:
    Error encoding an object to wire format.
        
- ``UnserializeError``
    Error decoding an object from wire format.

- ``DataTamperedError``
    Subclass of UnserializeError indicating data
    was tampered with or corrupted in transit.

