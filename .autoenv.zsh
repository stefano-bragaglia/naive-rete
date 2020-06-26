if [[ $autoenv_event == 'enter' ]]; then
    if [[ -a .env/bin/activate ]]; then
        source .env/bin/activate
    elif [[ -a .venv/bin/activate ]]; then
        source .venv/bin/activate
    fi
elif [[ $autoenv_event == 'leave' ]]; then
    if type deactivate > /dev/null; then
        deactivate
    fi
else
    autoenv_source_parent ../..
fi
