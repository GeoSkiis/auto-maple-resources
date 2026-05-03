"""A collection of all commands that a Night Lord can use to interact with the game."""

from src.common import config, settings, utils
import random
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up

# Cooldowns for SkillRotation (Key attribute name -> sec). 0 = no cooldown (spam).
SKILL_COOLDOWNS = {
    'SHOWDOWN': 0,
    'SHURIKANE': 25,
    'DEATH_STAR': 14,
    'SUDDEN_RAID': 14,
    'ERDA_SHOWER': 40,
    'TRUE_ARACHNID_REFLECTION': 250,
    'DARK_LORDS_OMEN': 60,
    'DARK_FLARE': 60,
    'THROW_BLASTING': 120,
    'BLEED_DART': 90,
    'EPIC_ADVENTURE': 120,
}


def skill_rotation_main_attack(main_key: str, duration: float) -> None:
    """
    Night Lord cannot move while holding Showdown (ctrl). Chain Shadow Leap + double jump
    in a direction and tap the main attack during airtime only.
    """
    direction = random.choice(('left', 'right'))
    end = time.time() + duration
    while config.enabled and time.time() < end:
        key_down(direction)
        time.sleep(0.04)
        press(Key.SHADOW_LEAP, 1, down_time=0.06, up_time=0.08)
        time.sleep(0.06)
        press(Key.JUMP, 1, down_time=0.05, up_time=0.08)
        for _ in range(random.randint(2, 4)):
            press(main_key, 1, down_time=0.04, up_time=0.05)
        press(Key.JUMP, 1, down_time=0.05, up_time=0.08)
        for _ in range(random.randint(2, 3)):
            press(main_key, 1, down_time=0.04, up_time=0.05)
        key_up(direction)
        if config.stage_fright and utils.bernoulli(0.5):
            time.sleep(utils.rand_float(0.05, 0.15))
        time.sleep(0.08)
    time.sleep(0.03)


class Key:
    JUMP = 'space'
    ROPE_LIFT = 'c'
    PICK_UP = 'z'
    # Mobility: chains with double jump for horizontal distance
    SHADOW_LEAP = 'x'

    DECENT_SHARP_EYES = 'f1'
    DECENT_HYPER_BODY = 'f2'
    DECENT_COMBAT_ORDERS = 'f3'
    DECENT_HOLY_SYMBOL = 'f4'

    SHOWDOWN = 'ctrl'
    SHURIKANE = '1'
    DEATH_STAR = '2'
    SUDDEN_RAID = '3'
    ERDA_SHOWER = '4'
    TRUE_ARACHNID_REFLECTION = '5'
    ORIGIN = '7'
    ASCENT = '8'

    DARK_LORDS_OMEN = 'e'
    DARK_FLARE = 'r'
    THROW_BLASTING = 't'

    SHADOW_PARTNER = '='
    LAST_RESORT = '-'
    BLEED_DART = '0'
    EPIC_ADVENTURE = 'home'


#########################
#       Commands        #
#########################


def step(direction, target):
    """
    Horizontal: Shadow Leap + double jump toward target with Showdown taps (not held).
    Up: rope lift. Down: same pattern as other thieves (jump / drop jump).
    """
    if direction == 'up':
        press(Key.ROPE_LIFT, 1)
        d_y = target[1] - config.player_pos[1]
        time.sleep(3.0 if abs(d_y) > 0.08 else 1.5)
        return
    if direction in ('left', 'right'):
        if config.stage_fright and utils.bernoulli(0.75):
            time.sleep(utils.rand_float(0.1, 0.3))
        key_down(direction)
        time.sleep(0.05)
        press(Key.SHADOW_LEAP, 1, down_time=0.06, up_time=0.08)
        time.sleep(0.07)
        press(Key.JUMP, 1, down_time=0.05, up_time=0.08)
        press(Key.SHOWDOWN, 2, down_time=0.04, up_time=0.05)
        press(Key.JUMP, 1, down_time=0.05, up_time=0.08)
        press(Key.SHOWDOWN, 2, down_time=0.04, up_time=0.05)
        key_up(direction)
        time.sleep(0.12)
        return
    num_presses = 2
    if direction == 'down':
        num_presses = 1
    if config.stage_fright and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if abs(d_y) > settings.move_tolerance * 1.5 and direction == 'down':
        press(Key.JUMP, 3)
    press(Key.JUMP, num_presses)


class Adjust(Command):
    """Fine-tunes position: walk horizontal (no held Showdown); rope / down-jump vertically."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        xy_threshold = settings.adjust_tolerance / math.sqrt(2)
        y_threshold = settings.adjust_tolerance
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                if abs(d_x) > xy_threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        press(Key.JUMP, 1, down_time=0.05, up_time=0.05)
                        while config.enabled and d_x < -1 * xy_threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        press(Key.JUMP, 1, down_time=0.05, up_time=0.05)
                        while config.enabled and d_x > xy_threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > y_threshold:
                    if d_y < 0:
                        FlashJump('up').main()
                    else:
                        key_down('down')
                        time.sleep(0.05)
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        time.sleep(0.05)
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class FlashJump(Command):
    """Shadow Leap + double jump horizontally; rope lift for up."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        if self.direction == 'up':
            press(Key.ROPE_LIFT, 1)
            time.sleep(1.5)
            return
        key_down(self.direction)
        time.sleep(0.1)
        press(Key.SHADOW_LEAP, 1, down_time=0.06, up_time=0.1)
        time.sleep(0.08)
        press(Key.JUMP, 2)
        key_up(self.direction)
        time.sleep(0.5)


class Buff(Command):
    """Decent skills (3 min), Shadow Partner (200 s), Last Resort (60 s)."""

    def __init__(self):
        super().__init__(locals())
        self.decent_buff_time = 0
        self.shadow_partner_time = 0
        self.last_resort_time = 0

    def main(self):
        decent_buffs = [
            Key.DECENT_SHARP_EYES,
            Key.DECENT_HYPER_BODY,
            Key.DECENT_COMBAT_ORDERS,
            Key.DECENT_HOLY_SYMBOL,
        ]
        DECENT_CD = 180
        now = time.time()

        if self.decent_buff_time == 0 or now - self.decent_buff_time > DECENT_CD:
            for key in decent_buffs:
                press(key, 3, up_time=0.3)
            self.decent_buff_time = now
        if self.shadow_partner_time == 0 or now - self.shadow_partner_time > 200:
            press(Key.SHADOW_PARTNER, 2)
            self.shadow_partner_time = now
        if self.last_resort_time == 0 or now - self.last_resort_time > 60:
            press(Key.LAST_RESORT, 2)
            self.last_resort_time = now


class Showdown(Command):
    """Primary attack: tap Showdown during Shadow Leap + double jump (not while walking)."""

    def __init__(self, direction, attacks=2, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(0.05)
        if config.stage_fright and utils.bernoulli(0.7):
            time.sleep(utils.rand_float(0.1, 0.3))
        for _ in range(self.repetitions):
            key_down(self.direction)
            time.sleep(0.05)
            press(Key.SHADOW_LEAP, 1, down_time=0.06, up_time=0.08)
            time.sleep(0.06)
            press(Key.JUMP, 1, down_time=0.05, up_time=0.08)
            for __ in range(max(1, self.attacks)):
                press(Key.SHOWDOWN, 1, down_time=0.04, up_time=0.05)
            press(Key.JUMP, 1, down_time=0.05, up_time=0.08)
            for __ in range(max(1, self.attacks)):
                press(Key.SHOWDOWN, 1, down_time=0.04, up_time=0.05)
            key_up(self.direction)
            time.sleep(0.15)


class Shurrikane(Command):
    def main(self):
        press(Key.SHURIKANE, 3)


class DeathStar(Command):
    def main(self):
        press(Key.DEATH_STAR, 3)


class SuddenRaid(Command):
    def main(self):
        press(Key.SUDDEN_RAID, 3)


class ErdaShower(Command):
    def __init__(self, direction, jump='False'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.direction == 'up':
            press(Key.ROPE_LIFT, 1)
            time.sleep(1.5)
            if settings.record_layout:
                config.layout.add(*config.player_pos)
            return
        num_presses = 3
        time.sleep(0.05)
        if self.direction == 'down':
            num_presses = 2
        key_down(self.direction)
        time.sleep(0.05)
        if self.jump:
            if self.direction == 'down':
                press(Key.JUMP, 3, down_time=0.1)
            else:
                press(Key.JUMP, 1)
        press(Key.ERDA_SHOWER, num_presses)
        key_up(self.direction)
        if settings.record_layout:
            config.layout.add(*config.player_pos)


class TrueArachnidReflection(Command):
    def main(self):
        press(Key.TRUE_ARACHNID_REFLECTION, 3)


class Arachnid(TrueArachnidReflection):
    """Alias for routines that use the short name (same as Shadower/Adele CSV style)."""


class DarkLordsOmen(Command):
    def main(self):
        press(Key.DARK_LORDS_OMEN, 3)


class DarkFlare(Command):
    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1, up_time=0.05)
            else:
                press('right', 1, down_time=0.1, up_time=0.05)
        press(Key.DARK_FLARE, 3)


class ThrowBlasting(Command):
    def main(self):
        press(Key.THROW_BLASTING, 3)


class BleedDart(Command):
    def main(self):
        press(Key.BLEED_DART, 3)


class EpicAdventure(Command):
    def main(self):
        press(Key.EPIC_ADVENTURE, 3)


class ShadowLeap(Command):
    """Shadow Leap in a horizontal direction (optional jump first). Chains with JUMP in routines."""

    def __init__(self, direction, jump='True'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        key_down(self.direction)
        time.sleep(0.05)
        if self.jump:
            press(Key.JUMP, 1, down_time=0.05, up_time=0.06)
        press(Key.SHADOW_LEAP, 1, down_time=0.08, up_time=0.1)
        key_up(self.direction)
        time.sleep(0.12)


class Origin(Command):
    def main(self):
        press(Key.ORIGIN, 3)


class Ascent(Command):
    def main(self):
        press(Key.ASCENT, 3)
