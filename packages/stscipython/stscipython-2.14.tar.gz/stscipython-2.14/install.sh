args="$*"

new_install/stp_list | python cfgdep.py -i -order | new_install/stp_install $args

