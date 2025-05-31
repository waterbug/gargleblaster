#!/bin/sh
sed s/Pangalaxian/Marvin/g ../pangalactic.node/pangalactic/node/docs/user_guide.md | \
    sed s/pangalaxian/marvin/ | \
    sed s/PANGALAXIAN/Marvin/ > doc/marvin_user_guide.md
