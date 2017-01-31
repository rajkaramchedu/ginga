#
# Blink.py -- Blink plugin for Ginga reference viewer
#
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from ginga import GingaPlugin
from ginga.gw import Widgets

class Blink(GingaPlugin.LocalPlugin):
    """
    Blink switches through the images shown in a channel at a rate
    chosen by the user.  Alternatively, it can switch between channels
    in the main workspace.  In both cases, the primary purpose is to
    compare and contrast the images (within a channel, or across
    channels) visually within a short timescale--like blinking your
    eyes.

    NOTE: Blink can be invoked either as a local plugin, in which case
    it cycles through the images in the channel, or as a global
    plugin, in which case it cycles through the channels.

    Local plugins are started from the "Operations" button, while
    global plugins are started from the "Plugins" menu.

    Usage
    -----
    Set the interval between image changes in terms of seconds in
    the box labeled "Interval".  Finally, press "Start Blink" to start
    the timed cycling, and "Stop Blink" to stop the cycling.

    You can change the number in "Interval" and press Enter to
    dynamically change the cycle time while the cycle is running.
    """
    def __init__(self, *args):
        # superclass defines some variables for us, like logger
        if len(args) == 2:
            super(Blink, self).__init__(*args)
        else:
            super(Blink, self).__init__(args[0], None)

        self.interval = 1.0
        self.blink_timer = self.fv.get_timer()
        self.blink_timer.set_callback('expired', self._blink_timer_cb)

        prefs = self.fv.get_preferences()
        self.settings = prefs.createCategory('plugin_Blink')
        self.settings.add_defaults(interval_max=30.0, interval_min=0.25)
        self.settings.load(onError='silent')

        # TODO: need to deprecate the blink_channels setting
        # the mode is now determined by whether the plugin is loaded
        # as a local or global
        self.blink_channels = (self.fitsimage is None)

        self.ival_min = self.settings.get('interval_min', 0.25)
        self.ival_max = self.settings.get('interval_max', 30.0)

    def build_gui(self, container):
        top = Widgets.VBox()
        top.set_border_width(4)

        vbox, sw, orientation = Widgets.get_oriented_box(container)
        vbox.set_border_width(4)
        vbox.set_spacing(2)

        fr = Widgets.Frame("Blink")
        vbox2 = Widgets.VBox()

        captions = (("Interval:", 'label', 'Interval', 'entry',
                     "Start Blink", 'button', "Stop Blink", 'button'),
                    ("Max:", 'label', 'max', 'llabel',
                     "Min:", 'label', 'min', 'llabel'),
                    ("Mode:", 'label', 'mode', 'llabel'),
                    )
        w, b = Widgets.build_info(captions, orientation=orientation)
        self.w = b

        b.interval.set_text(str(self.interval))
        b.interval.add_callback('activated', lambda w: self._set_interval_cb())
        b.interval.set_tooltip("Interval in seconds between changing images")

        b.start_blink.add_callback('activated',
                                   lambda w: self._start_blink_cb())
        b.stop_blink.add_callback('activated',
                                  lambda w: self._stop_blink_cb())

        b.min.set_text(str(self.ival_min))
        b.max.set_text(str(self.ival_max))

        mode = 'blink channels'
        if not self.blink_channels:
            mode = 'blink images in channel'
        b.mode.set_text(mode)

        vbox2.add_widget(w, stretch=0)

        fr.set_widget(vbox2)
        vbox.add_widget(fr, stretch=0)

        spacer = Widgets.Label('')
        vbox.add_widget(spacer, stretch=1)

        top.add_widget(sw, stretch=1)

        btns = Widgets.HBox()
        btns.set_spacing(3)

        btn = Widgets.Button("Close")
        btn.add_callback('activated', lambda w: self.close())
        btns.add_widget(btn, stretch=0)
        btn = Widgets.Button("Help")
        btn.add_callback('activated', lambda w: self.help())
        btns.add_widget(btn, stretch=0)
        btns.add_widget(Widgets.Label(''), stretch=1)
        top.add_widget(btns, stretch=0)

        container.add_widget(top, stretch=1)

    def help(self):
        name = str(self).capitalize()
        self.fv.show_help_text(name, self.__doc__)

    def close(self):
        if self.fitsimage is None:
            self.fv.stop_global_plugin(str(self))
        else:
            self.fv.stop_local_plugin(self.chname, str(self))
        return True

    def start(self):
        self.resume()

    def pause(self):
        self.stop_blinking()

    def resume(self):
        self.start_blinking()

    def stop(self):
        self.stop_blinking()

    def redo(self):
        pass

    def _blink_timer_cb(self, timer):
        # set timer
        if self.blink_channels:
            self.fv.gui_do(self.fv.next_channel)
        else:
            self.fv.gui_do(self.fv.next_img, loop=True)

        timer.set(self.interval)

    def start_blinking(self):
        self.blink_timer.set(self.interval)

    def stop_blinking(self):
        self.blink_timer.clear()

    def _start_blink_cb(self):
        self._set_interval_cb()
        self.start_blinking()

    def _stop_blink_cb(self):
        self.stop_blinking()

    def _set_interval_cb(self):
        interval = float(self.w.interval.get_text())
        self.interval = max(min(interval, self.ival_max), self.ival_min)
        self.stop_blinking()
        self.start_blinking()

    def _set_blink_mode_cb(self, tf):
        self.blink_channels = tf

    def __str__(self):
        return 'blink'

#END
