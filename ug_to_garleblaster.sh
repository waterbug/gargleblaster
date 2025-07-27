#!/bin/sh
sed s/Pangalaxian/Gargleblaster/g ../pangalactic.node/pangalactic/node/docs/user_guide.md | \
    sed s/pangalaxian/gargleblaster/ | \
    sed s/PANGALAXIAN/Gargleblaster/ > doc/gargleblaster_user_guide.md
