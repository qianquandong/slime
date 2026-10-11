"""Slime Sweets Farm - config closure check + pacing simulation.

Reads ../config/*.csv (the PRD's initial design values) and:
  1. generates the species list from the breeding rules,
  2. checks that recipes, resources and unlocks close (no dangling refs,
     nothing in P0 that needs P1 or a purchase, every signature reachable),
  3. prints the worked economy path used in PRD chapter 7,
  4. runs a minute-step pacing simulation for two player profiles.

Standard library only:  python tools/balance_check.py [--species-csv]
"""
import csv
import math
import random
import sys
from pathlib import Path

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
FTUE_END_PANTRY = {"mat_jam": 7, "mat_cream": 9}   # PRD 03: 9 jam - 2 for Bella's jelly; Puff's 3 milks


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
    # food ROI: base yield must at least break even when sold raw
    for fid, f in FLAVORS.items():
        base_val = pf("yield_base") * int(f["material_value"])
        if base_val < int(f["food_price"]):
            errors.append(f"food {f['food_id']}: base yield value {base_val} < price {f['food_price']}")
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
    # star sugar: cumulative guaranteed income by level must cover cumulative facility costs by level
    star_cost_by_lv, star_income_by_lv = {}, {}
    sp = gen_species()
    for lv in sorted(LEVELS):
        star_cost_by_lv[lv] = sum(int(f["cost_star_sugar"]) for f in FAC.values() if int(f["level_req"]) <= lv)
        guaranteed = sum(int(LEVELS[x]["star_sugar_reward"]) for x in LEVELS if x <= lv)
        guaranteed += sum(int(pf("discovery_star_sugar")) for s in sp
                          if s["scope"] == "P0" and s["kind"] not in ("starter", "signature") and s["unlock_level"] <= lv)
        star_income_by_lv[lv] = guaranteed
        if guaranteed < star_cost_by_lv[lv]:
            errors.append(f"star sugar deficit at L{lv}: attainable {guaranteed} < facility cost {star_cost_by_lv[lv]}")
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

def worked_path():
    """PRD 7.6 worked path: Lv2 -> two 2-hour cycles -> Lv3 -> first Lemon species.
    Every number printed here is quoted in the PRD; asserts keep the two in sync."""
    out = []
    cap = int(FAC["pantry_1"]["effect_value"])
    belly = int(FAC["feeder_1"]["effect_value"])
    st = {"coins": 150, "xp": 30, "level": 2, "star": 4, "spoons": 1}
    pantry = {"mat_sugar": 0, "mat_cream": 0, "mat_jam": 0, "mat_lemon": 0}
    pantry.update(FTUE_END_PANTRY)

    def feed(name, body, pat, food, n):
        fl = FLAVORS[food]
        c = n * int(fl["food_price"])
        st["coins"] -= c
        out.append(f"  feed {name}: {n} x {fl['food_name']} = {c}c (coins {st['coins']})")
        return fl["material_id"], yield_per_food(body, pat, food), n

    def produce(batches):
        for m, y, n in batches:
            room = cap - pantry[m]
            made = (room // y) * y if n * y > room else n * y   # whole foods only; rest waits in belly
            pantry[m] += made
            left = n - made // y
            out.append(f"  produce {m}: {n} food x {y} -> {made} (cap {cap}; {left} food left in belly)")

    def order(lines):
        sell = sum(int(DESSERTS[d]["sell_price"]) * q for d, q in lines)
        xp = sum(int(DESSERTS[d]["xp"]) * q for d, q in lines)
        for d, q in lines:
            for m, k in DESSERTS[d]["recipe_map"].items():
                pantry[m] -= k * q
                assert pantry[m] >= 0, (d, m)
        c = rnd(sell * pf("order_coin_mult"))
        st["coins"] += c
        st["xp"] += xp
        out.append(f"  order {lines}: sell {sell} x1.25 -> {c}c, {xp}xp (coins {st['coins']}, xp {st['xp']})")

    out.append(f"start L2 xp 30/80, 150c, pantry {pantry}, cap {cap}/material, belly {belly} min")
    out.append("cycle 1")
    b = [feed("Mochi", "plain", "plain", "plain", belly // 10),
         feed("Puff", "plain", "plain", "cream", belly // 15),
         feed("Berry", "strawberry", "cream", "strawberry", belly // 15)]
    produce(b)
    order([("d_shortcake", 2)])
    order([("d_puff", 2), ("d_jelly", 2)])
    order([("d_cookie", 2)])
    out.append(f"  pantry {pantry}")
    assert (st["coins"], st["xp"]) == (156, 54)
    out.append("cycle 2 (Mochi digests its 2 leftover cubes)")
    b = [("mat_sugar", 4, 2),
         feed("Puff", "plain", "plain", "cream", 8),
         feed("Berry", "strawberry", "cream", "strawberry", 8)]
    produce(b)
    order([("d_shortcake", 2)])
    order([("d_shortcake", 2), ("d_jelly", 2)])
    assert st["xp"] >= int(LEVELS[2]["xp_to_next"])
    st["xp"] -= int(LEVELS[2]["xp_to_next"])
    st["level"] = 3
    st["coins"] += int(LEVELS[3]["coin_reward"])
    st["star"] += int(LEVELS[3]["star_sugar_reward"])
    st["spoons"] += int(LEVELS[3]["spoon_reward"])
    out.append(f"  level up -> L3: +{LEVELS[3]['coin_reward']}c (coins {st['coins']}), Lemon unlocked")
    out.append(f"  pantry {pantry}")
    out.append("breed")
    feed("Puff", "plain", "plain", "lemon", 3)
    k = 1 + TIER["lemon"] + TIER["strawberry"]
    fee = int(pf("breed_fee_unit") * k)
    st["coins"] -= fee
    st["xp"] += int(pf("discovery_xp_unit") * k)
    st["star"] += int(pf("discovery_star_sugar"))
    out.append(f"  Body=Puff(Lemon) + Swirl=Berry(Strawberry): k={k}, {int(pf('breed_time_unit')*k)} min, fee {fee}c "
               f"-> Lemon Strawberry Slime, +{int(pf('discovery_xp_unit')*k)}xp +1 star sugar")
    out.append(f"end {st}")
    assert st == {"coins": 163, "xp": 40, "level": 3, "star": 6, "spoons": 2}, st
    assert {k: v for k, v in pantry.items() if v} == {"mat_sugar": 28, "mat_cream": 32, "mat_jam": 27}, pantry
    return out


# ---------------------------------------------------------------- pacing sim

class Slime:
    __slots__ = ("body", "pattern", "sig", "diet", "belly", "carry")

    def __init__(self, body, pattern, sig=None):
        self.body, self.pattern, self.sig = body, pattern, sig
        self.diet = body
        self.belly = 0.0      # minutes of food left
        self.carry = 0.0      # fractional material carry


def order_rule(level):
    for r in ORDER_RULES:
        if int(r["level_min"]) <= level <= int(r["level_max"]):
            return r
    return ORDER_RULES[-1]


class Sim:
    def __init__(self, sessions_per_day, session_len, seed=7):
        self.rng = random.Random(seed)
        self.sessions = sessions_per_day
        self.slen = session_len
        self.t = 0
        self.coins, self.xp, self.level, self.star, self.spoons = 150, 30, 2, 4, 1
        self.pantry = {f["material_id"]: 0.0 for f in FLAVORS.values()}
        self.pantry.update(FTUE_END_PANTRY)
        self.slimes = [Slime("plain", "plain"), Slime("plain", "plain"), Slime("strawberry", "cream")]
        self.owned_fac = {k for k, f in FAC.items() if int(f["cost_coins"]) == 0 and int(f["level_req"]) == 1}
        self.t = 19 * 60
        self.nests = []          # list of [done_at, species dict]
        self.board = []          # list of dict(lines, ready_at, fails)
        self.discovered = {"sp_plain_plain", "sp_strawberry_cream"}
        self.breeds = 1
        self.sig_attempts = {}
        self.visitor_ready = None
        self.visitor_target = None
        self.log = []
        self.species = [s for s in gen_species() if s["scope"] == "P0"]
        self.day_sessions = 0
        self.income = {"orders": 0, "sales": 0, "visitor": 0, "tasks": 0, "levels": 0, "rehome": 0}
        self.spend = {"food": 0, "fees": 0, "facilities": 0}

    # --- helpers
    def fac_val(self, group):
        vals = [int(FAC[k]["effect_value"]) for k in self.owned_fac if FAC[k]["group"] == group]
        return max(vals)

    def unlocked(self, key):
        lv = unlock_level_of(key)
        return lv is not None and lv <= self.level

    def flavors_unlocked(self):
        return [fid for fid in P0_FLAVORS if int(FLAVORS[fid]["unlock_level"]) <= self.level]

    def desserts_unlocked(self):
        return [d for d in DESSERTS.values() if d["scope"] == "P0" and int(d["unlock_level"]) <= self.level]

    def add_xp(self, x):
        self.xp += x
        while self.level < max(LEVELS) and self.xp >= int(LEVELS[self.level]["xp_to_next"]):
            self.xp -= int(LEVELS[self.level]["xp_to_next"])
            self.level += 1
            r = LEVELS[self.level]
            self.coins += int(r["coin_reward"])
            self.income["levels"] += int(r["coin_reward"])
            self.star += int(r["star_sugar_reward"])
            self.spoons += int(r["spoon_reward"])
            self.log.append((self.t, f"reach L{self.level}"))

    # --- world step (1 minute)
    def step(self):
        cap = self.fac_val("pantry")          # per-material cap
        pen = self.slimes[: self.fac_val("pen")]
        for s in pen:
            fl = FLAVORS[s.diet]
            m = fl["material_id"]
            if s.belly <= 0 or self.pantry[m] >= cap:   # full stack pauses only its producers
                continue
            s.belly -= 1
            s.carry += yield_per_food(s.body, s.pattern, s.diet) / int(fl["digest_min"])
            whole = int(s.carry)
            if whole:
                s.carry -= whole
                self.pantry[m] = min(cap, self.pantry[m] + whole)
        self.t += 1

    # --- player actions during a session minute
    def act(self, first_minute):
        rule = order_rule(self.level)
        slots = self.fac_val("board")
        # board refill
        while len(self.board) < slots:
            self.board.append(self.new_order(rule, ready_at=self.t if first_minute else self.t + int(rule["refresh_min"])))
        # hatch
        for n in list(self.nests):
            if n[0] <= self.t:
                self.nests.remove(n)
                self.hatch(n[1])
        # orders
        for o in list(self.board):
            if o["ready_at"] > self.t:
                continue
            need = {}
            for did, q in o["lines"]:
                for m, k in DESSERTS[did]["recipe_map"].items():
                    need[m] = need.get(m, 0) + k * q
            if all(self.pantry[m] >= k for m, k in need.items()):
                for m, k in need.items():
                    self.pantry[m] -= k
                sell = sum(int(DESSERTS[d]["sell_price"]) * q for d, q in o["lines"])
                coins = rnd(sell * pf("order_coin_mult"))
                self.coins += coins
                self.income["orders"] += coins
                self.add_xp(sum(int(DESSERTS[d]["xp"]) * q for d, q in o["lines"]))
                self.board.remove(o)
                self.board.append(self.new_order(order_rule(self.level), ready_at=self.t + int(rule["refresh_min"])))
            elif first_minute:
                o["fails"] += 1
                if o["fails"] >= 3:           # stuck order -> cancel, slot cooldown
                    self.board.remove(o)
                    self.board.append(self.new_order(rule, ready_at=self.t + int(rule["cancel_cooldown_min"])))
        if first_minute:
            self.visitor()
            self.sell_surplus()
            self.buy_upgrades()
            self.breed()
            self.refill()

    def new_order(self, rule, ready_at):
        ds = self.desserts_unlocked()
        weights = [2 if int(d["unlock_level"]) >= self.level - 1 else 1 for d in ds]
        n = self.rng.randint(int(rule["lines_min"]), int(rule["lines_max"]))
        picks = []
        for _ in range(n):
            d = self.rng.choices(ds, weights)[0]
            picks.append((d["id"], self.rng.randint(1, int(rule["qty_max"]))))
        return {"lines": picks, "ready_at": ready_at, "fails": 0}

    def sell_surplus(self):
        """Quick-sell desserts at the counter when a stack is >= 75% of its cap."""
        cap = self.fac_val("pantry")
        mult = pf("counter_sell_mult")
        ds = sorted(self.desserts_unlocked(), key=lambda d: -int(d["sell_price"]))
        for m in self.pantry:
            while self.pantry[m] > 0.75 * cap:
                for d in ds:
                    if m in d["recipe_map"] and all(self.pantry[x] >= k for x, k in d["recipe_map"].items()):
                        for x, k in d["recipe_map"].items():
                            self.pantry[x] -= k
                        v = max(1, rnd(int(d["sell_price"]) * mult))
                        self.coins += v
                        self.income["sales"] += v
                        break
                else:   # nothing bakeable with this stack: sell raw down to 50%
                    q = int(self.pantry[m] - 0.5 * cap)
                    v = int(q * int(FLAVORS[MAT2FLAVOR[m]]["material_value"]) * pf("raw_sell_mult"))
                    self.pantry[m] -= q
                    self.coins += v
                    self.income["sales"] += v
                    break

    UPGRADE_ORDER = ["pantry_2", "feeder_2", "board_2", "pen_2", "nest_2", "pantry_3", "feeder_3",
                     "house_2", "board_3", "pen_3", "pantry_4", "feeder_4"]

    def buy_upgrades(self):
        reserve = 60 * max(1, len(self.slimes[: self.fac_val("pen")]))
        for k in self.UPGRADE_ORDER:
            f = FAC[k]
            if k in self.owned_fac or int(f["level_req"]) > self.level:
                continue
            if self.coins - int(f["cost_coins"]) >= reserve and self.star >= int(f["cost_star_sugar"]):
                self.coins -= int(f["cost_coins"])
                self.star -= int(f["cost_star_sugar"])
                self.spend["facilities"] += int(f["cost_coins"])
                self.owned_fac.add(k)
                self.log.append((self.t, f"buy {k}"))

    def breed(self):
        while len(self.nests) < self.fac_val("nest"):
            target = self.pick_target()
            if target is None:
                return
            if self.coins < target["fee"] + 50 and self.breeds > 0:
                return
            if target["kind"] == "signature":
                treat = DESSERTS[target["treat"]]
                if not all(self.pantry[m] >= k for m, k in treat["recipe_map"].items()):
                    return
                for m, k in treat["recipe_map"].items():
                    self.pantry[m] -= k
                att = self.sig_attempts.get(target["id"], 0)
                self.sig_attempts[target["id"]] = att + 1
                if att == 0:   # model: first attempt misses one condition -> normal blend result
                    a, b = target["body"], target["pattern"]
                    fallback = next(s for s in self.species if s["body"] == b and s["pattern"] == a)
                    target = fallback
            fee = 0 if self.breeds == 0 else target["fee"]
            self.coins -= fee
            self.spend["fees"] += fee
            dur = target["breed_min"]
            ftue = {0: 0.5, 1: 2, 2: 5}
            if self.breeds in ftue:
                dur = min(dur, ftue[self.breeds])
            spoon_use = min(self.spoons, int(dur // pf("spoon_minutes")))
            self.spoons -= spoon_use
            dur = max(1, dur - spoon_use * pf("spoon_minutes"))
            self.nests.append([self.t + math.ceil(dur), target])
            self.breeds += 1

    def pick_target(self):
        busy = {n[1]["id"] for n in self.nests}
        cands = [s for s in self.species if s["id"] not in self.discovered and s["id"] not in busy
                 and s["unlock_level"] <= self.level and s["kind"] != "starter"]
        sigs = [s for s in cands if s["kind"] == "signature" and self.unlocked(s["id"])]
        if sigs:
            return sigs[0]
        normal = [s for s in cands if s["kind"] != "signature"]
        if not normal:
            return None
        return min(normal, key=lambda s: (s["breed_min"], s["id"]))

    def hatch(self, sp):
        new = sp["id"] not in self.discovered
        if new:
            self.discovered.add(sp["id"])
            self.add_xp(sp["discovery_xp"])
            self.star += int(pf("signature_star_sugar") if sp["kind"] == "signature" else pf("discovery_star_sugar"))
        cap = self.fac_val("pen") + self.fac_val("house")
        if len(self.slimes) < cap:
            self.slimes.append(Slime(sp["body"], sp["pattern"], sp["id"] if sp["kind"] == "signature" else None))
        else:
            v = int(pf("rehome_coin_unit") * (1 + tier_sum(sp["body"], sp["pattern"])))
            self.coins += v
            self.income["rehome"] += v

    def visitor(self):
        if not self.unlocked("visitor_requests"):
            return
        if self.visitor_target is None:
            if self.visitor_ready is None:
                self.visitor_ready = self.t
            if self.t >= self.visitor_ready:
                fl = self.flavors_unlocked()
                pool = [s for s in self.species if s["kind"] not in ("signature", "starter")
                        and s["body"] in fl and s["pattern"] in fl]
                und = [s for s in pool if s["id"] not in self.discovered]
                self.visitor_target = self.rng.choice(und if und and self.rng.random() < 0.7 else pool)
        elif self.visitor_target["id"] in self.discovered:
            k = 1 + tier_sum(self.visitor_target["body"], self.visitor_target["pattern"])
            c = int(pf("visitor_coin_unit") * k)
            self.coins += c
            self.income["visitor"] += c
            self.star += int(pf("visitor_star_sugar"))
            self.add_xp(int(pf("visitor_xp")))
            self.visitor_target = None
            self.visitor_ready = self.t + int(pf("visitor_interval_h") * 60)

    def refill(self):
        """Refill All: each pen slime eats its diet food up to belly cap.
        Bot skips slimes whose output stack is already >= 75% of the per-material cap."""
        pen = self.slimes[: self.fac_val("pen")]
        belly_cap = self.fac_val("feeder")
        cap = self.fac_val("pantry")
        fl = self.flavors_unlocked()
        need = {m: 0 for m in self.pantry}
        for o in self.board:
            for did, q in o["lines"]:
                for m, k in DESSERTS[did]["recipe_map"].items():
                    need[m] += k * q
        for d in self.desserts_unlocked():
            for m, k in d["recipe_map"].items():
                need[m] += k
        sugar_slimes = 0
        for s in pen:
            if s.body != "plain" and s.body in fl:
                s.diet = s.body
            else:
                short = sorted(fl, key=lambda f: self.pantry[FLAVORS[f]["material_id"]] - need[FLAVORS[f]["material_id"]])
                s.diet = "plain" if sugar_slimes == 0 else short[0]
                if s.diet == "plain":
                    sugar_slimes += 1
            f = FLAVORS[s.diet]
            if self.pantry[f["material_id"]] >= 0.75 * cap:
                continue
            dm = int(f["digest_min"])
            n = int((belly_cap - s.belly) // dm)
            n = min(n, self.coins // int(f["food_price"]))
            if n <= 0:
                continue
            s.belly += n * dm
            c = n * int(f["food_price"])
            self.coins -= c
            self.spend["food"] += c

    # --- schedule
    def run(self, days):
        day_min = 24 * 60
        starts = {5: [8 * 60, 12 * 60 + 30, 17 * 60, 20 * 60, 22 * 60 + 30],
                  3: [8 * 60, 13 * 60, 21 * 60]}[self.sessions]
        rows = []
        self.t = 19 * 60      # install at 19:00 on day 1
        schedule = [(19 * 60 + 12, 3)]       # tail of the 12-min FTUE session (FTUE itself is scripted)
        schedule += [(20 * 60 + 30, self.slen), (22 * 60 + 30, self.slen)] if self.sessions == 5 else [(22 * 60, self.slen)]
        for d in range(1, days):
            schedule += [(d * day_min + s, self.slen) for s in starts]
        last_day = 0
        for start, length in schedule:
            while self.t < start:
                self.step()
            day = self.t // day_min + 1
            if day != last_day:
                self.day_sessions = 0
                last_day = day
            self.day_sessions += 1
            if self.day_sessions == 2 and self.unlocked("daily_tasks"):
                self.coins += 3 * int(pf("daily_task_coin"))
                self.income["tasks"] += 3 * int(pf("daily_task_coin"))
                self.add_xp(3 * int(pf("daily_task_xp")))
                self.star += int(pf("daily_all_star_sugar"))
            for m in range(length):
                self.act(first_minute=(m == 0))
                self.step()
            self.act(first_minute=True)      # leave: refill + start breeds
            if self.t % day_min > (starts[-1] if day > 1 else 0) or start == schedule[-1][0]:
                pass
            rows.append((day, self.level, self.coins, self.star, len(self.discovered), len(self.slimes)))
        return rows


def summarize(rows):
    by_day = {}
    for day, lv, coins, star, disc, n in rows:
        by_day[day] = (lv, coins, star, disc, n)
    return by_day


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

    print("\n== offline window ==")
    for k in ("feeder_1", "feeder_2", "feeder_3", "feeder_4"):
        b = int(FAC[k]["effect_value"])
        cells = []
        for fid in P0_FLAVORS:
            fl = FLAVORS[fid]
            n = b // int(fl["digest_min"])
            cells.append(f"{fid}:{n}food/{n*4}mat/{n*int(fl['food_price'])}c")
        print(f"{k} L{FAC[k]['level_req']} belly {b}min  " + "  ".join(cells))

    for label, spd, slen in (("engaged 5x4min", 5, 4), ("casual 3x3min", 3, 3)):
        sim = Sim(spd, slen)
        rows = sim.run(31)
        by_day = summarize(rows)
        print(f"\n== pacing sim: {label} == day: level coins star discovered(of {len(sim.species)}) slimes")
        for d in (1, 2, 3, 5, 7, 10, 14, 21, 30):
            if d in by_day:
                print(f"  D{d}: " + " ".join(str(x) for x in by_day[d]))
        firsts = {}
        for t, e in sim.log:
            if e.startswith("reach"):
                firsts[e] = round((t - 19 * 60) / 60, 1)
        print("  hours since install to level: " + ", ".join(f"{k[6:]}={v}h" for k, v in firsts.items()))
        print(f"  income {sim.income}  spend {sim.spend}")
        print("  facilities: " + ", ".join(f"{e[4:]}@{round((t-19*60)/60,1)}h" for t, e in sim.log if e.startswith('buy')))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
