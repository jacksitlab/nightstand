# Nightstand

A python project for Raspberry Pi to control some audio files for falling asleep in combination with BTAudio setup to connect bluetooth speakers like JBL Flip 4. Therefore I installed a NeoTrellis Keypad with RGB lightning into a Ikea Kallax 1x1 and connected it via I2C to the Raspberry Pi.

For audio playback vlc-player will be used and remote controlled with python.

## Installation

  * just run ```preinstall.sh``` to get everything needed installed.
  * run ```sudo raspi-config``` to enable I2C interface for the NeoTrellis board
  * pair and connect your BT speaker once with bluetoothctl. Should autoconnect once started again

## Pairing BT device

run bluetoothctl (without sudo)
```
[bluetooth]# agent on
```
if you get an error message like there is no controller found or sth. equal you have to solve this first.

```
[bluetooth]# pairable on
[bluetooth]# scan on
CHG] Controller 00:1A:7D:DA:71:13 Discovering: yes
[NEW] Device 70:10:00:1A:92:20 70-10-00-1A-92-20
[NEW] Device 73:0C:0F:CF:F3:BE 73-0C-0F-CF-F3-BE
[CHG] Device 70:10:00:1A:92:20 LegacyPairing: no
[CHG] Device 70:10:00:1A:92:20 Name: Bluetooth 3.0 Keyboard
[CHG] Device 70:10:00:1A:92:20 Alias: Bluetooth 3.0 Keyboard
[CHG] Device 70:10:00:1A:92:20 LegacyPairing: yes
[NEW] Device 00:42:79:A7:6F:CE 00-42-79-A7-6F-CE
[CHG] Device 00:42:79:A7:6F:CE Name: JBL Flip 4
[bluetooth]# scan off
[bluetooth]# pair 00:42:79:A7:6F:CE
...
Pairing successful
[bluetooth]# trust 00:42:79:A7:6F:CE
Changing 00:42:79:A7:6F:CE trust succeeded
[bluetooth]# connect 00:42:79:A7:6F:CE
Attempting to connect to 00:42:79:A7:6F:CE
Connection successful
```


## Configuration

The config file ```config.json``` contains:

  * ```keys```: KeyConfigs with color definitions and connected mediaId (ref for media section)
  * ```media```: Key-Value-Pairs of media files, urls or even playlists
  * ```sleep```: settings for sleep mode

KeyConfig:

```
{
    "color":"#AA0000",
    "pressed":"#FF0000",
    "media":"",
    "player":"PLAY|STOP|PREV|NEXT|VOL+|VOL-"
}
```

## Dev Environment

To test it just run it in foreground with ```python3 nightstand.py --foreground```


## Planned features

  * REST-API to write configuration
  * SMB mount feature to support local NAS
  * 

## License

APACHE 2.0 License