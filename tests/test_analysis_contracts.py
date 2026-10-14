import unittest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import rebuild_case1_assets as case1
import rebuild_case2_narrative_assets as case2


class AnalysisContracts(unittest.TestCase):
    def test_boundary_hours_are_lower_inclusive(self):
        self.assertEqual([case1.stage(x) for x in [0,9.999,10,49.999,50,100,300,1000]],['0-10h','0-10h','10-50h','10-50h','50-100h','100-300h','300-1000h','1000h+'])

    def test_invalid_playtime_rejected(self):
        for value in [-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError): case1.stage(value)

    def test_recommendation_labels_are_explicit(self):
        self.assertFalse(case1.parse_bool('False'))
        self.assertTrue(case1.parse_bool('True'))
        with self.assertRaises(ValueError): case1.parse_bool('unknown')

    def test_empty_comparison_is_not_zero(self):
        self.assertIsNone(case2.pct(0,0))
        self.assertIsNone(case2.percentage_point_gap(100,case2.pct(0,0)))
        self.assertEqual(case2.pct(0,3),0)

    def test_theme_match_is_once_per_review_and_word_bounded(self):
        self.assertTrue(case1.mentions(case1.normalized('server server servers'),['server','servers']))
        self.assertFalse(case1.mentions(case1.normalized('observe'),['server']))
        self.assertTrue(case1.mentions(case1.normalized('co-op'),['co op']))

    def test_offline_missing_input_does_not_collect(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(sys,'argv',['rebuild','--reuse-private','--input-dir',folder,'--output-dir',folder]),patch.object(case2,'collect_game_reviews') as collect:
                with self.assertRaises(FileNotFoundError): case2.main()
                collect.assert_not_called()

    def test_count_rate_pair(self):
        self.assertAlmostEqual(case1.rate(63,138),0.45652173913043476)
        self.assertNotAlmostEqual(128*0.4565,round(128*0.4565),places=2)


if __name__=='__main__': unittest.main()
