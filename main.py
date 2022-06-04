#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication

from asciimatics.scene import Scene
from asciimatics.effects import Print, Effect, Stars
from asciimatics.renderers import Box

from asciimatics.widgets import Frame, Layout, Button, Divider, ListBox, Text
from asciimatics.event import KeyboardEvent

from time import sleep
from game_state import GameState

import os
import sys


class PauseEffect(Effect):

    def __init__(self, screen, **kwargs):
        super(PauseEffect, self).__init__(screen, **kwargs)
        self._is_indicator_active = True
        self._indicator_pos_x = self._prev_indicator_pos_x = screen.width // 2
        self._indicator_pos_y = self._prev_indicator_pos_y = screen.height // 2
        self._indicator_change_speed = 2
        self._frame_counter = 0

    def reset(self):
        pass

    def _update(self, frame_no):
        model.is_running = False
        self._prev_indicator_pos_y = self._indicator_pos_y
        self._prev_indicator_pos_x = self._indicator_pos_x

        self._screen.wait_for_input(0.1)
        event = self._screen.get_event()
        if event and isinstance(event, KeyboardEvent):
            if event.key_code == Screen.KEY_UP:
                self._move_up()
            elif event.key_code == Screen.KEY_DOWN:
                self._move_down()
            elif event.key_code == Screen.KEY_RIGHT:
                self._move_right()
            elif event.key_code == Screen.KEY_LEFT:
                self._move_left()
            elif event.key_code == 112:
                model.is_running = True
                raise NextScene("Play")
            elif event.key_code == 113:
                raise StopApplication("Quit")
            elif event.key_code == 109:
                raise NextScene("MainMenu")
            elif event.key_code == 32:
                self._check_and_set()
            elif event.key_code == 115:
                raise NextScene("SaveMenu")

        self._screen.print_at(
            ' ', self._prev_indicator_pos_x, self._prev_indicator_pos_y)

        if not self._is_indicator_active:
            self._screen.print_at(
                ' ', self._indicator_pos_x, self._indicator_pos_y)

        for pos in model.dead_cells:
            if is_visible(self._screen.height, self._screen.width, pos[0], pos[1]):
                self._screen.print_at(' ', pos[0], pos[1])

        for pos in model.active_cells:
            if is_visible(self._screen.height, self._screen.width, pos[0], pos[1]):
                self._screen.print_at('X', pos[0], pos[1])

        if self._is_indicator_active:
            self._screen.print_at(
                '█', self._indicator_pos_x, self._indicator_pos_y)

        if self._frame_counter == self._indicator_change_speed:
            self._is_indicator_active = not self._is_indicator_active
            self._frame_counter = 0
        else:
            self._frame_counter += 1

        model.update_cells()

    @property
    def stop_frame(self):
        return self._stop_frame

    def _move_right(self):
        if self._indicator_pos_x < self._screen.width - 2:
            self._indicator_pos_x += 1
        else:
            model.active_cells = model.shift_cells(1, 0)

    def _move_left(self):
        if self._indicator_pos_x > 1:
            self._indicator_pos_x -= 1
        else:
            model.active_cells = model.shift_cells(-1, 0)

    def _move_up(self):
        if self._indicator_pos_y > 1:
            self._indicator_pos_y -= 1
        else:
            model.active_cells = model.shift_cells(0, -1)

    def _move_down(self):
        if self._indicator_pos_y < self._screen.height - 3:
            self._indicator_pos_y += 1
        else:
            model.active_cells = model.shift_cells(0, 1)

    def _check_and_set(self):
        indicator_pos = (self._indicator_pos_x, self._indicator_pos_y)
        if indicator_pos in model.active_cells:
            model.active_cells.remove(indicator_pos)
        else:
            model.active_cells.add(indicator_pos)


class BgEffect(Effect):

    def __init__(self, screen, **kwargs):
        super(BgEffect, self).__init__(screen, **kwargs)

    def reset(self):
        pass

    def _update(self, frame_no):
        for pos in model.active_cells:
            if is_visible(self._screen.height, self._screen.width, pos[0], pos[1]):
                self._screen.print_at('X', pos[0], pos[1])

    @property
    def stop_frame(self):
        return self._stop_frame


class PlayEffect(Effect):

    def __init__(self, screen, **kwargs):
        super(PlayEffect, self).__init__(screen, **kwargs)

    def reset(self):
        pass

    def _update(self, frame_no):
        self._screen.wait_for_input(0.1)
        event = self._screen.get_event()
        if event and isinstance(event, KeyboardEvent):
            if event.key_code == Screen.KEY_UP:
                model.active_cells = model.shift_cells(0, -2)
            elif event.key_code == Screen.KEY_DOWN:
                model.active_cells = model.shift_cells(0, 2)
            elif event.key_code == Screen.KEY_RIGHT:
                model.active_cells = model.shift_cells(2, 0)
            elif event.key_code == Screen.KEY_LEFT:
                model.active_cells = model.shift_cells(-2, 0)
            elif event.key_code == 112:
                model.is_running = False
                raise NextScene("Pause")
            elif event.key_code == 113:
                raise StopApplication("Quit")
            elif event.key_code == 109:
                raise NextScene("MainMenu")

        for pos in model.dead_cells:
            if is_visible(self._screen.height, self._screen.width, pos[0], pos[1]):
                self._screen.print_at(' ', pos[0], pos[1])

        for pos in model.active_cells:
            if is_visible(self._screen.height, self._screen.width, pos[0], pos[1]):
                self._screen.print_at('X', pos[0], pos[1])

        model.update_cells()

    @property
    def stop_frame(self):
        return self._stop_frame


class Print_at(Effect):
    def __init__(self, screen, text, x, y, **kwargs):
        super(Print_at, self).__init__(screen, **kwargs)
        self._text = text
        self._x = x
        self._y = y

    def reset(self):
        pass

    def _update(self, frame_no):
        self._screen.print_at(self._text, self._x, self._y)

    @property
    def stop_frame(self):
        return self._stop_frame


class MainMenu(Frame):
    def __init__(self, screen):
        super(MainMenu, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            can_scroll=False,
            title="Conway's Game of Life"
        )

        layout1 = Layout([3], fill_frame=True)
        self.add_layout(layout1)
        layout1.add_widget(
            Divider(draw_line=False, height=screen.height * 2 // 8))
        layout1.add_widget(Button("Start empty", self._on_click_start))
        layout1.add_widget(Button("Select config", self._on_click_config))
        layout1.add_widget(Button("Quit", self._on_click_quit))
        self.fix()

    def _on_click_quit(self):
        raise StopApplication("Quit")

    def _on_click_config(self):
        raise NextScene("SelectConfig")

    def _on_click_start(self):
        global model
        model = GameState(set())
        raise NextScene("Pause")


class SelectConfigMenu(Frame):

    def __init__(self, screen):
        super(SelectConfigMenu, self).__init__(
            screen,
            screen.height // 3,
            screen.width // 3,
            can_scroll=False,
            title="Select available config",
            hover_focus=True
        )
        layout1 = Layout([100], fill_frame=True)
        self.add_layout(layout1)
        self._list_view = self._get_files()
        layout1.add_widget(self._list_view)

        self.fix()

    def _get_files(self):
        files = []
        try:
            for file in os.listdir("./examples"):
                if file.endswith(".life"):
                    files.append(file)
        except Exception:
            pass

        options = []
        for i, file in enumerate(files):
            options.append((file, i + 1))

        options.append(('Return to main menu', len(files) + 1))
        return ListBox(
            len(files) + 1,
            options,
            on_select=self._on_pick,
            add_scroll_bar=True
        )

    def _on_pick(self):
        if self._list_view._value == self._list_view._required_height:
            raise NextScene("MainMenu")
        else:
            cells = self._read_config(
                './examples/' + self._list_view._options[self._list_view._value - 1][0])
            global model
            model = GameState(cells)
            raise NextScene("Pause")

    def _read_config(self, path: str) -> set:
        cells = set()
        with open(path) as f:
            first_line = f.readline()
            for line in f:
                line = line.strip()
                pos = list(map(int, line.split()))
                cells.add((pos[0], pos[1]))
        return cells


class SaveMenu(Frame):
    def __init__(self, screen):
        super(SaveMenu, self).__init__(
            screen,
            screen.height // 3,
            screen.width // 3,
            can_scroll=False,
            title="Save current config",
            hover_focus=True
        )
        self._layout = Layout([2], fill_frame=True)
        self.add_layout(self._layout)

        self._layout.add_widget(Divider(draw_line=False, height=1))
        self._layout.add_widget(Text("Name:", "filename"))

        self._layout.add_widget(Divider(draw_line=False, height=2))
        self._layout.add_widget(Button("OK", self._on_click_ok, add_box=True))
        self._layout.add_widget(
            Button("Cancel", self._on_click_cancel, add_box=True))

        self.fix()

    def _on_click_ok(self):
        filename_widget = self._layout.find_widget("filename")
        if (filename_widget.value == ""):
            pass
        else:
            try:
                with open("./examples/" + filename_widget.value + ".life", "w") as f:
                    f.write("#Life 1.06\n")
                    for cell in model.active_cells:
                        f.write(f'{cell[0]} {cell[1]}\n')
            except Exception:
                pass

        raise NextScene("Pause")

    def _on_click_cancel(self):
        raise NextScene("Pause")


def is_visible(max_height, max_width, x, y):
    return ((x < max_width - 1) and
            (x > 0) and
            (y > 0) and
            (y < max_height - 2))


model = GameState(set())


def gol(screen):

    play_effects = [
        Print(screen,
              Box(screen.width, screen.height - 1, uni=screen.unicode_aware), 0, 0, colour=5),
        Print_at(screen, "Q to quit   P to pause   ARROWS to move   M to main menu",
                 1, screen.height - 1),
        PlayEffect(screen),
    ]

    pause_effects = [
        Print(screen,
              Box(screen.width, screen.height - 1, uni=screen.unicode_aware), 0, 0, colour=3),
        Print_at(screen, "Q to quit   P to start   ARROWS to move   M to main menu   SPACE to add/remove   S to save config", 1, screen.height - 1),
        PauseEffect(screen),
    ]

    scenes = [
        Scene([Stars(screen, (screen.width + screen.height) // 2),
              MainMenu(screen)], -1, name="MainMenu"),
        Scene([Stars(screen, (screen.width + screen.height) // 2),
              SelectConfigMenu(screen)], -1, name="SelectConfig"),
        Scene(play_effects, -1, name="Play"),
        Scene(pause_effects, -1, name="Pause"),
        Scene([BgEffect(screen), SaveMenu(screen)], -1, name="SaveMenu")
    ]

    screen.play(scenes, stop_on_resize=True)


if __name__ == "__main__":
    while True:
        try:
            Screen.wrapper(gol)
            sys.exit(0)
        except ResizeScreenError:
            pass
