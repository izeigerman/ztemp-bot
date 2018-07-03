# ZTemp Bot

## How to install
Python >= 3.4 is required.

1. Install required system packages.
```bash
$ sudo apt-get update
$ sudo apt-get install build-essential python3-dev python3-pip
```
2. Clone the Adafruit Python Sensor Library repo.
```bash
$ git clone https://github.com/adafruit/Adafruit_Python_DHT
$ cd Adafruit_Python_DHT
```
3. Build and install the library.
```bash
$ sudo python3 setup.py install
```
4. Clone the ZTemp Bot repo.
```bash
$ git clone https://github.com/izeigerman/ztemp-bot
$ cd ztemp-bot
```
5. Install the dependencies.
```bash
$ pip3 install -r requirements.txt
```

## How to launch
1. Copy the configuration template and update it with the required values (Telegram token and ID of the trusted chat).
```bash
$ cd ztemp-bot
$ cp ./conf/ztemp_conf.json.template ./conf/ztemp_conf.json
$ vim ./conf/ztemp_conf.json
```
2. Launch the bot.
```bash
$ sudo ./bin/ztemp start
```
