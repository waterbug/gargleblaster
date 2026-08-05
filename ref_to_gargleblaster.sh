#!/bin/sh
# Generate doc/gargleblaster_reference.md from pangalactic.node's reference.md,
# rebranding PGEF/Pangalaxian as Gargleblaster.
#
# NOTE on the PGEF expressions below.  This used to be a single
#
#     sed s/...PGEF...//g
#
# whose dots are unescaped regex wildcards, so it matched three *arbitrary*
# characters either side of "PGEF" and deleted them along with it.  For the
# usual "**PGEF**" that meant eating the surrounding spaces as well, and the
# generated document shipped with text like "in thestandard serialization
# format", "to theserver." and "hence,uses the term".  It also missed the one
# occurrence at the start of a line, which has no three characters before it.
#
# Replaced with two explicit expressions, in this order:
#   1. drop the parenthetical gloss "(**PGEF**)", which follows the expanded
#      name and is redundant once that name has become "Gargleblaster";
#   2. rewrite any remaining "**PGEF**" as "**Gargleblaster**", preserving the
#      bold that the source applies to it.
# Single-quoted so the asterisks reach sed rather than the shell.
sed s/The\ Pan\ Galactic\ Engineering\ Framework/Gargleblaster/g ../pangalactic.node/pangalactic/node/docs/reference.md | \
    sed s/Pan\ Galactic\ Engineering\ Framework/Gargleblaster/g | \
    sed 's/ (\*\*PGEF\*\*)//g' | \
    sed 's/\*\*PGEF\*\*/**Gargleblaster**/g' | \
    sed s/Pan\ Galactic/Gargleblaster/g | \
    sed s/pgef_arch/gargleblaster_arch/g | \
    sed s/pangalaxian/gargleblaster/g | \
    sed s/Pangalaxian/Gargleblaster/g | \
    sed s/PANGALAXIAN/Gargleblaster/g > doc/gargleblaster_reference.md
