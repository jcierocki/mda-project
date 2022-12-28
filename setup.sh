### works only on Unix-family operating systems

### install development packages required to build Python

## debian family inc. Ubuntu, Mint, PopOS
# sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev curl

## redhat family inc. Fedora
# sudo dnf groupinstall development

### install pyenv (google it)

pyenv install 3.9.5
pyenv local 3.9.5

### you can change this path as you wish, it's the default one for Linux
INSTALL_PATH="$HOME/.local/share/virtualenvs/mda-project"

python -m venv $INSTALL_PATH
source $INSTALL_PATH/bin/activate

if ! grep -q "mda_project_activate()"  ~/.bashrc; then
    echo "
        mda_project_activate() {
            source $INSTALL_PATH/bin/activate
        }
        export -f mda_project_activate
        " >> $HOME/.bashrc
fi

### you need to reboot in order to make this "alias" working
### then, type "mda_project_activate" in shell in order to activate suitable venv
### type "deactivate" to deactivate (going back to pyenv global env)

python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
python -m pip install -r requirements.txt

