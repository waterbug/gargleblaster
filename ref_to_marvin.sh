#!/bin/sh
sed s/The\ Pan\ Galactic\ Engineering\ Framework/Marvin/g ../pangalactic.node/pangalactic/node/docs/reference.md | \
    sed s/Pan\ Galactic\ Engineering\ Framework/Marvin/g | \
    sed s/...PGEF...//g | \
    sed s/Pan\ Galactic/Marvin/g | \
    sed s/pgef_arch/marvin_arch/g | \
    sed s/pangalaxian/marvin/g | \
    sed s/Pangalaxian/Marvin/g | \
    sed s/PANGALAXIAN/Marvin/g > doc/marvin_reference.md

