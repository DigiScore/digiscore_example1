import midi_data
from random import random, choice, seed
from time import sleep

from random import choice
from audio import Listener

from neoscore.core import neoscore
from neoscore.core.rich_text import RichText
from neoscore.core.text import Text
from neoscore.core.units import ZERO, Mm
from neoscore.western.staff import Staff
from neoscore.western.chordrest import Chordrest
from neoscore.western.clef import Clef
from neoscore.western.duration import Duration
from neoscore.western.barline import Barline
from neoscore.western.pedal_line import PedalLine


class Main:
    def __init__(self, source_midi):
        # start brainbit reading
        self.ear = Listener()
        self.ear.start()

        # get all midi note lists for s a t b
        self.midilist = midi_data.get_midi_lists(source_midi)

        # start neoscore
        neoscore.setup()

        # build digital score UI
        self.make_UI()
        self.beat = 1

        # build first bar
        self.audiodata = self.ear.read()
        self.beat_size = 20
        self.build_bar(1)
        self.build_bar(2)

    def build_bar(self, bar):
        if bar == 1:
            start_pos = Mm(10)
            self.notes_on_staff_list_1 = []

        else:
            start_pos = Mm(100)
            self.notes_on_staff_list_2 = []

        note_duration_sum = 0
        breakflag = False

        while note_duration_sum < 80:
            # position in bar
            pos_x = Mm(note_duration_sum) + start_pos

            # # 70% chance of note or rest
            # if random() >= 0.3:

            # get a random note from original source list,
            name, pitches, raw_duration = self.get_note()[0:3]

            # double length of original duration
            raw_duration *= 2

            # calculate duration
            if isinstance(raw_duration, float):
                raw_duration, neoduration = self.calc_duration(raw_duration)
            else:
                raw_duration, neoduration = self.calc_duration(1)
            length = raw_duration * self.beat_size

            # print note on neoscore unless over bar limit
            if note_duration_sum + length > 80:
                # what is remaining?
                raw_rest_gap = (80 - note_duration_sum) / 20
                raw_duration, neoduration = self.calc_duration(raw_rest_gap)
                pitches = []
                breakflag = True

            # add the note/rest to the score and to the note list
            n = Chordrest(pos_x, self.staff, pitches, neoduration)
            if bar == 1:
                self.notes_on_staff_list_1.append(n)
            else:
                self.notes_on_staff_list_2.append(n)

            # if end of bar length: break
            if breakflag:
                break
            else:
                note_duration_sum += length

    def calc_duration(self, raw_duration):
        if raw_duration < 0.25:
            neo_duration = (1, 16)
        elif raw_duration == 0.25:
            neo_duration = (1, 16)
        elif raw_duration == 0.5:
            neo_duration = (1, 8)
        elif raw_duration == 0.75:
            neo_duration = (3, 8)
        elif raw_duration == 1:
            neo_duration = (1, 4)
        elif raw_duration == 1.5:
            neo_duration = (3, 4)
        elif raw_duration == 2:
            neo_duration = (1, 2)

        else:
            neo_duration = (1, 4)
            raw_duration = 1

        return raw_duration, Duration(neo_duration[0], neo_duration[1])

    def get_note(self) -> list:
        # chance of live note or from midilist
        if random() > 0.36:
            new_note = choice(self.midilist)
            print("MIDI", new_note)

        else:
            new_note = self.ear.read()
            print("EAR", new_note)
        return new_note

    def make_UI(self):
        annotation = """
        DEMO digital score BLAH BLAH

        """
        # add text at top
        RichText((Mm(1), Mm(1)), None, annotation, width=Mm(170))

        # make 4 2 bar staves
        self.staff = Staff((ZERO, Mm(70)), None, Mm(180))


        # add barlines
        Barline(Mm(90), [self.staff])
        Barline(Mm(180), [self.staff])

        # add clefs
        Clef(ZERO, self.staff, "treble")

        # mark conductor points
        bar1_origin = Mm(10)
        self.conductor_1_1 = Text((bar1_origin, Mm(50)), None, "1")
        self.conductor_1_2 = Text((bar1_origin + Mm(40), Mm(50)), None, "2")
        self.conductor_2_1 = Text((bar1_origin + Mm(90), Mm(50)), None, "3")
        self.conductor_2_2 = Text((bar1_origin + Mm(130), Mm(50)), None, "4")
        self.conductor_list = [self.conductor_1_1,
                               self.conductor_1_2,
                               self.conductor_2_1,
                               self.conductor_2_2
                               ]

        self.bar_indicator = PedalLine(
            (Mm(0), Mm(20)),
            self.staff,
            Mm(90),
            half_lift_positions=[Mm(45)]
        )

    def change_beat(self, beat):
        if beat > 4:
            beat -= 4
        # flatten all scales
        for b in self.conductor_list:
            b.scale = 1
        # boost the beat
        self.conductor_list[beat-1].scale = 3

    def refresh_func(self, time):
        # calc which beat and change score
        now_beat = (int(time) % 8) + 1  # 8 beats = 2 bars
        if now_beat != self.beat:
            self.change_beat(now_beat)
            self.beat = now_beat
        if now_beat == 1:
            self.bar_indicator.pos = (Mm(0), Mm(20))
            for n in self.notes_on_staff_list_2:
                n.remove()
            self.build_bar(2)
        elif now_beat == 5:
            self.bar_indicator.pos = (Mm(90), Mm(20))
            for n in self.notes_on_staff_list_1:
                n.remove()
            self.build_bar(1)


if __name__ == "__main__":
    run = Main("A Sleepin' Bee.mid")
    neoscore.show(run.refresh_func,
                  display_page_geometry=False)
