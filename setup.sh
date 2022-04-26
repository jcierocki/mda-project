pyenv install 3.9.5
pyenv local 3.9.5

INSTALL_PATH="$HOME/.local/share/virtualenvs/mda-project"

python -m venv $INSTALL_PATH
source $INSTALL_PATH/bin/activate

activate_command="source $INSTALL_PATH/bin/activate"
echo "mda_project_activate() {
    source $INSTALL_PATH/bin/activate
}
export -f mda_project_activate" >> $HOME/.bashrc

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
