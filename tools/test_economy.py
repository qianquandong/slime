"""Regression scenarios for the PRD's economic promises (standard library)."""
import copy
import unittest

from balance_check import Economy, FAC, Pet, gen_species, worked_path


class EconomyRegressionTests(unittest.TestCase):
    def bare(self):
        g = Economy()
        g.coins = 1000
        g.pantry = {k: 0 for k in g.pantry}
        g.pets = {"A": Pet("A", "plain", "plain", "plain", "sp_plain_plain")}
        return g

    def test_ftue_leaves_money_for_second_discovery(self):
        g = Economy.ftue_end()
        self.assertEqual(g.coins, 90)
        self.assertEqual([sum(f.remaining for f in p.queue) for p in g.pets.values()], [60, 60, 60])
        job = g.breed("Puff", "Mochi")
        self.assertEqual(g.coins, 50)
        g.advance(2)
        g.hatch(job, "Creamy")
        self.assertIn("sp_cream_plain", g.discovered)
        self.assertEqual((g.xp, g.star), (50, 5))

    def test_starter_refill_cannot_repeat(self):
        g = Economy.ftue_end()
        before = copy.deepcopy(g.__dict__)
        with self.assertRaises(ValueError):
            g.starter_bowls()
        self.assertEqual(g.__dict__, before)

    def test_full_documented_path(self):
        self.assertIn("226 coins", "\n".join(worked_path()))

    def test_production_requires_whole_food_time(self):
        g = self.bare()
        g.feed("A", "plain", 1)
        g.advance(9)
        self.assertEqual(g.pantry["mat_sugar"], 0)
        g.advance(1)
        self.assertEqual(g.pantry["mat_sugar"], 4)

    def test_blocked_sugar_does_not_block_milk(self):
        g = self.bare()
        g.pantry["mat_sugar"] = 38
        g.feed("A", "plain", 1)
        g.feed("A", "cream", 2)
        g.advance(30)
        self.assertEqual((g.pantry["mat_sugar"], g.pantry["mat_cream"]), (38, 6))
        self.assertEqual(len(g.pets["A"].queue), 1)
        self.assertEqual(g.pets["A"].queue[0].remaining, 10)
        g.order([("d_cookie", 1)])
        g.advance(10)
        self.assertEqual(g.pantry["mat_sugar"], 39)

    def test_two_producers_cannot_overbook_last_jar_space(self):
        g = self.bare()
        g.pets["B"] = Pet("B", "plain", "plain", "plain")
        g.pantry["mat_sugar"] = 36
        for uid in ("A", "B"):
            g.feed(uid, "plain", 1)
        g.advance(10)
        self.assertEqual(g.pantry["mat_sugar"], 40)
        self.assertEqual(len(g.pets["B"].queue), 1)
        self.assertEqual(g.pets["B"].queue[0].remaining, 10)

    def test_refund_preserves_active_food_and_releases_only_queued_food(self):
        g = self.bare()
        g.feed("A", "cream", 3)
        g.advance(1)
        self.assertEqual(g.swap_snack("A"), 12)
        self.assertEqual(g.coins, 994)
        self.assertEqual((len(g.pets["A"].queue), g.pets["A"].queue[0].remaining), (1, 14))
        self.assertEqual(g.pets["A"].showing, "cream")
        g.advance(14)
        self.assertEqual(g.pantry["mat_cream"], 3)

    def test_free_food_cannot_be_refunded_for_coins(self):
        g = self.bare()
        g.feed("A", "plain", 6, free=True)
        self.assertEqual(g.swap_snack("A"), 0)
        self.assertEqual(g.coins, 1000)

    def test_failed_feed_is_atomic(self):
        g = self.bare()
        g.feed("A", "plain", 12)
        before = copy.deepcopy(g.__dict__)
        with self.assertRaises(ValueError):
            g.feed("A", "cream", 3)
        self.assertEqual(g.__dict__, before)

    def test_full_bowl_can_prepare_a_different_flavor(self):
        g = self.bare()
        g.feed("A", "plain", 12)
        g.advance(1)
        g.swap_snack("A")
        g.feed("A", "cream", 3)
        self.assertEqual(g.pets["A"].showing, "cream")
        self.assertEqual(sum(f.remaining for f in g.pets["A"].queue), 54)

    def test_same_parent_and_busy_parent_rejected_without_charges(self):
        g = Economy.ftue_end()
        with self.assertRaises(ValueError):
            g.breed("Puff", "Puff")
        self.assertEqual(g.coins, 90)
        g.breed("Puff", "Mochi")
        g.nest_cap = 2
        with self.assertRaises(ValueError):
            g.breed("Puff", "Berry")
        self.assertEqual(g.coins, 50)

    def test_breeding_uses_expression_snapshot(self):
        g = Economy.ftue_end()
        g.coins = 500
        job = g.breed("Puff", "Mochi")
        g.feed("Puff", "strawberry", 3)
        self.assertEqual(g.pets["Puff"].showing, "strawberry")
        g.advance(2)
        g.hatch(job, "Creamy")
        self.assertEqual(g.pets["Creamy"].species_id, "sp_cream_plain")

    def test_full_capacity_keeps_pod_and_parent_locks_until_hatch(self):
        g = Economy.ftue_end()
        g.pen_cap, g.house_cap = 3, 0
        job = g.breed("Puff", "Mochi")
        g.advance(2)
        before = copy.deepcopy(g.__dict__)
        with self.assertRaises(ValueError):
            g.hatch(job, "Creamy")
        self.assertEqual(g.__dict__, before)
        g.house_cap = 1
        g.hatch(job, "Creamy")
        self.assertFalse(g.pets["Creamy"].in_pen)
        self.assertFalse(g.pets["Puff"].in_nest)

    def test_housed_pets_do_not_produce(self):
        g = self.bare()
        g.pets["A"].in_pen = False
        g.feed("A", "plain", 1)
        g.advance(120)
        self.assertEqual(g.pantry["mat_sugar"], 0)
        self.assertEqual(g.pets["A"].queue[0].remaining, 10)

    def test_codex_discovery_is_not_live_visitor_ownership(self):
        g = self.bare()
        g.discovered.add("sp_lemon_strawberry")
        self.assertFalse(g.has_visitor_match("lemon", "strawberry"))
        g.pets["L"] = Pet("L", "lemon", "strawberry", "cream", in_pen=False)
        self.assertTrue(g.has_visitor_match("lemon", "strawberry"))

    def test_missing_order_materials_do_not_consume_partial_inventory(self):
        g = self.bare()
        g.pantry["mat_jam"] = 10
        before = copy.deepcopy(g.__dict__)
        with self.assertRaises(ValueError):
            g.order([("d_jelly", 1)])
        self.assertEqual(g.__dict__, before)

    def test_signature_rejects_missing_treat_without_charging(self):
        g = Economy.ftue_end()
        g.level = 4
        before = copy.deepcopy(g.__dict__)
        with self.assertRaises(ValueError):
            g.breed("Berry", "Puff", "d_shortcake")
        self.assertEqual(g.__dict__, before)

    def test_signature_consumes_treat_and_awards_only_on_hatch(self):
        g = Economy.ftue_end()
        g.level, g.breed_count = 4, 3
        g.pantry["mat_sugar"] = 1
        before = (g.pantry["mat_jam"], g.pantry["mat_cream"], g.xp, g.star)
        job = g.breed("Berry", "Puff", "d_shortcake")
        self.assertEqual((job["result"]["id"], job["ready"], g.coins), ("sig_shortcake", 90, 30))
        self.assertEqual((g.pantry["mat_sugar"], g.pantry["mat_jam"], g.pantry["mat_cream"]), (0, before[0] - 2, before[1] - 2))
        self.assertEqual((g.xp, g.star), before[2:])
        g.advance(90)
        g.hatch(job, "Cake")
        self.assertEqual((g.xp, g.star), (before[2] + 100, before[3] + 5))
        self.assertEqual(g.pets["Cake"].species_id, "sig_shortcake")

    def test_ordinary_fourth_breed_uses_normal_duration(self):
        g = Economy.ftue_end()
        g.breed_count = 3
        job = g.breed("Puff", "Mochi")
        self.assertEqual(job["ready"], 20)

    def test_initial_free_capacity_holds_every_p0_species(self):
        capacity = int(FAC["pen_1"]["effect_value"]) + int(FAC["house_1"]["effect_value"])
        self.assertGreaterEqual(capacity, len([s for s in gen_species() if s["scope"] == "P0"]))


if __name__ == "__main__":
    unittest.main()
