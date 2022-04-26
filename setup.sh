## works only on Unix-family operations systems
## first install pyenv

pyenv install 3.9.5
pyenv local 3.9.5

## you can change this path as you wish, it's the default one for Linux
INSTALL_PATH="$HOME/.local/share/virtualenvs/mda-project"

python -m venv $INSTALL_PATH
source $INSTALL_PATH/bin/activate

activate_command="source $INSTALL_PATH/bin/activate"
echo "mda_project_activate() {
    source $INSTALL_PATH/bin/activate
}
export -f mda_project_activate" >> $HOME/.bashrc

## you need to reboot in order to make this "alias" working
## then, type "mda_project_activate" in shell in order to activate suitable venv
## type "deactivate" to deactivate (going back to pyenv global env)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
