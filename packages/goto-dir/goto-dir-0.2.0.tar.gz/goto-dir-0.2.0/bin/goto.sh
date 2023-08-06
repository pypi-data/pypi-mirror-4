#!/usr/bin/env sh

goto_dir() {
    cd "$@"
}

label() {
    ARGS="$@"
    bootstrap_goto.py label $ARGS
}

goto() {
    ARGS="$@"
    bootstrap_goto.py goto $ARGS > /tmp/goto

    if [ "$?" = "0" ]; then
        DIR=$(head -1 /tmp/goto)

        if [ "$DIR" == "<PATH>" ]; then
            DIR=$(sed -n '2p' /tmp/goto)
            goto_dir "$DIR"
        else
            cat /tmp/goto
        fi

    else
        cat /tmp/goto
    fi

    rm /tmp/goto
}
