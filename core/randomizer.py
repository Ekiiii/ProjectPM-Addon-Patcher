# -*- coding: utf-8 -*-
"""
core/randomizer.py
Project PM ROM Randomizer Engine (v8 compatibility).
Supports wild encounters, starter trio, statics, gifts, trades,
co-op trainers, types, abilities, movesets, and shiny odds.
"""
import os
import sys
import re
import struct
import random
import hashlib
import itertools
import base64
import datetime
from typing import Dict, List, Tuple, Set, Optional, Any, Callable

from core.i18n import t, get_lang

APP_NAME = "Project PM Randomizer"
RAND_VERSION = 8
MAX_SPECIES_ID = 493
RAND_NUM_TYPES = 18
RAND_AREA_SIZES = (424, 428)
RAND_AREA_SIZE = 424  # Standard Platinum area size (DP is 428)
RAND_BST_TOLERANCE = 0.15
SHINY_VANILLA = 8

# Linked area groups that must share randomization state
RAND_LINKED_AREAS = [
    (8, 184) # Eterna Forest & Eterna Forest North
]

# 35 Legendary / Mythical Pokemon
RAND_LEGENDARIES = frozenset({
    144, 145, 146, 150, 151, # Kanto Birds, Mewtwo, Mew
    243, 244, 245, 249, 250, 251, # Johto Beasts, Lugia, Ho-Oh, Celebi
    377, 378, 379, 380, 381, 382, 383, 384, 385, 386, # Hoenn Regis, Lati@s, Weather Trio, Jirachi, Deoxys
    480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493 # Sinnoh Lake Trio, Dialga, Palkia, Heatran, Regigigas, Giratina, Cresselia, Phione, Manaphy, Darkrai, Shaymin, Arceus
})

VANILLA_STARTERS = (387, 390, 393) # Turtwig, Chimchar, Piplup
STARTER_UNENCODABLE = frozenset(range(256, 269))

ENC_LAND_RATES = (20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1)
ENC_OLD_SURF_RATES = (60, 30, 5, 4, 1)
ENC_GOOD_SUPER_RATES = (40, 40, 15, 4, 1)
ENC_REPLACE_SLOTS = {
    'swarm': (0, 1),
    'day': (2, 3),
    'night': (2, 3),
    'radar': (4, 5, 10, 11),
    'dual': (8, 9)
}

_RG = 0
_RSW = 100
_RDA = 108
_RNI = 116
_RRA = 124
_RDUAL = 164
_RSU = 204
_ROR = 292
_RGR = 336
_RSR = 380

STATIC_BATTLES = (
    ('Acuity Cavern Uxie', 701, 480, 50),
    ('Valor Cavern Azelf', 701, 482, 50),
    ('Spear Pillar Dialga', 701, 483, 70),
    ('Spear Pillar Palkia', 701, 484, 70),
    ('Turnback Cave Giratina', 701, 487, 47),
    ('Stark Mountain Heatran', 701, 485, 50),
    ('Rock Peak Ruins Regirock', 701, 377, 30),
    ('Iceberg Ruins Regice', 701, 378, 30),
    ('Iron Ruins Registeel', 701, 379, 30),
    ('Snowpoint Temple Regigigas', 701, 486, 1),
    ('Newmoon Island Darkrai', 701, 491, 50),
    ('Hall of Origin Arceus', 701, 493, 80),
    ('Old Chateau Rotom', 292, 479, 20),
    ('Route 209 Spiritomb', 292, 442, 25),
    ('Valley Windworks Drifloon', 701, 425, 15),
    ('Flower Paradise Shaymin', 792, 492, 30),
    ('Distortion World Giratina', 793, 487, 47, {'as_op': 701}),
    ('Eterna Forest Spiky-eared Pichu', 859, 172, 14, {'form': 1, 'hits': 2})
)

STATIC_GIFTS = (
    ('Hearthome Eevee', 133, 20),
    ('Veilstone Porygon', 137, 25)
)

FOSSIL_TABLE = (
    ('Old Amber', 103, 142),
    ('Helix Fossil', 101, 138),
    ('Dome Fossil', 102, 140),
    ('Root Fossil', 99, 345),
    ('Claw Fossil', 100, 347),
    ('Armor Fossil', 104, 410),
    ('Skull Fossil', 105, 408)
)

STATICS_HONEY_NARC = 'arc/encdata_ex.narc'
STATICS_HONEY_MEMBERS = (2, 3, 4)
STATICS_HONEY_MIRROR = (5, 6, 7)
STATICS_EGG_NARC = 'fielddata/script/scr_seq.narc'
STATICS_GIVEEGG_OPCODE = 151
STATICS_EGG_GIFTS = (("Cynthia's egg", 175), ("Riley's egg", 447))

SPECIAL_FEEBAS_MEMBER = 0
SPECIAL_TROPHY_MEMBER = 8
SPECIAL_MARSH_MEMBERS = (6, 7)

TRADE_NARC = 'fielddata/pokemon_trade/fld_trade.narc'
TRADE_RECORD_SIZE = 80
TRADE_OFF_SPECIES = 0
TRADE_OFF_REQUESTED = 76
TRADE_NPCS = ('Kazza', 'Charap', 'Gaspar', 'Foppa')
TRADE_TEXT_NOTE = "Note: in-game trade dialogue strings remain unaltered; real trades reflect the randomized table."

TRAINER_HEADER_SIZE = 20
TRDATA_OFF_MON_TYPE = 0
TRDATA_OFF_PARTY_SIZE = 3
TRAINER_HEADER_SIZE_HARD = 28
TRDATA_OFF_HARD_MEMBER = 24
TRDATA_OFF_HARD_PARTY_SIZE = 26
TRDATA_OFF_HARD_MON_TYPE = 27
TRDATATYPE_BASE = 0
TRMON_OFF_SPECIES = 4
TRMON_OFF_NATURE = 10
TRMON_NATURE_UNSET = 25
TRAINER_MON_FORM_SHIFT = 10
TRAINER_MON_SPECIES_MASK = (1 << TRAINER_MON_FORM_SHIFT) - 1

TRMON_SIZE_EXTENDED = {0: 16, 1: 24, 2: 20, 3: 28}
TRMON_SIZE_VANILLA = {0: 8, 1: 16, 2: 12, 3: 20}
TRMON_OFF_ABILITY = {0: 8, 1: 16, 2: 10, 3: 18}

PERSONAL_ENTRY_SIZE = 44
PERSONAL_OFF_TYPE1 = 6
PERSONAL_OFF_TYPE2 = 7
PERSONAL_OFF_ABILITY1 = 22
PERSONAL_OFF_ABILITY2 = 23

LEARNSET_MOVE_BITS = 9
LEARNSET_MOVE_MASK = (1 << LEARNSET_MOVE_BITS) - 1

COOP_KEYS = ('trainers', 'types', 'abilities', 'movesets')
PERSONAL_KEYS = ('wilds', 'starters', 'statics', 'battles', 'gifts', 'trade_get', 'trade_want', 'wild_special', 'gba_slots')

SHARE_PREFIX_COOP = 'PMC'
SHARE_PREFIX_WORLD = 'PMW'
SHARE_B32_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

SPECIES_NAMES = (
    "Bulbasaur|Ivysaur|Venusaur|Charmander|Charmeleon|Charizard|Squirtle|Wartortle|Blastoise|"
    "Caterpie|Metapod|Butterfree|Weedle|Kakuna|Beedrill|Pidgey|Pidgeotto|Pidgeot|Rattata|Raticate|"
    "Spearow|Fearow|Ekans|Arbok|Pikachu|Raichu|Sandshrew|Sandslash|Nidoran F|Nidorina|Nidoqueen|"
    "Nidoran M|Nidorino|Nidoking|Clefairy|Clefable|Vulpix|Ninetales|Jigglypuff|Wigglytuff|Zubat|"
    "Golbat|Oddish|Gloom|Vileplume|Paras|Parasect|Venonat|Venomoth|Diglett|Dugtrio|Meowth|Persian|"
    "Psyduck|Golduck|Mankey|Primeape|Growlithe|Arcanine|Poliwag|Poliwhirl|Poliwrath|Abra|Kadabra|"
    "Alakazam|Machop|Machoke|Machamp|Bellsprout|Weepinbell|Victreebel|Tentacool|Tentacruel|Geodude|"
    "Graveler|Golem|Ponyta|Rapidash|Slowpoke|Slowbro|Magnemite|Magneton|Farfetch'd|Doduo|Dodrio|Seel|"
    "Dewgong|Grimer|Muk|Shellder|Cloyster|Gastly|Haunter|Gengar|Onix|Drowzee|Hypno|Krabby|Kingler|"
    "Voltorb|Electrode|Exeggcute|Exeggutor|Cubone|Marowak|Hitmonlee|Hitmonchan|Lickitung|Koffing|"
    "Weezing|Rhyhorn|Rhydon|Chansey|Tangela|Kangaskhan|Horsea|Seadra|Goldeen|Seaking|Staryu|Starmie|"
    "Mr. Mime|Scyther|Jynx|Electabuzz|Magmar|Pinsir|Tauros|Magikarp|Gyarados|Lapras|Ditto|Eevee|"
    "Vaporeon|Jolteon|Flareon|Porygon|Omanyte|Omastar|Kabuto|Kabutops|Aerodactyl|Snorlax|Articuno|"
    "Zapdos|Moltres|Dratini|Dragonair|Dragonite|Mewtwo|Mew|Chikorita|Bayleef|Meganium|Cyndaquil|"
    "Quilava|Typhlosion|Totodile|Croconaw|Feraligatr|Sentret|Furret|Hoothoot|Noctowl|Ledyba|Ledian|"
    "Spinarak|Ariados|Crobat|Chinchou|Lanturn|Pichu|Cleffa|Igglybuff|Togepi|Togetic|Natu|Xatu|Mareep|"
    "Flaaffy|Ampharos|Bellossom|Marill|Azumarill|Sudowoodo|Politoed|Hoppip|Skiploom|Jumpluff|Aipom|"
    "Sunkern|Sunflora|Yanma|Wooper|Quagsire|Espeon|Umbreon|Murkrow|Slowking|Misdreavus|Unown|Wobbuffet|"
    "Girafarig|Pineco|Forretress|Dunsparce|Gligar|Steelix|Snubbull|Granbull|Qwilfish|Scizor|Shuckle|"
    "Heracross|Sneasel|Teddiursa|Ursaring|Slugma|Magcargo|Swinub|Piloswine|Corsola|Remoraid|Octillery|"
    "Delibird|Mantine|Skarmory|Houndour|Houndoom|Kingdra|Phanpy|Donphan|Porygon2|Stantler|Smeargle|"
    "Tyrogue|Hitmontop|Smoochum|Elekid|Magby|Miltank|Blissey|Raikou|Entei|Suicune|Larvitar|Pupitar|"
    "Tyranitar|Lugia|Ho-Oh|Celebi|Treecko|Grovyle|Sceptile|Torchic|Combusken|Blaziken|Mudkip|Marshtomp|"
    "Swampert|Poochyena|Mightyena|Zigzagoon|Linoone|Wurmple|Silcoon|Beautifly|Cascoon|Dustox|Lotad|"
    "Lombre|Ludicolo|Seedot|Nuzleaf|Shiftry|Taillow|Swellow|Wingull|Pelipper|Ralts|Kirlia|Gardevoir|"
    "Surskit|Masquerain|Shroomish|Breloom|Slakoth|Vigoroth|Slaking|Nincada|Ninjask|Shedinja|Whismur|"
    "Loudred|Exploud|Makuhita|Hariyama|Azurill|Nosepass|Skitty|Delcatty|Sableye|Mawile|Aron|Lairon|"
    "Aggron|Meditite|Medicham|Electrike|Manectric|Plusle|Minun|Volbeat|Illumise|Roselia|Gulpin|Swalot|"
    "Carvanha|Sharpedo|Wailmer|Wailord|Numel|Camerupt|Torkoal|Spoink|Grumpig|Spinda|Trapinch|Vibrava|"
    "Flygon|Cacnea|Cacturne|Swablu|Altaria|Zangoose|Seviper|Lunatone|Solrock|Barboach|Whiscash|"
    "Corphish|Crawdaunt|Baltoy|Claydol|Lileep|Cradily|Anorith|Armaldo|Feebas|Milotic|Castform|Kecleon|"
    "Shuppet|Banette|Duskull|Dusclops|Tropius|Chimecho|Absol|Wynaut|Snorunt|Glalie|Spheal|Sealeo|"
    "Walrein|Clamperl|Huntail|Gorebyss|Relicanth|Luvdisc|Bagon|Shelgon|Salamence|Beldum|Metang|Metagross|"
    "Regirock|Regice|Registeel|Latias|Latios|Kyogre|Groudon|Rayquaza|Jirachi|Deoxys|Turtwig|Grotle|"
    "Torterra|Chimchar|Monferno|Infernape|Piplup|Prinplup|Empoleon|Starly|Staravia|Staraptor|Bidoof|"
    "Bibarel|Kricketot|Kricketune|Shinx|Luxio|Luxray|Budew|Roserade|Cranidos|Rampardos|Shieldon|"
    "Bastiodon|Burmy|Wormadam|Mothim|Combee|Vespiquen|Pachirisu|Buizel|Floatzel|Cherubi|Cherrim|"
    "Shellos|Gastrodon|Ambipom|Drifloon|Drifblim|Buneary|Lopunny|Mismagius|Honchkrow|Glameow|Purugly|"
    "Chingling|Stunky|Skuntank|Bronzor|Bronzong|Bonsly|Mime Jr.|Happiny|Chatot|Spiritomb|Gible|Gabite|"
    "Garchomp|Munchlax|Riolu|Lucario|Hippopotas|Hippowdon|Skorupi|Drapion|Croagunk|Toxicroak|Carnivine|"
    "Finneon|Lumineon|Mantyke|Snover|Abomasnow|Weavile|Magnezone|Lickilicky|Rhyperior|Tangrowth|"
    "Electivire|Magmortar|Togekiss|Yanmega|Leafeon|Glaceon|Gliscor|Mamoswine|Porygon-Z|Gallade|"
    "Probopass|Dusknoir|Froslass|Rotom|Uxie|Mesprit|Azelf|Dialga|Palkia|Heatran|Regigigas|Giratina|"
    "Cresselia|Phione|Manaphy|Darkrai|Shaymin|Arceus"
).split("|")


def _rr(b: bytearray, o: int) -> int:
    """Reads 32-bit uint from bytearray at offset o."""
    return struct.unpack_from('<I', b, o)[0]

def _rw(b: bytearray, o: int, v: int) -> None:
    """Writes 32-bit uint into bytearray at offset o."""
    struct.pack_into('<I', b, o, int(v))

def species_name(sid: int) -> str:
    """Returns 'Bulbasaur' for 1, etc., or '#sid' if unknown."""
    try:
        sid = int(sid)
    except (TypeError, ValueError):
        return str(sid)
    if 1 <= sid <= len(SPECIES_NAMES):
        return SPECIES_NAMES[sid - 1]
    return f"#{sid}"

def species_id(name: str) -> Optional[int]:
    """Resolves a species name or ID string back to an integer 1..493."""
    if not name:
        return None
    s = str(name).strip().lower()
    if s.isdigit():
        val = int(s)
        return val if 1 <= val <= MAX_SPECIES_ID else None
    for i, n in enumerate(SPECIES_NAMES):
        if n.lower() == s:
            return i + 1
    return None

class RandNDSRom:
    """Minimal NDS filesystem reader/writer for in-place file replacement."""
    def __init__(self, path: str):
        self.path = path
        with open(path, 'rb') as f:
            self.data = bytearray(f.read())
        fo = struct.unpack_from('<I', self.data, 64)[0]
        fs = struct.unpack_from('<I', self.data, 68)[0]
        ao = struct.unpack_from('<I', self.data, 72)[0]
        asz = struct.unpack_from('<I', self.data, 76)[0]
        self._fnt = self.data[fo:fo + fs]
        self._fat = self.data[ao:ao + asz]

    def _traverse(self, dir_id: int, parts: List[str], depth: int) -> Optional[Tuple[int, int]]:
        idx = dir_id & 0x0FFF
        sub_off, first_fid = struct.unpack_from('<IH', self._fnt, idx * 8)
        target = parts[depth].lower()
        fid = first_fid
        pos = sub_off
        while pos < len(self._fnt):
            lf = self._fnt[pos]
            pos += 1
            if lf == 0:
                break
            is_dir = bool(lf & 0x80)
            nlen = lf & 0x7F
            name = self._fnt[pos:pos + nlen].decode('ascii', errors='ignore')
            pos += nlen
            if is_dir:
                sub_id = struct.unpack_from('<H', self._fnt, pos)[0]
                pos += 2
                if name.lower() == target and depth < len(parts) - 1:
                    return self._traverse(sub_id, parts, depth + 1)
            else:
                if name.lower() == target and depth == len(parts) - 1:
                    return struct.unpack_from('<II', self._fat, fid * 8)
                fid += 1
        return None

    def find(self, path: str) -> Optional[Tuple[int, int]]:
        parts = [p for p in path.split('/') if p]
        return self._traverse(0xF000, parts, 0)

    def read(self, s: int, e: int) -> bytes:
        return bytes(self.data[s:e])

    def write(self, s: int, e: int, new: bytes) -> None:
        if len(new) != e - s:
            raise ValueError(f"size mismatch {len(new)} vs {e - s}")
        self.data[s:e] = new

    def save(self, path: str) -> None:
        with open(path, 'wb') as f:
            f.write(self.data)

class RandNARC:
    """Parser and serializer for Nitro NARC archives with same-size file updates."""
    def __init__(self, data: bytes):
        self._d = bytearray(data)
        if self._d[:4] != b'NARC':
            raise ValueError('not a NARC')
        hs = struct.unpack_from('<H', self._d, 12)[0]
        b = hs
        if self._d[b:b + 4] != b'BTAF':
            raise ValueError('BTAF not found')
        bsz = struct.unpack_from('<I', self._d, b + 4)[0]
        nf = struct.unpack_from('<I', self._d, b + 8)[0]
        self.num_files = nf
        self._fat = [struct.unpack_from('<II', self._d, b + 12 + i * 8) for i in range(nf)]
        nb = b + bsz
        if self._d[nb:nb + 4] != b'BTNF':
            raise ValueError('BTNF not found')
        nbsz = struct.unpack_from('<I', self._d, nb + 4)[0]
        gb = nb + nbsz
        if self._d[gb:gb + 4] != b'GMIF':
            raise ValueError('GMIF not found')
        self._ds = gb + 8

    def get(self, i: int) -> bytes:
        s, e = self._fat[i]
        return bytes(self._d[self._ds + s:self._ds + e])

    def put(self, i: int, data: bytes) -> None:
        s, e = self._fat[i]
        if len(data) != e - s:
            raise ValueError(f"file {i}: expected {e - s}, got {len(data)}")
        self._d[self._ds + s:self._ds + e] = data

    def to_bytes(self) -> bytes:
        return bytes(self._d)

class RandArea:
    """Manages wild encounter slots for one 428-byte area file."""
    def __init__(self, raw: bytes, area_idx: int = -1):
        self.b = bytearray(raw)
        self.idx = area_idx

    def _has(self, off: int) -> bool:
        return _rr(self.b, off) != 0

    def slots(self, do_grass: bool, do_surf: bool, do_fish: bool, do_spec: bool):
        b = self.b
        if do_grass and self._has(_RG):
            for i in range(12):
                o = _RG + 4 + i * 8 + 4
                yield (lambda o=o: _rr(b, o), lambda v, o=o: _rw(b, o, v))
        if do_spec:
            for i in range(2):
                for base in (_RSW, _RDA, _RNI):
                    o = base + i * 4
                    yield (lambda o=o: _rr(b, o), lambda v, o=o: _rw(b, o, v))
            for i in range(4):
                o = _RRA + i * 4
                yield (lambda o=o: _rr(b, o), lambda v, o=o: _rw(b, o, v))
        if do_surf and self._has(_RSU):
            for i in range(5):
                o = _RSU + 4 + i * 8 + 4
                yield (lambda o=o: _rr(b, o), lambda v, o=o: _rw(b, o, v))
        if do_fish:
            for base in (_ROR, _RGR, _RSR):
                if self._has(base):
                    for i in range(5):
                        o = base + 4 + i * 8 + 4
                        yield (lambda o=o: _rr(b, o), lambda v, o=o: _rw(b, o, v))

    def to_bytes(self) -> bytes:
        return bytes(self.b)


def rand_load_pokemon_db(rom: RandNDSRom) -> Dict[int, Dict[str, Any]]:
    """Loads base stats, types and BST for Pokemon 1..493 from pl_personal.narc."""
    res = rom.find('poketool/personal/pl_personal.narc')
    if res is None:
        return {}
    try:
        narc = RandNARC(rom.read(*res))
    except Exception:
        return {}
    db = {}
    limit = min(narc.num_files - 1, 493)
    for i in range(1, limit + 1):
        try:
            fd = narc.get(i)
            if len(fd) < 8:
                continue
            bst = sum(fd[0:6])
            db[i] = {
                'type1': fd[6],
                'type2': fd[7],
                'bst': bst
            }
        except Exception:
            pass
    return db

def rand_build_pool(db: Dict[int, Dict[str, Any]], exclude_legendaries: bool) -> List[int]:
    """Builds list of eligible Pokemon species IDs."""
    pool = []
    for sid in range(1, 494):
        if db and sid not in db:
            continue
        if exclude_legendaries and sid in RAND_LEGENDARIES:
            continue
        pool.append(sid)
    return pool if pool else list(range(1, 494))

def _rand_strength(cands: List[int], db: Dict[int, Dict[str, Any]], orig_bst: int) -> List[int]:
    """Filters candidate species within BST tolerance (+/- 15%)."""
    lo = orig_bst * (1 - RAND_BST_TOLERANCE)
    hi = orig_bst * (1 + RAND_BST_TOLERANCE)
    filt = [s for s in cands if lo <= db.get(s, {}).get('bst', orig_bst) <= hi]
    return filt if filt else list(cands)

def _rand_typefilter(pool: List[int], db: Dict[int, Dict[str, Any]], types: Set[int]) -> List[int]:
    """Filters species that share at least one matching type."""
    filt = [s for s in pool if db.get(s, {}).get('type1') in types or db.get(s, {}).get('type2') in types]
    return filt if filt else list(pool)

def _rand_pick(orig: int, pool: List[int], db: Dict[int, Dict[str, Any]], sim_str: bool, typed_pool: Optional[List[int]] = None) -> int:
    """Picks a random species respecting strength and type filters."""
    cands = typed_pool if typed_pool is not None else pool
    if sim_str and orig in db:
        cands = _rand_strength(cands, db, db[orig]['bst'])
    return random.choice(cands) if cands else random.choice(pool)

def _rand_area_groups(areas: List[RandArea]):
    """Yields lists of areas that must share encounter state (e.g. linked caves)."""
    linked = {}
    for group in RAND_LINKED_AREAS:
        for idx in group:
            linked[idx] = group
    emitted = set()
    by_idx = {a.idx: a for a in areas if a is not None}
    for area in areas:
        if area is None:
            continue
        if area.idx in linked:
            key = linked[area.idx]
            if key in emitted:
                continue
            emitted.add(key)
            yield [by_idx[i] for i in key if i in by_idx]
        else:
            yield [area]

def rand_substream(name: str, seed_norm: Any) -> random.Random:
    """Returns an isolated reproducible random stream for a specific sub-task."""
    if seed_norm is None or seed_norm == '':
        return random.Random()
    tag = f"PLMP-{name}|v{RAND_VERSION}|{seed_norm}"
    h = hashlib.sha256(tag.encode('utf-8')).hexdigest()
    return random.Random(int(h[:16], 16))

def _cat_rng(seed: Any, category: str) -> random.Random:
    """Returns an isolated random stream for a co-op category."""
    return random.Random(f"{seed}|{category}|v{RAND_VERSION}")


def _starter_sigs():
    blocks = [struct.pack('<HHHHH', 8704 | (129 + i), 146, 6312, 7209, 14848 | (129 + i)) for i in range(3)]
    selector = struct.pack('<14H', 46344, 10240, 53252, 10241, 53252, 10242, 53252, 57349, 18436, 48392, 18436, 48392, 18436, 48392)
    pool = struct.pack('<III', 387, 390, 393)
    return (blocks, selector, pool)

def _starter_find_once(data: bytearray, sig: bytes, what: str) -> int:
    first = data.find(sig)
    if first < 0:
        raise ValueError(f"starter patch: {what} signature not found")
    if data.find(sig, first + 1) >= 0:
        raise ValueError(f"starter patch: {what} signature is not unique")
    return first

def starter_find_sites(data: bytearray) -> Dict[str, Any]:
    """Locates the 4 patch sites in the ROM for starter briefcase selection."""
    blocks, selector, pool = _starter_sigs()
    b = [_starter_find_once(data, s, f"sprite-arg block {i}") for i, s in enumerate(blocks)]
    if b[1] - b[0] != 14 or b[2] - b[1] != 14:
        raise ValueError(f"starter patch: sprite-arg blocks not adjacent - refusing")
    sel = _starter_find_once(data, selector, 'species selector')
    pl = _starter_find_once(data, pool, 'species literal pool')
    if pl != sel + 36:
        raise ValueError(f"starter patch: literal pool 0x{pl:X} not at selector+0x24 (0x{sel:X})")
    return {'blocks': b, 'pool': pl}

def starter_encode_arg(slot: int, species: int) -> int:
    """Encodes the 16-bit Thumb instruction parameter for the starter sprite."""
    if 1 <= species <= 255:
        return 8704 | species
    base = 516 + 4 * slot
    if 0 <= base - species <= 255:
        return 14848 | (base - species)
    raise ValueError(f"starter patch: species {species} not encodable for slot {slot}")

def starter_encodable(slot: int, species: int) -> bool:
    try:
        starter_encode_arg(slot, species)
        return True
    except ValueError:
        return False

def starter_build_pool(rom: RandNDSRom, db: Dict[int, Dict[str, Any]], evolving_only: bool = True) -> List[int]:
    """Builds list of Pokemon eligible to be briefcase starters."""
    res = rom.find('poketool/personal/evo.narc')
    if res is None:
        raise ValueError('starter patch: poketool/personal/evo.narc not found')
    narc = RandNARC(rom.read(*res))
    evolves = set()
    for sid in range(1, min(narc.num_files, 494)):
        entry = narc.get(sid)
        for i in range(min(7, len(entry) // 6)):
            if struct.unpack_from('<H', entry, i * 6)[0] != 0:
                evolves.add(sid)
                break
    pool = [sid for sid in range(1, 494) if sid not in STARTER_UNENCODABLE and (not evolving_only or sid in evolves)]
    if len(pool) < 3:
        raise ValueError(f"starter patch: pool has only {len(pool)} species - refusing")
    return pool

def starter_pick(pool: List[int], seed_norm: Any) -> Tuple[int, int, int]:
    """Picks three distinct species from a derived random stream."""
    if seed_norm is None or seed_norm == '':
        rng = random
    else:
        rng = random.Random(f"PLMP-starters|v{RAND_VERSION}|{seed_norm}")
    return tuple(rng.sample(pool, 3))

def starter_arrange(trio: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Orders a trio into slot positions that the briefcase code can encode."""
    trio = tuple(int(x) for x in trio)
    if len(trio) != 3:
        raise ValueError('choose exactly three starters')
    bad = [x for x in trio if not (1 <= x <= MAX_SPECIES_ID)]
    if bad:
        raise ValueError('not a Pokemon: ' + ', '.join(str(x) for x in bad))
    if len(set(trio)) != 3:
        raise ValueError('the three starters must be different Pokemon')
    never = [x for x in trio if not any(starter_encodable(i, x) for i in range(3))]
    if never:
        raise ValueError(f"{', '.join(species_name(x) for x in never)} cannot be a starter (no slot fits #256-260)")
    for order in itertools.permutations(trio):
        if all(starter_encodable(i, x) for i, x in enumerate(order)):
            return tuple(order)
    raise ValueError(f"{' / '.join(species_name(x) for x in trio)} cannot share the briefcase: slot conflict")

def starter_apply(rom: RandNDSRom, trio: Tuple[int, int, int], log: Callable = print) -> None:
    """Applies the starter trio patch into the ROM in place."""
    sites = starter_find_sites(rom.data)
    for i, sp in enumerate(trio):
        starter_encode_arg(i, sp)
    for i, sp in enumerate(trio):
        insn_off = sites['blocks'][i] + 8
        pool_off = sites['pool'] + 4 * i
        struct.pack_into('<H', rom.data, insn_off, starter_encode_arg(i, sp))
        struct.pack_into('<I', rom.data, pool_off, sp)
        log(f"    starter slot {i}: {VANILLA_STARTERS[i]} -> {sp} (insn @0x{insn_off:X}, pool @0x{pool_off:X})")
    if struct.unpack_from('<III', rom.data, sites['pool']) != tuple(trio):
        raise ValueError('starter patch: readback mismatch - aborting')


def statics_honey(rom: RandNDSRom, db: Dict[int, Dict[str, Any]], pool: List[int], mode: str, rule: str, rng: random.Random, log: Callable = print) -> Optional[Dict[str, Any]]:
    """Randomizes the 21 honey tree encounters in arc/encdata_ex.narc."""
    res = rom.find(STATICS_HONEY_NARC)
    if res is None:
        log(f"[rand] honey trees: {STATICS_HONEY_NARC} not found - skipped")
        return None
    ss, se = res
    narc = RandNARC(rom.read(ss, se))
    sim_str = (rule == 'similar_strength')
    assigned = {}
    for idx in STATICS_HONEY_MEMBERS:
        if idx >= narc.num_files:
            continue
        data = bytearray(narc.get(idx))
        n_slots = len(data) // 4
        for slot in range(n_slots):
            orig = struct.unpack_from('<I', data, slot * 4)[0]
            if orig <= 0:
                continue
            if mode == 'area_1to1' and orig in assigned:
                new = assigned[orig]
            else:
                cands = pool
                if sim_str and orig in db:
                    cands = _rand_strength(cands, db, db[orig]['bst'])
                new = rng.choice(cands) if cands else rng.choice(pool)
                if mode == 'area_1to1':
                    assigned[orig] = new
            struct.pack_into('<I', data, slot * 4, new)
        narc.put(idx, bytes(data))
    for src, dst in zip(STATICS_HONEY_MEMBERS, STATICS_HONEY_MIRROR):
        if src < narc.num_files and dst < narc.num_files:
            narc.put(dst, narc.get(src))
    rom.write(ss, se, narc.to_bytes())
    log(f"[rand] honey trees: randomized across {len(STATICS_HONEY_MEMBERS)} tiers (and mirrors)")
    return {'honey_randomized': True}

def statics_eggs(rom: RandNDSRom, db: Dict[int, Dict[str, Any]], pool: List[int], rule: str, rng: random.Random, log: Callable = print) -> Optional[Dict[str, Any]]:
    """Randomizes the two gift eggs (Togepi and Happiny) in script bytecode."""
    res = rom.find(STATICS_EGG_NARC)
    if res is None:
        log(f"[rand] gift eggs: {STATICS_EGG_NARC} not found - skipped")
        return None
    ss, se = res
    buf = bytearray(rom.read(ss, se))
    sim_str = (rule == 'similar_strength')
    out = {}
    found_any = False
    for label, orig in STATICS_EGG_GIFTS:
        sig = struct.pack('<HH', STATICS_GIVEEGG_OPCODE, orig)
        pos = buf.find(sig)
        if pos < 0:
            log(f"[rand] {label}: signature not found - skipped")
            continue
        if buf.find(sig, pos + 1) >= 0:
            log(f"[rand] {label}: signature not unique - skipped")
            continue
        cands = pool
        if sim_str and orig in db:
            cands = _rand_strength(cands, db, db[orig]['bst'])
        new = rng.choice(cands) if cands else rng.choice(pool)
        struct.pack_into('<HH', buf, pos, STATICS_GIVEEGG_OPCODE, new)
        out[label] = (orig, new)
        log(f"[rand] {label}: {species_name(orig)} -> {species_name(new)}")
        found_any = True
    if found_any:
        rom.write(ss, se, bytes(buf))
    return out if out else None

def statics_script_sites(rom: RandNDSRom, db: Dict[int, Dict[str, Any]], pool: List[int], rule: str, rng_battles: random.Random, rng_gifts: random.Random, do_battles: bool, do_gifts: bool, log: Callable = print) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Randomizes one-time legendary/scripted battles and gift Pokemon inside scr_seq.narc."""
    res = rom.find(STATICS_EGG_NARC)
    if res is None:
        log(f"[rand] script sites: {STATICS_EGG_NARC} not found - skipped")
        return (None, None)
    ss, se = res
    buf = bytearray(rom.read(ss, se))
    sim_str = (rule == 'similar_strength')
    plan = []
    if do_battles:
        for site in STATIC_BATTLES:
            label, op, sp, lv = site[:4]
            opt = site[4] if len(site) > 4 else {}
            sig = struct.pack('<HHH', op, sp, lv)
            cands = pool
            if sim_str and sp in db:
                cands = _rand_strength(cands, db, db[sp]['bst'])
            new = rng_battles.choice(cands) if cands else rng_battles.choice(pool)
            plan.append(('battle', label, sig, sp, new, opt))
    if do_gifts:
        for label, sp, lv in STATIC_GIFTS:
            sig = struct.pack('<HH', 273, sp)
            cands = pool
            if sim_str and sp in db:
                cands = _rand_strength(cands, db, db[sp]['bst'])
            new = rng_gifts.choice(cands) if cands else rng_gifts.choice(pool)
            plan.append(('gift', label, sig, sp, new, {}))
    found = []
    for kind, label, sig, old, new, opt in plan:
        hits = []
        pos = buf.find(sig)
        while pos >= 0:
            hits.append(pos)
            pos = buf.find(sig, pos + 1)
        expected = opt.get('hits', 1)
        if len(hits) != expected:
            log(f"[rand] {label}: signature count {len(hits)} vs expected {expected} - skipped")
            continue
        found.append((kind, label, hits, old, new, opt))
    gifts = {}
    battles = {}
    for kind, label, hits, old, new, opt in found:
        for at in hits:
            if 'as_op' in opt:
                struct.pack_into('<H', buf, at, opt['as_op'])
            struct.pack_into('<H', buf, at + 2, new)
            if 'form' in opt:
                struct.pack_into('<H', buf, at + 6, 0)
        if kind == 'battle':
            battles[label] = (old, new)
        else:
            gifts[label] = (old, new)
        log(f"[rand] {label}: {species_name(old)} -> {species_name(new)}")
    if found:
        rom.write(ss, se, bytes(buf))
    return (battles if battles else None, gifts if gifts else None)

def fossils_randomize(rom: RandNDSRom, db: Dict[int, Dict[str, Any]], pool: List[int], rule: str, rng: random.Random, log: Callable = print) -> Optional[Dict[str, Any]]:
    """Randomizes revived fossil Pokemon."""
    res = rom.find('fielddata/script/scr_seq.narc')
    if res is None:
        return None
    ss, se = res
    buf = bytearray(rom.read(ss, se))
    sim_str = (rule == 'similar_strength')
    out = {}
    found_any = False
    for label, item_id, sp in FOSSIL_TABLE:
        sig = struct.pack('<HHH', 273, sp, 20)
        pos = buf.find(sig)
        if pos < 0:
            continue
        cands = pool
        if sim_str and sp in db:
            cands = _rand_strength(cands, db, db[sp]['bst'])
        new = rng.choice(cands) if cands else rng.choice(pool)
        struct.pack_into('<H', buf, pos + 2, new)
        out[label] = (sp, new)
        log(f"[rand] {label}: {species_name(sp)} -> {species_name(new)}")
        found_any = True
    if found_any:
        rom.write(ss, se, bytes(buf))
    return out if out else None

def special_wilds(rom: RandNDSRom, db: Dict[int, Dict[str, Any]], pool: List[int], mode: str, rule: str, rng: random.Random, log: Callable = print, do_special: bool = True, do_gba: bool = False) -> Optional[Dict[str, Any]]:
    """Randomizes Trophy Garden, Great Marsh, and Feebas special slots in arc/encdata_ex.narc."""
    res = rom.find(STATICS_HONEY_NARC)
    if res is None:
        return None
    ss, se = res
    narc = RandNARC(rom.read(ss, se))
    sim_str = (rule == 'similar_strength')
    changed = 0
    if do_special and SPECIAL_TROPHY_MEMBER < narc.num_files:
        d = bytearray(narc.get(SPECIAL_TROPHY_MEMBER))
        n_sp = len(d) // 4
        for slot in range(n_sp):
            orig = struct.unpack_from('<I', d, slot * 4)[0]
            if orig <= 0:
                continue
            cands = pool
            if sim_str and orig in db:
                cands = _rand_strength(cands, db, db[orig]['bst'])
            new = rng.choice(cands) if cands else rng.choice(pool)
            struct.pack_into('<I', d, slot * 4, new)
            changed += 1
        narc.put(SPECIAL_TROPHY_MEMBER, bytes(d))
    for m in SPECIAL_MARSH_MEMBERS:
        if do_special and m < narc.num_files:
            d = bytearray(narc.get(m))
            n_sp = len(d) // 4
            for slot in range(n_sp):
                orig = struct.unpack_from('<I', d, slot * 4)[0]
                if orig <= 0:
                    continue
                cands = pool
                if sim_str and orig in db:
                    cands = _rand_strength(cands, db, db[orig]['bst'])
                new = rng.choice(cands) if cands else rng.choice(pool)
                struct.pack_into('<I', d, slot * 4, new)
                changed += 1
            narc.put(m, bytes(d))
    if changed > 0:
        rom.write(ss, se, narc.to_bytes())
        log(f"[rand] special encounters: {changed} slots randomized in Trophy Garden & Great Marsh")
    return {'special_wilds': changed} if changed > 0 else None

def trades_randomize(rom: RandNDSRom, db: Dict[int, Dict[str, Any]], pool: List[int], rule: str, wild_species: Set[int], rng_get: random.Random, rng_want: random.Random, do_get: bool, do_want: bool, log: Callable = print) -> Optional[Dict[str, Any]]:
    """Randomizes in-game trades in fielddata/pokemon_trade/fld_trade.narc."""
    res = rom.find(TRADE_NARC)
    if res is None:
        return None
    ss, se = res
    narc = RandNARC(rom.read(ss, se))
    sim_str = (rule == 'similar_strength')
    trades = {}
    want_pool = list(wild_species) if wild_species else pool
    for i in range(min(narc.num_files, len(TRADE_NPCS))):
        npc = TRADE_NPCS[i]
        d = bytearray(narc.get(i))
        if len(d) < TRADE_RECORD_SIZE:
            continue
        give_sp = struct.unpack_from('<I', d, TRADE_OFF_SPECIES)[0]
        want_sp = struct.unpack_from('<I', d, TRADE_OFF_REQUESTED)[0]
        new_give = give_sp
        new_want = want_sp
        if do_get:
            cands = pool
            if sim_str and give_sp in db:
                cands = _rand_strength(cands, db, db[give_sp]['bst'])
            new_give = rng_get.choice(cands) if cands else rng_get.choice(pool)
            struct.pack_into('<I', d, TRADE_OFF_SPECIES, new_give)
        if do_want:
            cands = want_pool
            if sim_str and want_sp in db:
                cands = _rand_strength(cands, db, db[want_sp]['bst'])
            new_want = rng_want.choice(cands) if cands else rng_want.choice(pool)
            struct.pack_into('<I', d, TRADE_OFF_REQUESTED, new_want)
        narc.put(i, bytes(d))
        trades[npc] = {
            'give_old': give_sp, 'give_new': new_give,
            'want_old': want_sp, 'want_new': new_want
        }
        log(f"[rand] trade {npc}: gives {species_name(new_give)} (was {species_name(give_sp)}), wants {species_name(new_want)} (was {species_name(want_sp)})")
    rom.write(ss, se, narc.to_bytes())
    return trades if trades else None

def trade_dialogue_buffered(rom: RandNDSRom) -> bool:
    return True


def _open_narc(rom: RandNDSRom, path: str, log: Callable = print):
    res = rom.find(path)
    if res is None:
        log(f"[rand] ERROR: {path} not found in this ROM")
        return (None, None)
    start, end = res
    return ((start, end), RandNARC(rom.read(start, end)))

def _save_narc(rom: RandNDSRom, span: Tuple[int, int], narc: RandNARC, path: str, log: Callable = print) -> bool:
    start, end = span
    new = narc.to_bytes()
    if len(new) != end - start:
        log(f"[rand] ERROR: {path} changed size ({len(new)} vs {end - start}). Aborting.")
        return False
    rom.write(start, end, new)
    return True

def evo_randomize(rom: RandNDSRom, db: Dict[int, Dict[str, Any]], pool: List[int], evo_mode: str, rng: random.Random, log: Callable = print) -> Optional[Dict[str, Any]]:
    """
    Randomizes evolution target species in poketool/personal/evo.narc.
    evo_mode: 'vanilla' (no change), 'similar_strength' (matched BST range), 'chaos' (any species).
    """
    if evo_mode in ('vanilla', None, False, ''):
        return None

    path = 'poketool/personal/evo.narc'
    span, narc = _open_narc(rom, path, log)
    if narc is None:
        return None

    sim_str = (evo_mode == 'similar_strength')
    assigned: Dict[int, int] = {}
    changed_count = 0

    max_idx = min(narc.num_files, 494)
    for i in range(1, max_idx):
        data = bytearray(narc.get(i))
        if len(data) < 42:
            continue
        file_changed = False
        for slot in range(7):
            off = slot * 6
            method, param, target = struct.unpack_from('<HHH', data, off)
            if method == 0 or target == 0 or target > 493:
                continue

            if target in assigned:
                new_target = assigned[target]
            else:
                if sim_str and target in db:
                    old_bst = db[target].get('bst', 400)
                    candidates = [
                        p for p in pool
                        if p in db and abs(db[p].get('bst', 400) - old_bst) <= max(40, int(old_bst * 0.20))
                    ]
                    if not candidates:
                        candidates = pool
                    new_target = rng.choice(candidates)
                else:
                    new_target = rng.choice(pool)
                assigned[target] = new_target

            struct.pack_into('<H', data, off + 4, new_target)
            file_changed = True
            changed_count += 1

        if file_changed:
            narc.put(i, bytes(data))

    if not _save_narc(rom, span, narc, path, log):
        return None

    log(f"[rand] evolutions: randomized {changed_count} targets across {len(assigned)} target species (mode: {evo_mode})")
    return {'evolutions_randomized': changed_count, 'mode': evo_mode, 'targets': assigned}

def randomize_species_data(rom: RandNDSRom, seed: Any, do_types: bool, do_abilities: bool, log: Callable = print) -> Tuple[bool, Dict[str, Any]]:
    """Randomizes types and/or abilities in poketool/personal/pl_personal.narc."""
    path = 'poketool/personal/pl_personal.narc'
    span, narc = _open_narc(rom, path, log)
    if narc is None:
        return (False, {})
    rng_types = _cat_rng(seed, 'types')
    rng_abil = _cat_rng(seed, 'abilities')
    entries = []
    types = set()
    abilities = set()
    for i in range(narc.num_files):
        fd = narc.get(i)
        if len(fd) < PERSONAL_ENTRY_SIZE:
            continue
        entries.append(i)
        types.add(fd[PERSONAL_OFF_TYPE1])
        types.add(fd[PERSONAL_OFF_TYPE2])
        for off in (PERSONAL_OFF_ABILITY1, PERSONAL_OFF_ABILITY2):
            if fd[off]:
                abilities.add(fd[off])
    type_pool = sorted(types)
    ability_pool = sorted(abilities)
    if (do_types and not type_pool) or (do_abilities and not ability_pool):
        log('[rand] ERROR: could not read the type/ability pools from this ROM')
        return (False, {})
    log(f"[rand] species data: {len(entries)} entries, {len(type_pool)} types, {len(ability_pool)} abilities")
    changed = 0
    for i in entries:
        fd = bytearray(narc.get(i))
        if do_types:
            if fd[PERSONAL_OFF_TYPE1] == fd[PERSONAL_OFF_TYPE2]:
                t = rng_types.choice(type_pool)
                fd[PERSONAL_OFF_TYPE1] = t
                fd[PERSONAL_OFF_TYPE2] = t
            else:
                t1 = rng_types.choice(type_pool)
                cands = [t for t in type_pool if t != t1]
                t2 = rng_types.choice(cands) if cands else t1
                fd[PERSONAL_OFF_TYPE1] = t1
                fd[PERSONAL_OFF_TYPE2] = t2
        if do_abilities:
            for off in (PERSONAL_OFF_ABILITY1, PERSONAL_OFF_ABILITY2):
                if fd[off]:
                    fd[off] = rng_abil.choice(ability_pool)
        narc.put(i, bytes(fd))
        changed += 1
    if not _save_narc(rom, span, narc, path, log):
        return (False, {})
    return (True, {'species_entries': changed, 'types': len(type_pool), 'abilities': len(ability_pool)})

def randomize_learnsets(rom: RandNDSRom, seed: Any, log: Callable = print) -> Tuple[bool, Dict[str, Any]]:
    """Randomizes moves in wotbl.narc while preserving learn levels."""
    path = 'poketool/personal/wotbl.narc'
    span, narc = _open_narc(rom, path, log)
    if narc is None:
        return (False, {})
    moves = set()
    for i in range(narc.num_files):
        data = narc.get(i)
        for idx in range(0, len(data) - 1, 2):
            word = struct.unpack_from('<H', data, idx)[0]
            if word == 0xFFFF:
                break
            mv = word & LEARNSET_MOVE_MASK
            if mv:
                moves.add(mv)
    move_pool = sorted(moves)
    if not move_pool:
        log('[rand] ERROR: no moves found in wotbl.narc')
        return (False, {})
    rng = _cat_rng(seed, 'movesets')
    total_moves = 0
    for i in range(narc.num_files):
        data = bytearray(narc.get(i))
        for idx in range(0, len(data) - 1, 2):
            word = struct.unpack_from('<H', data, idx)[0]
            if word == 0xFFFF:
                break
            lvl = word >> LEARNSET_MOVE_BITS
            new_move = rng.choice(move_pool)
            new_word = (lvl << LEARNSET_MOVE_BITS) | (new_move & LEARNSET_MOVE_MASK)
            struct.pack_into('<H', data, idx, new_word)
            total_moves += 1
        narc.put(i, bytes(data))
    if not _save_narc(rom, span, narc, path, log):
        return (False, {})
    log(f"[rand] learnsets: {total_moves} move slots randomized across {narc.num_files} species (pool {len(move_pool)})")
    return (True, {'learnsets_species': narc.num_files, 'total_moves': total_moves})

def _mon_stride(party_size: int, body: bytes) -> int:
    if not party_size or len(body) < 8:
        return 0
    return len(body) // party_size

def trainer_mon_stride(head: bytes, body: bytes) -> int:
    if len(head) < TRAINER_HEADER_SIZE or not body:
        return 0
    party_size = head[TRDATA_OFF_PARTY_SIZE]
    return _mon_stride(party_size, body)

def trainer_party_is_sane(body: bytes, party_size: int, stride: int) -> bool:
    if not party_size or not stride or len(body) < party_size * stride:
        return False
    for m in range(party_size):
        off = m * stride + TRMON_OFF_SPECIES
        if off + 2 > len(body):
            return False
        sp = struct.unpack_from('<H', body, off)[0] & TRAINER_MON_SPECIES_MASK
        if not (1 <= sp <= MAX_SPECIES_ID):
            return False
    return True

def detect_trainer_layout(trdata: RandNARC, trpoke: RandNARC, count: int) -> Tuple[str, Dict[int, int], int]:
    extended_votes = 0
    vanilla_votes = 0
    usable = 0
    for i in range(count):
        head = trdata.get(i)
        body = trpoke.get(i)
        if len(head) < TRAINER_HEADER_SIZE or not body:
            continue
        ps = head[TRDATA_OFF_PARTY_SIZE]
        stride = _mon_stride(ps, body)
        if not stride or not trainer_party_is_sane(body, ps, stride):
            continue
        usable += 1
        if stride in (16, 20, 24, 28):
            extended_votes += 1
        elif stride in (8, 12, 16, 18, 20):
            vanilla_votes += 1
    layout = 'extended' if extended_votes >= vanilla_votes else 'vanilla'
    return (layout, TRMON_OFF_ABILITY, usable)

def randomize_trainers(rom: RandNDSRom, seed: Any, db: Dict[int, Dict[str, Any]], exclude_legendaries: bool, similar_strength: bool, log: Callable = print) -> Tuple[bool, Dict[str, Any]]:
    """Randomizes every trainer party in poketool/trainer/trdata.narc and trpoke.narc."""
    tr_path = 'poketool/trainer/trdata.narc'
    tp_path = 'poketool/trainer/trpoke.narc'
    tr_span, trdata = _open_narc(rom, tr_path, log)
    if trdata is None:
        return (False, {})
    tp_span, trpoke = _open_narc(rom, tp_path, log)
    if trpoke is None:
        return (False, {})
    rng = _cat_rng(seed, 'trainers')
    pool = rand_build_pool(db, exclude_legendaries)
    count = min(trdata.num_files, trpoke.num_files)
    layout, _, usable = detect_trainer_layout(trdata, trpoke, count)
    base_size = TRMON_SIZE_EXTENDED[TRDATATYPE_BASE] if layout == 'extended' else TRMON_SIZE_VANILLA[TRDATATYPE_BASE]
    log(f"[rand] trainers: {count} entries, pool {len(pool)} species, layout={layout} ({usable}/{count} parties readable)")
    if usable * 2 < count:
        log('[rand] ERROR: trainer party data format unsupported in this ROM.')
        return (False, {})

    def _reroll(body: bytes, party_size: int, size: int) -> Tuple[bytearray, int]:
        rolled = 0
        new_body = bytearray(len(body))
        for m in range(party_size):
            src = m * size
            dst = m * base_size
            sp = struct.unpack_from('<H', body, src + TRMON_OFF_SPECIES)[0] & TRAINER_MON_SPECIES_MASK
            if not sp:
                continue
            cands = pool
            if similar_strength and sp in db:
                filt = _rand_strength(cands, db, db[sp]['bst'])
                if filt:
                    cands = filt
            new_sp = rng.choice(cands)
            new_body[dst + 2:dst + 4] = body[src + 2:src + 4] # copy level & IVs
            struct.pack_into('<H', new_body, dst + TRMON_OFF_SPECIES, new_sp & TRAINER_MON_SPECIES_MASK)
            if layout == 'extended':
                new_body[dst + TRMON_OFF_NATURE] = TRMON_NATURE_UNSET
            rolled += 1
        return (new_body, rolled)

    mons = 0
    skipped = 0
    for i in range(count):
        head = trdata.get(i)
        if len(head) < TRAINER_HEADER_SIZE:
            skipped += 1
            continue
        ps = head[TRDATA_OFF_PARTY_SIZE]
        body = bytearray(trpoke.get(i))
        if not ps:
            continue
        stride = trainer_mon_stride(head, body)
        if not stride or not trainer_party_is_sane(body, ps, stride):
            skipped += 1
            continue
        new_body, n = _reroll(body, ps, stride)
        mons += n
        trpoke.put(i, bytes(new_body))
        new_head = bytearray(head)
        new_head[TRDATA_OFF_MON_TYPE] &= 0xFC
        trdata.put(i, bytes(new_head))

    hard_mons = 0
    for i in range(count):
        head = trdata.get(i)
        if len(head) < TRAINER_HEADER_SIZE_HARD:
            continue
        member = struct.unpack_from('<H', head, TRDATA_OFF_HARD_MEMBER)[0]
        hsize = head[TRDATA_OFF_HARD_PARTY_SIZE]
        if not member or not hsize or member >= trpoke.num_files or hsize > 6:
            continue
        body = bytearray(trpoke.get(member))
        stride = _mon_stride(hsize, body)
        if not stride or not trainer_party_is_sane(body, hsize, stride):
            continue
        new_body, n = _reroll(body, hsize, stride)
        hard_mons += n
        trpoke.put(member, bytes(new_body))
        new_head = bytearray(head)
        new_head[TRDATA_OFF_HARD_MON_TYPE] &= 0xFC
        trdata.put(i, bytes(new_head))

    if not _save_narc(rom, tp_span, trpoke, tp_path, log):
        return (False, {})
    if not _save_narc(rom, tr_span, trdata, tr_path, log):
        return (False, {})
    log(f"[rand] trainers: {mons} Pokemon rerolled (+ {hard_mons} hard-mode)")
    return (True, {'trainer_mons': mons, 'hard_mons': hard_mons, 'skipped': skipped})

def _shiny_hits(data: bytes) -> List[int]:
    """Finds threshold byte offset in ARM9 shiny check pattern (48 40 50 40 <thr> 28 01 D2)."""
    prefix = bytes((72, 64, 80, 64))
    suffix = bytes((40, 1, 210))
    out = []
    i = data.find(prefix)
    while i != -1:
        if data[i + 5:i + 8] == suffix:
            out.append(i + 4)
        i = data.find(prefix, i + 1)
    return out

def apply_shiny_odds(rom_path: str, threshold: int, log: Callable = print) -> Tuple[bool, str]:
    """Rewrites the shiny threshold byte in-place (1..255)."""
    threshold = max(1, min(255, int(threshold)))
    try:
        with open(rom_path, 'rb') as f:
            data = f.read()
    except OSError as e:
        return (False, f"could not read ROM: {e}")
    hits = _shiny_hits(data)
    if len(hits) != 1:
        return (False, f"shiny check not found ({len(hits)} matches)")
    pos = hits[0]
    cur = data[pos]
    odds = round(65536 / threshold)
    if cur == threshold:
        log(f"[shiny] already 1/{odds} - no change")
        return (True, 'already set')
    buf = bytearray(data)
    buf[pos] = threshold
    try:
        with open(rom_path, 'wb') as f:
            f.write(buf)
    except OSError as e:
        return (False, f"could not write ROM: {e}")
    log(f"[shiny] threshold {cur} -> {threshold} (~1/{odds}) at offset 0x{pos:X}")
    return (True, f"shiny odds set to ~1/{odds}")


def _b32(n: int, width: int = 0) -> str:
    out = []
    while n:
        n, rem = divmod(n, 32)
        out.append(SHARE_B32_ALPHABET[rem])
    res = ''.join(reversed(out)) or 'A'
    return res.rjust(width, 'A')

def _unb32(s: str) -> int:
    val = 0
    for ch in s.upper():
        idx = SHARE_B32_ALPHABET.find(ch)
        if idx < 0:
            raise ValueError(f"invalid base32 char: {ch}")
        val = val * 32 + idx
    return val

def _pack_flags(flags: Dict[str, Any], keys: Tuple[str, ...]) -> int:
    out = 0
    for i, k in enumerate(keys):
        if flags.get(k):
            out |= (1 << i)
    return out

def _pack_seed(s: Any) -> str:
    clean = str(s).strip() if s is not None else ''
    if not clean:
        return '0'
    if clean.isdigit() and len(clean) <= 15:
        return _b32(int(clean))
    return 'X' + base64.b32encode(clean.encode('utf-8')).decode('ascii').rstrip('=')

def _unpack_seed(s: str) -> str:
    if not s or s == '0':
        return ''
    if s.startswith('X'):
        pad = '=' * ((8 - len(s[1:]) % 8) % 8)
        try:
            return base64.b32decode((s[1:] + pad).encode('ascii')).decode('utf-8', errors='replace')
        except Exception:
            return ''
    return str(_unb32(s))

def _finish_code(prefix: str, payload: str) -> str:
    ck = hashlib.sha256(f"{prefix}-{payload}".encode('ascii')).hexdigest()[:4]
    return f"{prefix}-{payload}-{ck}"

def encode_coop_code(settings: Dict[str, Any]) -> str:
    """Encodes co-op settings into a shareable PMC-XXXX-XXXX string."""
    seed_str = _pack_seed(settings.get('coop_seed'))
    flags = _pack_flags(settings, COOP_KEYS)
    opt = 0
    if settings.get('coop_noleg'):
        opt |= 1
    if settings.get('coop_simstr'):
        opt |= 2
    raw = f"{_b32(flags, 2)}{_b32(opt, 1)}{seed_str}"
    return _finish_code(SHARE_PREFIX_COOP, raw)

def encode_world_code(settings: Dict[str, Any]) -> str:
    """Encodes personal/world settings into a shareable PMW-XXXX-XXXX string."""
    seed_str = _pack_seed(settings.get('seed'))
    flags = _pack_flags(settings, PERSONAL_KEYS)
    mode_idx = 0
    if settings.get('mode') == 'global_1to1':
        mode_idx = 1
    elif settings.get('mode') == 'random':
        mode_idx = 2
    rule_idx = 1 if settings.get('rule') == 'similar_strength' else 0
    opt = (mode_idx & 3) | ((rule_idx & 1) << 2)
    if settings.get('noleg'):
        opt |= 8
    shiny_thr = int(settings.get('shiny', SHINY_VANILLA))
    raw = f"{_b32(flags, 3)}{_b32(opt, 1)}{_b32(shiny_thr, 2)}{seed_str}"
    return _finish_code(SHARE_PREFIX_WORLD, raw)

def decode_share_code(code: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Decodes a PMC or PMW share code back into a settings dictionary."""
    clean = re.sub(r'\s+', '', str(code).upper())
    parts = clean.split('-')
    if len(parts) != 3:
        return (None, "format invalide (attendu: PREFIX-PAYLOAD-CHECKSUM)" if get_lang() == "fr" else "invalid format (expected: PREFIX-PAYLOAD-CHECKSUM)")
    prefix, payload, ck = parts
    expected_ck = hashlib.sha256(f"{prefix}-{payload}".encode('ascii')).hexdigest()[:4].upper()
    if ck != expected_ck:
        return (None, "code altéré ou corrompu (somme de contrôle incorrecte)" if get_lang() == "fr" else "tampered or corrupted code (checksum mismatch)")
    settings: Dict[str, Any] = {}
    if prefix == SHARE_PREFIX_COOP:
        flags = _unb32(payload[:2])
        for i, k in enumerate(COOP_KEYS):
            settings[k] = bool(flags & (1 << i))
        opt = _unb32(payload[2:3])
        settings['coop_noleg'] = bool(opt & 1)
        settings['coop_simstr'] = bool(opt & 2)
        settings['coop_seed'] = _unpack_seed(payload[3:])
        return (settings, None)
    elif prefix == SHARE_PREFIX_WORLD:
        flags = _unb32(payload[:3])
        for i, k in enumerate(PERSONAL_KEYS):
            settings[k] = bool(flags & (1 << i))
        opt = _unb32(payload[3:4])
        mode_idx = opt & 3
        settings['mode'] = 'global_1to1' if mode_idx == 1 else ('random' if mode_idx == 2 else 'area_1to1')
        settings['rule'] = 'similar_strength' if (opt & 4) else 'none'
        settings['noleg'] = bool(opt & 8)
        settings['shiny'] = _unb32(payload[4:6])
        settings['seed'] = _unpack_seed(payload[6:])
        return (settings, None)
    return (None, f"préfixe inconnu: {prefix}" if get_lang() == "fr" else f"unknown prefix: {prefix}")

def roll_seed() -> str:
    """Generates a random 10-digit numeric seed string."""
    return str(random.randint(1000000000, 9999999999))

def coop_categories_on(settings: Dict[str, Any]) -> bool:
    return any(bool(settings.get(k)) for k in COOP_KEYS)

def must_match_categories(settings: Dict[str, Any]) -> List[str]:
    if get_lang() == "en":
        labels = {'trainers': 'Trainers', 'types': 'Types', 'abilities': 'Abilities', 'movesets': 'Movesets'}
    else:
        labels = {'trainers': 'Dresseurs', 'types': 'Types', 'abilities': 'Talents', 'movesets': 'Capacités'}
    return [labels[k] for k in COOP_KEYS if settings.get(k)]

def rand_sidecar_path(rom_path: str) -> str:
    return rom_path + ".rand.txt"

def write_rand_sidecar(rom_path: str, summary: Dict[str, Any], settings: Dict[str, Any], in_sha1: str, out_sha1: str) -> str:
    """Writes the human-readable .rand.txt companion summary next to the ROM."""
    p = rand_sidecar_path(rom_path)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lines = [
        "Project PM randomization record",
        f"made by:      Project PM Addon Patcher (randomizer v{RAND_VERSION})",
        f"date:         {now}",
        "",
        f"input ROM:    {settings.get('in_rom', '')}",
        f"input sha1:   {in_sha1[:16]}",
        f"output sha1:  {out_sha1[:16]}",
        ""
    ]
    if summary.get('coop_code'):
        lines.append(f"co-op code (must match your friends):    {summary['coop_code']}")
    if summary.get('world_code'):
        lines.append(f"world code (optional to share):          {summary['world_code']}")
    lines.append("")
    if summary.get('coop_seed'):
        lines.append(f"co-op seed:   {summary['coop_seed']}")
    if summary.get('seed'):
        lines.append(f"personal seed: {summary['seed']}")
    shiny = settings.get('shiny', SHINY_VANILLA)
    lines.append(f"shiny odds:   {shiny} (~1/{round(65536 / max(1, shiny))})")
    lines.append("")
    if summary.get('starters'):
        s = summary['starters']
        lines.append(f"starters:     {species_name(s[0])} / {species_name(s[1])} / {species_name(s[2])}")
    if summary.get('evolutions'):
        evo_info = summary['evolutions']
        lines.append(f"evolutions:   mode = {evo_info.get('mode', 'vanilla')} ({evo_info.get('evolutions_randomized', 0)} targets changed)")
    if summary.get('honey'):
        lines.append("honey trees:  randomized across 21 trees")
    if summary.get('eggs'):
        lines.append("static encounters: randomized (Drifloon, Rotom, Spiritomb, eggs)")
    if summary.get('trades'):
        for npc, t in summary['trades'].items():
            lines.append(f"trade {npc:7s}: gives {species_name(t['give_new'])} (was {species_name(t['give_old'])}), wants {species_name(t['want_new'])} (was {species_name(t['want_old'])})")
    if summary.get('battles'):
        for label, (old, new) in summary['battles'].items():
            lines.append(f"{label}: {species_name(new)}")
    if summary.get('gifts'):
        for label, (old, new) in summary['gifts'].items():
            lines.append(f"{label}: {species_name(new)}")
    lines.append("")
    lines.append("Keep this file next to the ROM. It confirms multiplayer sync compatibility.")
    with open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    return p

def rand_run(rom_path: str, out_path: str, mode: str, rule: str,
             do_grass: bool, do_surf: bool, do_fish: bool, do_spec: bool,
             exclude_legendaries: bool, seed: Any, log: Callable = print,
             do_starters: bool = False, do_statics: bool = False, do_wilds: bool = True,
             do_battles: bool = False, do_gifts: bool = False, do_trade_get: bool = False,
             do_trade_want: bool = False, do_wild_special: bool = False,
             starters_any: bool = False, starters_pick: Optional[Tuple[int, int, int]] = None,
             do_gba_slots: bool = False, do_honey: bool = True, evo_mode: str = 'vanilla') -> Tuple[bool, Dict[str, Any]]:
    """Core wild encounters, starters, statics, and trades randomizer routine."""
    if seed is not None and seed != '':
        try:
            seed = int(seed)
        except ValueError:
            pass
        random.seed(seed)
        log(f"[rand] seed: {seed}")
    else:
        random.seed()
        log("[rand] seed: (random)")
    rom = RandNDSRom(rom_path)
    db = rand_load_pokemon_db(rom)
    res = rom.find('fielddata/encountdata/pl_enc_data.narc')
    if res is None:
        log('[rand] ERROR: pl_enc_data.narc not found')
        return (False, {})
    es, ee = res
    narc = RandNARC(rom.read(es, ee))
    areas = []
    for i in range(narc.num_files):
        fd = narc.get(i)
        areas.append(RandArea(fd, i) if len(fd) in RAND_AREA_SIZES else None)
    active = [a for a in areas if a is not None]
    pool = rand_build_pool(db, exclude_legendaries)
    sim_str = (rule == 'similar_strength')
    log(f"[rand] {len(active)} encounter areas, pool of {len(pool)} species, mode={mode}, rule={rule}")

    if do_wilds:
        if mode == 'global_1to1':
            all_sp = set()
            for a in active:
                for g, _ in a.slots(do_grass, do_surf, do_fish, do_spec):
                    v = g()
                    if v > 0:
                        all_sp.add(v)
            used = set()
            mapping = {}
            for orig in sorted(all_sp):
                cands = [s for s in pool if s not in used]
                if sim_str and orig in db:
                    filt = _rand_strength(cands, db, db[orig]['bst'])
                    if filt:
                        cands = filt
                if not cands:
                    cands = pool
                choice = random.choice(cands)
                mapping[orig] = choice
                used.add(choice)
            for a in active:
                for g, s in a.slots(do_grass, do_surf, do_fish, do_spec):
                    o = g()
                    if o > 0 and o in mapping:
                        s(mapping[o])
        elif mode == 'area_1to1':
            for group in _rand_area_groups(active):
                local = {}
                for a in group:
                    for g, s in a.slots(do_grass, do_surf, do_fish, do_spec):
                        o = g()
                        if o <= 0:
                            continue
                        if o not in local:
                            local[o] = _rand_pick(o, pool, db, sim_str)
                        s(local[o])
        else: # completely random
            for group in _rand_area_groups(active):
                first = group[0]
                pre = bytes(first.b)
                for g, s in first.slots(do_grass, do_surf, do_fish, do_spec):
                    o = g()
                    if o <= 0:
                        continue
                    s(_rand_pick(o, pool, db, sim_str))
                for a in group[1:]:
                    if bytes(a.b) == pre:
                        a.b[:] = first.b
                        continue
                    for g, s in a.slots(do_grass, do_surf, do_fish, do_spec):
                        o = g()
                        if o <= 0:
                            continue
                        s(_rand_pick(o, pool, db, sim_str))

        for i, a in enumerate(areas):
            if a is not None:
                narc.put(i, a.to_bytes())
        new = narc.to_bytes()
        if len(new) != ee - es:
            log(f"[rand] ERROR: NARC size changed {len(new)} vs {ee - es}")
            return (False, {})
        rom.write(es, ee, new)

    honey = None
    if do_honey:
        seed_norm = seed if seed not in (None, '') else None
        honey = statics_honey(rom, db, pool, mode, rule, rand_substream('honey', seed_norm), log)

    eggs = None
    if do_statics:
        seed_norm = seed if seed not in (None, '') else None
        eggs = statics_eggs(rom, db, pool, rule, rand_substream('eggs', seed_norm), log)

    evolutions = None
    if evo_mode and evo_mode != 'vanilla':
        seed_norm = seed if seed not in (None, '') else None
        evolutions = evo_randomize(rom, db, pool, evo_mode, rand_substream('evolutions', seed_norm), log)

    starters = None
    if do_starters and starters_pick:
        starters = starter_arrange(starters_pick)
        starter_apply(rom, starters, log)
        log(f"[rand] starters (chosen): {' / '.join(species_name(x) for x in starters)}")
    elif do_starters:
        spool = starter_build_pool(rom, db, evolving_only=(not starters_any))
        starters = starter_pick(spool, seed if seed not in (None, '') else None)
        starters = starter_arrange(starters)
        starter_apply(rom, starters, log)
        log(f"[rand] starters: {species_name(starters[0])} / {species_name(starters[1])} / {species_name(starters[2])}")

    battles = None
    gifts = None
    seed_x = seed if seed not in (None, '') else None
    if do_battles or do_gifts:
        battles, gifts = statics_script_sites(rom, db, pool, rule, rand_substream('battles', seed_x), rand_substream('gifts', seed_x), do_battles, do_gifts, log)
    if do_gifts:
        fossils = fossils_randomize(rom, db, pool, rule, rand_substream('fossils', seed_x), log)
        if fossils:
            gifts = dict(gifts or {}, **fossils)

    wild_special = None
    if do_wild_special or do_gba_slots:
        wild_special = special_wilds(rom, db, pool, mode, rule, rand_substream('wild-special', seed_x), log, do_special=do_wild_special, do_gba=do_gba_slots)

    trades = None
    if do_trade_get or do_trade_want:
        wild_species = set()
        for a in active:
            for g, _ in a.slots(True, True, True, True):
                v = g()
                if v > 0:
                    wild_species.add(v)
        trades = trades_randomize(rom, db, pool, rule, wild_species, rand_substream('trade-get', seed_x), rand_substream('trade-want', seed_x), do_trade_get, do_trade_want, log)

    rom.save(out_path)
    return (True, {
        'areas': len(active),
        'pool': len(pool),
        'starters': starters,
        'honey': honey,
        'eggs': eggs,
        'evolutions': evolutions,
        'battles': battles,
        'gifts': gifts,
        'trades': trades,
        'wild_special': wild_special
    })

def randomize_rom(
    in_rom: Optional[str] = None,
    out_rom: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None,
    log: Callable = print,
    rom_path: Optional[str] = None,
    out_path: Optional[str] = None
) -> Tuple[bool, Dict[str, Any]]:
    """Master coordinator that randomizes in_rom -> out_rom and outputs .rand.txt."""
    actual_in = in_rom or rom_path
    actual_out = out_rom or out_path or actual_in
    if not actual_in or not os.path.isfile(actual_in):
        log(f"[rand] ERROR: no such ROM: {actual_in}")
        return (False, {})
    in_rom = actual_in
    out_rom = actual_out
    if settings is None:
        settings = {}

    # Ensure any existing save file (.sav / .dsv) is safely backed up before randomizing!
    try:
        from core.save_manager import backup_and_sync_save
        backup_and_sync_save(actual_in, actual_out, log_cb=log)
    except Exception as e:
        log(f"[Backup] Note sauvegarde: {e}")

    with open(actual_in, 'rb') as f:
        in_sha = hashlib.sha1(f.read()).hexdigest()

    do_wilds = bool(settings.get('wilds', True))
    do_starters = bool(settings.get('starters', True))
    do_honey = bool(settings.get('honey', True))
    do_statics = bool(settings.get('statics', True))
    evo_mode = settings.get('evolutions_mode', 'vanilla')
    do_battles = bool(settings.get('battles', False))
    do_gifts = bool(settings.get('gifts', False))
    do_trade_get = bool(settings.get('trade_get', False))
    do_trade_want = bool(settings.get('trade_want', False))
    do_wild_special = bool(settings.get('wild_special', False))
    do_gba_slots = bool(settings.get('gba_slots', False))
    mode = settings.get('mode', 'area_1to1')
    rule = settings.get('rule', 'similar_strength')
    noleg = bool(settings.get('noleg', True))
    starters_any = bool(settings.get('starters_any', False))
    starters_pick = settings.get('starters_pick')
    seed = settings.get('seed') or roll_seed()
    settings['seed'] = seed

    log(t("rand_log_start_world"))
    ok, summary = rand_run(
        in_rom, out_rom, mode=mode, rule=rule,
        do_grass=True, do_surf=True, do_fish=True, do_spec=True,
        exclude_legendaries=noleg, seed=seed, log=log,
        do_starters=do_starters, do_statics=do_statics, do_wilds=do_wilds,
        do_battles=do_battles, do_gifts=do_gifts, do_trade_get=do_trade_get,
        do_trade_want=do_trade_want, do_wild_special=do_wild_special,
        starters_any=starters_any, starters_pick=starters_pick, do_gba_slots=do_gba_slots,
        do_honey=do_honey, evo_mode=evo_mode
    )
    if not ok:
        return (False, {})

    coop_on = coop_categories_on(settings)
    coop_code = None
    if coop_on:
        coop_seed = settings.get('coop_seed') or roll_seed()
        settings['coop_seed'] = coop_seed
        log(t("rand_log_start_coop"))
        rom = RandNDSRom(out_rom)
        db = rand_load_pokemon_db(rom)
        c_noleg = bool(settings.get('coop_noleg', True))
        c_simstr = bool(settings.get('coop_simstr', False))
        if settings.get('types') or settings.get('abilities'):
            randomize_species_data(rom, coop_seed, bool(settings.get('types')), bool(settings.get('abilities')), log)
        if settings.get('movesets'):
            randomize_learnsets(rom, coop_seed, log)
        if settings.get('trainers'):
            randomize_trainers(rom, coop_seed, db, c_noleg, c_simstr, log)
        rom.save(out_rom)
        coop_code = encode_coop_code(settings)
        summary['coop_code'] = coop_code
        summary['coop_seed'] = coop_seed
        coop_label = "[rand] Co-op Code (to share):" if get_lang() == "en" else "[rand] Code Co-op (à partager) :"
        log(f"{coop_label} {coop_code}")

    world_code = encode_world_code(settings)
    summary['world_code'] = world_code
    summary['seed'] = seed

    shiny = int(settings.get('shiny', SHINY_VANILLA))
    if shiny != SHINY_VANILLA:
        log(t("rand_log_shiny"))
        apply_shiny_odds(out_rom, shiny, log)

    with open(out_rom, 'rb') as f:
        out_sha = hashlib.sha1(f.read()).hexdigest()
    sidecar = write_rand_sidecar(out_rom, summary, settings, in_sha, out_sha)
    log(t("rand_log_complete", os.path.basename(sidecar)))
    return (True, summary)

def run_selftest() -> bool:
    """Verifies all invariants and compatibility assertions."""
    assert max(RAND_LEGENDARIES) == 493
    assert len(RAND_LEGENDARIES) == 35
    assert len(SPECIES_NAMES) == 493
    assert _mon_stride(0, bytes(16)) == 0
    assert TRMON_SIZE_EXTENDED == {0: 16, 1: 24, 2: 20, 3: 28}
    assert TRMON_SIZE_VANILLA == {0: 8, 1: 16, 2: 12, 3: 20}
    test_settings = {'coop_seed': '9854609529', 'trainers': True, 'coop_noleg': False, 'coop_simstr': False}
    c_code = encode_coop_code(test_settings)
    dec, err = decode_share_code(c_code)
    assert err is None
    assert dec['coop_seed'] == '9854609529'
    assert dec['trainers'] is True
    assert dec['coop_noleg'] is False
    return True

if __name__ == '__main__':
    print("Running randomizer selftest...")
    if run_selftest():
        print("[OK] All randomizer selftests passed successfully!")

