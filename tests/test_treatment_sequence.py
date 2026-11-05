"""Analytical boundary, independently computed examples and artifact replay."""
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sequence", ROOT / "tools/analyze_treatment_sequence.py")
sequence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sequence)


class TreatmentSequenceTests(unittest.TestCase):
    def test_hand_calculated_example_and_reversal(self):
        # 90 sensitive and 10 resistant -> 9 sensitive and 10 resistant after C.
        result = sequence.build_result()
        self.assertEqual(result['growth_boundary_example']['after_to_before_resistant_ratio'], '20/29')
        example = result['example']
        self.assertEqual(example['fixed_surgery_first']['resistant'], '1')
        self.assertEqual(example['fixed_surgery_first']['sensitive'], '9/10')
        self.assertEqual(example['fixed_chemo_first']['sensitive'], '90/19')
        self.assertEqual(example['fixed_chemo_first']['resistant'], '100/19')
        self.assertEqual(example['fixed_chemo_first']['resistant_fraction'], '10/19')
        self.assertEqual(result['lower_second_sequence_target_example']['after_to_before_resistant_ratio'], '10/19')

    def test_scalar_retention_commutes_with_nondiagonal_linear_map(self):
        # Includes conversion and growth, outside the diagonal grid.
        for x in ((0,0), (2,7), (F(1,3), 0)):
            for q in (F(0), F(1,7), F(1)):
                c = ((F(1,2), F(1,4)), (F(1,3), F(3,2)))
                self.assertEqual(sequence.proportional(sequence.linear(x,c),q),
                                 sequence.linear(sequence.proportional(x,q),c))

    def test_selective_removal_boundary(self):
        x=(F(8), F(2)); surgery=((F(1,2),0),(0,F(1,4)))
        diagonal=((F(1,10),0),(0,F(1)))
        self.assertEqual(sequence.linear(sequence.linear(x,surgery),diagonal),
                         sequence.linear(sequence.linear(x,diagonal),surgery))
        conversion=((F(1,2),0),(F(1,2),F(1)))
        self.assertEqual(sequence.linear(sequence.linear(x,surgery),conversion), (F(2),F(5,2)))
        self.assertEqual(sequence.linear(sequence.linear(x,conversion),surgery), (F(2),F(3,2)))

    def test_surgery_never_adds_burden_and_handles_zero(self):
        for x in ((0,0),(2,3),(F(1,7),F(1,13))):
            for k in (F(0), F(1,5), F(5), F(10)):
                after=sequence.fixed_residual(x,k)
                self.assertTrue(all(0<=v<=w for v,w in zip(after,x)))
                self.assertEqual(sum(after),min(sum(x),k))
        self.assertIsNone(sequence.summary((0,0))['resistant_fraction'])

    def test_exact_formula_over_grid(self):
        result=sequence.build_result()
        self.assertEqual(len(result['synthetic_cases']),84)
        for case in result['synthetic_cases']:
            self.assertTrue(case['fraction_equal'])
            self.assertTrue(case['proportional_equal'])
            q=F(case['retain']);g=F(case['chemo_total_multiplier'])
            ratio=F(case['fixed_after_to_before_resistant_ratio'])
            self.assertEqual(ratio,min(1/q,1/g))
            self.assertGreaterEqual(ratio,1)

    def test_paired_calibration_does_not_identify_other_order(self):
        x=(F(90),F(10)); matrix=((F(1,10),0),(0,F(1)))
        # Both models agree before surgery, after surgery and after chemotherapy.
        p=sequence.proportional(x,F(1,10)); f=sequence.fixed_residual(x,F(10))
        self.assertEqual(p,f)
        self.assertEqual(sequence.linear(p,matrix),sequence.linear(f,matrix))
        # Nevertheless their other-order predictions disagree.
        c=sequence.linear(x,matrix)
        self.assertNotEqual(sequence.proportional(c,F(1,10)),sequence.fixed_residual(c,F(10)))

    def test_invalid_inputs_rejected(self):
        for bad in (True,-1,0.1,float('nan'),float('inf'),'1'):
            with self.assertRaises(ValueError): sequence.proportional((1,1),bad)
        with self.assertRaises(ValueError): sequence.proportional((1,1),2)
        with self.assertRaises(ValueError): sequence.fixed_residual((1,-1),1)
        with self.assertRaises(ValueError): sequence.fixed_residual((1,2,3),1)
        with self.assertRaises(ValueError): sequence.linear((1,2),((1,0),))
        with self.assertRaises(ValueError): sequence.compare((1,1),1,F(1,2),F(1,2))
        with self.assertRaises(ValueError): sequence.compare((1,0),1,1,1)

    def test_committed_artifact_matches(self):
        self.assertEqual(sequence.build_result(),json.loads((ROOT / sequence.OUTPUT).read_text()))
