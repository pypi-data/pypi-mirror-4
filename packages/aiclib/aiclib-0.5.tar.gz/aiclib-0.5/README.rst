======
aiclib
======

A declarative system to consume the NVP api.

Current Build Status
====================
.. image:: https://api.travis-ci.org/jkoelker/aiclib.png
    :target: https://travis-ci.org/jkoelker/aiclib


Use of AIC wrapper lib
======================

The AIC wrapper command, or sentence, consists of two
parts:
- An object and its parameters
- A verb that acts on that object

Typical use looks as follows:
library.[possible parameters].object.[params].verb

It is possible for the object to be a collection of the
same type of object. The AIC wrapper lib will perform a
bulk operation on all of the objects.

If an object is not given it is assumed that the user
wishes to create an object (this is finalized through the
CREATE verb).

Object's parameters are completely optional if they are
set through a 'dot' function. Parameters that are required
are set during the declaration of the object.

A verb works on the object and is always the last portion
of a normal command.


Querying using the wrapper lib
==============================

The exception to the normal command pattern is when a user
wishes to query. A query works much like the typical use
but acts works as a modifer to the verb (an adverb).

Typical query use is as follows:
library.[params].object.query.[params].verb

The object stated in the command is what query is looking
for. Parameters may be passed to the query to make the
search more precise.

Extending the wrapper lib
=========================

The creation of a custom entity requires that the entity,
somewhere in its inheritance chain, inherit from
core.Entity. For it to properly return responses from the
server it also needs to overload unroll.
