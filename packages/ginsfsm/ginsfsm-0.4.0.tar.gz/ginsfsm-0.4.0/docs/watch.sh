# watch the sources and build automatically the doc when they change
# Dependencies: watchdog

make html
watchmedo shell-command \
    --patterns="*.py;*.rst" \
    --recursive \
    --command='make html' \
    . ../ginsfsm
