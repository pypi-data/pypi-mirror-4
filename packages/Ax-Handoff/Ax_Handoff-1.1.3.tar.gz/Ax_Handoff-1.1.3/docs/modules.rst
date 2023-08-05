==============================================================================
Modules
==============================================================================

The following modules are included in this packages:
        
- ``axonchisel.handoff.object``
    high-level support for encodeing/decoding Python
    objects for handoff.  
    Contains the primary interface to this package!
                
- ``axonchisel.handoff.error``
    exceptions raised by this package.
    Developers should import this module.

- ``axonchisel.handoff.protocol.*``
    elements able to serialize/unserialize to/from 
    encoded wire format strings.
    Not useful for developers unless desiring lower
    level access for custom integration.
                
- ``axonchisel.handoff.config``
    constants defining aspects of cryptography 
    used by the current variant of this package.
    Not useful for developers.

- ``axonchisel.handoff.util``
    utility functions used internally.
    Not useful for developers.
                
- ``axonchisel.handoff.tests``
    comprehensive unit tests built on ``unittest``.
    Not useful for developers.

