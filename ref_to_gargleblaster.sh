#!/bin/sh
sed s/The\ Pan\ Galactic\ Engineering\ Framework/Gargleblaster/g ../pangalactic.node/pangalactic/node/docs/reference.md | \
    sed s/Pan\ Galactic\ Engineering\ Framework/Gargleblaster/g | \
    sed s/...PGEF...//g | \
    sed s/Pan\ Galactic/Gargleblaster/g | \
    sed s/pgef_arch/gargleblaster_arch/g | \
    sed s/pangalaxian/gargleblaster/g | \
    sed s/Pangalaxian/Gargleblaster/g | \
    sed s/PANGALAXIAN/Gargleblaster/g > doc/gargleblaster_reference.md

