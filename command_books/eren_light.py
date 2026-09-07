"""A collection of all commands that Eren Light can use to interact with the game."""

from src.common import config, settings, utils
import random
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up

# Cooldowns for SkillRotation (Key attribute name -> sec). 0 = no cooldown (spam).
# Charge of Fionn is ground-only and omitted from rotation.
SKILL_COOLDOWNS = {
    'ENHANCED_SPEAR_OF_LUGH_3': 0,
    'SENTINEL_RISE': 60,
    'ETERNAL_GUARDIAN': 120,
    'DESTRUCTION_OF_ROAN': 120,
    'STING_OF_ROAN': 10,
    'PATH_OF_FIONN': 60,
    'SHIELD_OF_CHULAINN': 120,
    'SPEAR_OF_LIGHT': 60,
    'ENHANCED_FURY_OF_ROAN': 10,
    'IMPULSE_OF_CHULAINN': 60,
    'ERDA_SHOWER': 60,
    'TRUE_ARACHNID_REFLECTION': 250,
}

# Path of Fionn can be re-cast several times after the first use.
SKILL_PRESS_COUNTS = {
    'PATH_OF_FIONN': 4,
}

# Move() must not inject an extra jump before step(); air-only ctrl attacks need a clean double jump.
SKIP_MOVE_RANDOM_JUMP = True


def _perform_double_jump():
    """Two jump presses in rapid succession while direction is held (must finish before ctrl)."""
    press(Key.JUMP, 1, down_time=0.05, up_time=0.06)
    time.sleep(0.04)
    press(Key.JUMP, 1, down_time=0.05, up_time=0.08)
    time.sleep(0.12)


def _double_jump_then_attack(main_key, attacks=2):
    """Full double jump first, then ctrl taps during the extended airtime."""
    _perform_double_jump()
    for _ in range(max(1, attacks)):
        press(main_key, 1, down_time=0.04, up_time=0.05)


def skill_rotation_main_attack(main_key: str, duration: float) -> None:
    """
    Enhanced Spear of Lugh 3 only works well after a full double jump — never ctrl on the first jump.
    Always finish jump + jump before any ctrl presses.
    """
    direction = random.choice(('left', 'right'))
    end = time.time() + duration
    while config.enabled:
        key_down(direction)
        time.sleep(0.04)
        _perform_double_jump()
        for _ in range(random.randint(3, 5)):
            press(main_key, 1, down_time=0.04, up_time=0.05)
        key_up(direction)
        if config.stage_fright and utils.bernoulli(0.5):
            time.sleep(utils.rand_float(0.05, 0.15))
        time.sleep(0.08)
        if time.time() >= end:
            break
    time.sleep(0.03)


class Key:
    JUMP = 'space'
    ROPE_LIFT = 'c'
    PICK_UP = 'z'

    DECENT_SHARP_EYES = 'f1'
    DECENT_HYPER_BODY = 'f2'
    DECENT_COMBAT_ORDERS = 'f3'
    DECENT_HOLY_SYMBOL = 'f4'

    ENHANCED_SPEAR_OF_LUGH_3 = 'ctrl'
    CHARGE_OF_FIONN = 'shift'

    SENTINEL_RISE = '1'
    ETERNAL_GUARDIAN = '2'
    DESTRUCTION_OF_ROAN = '3'

    ERDA_SHOWER = '4'
    TRUE_ARACHNID_REFLECTION = '5'

    ORIGIN = '7'
    ASCENT = '8'

    STING_OF_ROAN = 'q'
    PATH_OF_FIONN = 'w'
    SHIELD_OF_CHULAINN = 'e'
    SPEAR_OF_LIGHT = 'r'
    ENHANCED_FURY_OF_ROAN = 'a'
    IMPULSE_OF_CHULAINN = 's'

    LIGHT_ENCHANT = '='
    HELIAN_BLESSING = '-'
    PIERCING_OF_CHULAINN = 'home'
    HUNDRED_POLE = 'page up'


#########################
#       Commands        #
#########################


def step(direction, target):
    """
    Horizontal: double jump toward target with Spear taps during airtime (no walking attack).
    Up: rope lift. Down: jump / drop jump.
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
        _double_jump_then_attack(Key.ENHANCED_SPEAR_OF_LUGH_3, attacks=2)
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
    """Fine-tunes position: walk horizontal; rope / down-jump vertically."""

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
    """Double jump horizontally; rope lift for up."""

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
        _perform_double_jump()
        key_up(self.direction)
        time.sleep(0.5)


class Buff(Command):
    """Decent skills (3 min), Light Enchant / Helian Blessing (180 s), Piercing / Hundred Pole (60 s)."""

    def __init__(self):
        super().__init__(locals())
        self.decent_buff_time = 0
        self.cd180_buff_time = 0
        self.cd60_buff_time = 0

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
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 180:
            press(Key.LIGHT_ENCHANT, 2)
            press(Key.HELIAN_BLESSING, 2)
            self.cd180_buff_time = now
        if self.cd60_buff_time == 0 or now - self.cd60_buff_time > 60:
            press(Key.PIERCING_OF_CHULAINN, 2)
            press(Key.HUNDRED_POLE, 2)
            self.cd60_buff_time = now


class EnhancedSpearOfLugh3(Command):
    """Primary attack: double jump + tap Spear during airtime."""

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
            _double_jump_then_attack(Key.ENHANCED_SPEAR_OF_LUGH_3, self.attacks)
            key_up(self.direction)
            time.sleep(0.15)


class ChargeOfFionn(Command):
    """Ground-only charge forward; do not use while jumping."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(0.05)
        press(Key.CHARGE_OF_FIONN, 1, down_time=0.08, up_time=0.1)
        key_up(self.direction)
        time.sleep(0.2)


class SentinelRise(Command):
    def main(self):
        press(Key.SENTINEL_RISE, 3)


class EternalGuardian(Command):
    def main(self):
        press(Key.ETERNAL_GUARDIAN, 3)


class DestructionOfRoan(Command):
    def main(self):
        press(Key.DESTRUCTION_OF_ROAN, 3)


class StingOfRoan(Command):
    def main(self):
        press(Key.STING_OF_ROAN, 3)


class PathOfFionn(Command):
    """Uses Path of Fionn with follow-up casts after the first hit."""

    def main(self):
        press(Key.PATH_OF_FIONN, 4, down_time=0.05, up_time=0.05)


class ShieldOfChulainn(Command):
    def main(self):
        press(Key.SHIELD_OF_CHULAINN, 3)


class SpearOfLight(Command):
    def main(self):
        press(Key.SPEAR_OF_LIGHT, 3)


class EnhancedFuryOfRoan(Command):
    def main(self):
        press(Key.ENHANCED_FURY_OF_ROAN, 3)


class ImpulseOfChulainn(Command):
    def main(self):
        press(Key.IMPULSE_OF_CHULAINN, 3)


class LightEnchant(Command):
    def main(self):
        press(Key.LIGHT_ENCHANT, 2)


class HelianBlessing(Command):
    def main(self):
        press(Key.HELIAN_BLESSING, 2)


class PiercingOfChulainn(Command):
    def main(self):
        press(Key.PIERCING_OF_CHULAINN, 2)


class HundredPole(Command):
    def main(self):
        press(Key.HUNDRED_POLE, 2)


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
    """Alias for routines that use the short name."""


class Origin(Command):
    def main(self):
        press(Key.ORIGIN, 3)


class Ascent(Command):
    def main(self):
        press(Key.ASCENT, 3)
