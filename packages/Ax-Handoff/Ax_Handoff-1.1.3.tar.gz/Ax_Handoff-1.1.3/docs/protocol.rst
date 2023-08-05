==============================================================================
Protocol Specification
==============================================================================

This section contains a detailed description of the encoding protocol
wire format.  This is purely optional reading for the casual user,
as the details of encoding and decoding this protocol are handled by
the package itself.

Developers interested in implementing this protocol in other languages or
verifying the security of this protocol will find this document useful.


------------------------------------------------------------------------------
Encodings Used
------------------------------------------------------------------------------

"UB64 Encoding" is URL-safe Base64 encoding ('base64url'), which is 
defined as regular Base64 encoding with the following conversions:

- "=" becomes "" (removed, and re-padded on decode)
- "+" becomes "-" (hyphen)
- "/" becomes "_" (underscore)

The set of characters produced by UB64 is:

- abcdefghijklmnopqrstuvwxyz (26)
- ABCDEFGHIJKLMNOPQRSTUVWXYZ (26)
- 0123456789 (10)
- -_ (2)


------------------------------------------------------------------------------
Elements
------------------------------------------------------------------------------

The protocol wraps all data in an ``Envelope`` which is comprised 
entirely of URL-safe characters that may be assigned to an HTTP
GET query param without further encoding.

The ``Envelope`` is a concatenation of:

- ``Header``
- ``Body``
- ``Footer``

The ``Header`` is concatenated strings:

- Magic chars "XH".
- Variant indicator char "A" or "B".
- UB64 encoding of HMAC of serialized ``Body``.
 
The HMAC uses SHA-1 with a key obtained by the SHA-512 hash of 
the secret phrase.  This hash is verified upon decoding, prior to
decryption of the body, in order to detect tampering or transmission
errors.

The ``Body`` is a UB64 encoding of concatenated byte strings:

- Variant A:

  - 16 byte initialization vector (random).
  - AES-encrypted padded Gzipped data payload.

- Variant B:

  - Gzipped data payload.
 
In variant A, the data payload is gzipped then padded to 16-byte block size
(using padding algorithm described in 6.3. Content-encryption Process
of http://www.ietf.org/rfc/rfc5652.txt and previously PKCS #5) and
encrypted with AES-128 in CBC mode using a key obtained by the first
128 bits of the SHA-256 hash of the secret phrase.

The ``Footer`` is the string:

- Magic chars "HX".


------------------------------------------------------------------------------
Space Requirements
------------------------------------------------------------------------------

``Header`` and ``Footer`` sizes are fixed:

- ``Header`` = 30 chars
- ``Footer`` = 2 chars

The ``Body`` size is variable dependent on the data payload and degree
of compressibility.
Very small or totally random payloads may incur ~14 char overhead.
Worst case non-compressible payloads will require 4/3 x data size
(due to Base64 encoding).
Common JSON payloads will compress and encode to approximately
1/2 x original data size.

Because variant "B" forgoes AES encryption, several space saving factors
are relevant, which save ~20-40 characters in the final encoded output:

- no 16-byte initialization vector (iv)
- no padding to 16-byte blocks

------------------------------------------------------------------------------
Limitations
------------------------------------------------------------------------------

Maximum Effective Data Size (for URL query params)
..................................................

URLs should be kept under 2000 chars for widest browser compatibility.
A fairly conservative (but totally unenforced) maximum JSON size when
using Ax_Handoff over URLs is ~1000 chars (1KB).  
Assuming 1:1 compression, this might require ~1400 characters to 
encode as Ax_Handoff, leaving several hundred left over for other URL
path elements and query parameters.
When using Ax_Handoff for non-URL use cases, this limit is irrelevant,
and data length is unbounded.



