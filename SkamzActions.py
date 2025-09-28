# self.canonical_parent.show_message(msg)

from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

class SkamzActions(UserActionsBase):
    def create_actions(self):
        self.add_global_action("skamz_stop_or_reset", self.stop_or_reset)
        self.add_global_action("skamz_load_def", self.load_device_definition)
        self.add_global_action("skamz_play", self.play)
        self.add_global_action("skamz_send_macro", self.send_macro)

        self.add_global_action("exarm", self.exarm)
        self.add_global_action("exarmin", self.exarmin)
        self.add_global_action("armin", self.armin)

        self.add_global_action("noin", self.noin)
        self.add_global_action("exin", self.exin)

        self.add_global_action("looprec", self.looprec)
        self.add_global_action("looprecin", self.looprecin)
        self.add_global_action("listen", self.listen)

        self.add_global_action("resetstate", self.resetstate)
        self.add_global_action("showstate", self.showstate)

        self.add_global_action("exsolo", self.exsolo)
        self.add_global_action("tweak_knobs", self.tweak_knobs)
        self.add_global_action("go_to_start_and_stop", self.go_to_start_and_stop)

    def _run_cmd(self, cmd):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(cmd)

    def go_to_start_and_stop(self, action_def, args):
        cmd = "SETPLAY ON; RESTART; SETPLAY OFF;"
        self._run_cmd(cmd)

    def tweak_knobs(self, action_def, args):
        instrument_name = "Skamz MultiMap"
        matching_tracks = []

        for track in self.song().tracks:
            for device in track.devices:
                if device.name == instrument_name:
                    matching_tracks.append(track.name)
                    for parameter in device.parameters:
                        if parameter.is_enabled and parameter.name not in ["Device On", "Chain Selector"]:
                            parameter.value = parameter.value + 0.1

    # Exclusive solo. Usage: exsolo "TRACK-NAME"
    # Note that the track name cannot have spaces.
    def exsolo(self, action_def, args):
        cmd = f"ALL/SOLO OFF; {args}/SOLO ON;"
        self._run_cmd(cmd)

    # Tracks prefixed with "IN_" will be set to monitor in
    def retain_input_tracks(self):
        cmd = ""
        for track in self.song().tracks:
            if track.name.startswith("IN_") or track.name.startswith("REC_IN_"):
                cmd += f"\"{track.name}\"/MON IN;"
        self.canonical_parent.show_message(cmd)
        self._run_cmd(cmd)

    def retain_rec_tracks(self):
        cmd = ""
        for track in self.song().tracks:
            if track.name.startswith("REC_"):
                cmd += f"\"{track.name}\"/ARM ON;"
        self.canonical_parent.show_message(cmd)
        self._run_cmd(cmd)


    def showstate(self, action_def, args):
        self.canonical_parent.show_message("looprec={}; looprecin={}".format(
            getattr(self, "_looprec", False),
            getattr(self, "_looprecin", False)
        ))

    def resetstate(self, action_def, args):
        self._looprec = False
        self._looprecin = False
        self._listen = False
        self.canonical_parent.show_message("reset state")

    # listen = "listen mode"
    # nothing will be recorded and monitoring will be set to auto
    def listen(self, action_def, args):
        val = (args or "true").split()[0]
        self._listen = val == "true"
        if self._listen:
            self._looprecin = False
            self._looprec = False
            cmd = f"ALL/ARM OFF; ALL/MON AUTO;"
            self._run_cmd(cmd)
        self.canonical_parent.show_message("listen set to {}".format(getattr(self, "_listen", False)))
        self.retain_input_tracks()
        self.retain_rec_tracks()

    # looprec = "loop record"
    # This alters the behavior or "exarm" and "exarmin" to be no-ops
    # This is to allow loopback recording despite existing automation
    # No inputs will be received except loopback in this mode.
    # Loopback is assumed to be on a track named LOOPBACK
    def looprec(self, action_def, args):
        val = (args or "true").split()[0]
        self._looprec = val == "true"
        if self._looprec:
            self._looprecin = False
            self._listen = False
            cmd = f"ALL/ARM OFF; ALL/MON AUTO; \"LOOPBACK\"/ARM ON;"
        else:
            cmd = f"ALL / MON AUTO; ALL/ARM OFF;"
        self._run_cmd(cmd)
        self.canonical_parent.show_message("looprec set to {}".format(getattr(self, "_looprec", False)))

    # looprec = "loop record in"
    # This alters the behavior or "exarm" to be a no-op and "exarmin" to NOT arm the track
    # This is to allow loopback recording despite existing automation
    # Multiple inputs can be received in this mode, but they won't be recorded except for in loopback.
    # Loopback is assumed to be on a track named LOOPBACK
    def looprecin(self, action_def, args):
        val = (args or "true").split()[0]
        self._looprecin = val == "true"
        if self._looprecin:
            self._looprec = False
            self._listen = False
            cmd = f"ALL/ARM OFF; ALL / MON AUTO; \"LOOPBACK\"/ARM ON;"
        else:
            cmd = f"ALL / MON AUTO; ALL/ARM OFF;"
        self._run_cmd(cmd)
        self.canonical_parent.show_message("looprecin set to {}".format(getattr(self, "_looprecin", False)))

    # noin = "no inputs"
    # Turns recording off and monitoring to auto on all tracks
    def noin(self, action_def, args):
        if getattr(self, "_looprec", False) or getattr(self, "_looprecin", False):
            self.canonical_parent.show_message("noin modified by state")
            cmd = f"ALL/MON AUTO;"
        else:
            cmd = f"ALL/ARM OFF; ALL/MON AUTO;"
        self._run_cmd(cmd)
        self.retain_input_tracks()
        self.retain_rec_tracks()
    # exarm = "exclusive arm"
    # Turns recording on for the named track, and off for all others.
    def exarm(self, action_def, args):
        if getattr(self, "_looprec", False) or getattr(self, "_looprecin", False) or getattr(self, "_listen", False):
            self.canonical_parent.show_message("exarm disabled by state")
            return

        args = args.split()
        track_name = args[0]
        cmd = f"ALL/ARM OFF; {track_name}/ARM ON;"
        self._run_cmd(cmd)

    # exarmin = "exclusive arm and input"
    # Turns recording on for the named track, and off for all others.
    # Turns monitoring to 'in' for the named track, and 'auto' for all others.
    def exarmin(self, action_def, args):
        args = args.split()
        track_name = args[0]
        if getattr(self, "_looprec", False) or getattr(self, "_listen", False):
            self.canonical_parent.show_message("exarmin disabled by state")
            return
        elif getattr(self, "_looprecin", False):
            self.canonical_parent.show_message("exarmin modified by state")
            cmd = f"ALL/MON AUTO; {track_name}/MON IN;"
        else:
            cmd = f"ALL/ARM OFF; {track_name}/ARM ON; ALL/MON AUTO; {track_name}/MON IN;"
        self._run_cmd(cmd)
        self.retain_input_tracks()
        self.retain_rec_tracks()
    
    def exin(self, action_def, args):
        args = args.split()
        track_name = args[0]
        cmd = f"ALL/MON AUTO; {track_name}/MON IN;"
        self._run_cmd(cmd)
        self.retain_input_tracks()

    # armin = "arm and input"
    # Turns recording on for the named track, and monitoring to 'in'
    def armin(self, action_def, args):
        args = args.split()
        track_name = args[0]
        if getattr(self, "_looprec", False) or getattr(self, "_listen", False):
            self.canonical_parent.show_message("armin disabled by state")
            return
        elif getattr(self, "_looprecin", False):
            self.canonical_parent.show_message("armin modified by state")
            cmd = f"{track_name}/MON IN;"
        else:
            cmd = f"{track_name}/ARM ON; {track_name}/MON IN;"
        self._run_cmd(cmd)
        self.retain_input_tracks()
        self.retain_rec_tracks()

    def send_macro(self, action_def, _):
        live_set = self.song()
        master = live_set.master_track
        device_name = "ClyphX Popup Commands"  # Change this
        param_name = "live.text"  # Change this

        # Find device
        device = next((d for d in master.devices if d.name == device_name), None)
        if device:
            # Find parameter
            param = next((p for p in device.parameters if p.name == param_name), None)
            if param:
                param.value = 1  # Press button
                self.canonical_parent.show_message(f"Triggered: {device_name} -> {param_name}")
            else:
                self.canonical_parent.show_message(f"Parameter '{param_name}' not found!")
        else:
            self.canonical_parent.show_message(f"Device '{device_name}' not found!")

    def play(self, action_def, _):
        if not self._song.is_playing:
            # Counter-intuitively, SETSTOP actually toggles playback.
            self._run_cmd("SETSTOP")

    def stop_or_reset(self, action_def, _):
        if self._song.is_playing:
            self._run_cmd("SETSTOP")
        else:
            self._run_cmd("SETJUMP 1.1.1")

    def load_device_definition(self, action_def, _):
        name = self._song.view.selected_track.view.selected_device.name
        self._run_cmd(f'SWAP "{name}.adg"')