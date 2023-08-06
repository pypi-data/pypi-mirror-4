def install(node):
    cmds = """
    pip install virtualenvwrapper --user
    source $HOME/.local/bin/virtualenvwrapper.sh
    echo "source $HOME/.local/bin/virtualenvwrapper.sh" >> ~/bash.rc
    mkvirtualenv cosmos
    echo PATH=/home/erik/projects/Cosmos/bin:$PATH >> $HOME/.virtualenvs/cosmos/bin/postactiveF
    pip install distribute --upgrade
    cd /home/erik/projects/Cosmos
    pip install ./
    """