"""Support for SHARP TV running """
from datetime import timedelta
import logging

from requests import RequestException
import voluptuous as vol

from homeassistant import util
from homeassistant.components.media_player import MediaPlayerDevice, PLATFORM_SCHEMA
from homeassistant.components.media_player.const import (
    SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE,
    SUPPORT_PLAY,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_STEP,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    STATE_ON,
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "SHARP TV Remote"
DEFAULT_PORT = 9688

SUPPORT_SHARPTV = (
    SUPPORT_PAUSE
    | SUPPORT_VOLUME_STEP
    | SUPPORT_VOLUME_MUTE
    | SUPPORT_PREVIOUS_TRACK
    | SUPPORT_NEXT_TRACK
    | SUPPORT_TURN_OFF
    | SUPPORT_TURN_ON
    | SUPPORT_PLAY
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
		vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the LG TV platform."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    port = config.get(CONF_PORT)

    add_entities([SharpTVDevice(host, port, name)], True)


class SharpTVDevice(MediaPlayerDevice):
    """Representation of a LG TV."""

    def __init__(self, host, port, name):
        """Initialize the LG TV device."""
        self._host = host
        self._port = port
        self._name = name
        self._muted = False
        # Assume that the TV is in Play mode
        self._playing = True
        self._volume = 0
        self._state = None

    def send_command(self, command):
        """Send remote control commands to the TV."""
        import socket
        import time
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((self._host,self._port))
            s.send(command.encode('utf-8'))
            s.close()
            self._state = STATE_ON
        except socket.error as err:
            self._state = STATE_OFF

    def update(self):
        self.send_command('test')

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume / 100.0

    
    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_SHARPTV

    def turn_on(self):
        """Wake the TV back up from sleep."""
        if self._state is not STATE_ON:
            if self.hass.services.has_service('hdmi_cec','power_on'):
                self.hass.services.call('hdmi_cec','power_on')
            else:
                _LOGGER.warning("hdmi_cec.power_on not exist!")

    def turn_off(self):
        """Turn off media player."""
        self.send_command('SPRC#DIRK#19#1#2#1|22#')

    def volume_up(self):
        """Volume up the media player."""
        self.send_command('SPRC#DIRK#19#1#2#1|20#')

    def volume_down(self):
        """Volume down media player."""
        self.send_command('SPRC#DIRK#19#1#2#1|21#')

    def mute_volume(self, mute):
        """Send mute command."""
        self.send_command('SPRC#DIRK#19#1#2#1|23#')

    def media_play_pause(self):
        """Simulate play pause media player."""
        if self._playing:
            self.media_pause()
        else:
            self.media_play()

    def media_play(self):
        """Send play command."""
        self._playing = True
        self._state = STATE_PLAYING
        self.send_command('SPRC#DIRK#19#1#2#1|36#')

    def media_pause(self):
        """Send media pause command to media player."""
        self._playing = False
        self._state = STATE_PAUSED
        self.send_command('SPRC#DIRK#19#1#2#1|36#')

    def media_next_track(self):
        """Send next track command."""
        self.send_command('SPRC#DIRK#19#1#2#1|246#')

    def media_previous_track(self):
        """Send the previous track command."""
        self.send_command('SPRC#DIRK#19#1#2#1|245#')
