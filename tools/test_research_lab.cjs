/* Standalone browser-model checks: node tools/test_research_lab.cjs.
   Original artificial examples, independent hand-calculated authority. */
'use strict';
const assert = require('node:assert/strict');
const { calculate } = require('../assets/research-lab.js');

function near(actual, expected, tolerance = 1e-12) {
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} differs from ${expected}`);
}

// 90/10 initial mixture -> 9/10 after contraction. Remove first to 9/1,
// then contract to 0.9/1; reverse order with target 10 gives 90/19, 100/19.
const fixed = calculate({ survivalPercent: 10, retainedPercent: 10, model: 'fixed' });
near(fixed.first.sensitive, 9 / 10);
near(fixed.first.resistant, 1);
near(fixed.first.total, 19 / 10);
near(fixed.second.sensitive, 90 / 19);
near(fixed.second.resistant, 100 / 19);
near(fixed.second.total, 10);
near(fixed.resistantRatio, 100 / 19);
near(fixed.resistantFractionPercent, 1000 / 19);
assert.equal(fixed.capped, false);

// Same fractional removal and fixed linear contraction commute.
const proportional = calculate({ survivalPercent: 10, retainedPercent: 10, model: 'proportional' });
assert.deepEqual(proportional.first, proportional.second);
near(proportional.resistantRatio, 1);

// Target 50 exceeds the 19 units available after contraction: never add burden.
const capped = calculate({ survivalPercent: 10, retainedPercent: 50, model: 'fixed' });
assert.equal(capped.capped, true);
near(capped.first.total, 9.5);
near(capped.second.total, 19);
near(capped.second.sensitive, 9);
near(capped.second.resistant, 10);
near(capped.resistantRatio, 2);

// Boundary operations: no contraction or no removal gives the same endpoint.
for (const model of ['fixed', 'proportional']) {
  for (const [survivalPercent, retainedPercent] of [[100, 10], [10, 100], [100, 100]]) {
    const result = calculate({ survivalPercent, retainedPercent, model });
    near(result.first.total, result.second.total);
    near(result.resistantRatio, 1);
  }
}

// Enumerate the UI's discrete range. Validate an independently derived scalar
// ratio and composition invariance, including all cap transitions.
let comparisons = 0;
for (let survivalPercent = 1; survivalPercent <= 100; survivalPercent++) {
  for (let retainedPercent = 1; retainedPercent <= 100; retainedPercent++) {
    const result = calculate({ survivalPercent, retainedPercent, model: 'fixed' });
    const totalAfterContraction = 0.9 * survivalPercent + 10;
    near(result.resistantRatio, Math.min(100 / retainedPercent, 100 / totalAfterContraction));
    near(result.first.resistant / result.first.total, result.second.resistant / result.second.total);
    assert.ok(result.second.total <= totalAfterContraction + 1e-12);
    assert.ok(result.second.total <= retainedPercent + 1e-12);
    const nullResult = calculate({ survivalPercent, retainedPercent, model: 'proportional' });
    assert.deepEqual(nullResult.first, nullResult.second);
    comparisons++;
  }
}

for (const invalid of [0, -1, 101, NaN, Infinity, -Infinity, '10', true, null, undefined]) {
  assert.throws(() => calculate({ survivalPercent: invalid, retainedPercent: 10, model: 'fixed' }), RangeError);
  assert.throws(() => calculate({ survivalPercent: 10, retainedPercent: invalid, model: 'fixed' }), RangeError);
}
assert.throws(() => calculate({ survivalPercent: 10, retainedPercent: 10, model: 'unknown' }), RangeError);
assert.throws(() => calculate(null), TypeError);
console.log(`PASS: exact examples, boundaries, invalid inputs and ${comparisons} artificial slider pairs.`);
