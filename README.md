# Pyorick

uHandPi exploration to power Yorick using the built-in tools to some degree



## Raspberry Pi

```bash
sudo apt install libdbus-1-dev libglib2.0-dev python3-gi bluetooth bluez
```

```bash
sudo apt install python3.11-venv
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements
pip install -e ../uhandpi/common_sdk
```