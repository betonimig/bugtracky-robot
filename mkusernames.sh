#!/usr/bin/env bash

EXPN=/usr/local/symlinks/expn
JS=js/usernames.js

if [[ "$1x" == "x" ]]; then
        echo "Usage: $0 <mailing-list>"
        exit 1
fi

if [[ ! -a $EXPN ]]; then
        echo "expn not found at $EXPN"
        exit 1
fi

echo "var usernames = [" > $JS
$EXPN -s $1 | sed s/.*/\"\&\",/ >> $JS
echo "\"\"]" >> $JS
