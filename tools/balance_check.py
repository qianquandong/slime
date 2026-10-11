"""Slime Sweets Farm - config closure check + deterministic economy replay.

Reads ../config/*.csv (the PRD's initial design values) and:
  1. generates the species list from the breeding rules,
  2. checks that recipes, resources and unlocks close (no dangling refs,
     nothing in P0 that needs P1 or a purchase, every signature reachable),
  3. prints the worked economy path used in PRD chapter 7,
  4. validates a real post-FTUE economic path; does not forecast player pacing.

Standard library only:  python tools/balance_check.py [--species-csv]
"""
import csv
import math
import sys
from pathlib import Path
from dataclasses import dataclass, field

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config"


def load(name):
    with open(CFG / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


FLAVORS = {r["id"]: r for r in load("flavors.csv")}
DESSERTS = {r["id"]: r for r in load("desserts.csv")}
SIGS = {r["id"]: r for r in load("signatures.csv")}
LEVELS = {int(r["level"]): r for r in load("levels.csv")}
FAC = {r["id"]: r for r in load("facilities.csv")}
ORDER_RULES = load("order_rules.csv")
P = {r["key"]: r["value"] for r in load("params.csv")}
COSMETICS = {r["id"]: r for r in load("cosmetics.csv")}
DAILY_TASKS = load("daily_tasks.csv")
IAP = load("iap_products.csv")
ADS = load("ad_placements.csv")
VISITORS = load("visitors.csv")


def pf(k):
    return float(P[k])


def rnd(x):
    """Round half up (the PRD's rounding rule; Python's round() is half-to-even)."""
    return int(math.floor(x + 0.5))


for d in DESSERTS.values():
    d["recipe_map"] = {k: int(v) for k, v in (x.split(":") for x in d["recipe"].split("|"))}
MAT2FLAVOR = {f["material_id"]: fid for fid, f in FLAVORS.items()}
FOOD2FLAVOR = {f["food_id"]: fid for fid, f in FLAVORS.items()}
TIER = {fid: int(f["tier"]) for fid, f in FLAVORS.items()}
P0_FLAVORS = [fid for fid, f in FLAVORS.items() if f["scope"] == "P0"]

# ---------------------------------------------------------------- species


def species_name(body, pattern):
    b = FLAVORS[body]["flavor_name"]
    if body == pattern:
        return "Sugar Slime" if body == "plain" else f"Pure {b} Slime"
    if pattern == "plain":
        return f"{b} Slime"
    return f"{b} {FLAVORS[pattern]['flavor_name']} Slime"


def species_kind(body, pattern):
    if body == pattern:
        return "starter" if body == "plain" else "pure"
    if pattern == "plain":
        return "basic"
    if body == "plain":
        return "sugar-pattern"
    return "blend"


def tier_sum(body, pattern):
    return TIER[body] + TIER[pattern]


def gen_species(scopes=("P0",)):
    flv = [fid for fid, f in FLAVORS.items() if f["scope"] in scopes]
    out = []
    for a in flv:
        for b in flv:
            k = 1 + tier_sum(a, b)
            out.append({
                "id": f"sp_{a}_{b}",
                "name": species_name(a, b),
                "kind": species_kind(a, b),
                "body": a,
                "pattern": b,
                "treat": "",
                "unlock_level": max(int(FLAVORS[a]["unlock_level"]), int(FLAVORS[b]["unlock_level"])),
                "breed_min": int(pf("breed_time_unit") * k),
                "fee": int(pf("breed_fee_unit") * k),
                "discovery_xp": int(pf("discovery_xp_unit") * k),
                "scope": "P0" if all(FLAVORS[x]["scope"] == "P0" for x in (a, b)) else "P1",
            })
    for s in SIGS.values():
        a, b = s["body_flavor"], s["pattern_flavor"]
        k = 1 + tier_sum(a, b)
        out.append({
            "id": s["id"], "name": s["name"], "kind": "signature", "body": a, "pattern": b,
            "treat": s["treat_dessert"],
            "unlock_level": max(int(FLAVORS[a]["unlock_level"]), int(FLAVORS[b]["unlock_level"]),
                                int(DESSERTS[s["treat_dessert"]]["unlock_level"]), unlock_level_of("treat_slot")),
            "breed_min": int(pf("breed_time_unit") * k * pf("signature_time_mult")),
            "fee": int(pf("breed_fee_unit") * k),
            "discovery_xp": int(pf("signature_discovery_xp")),
            "scope": s["scope"],
        })
    return out


def unlock_level_of(key):
    for lv, r in LEVELS.items():
        if key in r["unlocks"].split("|"):
            return lv
    return None


def yield_per_food(body, pattern, food_flavor, best_friend=False):
    y = pf("yield_base")
    if food_flavor == body:
        y += pf("yield_body_bonus")
    if pattern != "plain" and food_flavor == pattern:
        y += pf("yield_pattern_bonus")
    if best_friend:
        y += pf("yield_bestfriend_bonus")
    return int(y)


# Scripted FTUE: three free snacks each, one Sugar from squeezing, one Jelly order.
FTUE_END_PANTRY = {
    "mat_jam": int(pf("expression_streak")) * yield_per_food("plain", "plain", "strawberry")
               - DESSERTS["d_jelly"]["recipe_map"]["mat_jam"],
    "mat_cream": int(pf("expression_streak")) * yield_per_food("plain", "plain", "cream"),
    "mat_sugar": 1 - DESSERTS["d_jelly"]["recipe_map"]["mat_sugar"],
}

# ---------------------------------------------------------------- closure checks

FEATURE_KEYS = {"kitchen", "order_board", "squeeze", "codex", "daily_tasks", "treat_slot",
                "visitor_requests",
                "p1_hook_matcha", "mvp_level_cap", "none"}


def check_closure():
    errors, notes = [], []
    known = set(FAC) | set(DESSERTS) | set(SIGS) | set(COSMETICS) | FEATURE_KEYS | {f["food_id"] for f in FLAVORS.values()}
    known |= {f"flavor_{fid}" for fid in FLAVORS}
    for lv, r in LEVELS.items():
        for k in r["unlocks"].split("|"):
            if k not in known:
                errors.append(f"levels.csv L{lv}: unknown unlock key '{k}'")
    # flavor unlock levels must match level table
    for fid, f in FLAVORS.items():
        if f["scope"] != "P0":
            continue
        lv = int(f["unlock_level"])
        key_lv = unlock_level_of(f"flavor_{fid}") or unlock_level_of(f["food_id"])
        if key_lv != lv:
            errors.append(f"flavor {fid}: unlock_level {lv} but level table says {key_lv}")
    # dessert materials available by dessert unlock; formula consistency
    for did, d in DESSERTS.items():
        lv = int(d["unlock_level"])
        if d["scope"] == "P0" and unlock_level_of(did) != lv:
            errors.append(f"dessert {did}: unlock_level {lv} but level table says {unlock_level_of(did)}")
        raw = 0
        for m, q in d["recipe_map"].items():
            fl = FLAVORS[MAT2FLAVOR[m]]
            raw += int(fl["material_value"]) * q
            if int(fl["unlock_level"]) > lv:
                errors.append(f"dessert {did} (L{lv}) needs {m} unlocked at L{fl['unlock_level']}")
            if d["scope"] == "P0" and fl["scope"] != "P0":
                errors.append(f"P0 dessert {did} needs P1 material {m}")
        price = rnd(raw * pf("dessert_price_mult"))
        xp = rnd(price / pf("dessert_xp_div"))
        if price != int(d["sell_price"]) or xp != int(d["xp"]):
            errors.append(f"dessert {did}: price/xp {d['sell_price']}/{d['xp']} != formula {price}/{xp}")
        if price <= raw:
            errors.append(f"dessert {did}: sell price {price} <= raw material value {raw}")
    # Positive food inputs. Reference material value is NOT raw-sale proceeds.
    for fid, f in FLAVORS.items():
        if int(f["food_price"]) <= 0 or int(f["digest_min"]) <= 0:
            errors.append(f"food {fid}: invalid price/duration")
    # Free housing supports one of each P0 species without rehoming or IAP.
    p0_species = [s for s in gen_species() if s["scope"] == "P0"]
    free_capacity = int(FAC["pen_1"]["effect_value"]) + int(FAC["house_1"]["effect_value"])
    if free_capacity < len(p0_species):
        errors.append(f"free initial capacity {free_capacity} < P0 species {len(p0_species)}")
    # signatures: inputs unlocked by card level, unique combos, no clash with P0-only rules
    seen = set()
    treat_lv = unlock_level_of("treat_slot")
    for sid, s in SIGS.items():
        lv = int(s["card_unlock_level"])
        if s["scope"] == "P0" and unlock_level_of(sid) != lv:
            errors.append(f"signature {sid}: card level {lv} but level table says {unlock_level_of(sid)}")
        for fl in (s["body_flavor"], s["pattern_flavor"]):
            if int(FLAVORS[fl]["unlock_level"]) > lv:
                errors.append(f"signature {sid}: flavor {fl} unlocks after card level {lv}")
            if s["scope"] == "P0" and FLAVORS[fl]["scope"] != "P0":
                errors.append(f"P0 signature {sid} needs P1 flavor {fl}")
        t = DESSERTS[s["treat_dessert"]]
        if int(t["unlock_level"]) > lv:
            errors.append(f"signature {sid}: treat {t['id']} unlocks after card level {lv}")
        if treat_lv is None or treat_lv > lv:
            errors.append(f"signature {sid}: treat slot not unlocked by L{lv}")
        key = (s["body_flavor"], s["pattern_flavor"], s["treat_dessert"])
        if key in seen:
            errors.append(f"signature {sid}: duplicate recipe {key}")
        seen.add(key)
    # facilities referenced by levels exist with matching level_req
    for fid, f in FAC.items():
        lv = unlock_level_of(fid)
        if int(f["level_req"]) > 1 and lv != int(f["level_req"]):
            errors.append(f"facility {fid}: level_req {f['level_req']} but level table says {lv}")
    # Attainable potential before optional spending, not guaranteed actual income.
    star_cost_by_lv, star_income_by_lv = {}, {}
    sp = gen_species()
    for lv in sorted(LEVELS):
        star_cost_by_lv[lv] = sum(int(f["cost_star_sugar"]) for f in FAC.values() if int(f["level_req"]) <= lv)
        attainable = sum(int(LEVELS[x]["star_sugar_reward"]) for x in LEVELS if x <= lv)
        attainable += sum(int(pf("discovery_star_sugar")) for s in sp
                          if s["scope"] == "P0" and s["kind"] not in ("starter", "signature") and s["unlock_level"] <= lv)
        star_income_by_lv[lv] = attainable
        if attainable < star_cost_by_lv[lv]:
            errors.append(f"star sugar deficit at L{lv}: attainable {attainable} < facility cost {star_cost_by_lv[lv]}")
    notes.append(("star_sugar", star_cost_by_lv, star_income_by_lv))
    # reachability: BFS over owned species from two starters, flavors gated by level 12
    owned = {("plain", "plain")}
    unlocked = [fid for fid in P0_FLAVORS]
    changed = True
    while changed:
        changed = False
        for a in unlocked:      # any owned slime can express any unlocked flavor by diet
            for b in unlocked:
                if (a, b) not in owned and len(owned) >= 1:
                    owned.add((a, b))
                    changed = True
    for s in sp:
        if s["scope"] == "P0" and (s["body"], s["pattern"]) not in owned:
            errors.append(f"species {s['id']} unreachable")
    return errors, notes


# ---------------------------------------------------------------- strings

# Worst-case lengths used to check max_chars (longest real value of each placeholder).
PLACEHOLDER_LEN = {"name": 12, "count": 2, "coins": 5, "time": 6, "level": 2, "species": 24,
                   "material": 13, "flavor": 10, "dessert": 20, "customer": 13, "visitor": 13,
                   "color": 15, "pattern": 17, "body": 10, "swirl": 10, "item": 20, "facility": 16,
                   "star": 2, "xp": 3, "progress": 1, "max": 2, "found": 2, "total": 2, "date": 12,
                   "hours": 2, "days": 2, "version": 8, "id": 12, "personality": 8, "food": 12, "price": 6}


def icu_variants(text):
    """Expand '{count, plural, one {...} other {...}}' into its branches ('#' -> count)."""
    import re
    m = re.search(r"\{(\w+), plural,", text)
    if not m:
        return [text]
    start = m.start()
    depth, i = 0, start
    while i < len(text):
        depth += text[i] == "{"
        depth -= text[i] == "}"
        i += 1
        if depth == 0:
            break
    body = text[m.end():i - 1]
    branches = re.findall(r"\w+\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", body)
    out = []
    for b in branches:
        out += icu_variants(text[:start] + b.replace("#", "{" + m.group(1) + "}") + text[i:])
    return out


def rendered_len(text):
    import re
    best = 0
    for v in icu_variants(text):
        n = len(re.sub(r"\{(\w+)\}", lambda mm: "x" * PLACEHOLDER_LEN.get(mm.group(1), 10), v))
        best = max(best, n)
    return best


def check_strings():
    rows = list(csv.DictReader(open(CFG / "strings.csv", newline="", encoding="utf-8")))
    errs, ids = [], set()
    for r in rows:
        if r["string_id"] in ids:
            errs.append(f"duplicate string id {r['string_id']}")
        ids.add(r["string_id"])
        n = rendered_len(r["english"])
        if n > int(r["max_chars"]):
            errs.append(f"{r['string_id']}: worst-case {n} chars > max {r['max_chars']}")
    return rows, errs


def check_config_string_refs(rows):
    """String ids and item ids referenced from config tables must exist."""
    ids = {r["string_id"] for r in rows}
    refs = [("signatures", s["clue_string_id"]) for s in SIGS.values()]
    refs += [("cosmetics", c["name_string_id"]) for c in COSMETICS.values()]
    refs += [("daily_tasks", t["string_id"]) for t in DAILY_TASKS]
    refs += [("iap_products", i[k]) for i in IAP for k in ("name_string_id", "desc_string_id")]
    refs += [("ad_placements", a["string_id"]) for a in ADS]
    refs += [("visitors", v["name_string_id"]) for v in VISITORS]
    errs = [f"{t}: string id {sid} missing" for t, sid in refs if sid not in ids]
    for i in IAP:
        for g in i["grants"].split("|"):
            if g.startswith("hat_") and g not in COSMETICS:
                errs.append(f"iap_products {i['product_id']}: grants unknown cosmetic {g}")
            if g.startswith("hat_") and COSMETICS.get(g, {}).get("price") != i["product_id"]:
                errs.append(f"iap_products {i['product_id']}: cosmetic {g} not sourced from this product")
    for c in COSMETICS.values():
        if c["price_type"] == "iap" and not any(i["product_id"] == c["price"] for i in IAP):
            errs.append(f"cosmetics {c['id']}: unknown iap product {c['price']}")
    return errs


def check_doc_string_refs(rows):
    """Every `UPPER_CASE` token cited in docs/prd/*.md must be a real string id."""
    import re
    ids = {r["string_id"] for r in rows} | {species_string_id(sp) for sp in gen_species(("P0", "P1"))}
    ignore = {"ROUND_HALF_UP", "P0", "P1", "P2", "IDFA", "ATT", "CRC32", "JWS", "UTC", "CDN", "SDK", "UI", "XP",
              "IAP", "FTUE", "ASTC", "LUT", "MVP", "OK", "CJK", "NPPA", "ICP", "ID", "URL"}
    errs = []
    for md in sorted((ROOT / "docs" / "prd").glob("*.md")):
        if md.name.startswith("_"):
            continue
        for tok in set(re.findall(r"`([A-Z][A-Z0-9_]{2,})`", md.read_text(encoding="utf-8"))):
            if tok not in ids and tok not in ignore:
                errs.append(f"{md.name}: `{tok}` is not in config/strings.csv")
    return errs


def species_string_id(sp):
    return "SP_" + sp["id"].upper().replace("SP_", "")


def strings_markdown(rows):
    sp = gen_species(("P0", "P1"))
    out = ["| String ID | English Text | 中文用途说明 | 出现位置 | 上限 |", "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| `{r['string_id']}` | {r['english'].replace('|', '/')} | {r['zh_note']} | {r['location']} | {r['max_chars']} |")
    for s in sp:
        sid = species_string_id(s)
        note = "品种名（" + ("招牌品种" if s["kind"] == "signature" else "规则生成") + f"，{s['scope']}）"
        out.append(f"| `{sid}` | {s['name']} | {note} | 图鉴/宠物详情/孵化 | 24 |")
    return "\n".join(out)


# ---------------------------------------------------------------- worked path (PRD ch.7)

@dataclass
class Food:
    flavor: str
    remaining: int
    paid: int
    reserved: int = 0


@dataclass
class Pet:
    uid: str
    body: str
    pattern: str
    showing: str
    species_id: str = ""
    streak_food: str = ""
    streak_count: int = 0
    queue: list = field(default_factory=list)
    in_nest: bool = False
    in_pen: bool = True


class Economy:
    """Deterministic PRD economic replay, not a player or retention simulator.

    Covers integer food batches, reservations, feeding/expression, breeding
    snapshots/parent locks, hatch capacity and order debits. UI, friendship,
    randomness, daily tasks, clocks and save persistence are not modelled.
    """

    def __init__(self):
        first = next(s for s in gen_species() if s["id"] == "sp_strawberry_cream")
        self.level = 2  # the scripted first discovery crosses the L1 threshold
        self.coins = int(pf("ftue_initial_coins") + pf("ftue_order_coins")
                         + pf("ftue_visitor_coins")) + int(LEVELS[2]["coin_reward"])
        self.xp = int(pf("ftue_order_xp") + pf("ftue_visitor_xp")) + first["discovery_xp"] - int(LEVELS[1]["xp_to_next"])
        self.star = int(pf("discovery_star_sugar") + pf("visitor_star_sugar")) + int(LEVELS[2]["star_sugar_reward"])
        self.spoons = int(LEVELS[2]["spoon_reward"])
        self.pantry = {f["material_id"]: 0 for f in FLAVORS.values()}
        self.pantry.update(FTUE_END_PANTRY)
        self.pets = {
            "Mochi": Pet("Mochi", "plain", "plain", "strawberry", "sp_plain_plain"),
            "Puff": Pet("Puff", "plain", "plain", "cream", "sp_plain_plain"),
            "Berry": Pet("Berry", "strawberry", "cream", "strawberry", "sp_strawberry_cream"),
        }
        self.jar_cap = int(FAC["pantry_1"]["effect_value"])
        self.bowl_cap = int(FAC["feeder_1"]["effect_value"])
        self.pen_cap = int(FAC["pen_1"]["effect_value"])
        self.house_cap = int(FAC["house_1"]["effect_value"])
        self.nest_cap = int(FAC["nest_1"]["effect_value"])
        self.discovered = {"sp_plain_plain", "sp_strawberry_cream"}
        self.nests = []
        self.breed_count = 1  # scripted first breed already hatched
        self.starter_claimed = False
        self.minutes = 0

    @classmethod
    def ftue_end(cls):
        game = cls()
        game.starter_bowls()
        return game

    def starter_bowls(self):
        if self.starter_claimed:
            raise ValueError("starter bowls already claimed")
        minutes = int(pf("ftue_starter_bowl_min"))
        plan = [("Mochi", "plain"), ("Puff", "cream"), ("Berry", "strawberry")]
        batches = [(uid, f, minutes // int(FLAVORS[f]["digest_min"])) for uid, f in plan]
        if any(self.pets[uid].queue for uid, _, _ in batches):
            raise ValueError("starter snapshot requires empty bowls")
        cost = sum(n * int(FLAVORS[f]["food_price"]) for _, f, n in batches)
        if self.coins < cost:
            raise ValueError("not enough coins")
        for uid, f, n in batches:
            self.feed(uid, f, n)
        self.starter_claimed = True

    def feed(self, uid, flavor, count, free=False):
        pet = self.pets[uid]
        f = FLAVORS[flavor]
        if count <= 0 or f["scope"] != "P0" or int(f["unlock_level"]) > self.level:
            raise ValueError("invalid or locked food")
        duration = int(f["digest_min"])
        paid = 0 if free else int(f["food_price"])
        if sum(x.remaining for x in pet.queue) + duration * count > self.bowl_cap:
            raise ValueError("bowl full")
        if self.coins < paid * count:
            raise ValueError("not enough coins")
        self.coins -= paid * count
        for _ in range(count):
            pet.queue.append(Food(flavor, duration, paid))
            pet.streak_count = pet.streak_count + 1 if pet.streak_food == flavor else 1
            pet.streak_food = flavor
            pet.streak_count = min(int(pf("expression_streak")), pet.streak_count)
            if pet.streak_count == int(pf("expression_streak")):
                pet.showing = flavor

    def swap_snack(self, uid):
        """Return only not-yet-started food, at actual purchase price.

        Expression is sticky. An active food's reservation and time survive.
        Free food cannot create coins. Daily feeding counters are never reset.
        """
        pet = self.pets[uid]
        refund = sum(x.paid for x in pet.queue if not x.reserved)
        pet.queue = [x for x in pet.queue if x.reserved]
        self.coins += refund
        return refund

    def advance(self, minutes):
        for _ in range(minutes):
            reserved = {m: 0 for m in self.pantry}
            for pet in self.pets.values():
                for food in pet.queue:
                    reserved[FLAVORS[food.flavor]["material_id"]] += food.reserved
            # Reserve whole yields in stable UID order before advancing any pet.
            for uid in sorted(self.pets):
                pet = self.pets[uid]
                if not pet.in_pen or any(x.reserved for x in pet.queue):
                    continue
                for food in pet.queue:
                    mat = FLAVORS[food.flavor]["material_id"]
                    y = yield_per_food(pet.body, pet.pattern, food.flavor)
                    if self.pantry[mat] + reserved[mat] + y <= self.jar_cap:
                        food.reserved = y
                        reserved[mat] += y
                        break  # blocked foods stay queued; try another flavor
            for pet in self.pets.values():
                if not pet.in_pen:
                    continue
                food = next((x for x in pet.queue if x.reserved), None)
                if food is not None:
                    food.remaining -= 1
                    if food.remaining == 0:
                        mat = FLAVORS[food.flavor]["material_id"]
                        self.pantry[mat] += food.reserved
                        assert self.pantry[mat] <= self.jar_cap
                        pet.queue.remove(food)
            self.minutes += 1

    def add_xp(self, value):
        self.xp += value
        while self.level < max(LEVELS) and self.xp >= int(LEVELS[self.level]["xp_to_next"]):
            self.xp -= int(LEVELS[self.level]["xp_to_next"])
            self.level += 1
            reward = LEVELS[self.level]
            self.coins += int(reward["coin_reward"])
            self.star += int(reward["star_sugar_reward"])
            self.spoons += int(reward["spoon_reward"])

    def order(self, lines):
        need, price, xp = {}, 0, 0
        for did, count in lines:
            d = DESSERTS[did]
            if count <= 0 or d["scope"] != "P0" or int(d["unlock_level"]) > self.level:
                raise ValueError("invalid or locked dessert")
            for mat, qty in d["recipe_map"].items():
                need[mat] = need.get(mat, 0) + qty * count
            price += int(d["sell_price"]) * count
            xp += int(d["xp"]) * count
        if any(self.pantry[m] < n for m, n in need.items()):
            raise ValueError("missing materials")
        for mat, qty in need.items():
            self.pantry[mat] -= qty
        coins = rnd(price * pf("order_coin_mult"))
        self.coins += coins
        self.add_xp(xp)
        return coins, xp

    def breed(self, body_uid, swirl_uid, treat=""):
        if body_uid == swirl_uid:
            raise ValueError("parents must differ")
        a, b = self.pets[body_uid], self.pets[swirl_uid]
        if a.in_nest or b.in_nest or len(self.nests) >= self.nest_cap:
            raise ValueError("parent or nest busy")
        needs = {}
        if treat:
            d = DESSERTS[treat]
            if self.level < unlock_level_of("treat_slot") or d["scope"] != "P0" or int(d["unlock_level"]) > self.level:
                raise ValueError("treat locked")
            needs = d["recipe_map"]  # scenario bakes directly from ingredients
        sig = next((s for s in gen_species() if s["kind"] == "signature"
                    and (s["body"], s["pattern"], s["treat"]) == (a.showing, b.showing, treat)), None)
        result = sig or next(s for s in gen_species() if s["id"] == f"sp_{a.showing}_{b.showing}")
        if result["scope"] != "P0" or result["unlock_level"] > self.level:
            raise ValueError("species locked")
        if self.coins < result["fee"] or any(self.pantry[m] < n for m, n in needs.items()):
            raise ValueError("not enough breeding resources")
        self.coins -= result["fee"]
        for m, n in needs.items():
            self.pantry[m] -= n
        self.breed_count += 1
        duration = result["breed_min"]
        if self.breed_count in (2, 3):
            duration = min(duration, int(pf(f"ftue_{'second' if self.breed_count == 2 else 'third'}_breed_min")))
        job = {"ready": self.minutes + duration, "result": result,
               "parents": (body_uid, swirl_uid)}
        self.nests.append(job)
        a.in_nest = b.in_nest = True
        return job

    def hatch(self, job, name):
        if job not in self.nests or job["ready"] > self.minutes or name in self.pets:
            raise ValueError("invalid hatch")
        if len(self.pets) >= self.pen_cap + self.house_cap:
            raise ValueError("no room; ready pod is retained")
        sp = job["result"]
        in_pen = sum(p.in_pen for p in self.pets.values()) < self.pen_cap
        self.pets[name] = Pet(name, sp["body"], sp["pattern"], sp["body"], sp["id"], in_pen=in_pen)
        for uid in job["parents"]:
            self.pets[uid].in_nest = False
        self.nests.remove(job)
        if sp["id"] not in self.discovered:
            self.discovered.add(sp["id"])
            self.add_xp(sp["discovery_xp"])
            self.star += int(pf("signature_star_sugar" if sp["kind"] == "signature" else "discovery_star_sugar"))

    def has_visitor_match(self, body, pattern):
        return any((p.body, p.pattern) == (body, pattern) for p in self.pets.values())


def worked_path():
    """Replay PRD 7.7 from the actual post-tutorial, paid-bowl snapshot."""
    g = Economy.ftue_end()
    assert (g.coins, g.level, g.xp, g.star, g.spoons) == (90, 2, 30, 4, 1)
    assert all(sum(f.remaining for f in p.queue) == 60 for p in g.pets.values())
    out = ["FTUE end: L2, 30/80 XP, 90 coins, 4 stars, 1 spoon; bowls 60/60/60 min"]
    second = g.breed("Puff", "Mochi")
    assert second["result"]["id"] == "sp_cream_plain" and second["ready"] == 2
    assert g.coins == 50
    g.advance(2)
    g.hatch(second, "Creamy")
    assert (g.xp, g.star) == (50, 5)
    g.advance(58)
    assert (g.pantry["mat_sugar"], g.pantry["mat_cream"], g.pantry["mat_jam"]) == (24, 21, 23)
    out.append("t=60: second breed hatched; 50 coins, 50/80 XP; Sugar 24, Cream 21, Jam 23")
    for lines in [[("d_shortcake", 2)], [("d_puff", 2), ("d_jelly", 2)], [("d_cookie", 2)]]:
        g.order(lines)
    assert (g.coins, g.xp) == (176, 74)
    g.advance(1)  # L2 order-slot refill, explicitly selected fixture order
    g.order([("d_shortcake", 2), ("d_jelly", 2)])
    assert (g.coins, g.level, g.xp, g.star, g.spoons) == (336, 3, 10, 6, 2)
    assert (g.pantry["mat_sugar"], g.pantry["mat_cream"], g.pantry["mat_jam"]) == (6, 9, 7)
    g.feed("Puff", "lemon", 3)
    third = g.breed("Puff", "Berry")
    assert third["ready"] == 66  # third-breed 5-minute override, not the normal 40
    assert g.coins == 226
    g.advance(5)
    g.hatch(third, "Sunny")
    assert (g.level, g.xp, g.coins, g.star, g.spoons) == (3, 50, 226, 7, 2)
    assert (g.pantry["mat_sugar"], g.pantry["mat_cream"], g.pantry["mat_jam"], g.pantry["mat_lemon"]) == (6, 9, 7, 0)
    out.append("t=66 end: L3, 50/200 XP, 226 coins, 7 stars, 2 spoons; Sugar 6, Cream 9, Jam 7, Lemon 0")
    out.append("Puff: Lemon showing, 55 min food remaining; Sunny in Nap House; no production from housed pets")
    return out


def main():
    errors, notes = check_closure()
    rows, serr = check_strings()
    errors += serr + check_doc_string_refs(rows) + check_config_string_refs(rows)
    print("== closure check ==")
    print("OK" if not errors else "\n".join("ERROR " + e for e in errors))
    for kind, cost, inc in notes:
        print("star sugar  level: facility_cost_cum / attainable_cum (level rewards + first discoveries unlocked by that level; excludes tasks, visitors, ads)")
        print("  " + "  ".join(f"L{lv}:{cost[lv]}/{inc[lv]}" for lv in sorted(cost)))

    sp = gen_species(("P0", "P1"))
    if "--species-csv" in sys.argv:
        with open(CFG / "species.generated.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(sp[0].keys()))
            w.writeheader()
            w.writerows(sp)
        print(f"wrote config/species.generated.csv ({len(sp)} rows)")
    if "--strings-md" in sys.argv:
        out = ROOT / "docs" / "prd" / "appendix-a-strings.md"
        marker = "## A.2 文案总表"
        head = out.read_text(encoding="utf-8").split(marker)[0]
        out.write_text(head + marker + "\n\n" + strings_markdown(rows) + "\n", encoding="utf-8")
        print(f"rewrote table in {out.relative_to(ROOT)}")
    print(f"strings: {len(rows)} rows (all within max_chars at worst-case placeholder lengths)"
          if not serr else f"strings: {len(serr)} over limit")
    p0 = [s for s in sp if s["scope"] == "P0"]
    print(f"\n== species == P0 {len(p0)} (incl. starter), P1 adds {len(sp) - len(p0)}")
    print(f"P0 total first-discovery xp {sum(s['discovery_xp'] for s in p0 if s['kind'] != 'starter')}, "
          f"total breed minutes (one each) {sum(s['breed_min'] for s in p0 if s['kind'] != 'starter')}")

    print("\n== worked path ==")
    print("\n".join(worked_path()))

    print("\n== theoretical full-bowl output (before jar caps) ==")
    for k in ("feeder_1", "feeder_2", "feeder_3", "feeder_4"):
        b = int(FAC[k]["effect_value"])
        cells = []
        for fid in P0_FLAVORS:
            fl = FLAVORS[fid]
            n = b // int(fl["digest_min"])
            cells.append(f"{fid}:{n}food/{n*4}mat/{n*int(fl['food_price'])}c")
        print(f"{k} L{FAC[k]['level_req']} belly {b}min  " + "  ".join(cells))

    print("\nPacing forecast withdrawn: real-time multi-day player validation pending (PRD 12/14).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
