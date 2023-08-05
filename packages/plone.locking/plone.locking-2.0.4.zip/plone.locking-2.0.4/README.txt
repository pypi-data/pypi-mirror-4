Overview
========

Provides basic automatic locking support for Plone. Locks are stealable by
default, meaning that a user with edit privileges will be able to steal
another user's lock, but will be warned that someone else may be editing
the same object. Used by Plone, Archetypes and plone.app.iterate
