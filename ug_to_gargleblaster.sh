#!/bin/sh
# NOTE: every expression needs the "g" flag.  Without it sed rewrites only the
# first match per line, so a line mentioning the name twice keeps the second
# one.  The lowercase and uppercase expressions were missing it, unlike their
# counterparts in ref_to_gargleblaster.sh.  No line in the user guide happens
# to match twice today, so the generated doc is currently correct either way
# -- this is latent, and would surface the next time the guide is edited.
sed s/Pangalaxian/Gargleblaster/g ../pangalactic.node/pangalactic/node/docs/user_guide.md | \
    sed s/pangalaxian/gargleblaster/g | \
    sed s/PANGALAXIAN/Gargleblaster/g > doc/gargleblaster_user_guide.md
