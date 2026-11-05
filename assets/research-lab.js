/* Project Asma: an original, artificial intervention-order demonstration.
   No patient inputs, network requests, dependencies, storage or clinical model.
   Mathematical source: tools/analyze_treatment_sequence.py and the accompanying
   treatment-sequence assumption report. All burdens use invented arbitrary units.
   Original code is MIT licensed; see the repository LICENSE. */
(function (root, factory) {
  'use strict';
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.AsmaLab = api;
  if (root.document) {
    var start = function () {
      root.document.querySelectorAll('[data-assumption-lab]').forEach(api.mount);
    };
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', start);
    else start();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function percent(value, name) {
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 1 || value > 100) {
      throw new RangeError(name + ' must be a finite number from 1 to 100');
    }
    return value / 100;
  }

  function burden(sensitive, resistant) {
    return { sensitive: sensitive, resistant: resistant, total: sensitive + resistant };
  }

  function calculate(options) {
    if (!options || typeof options !== 'object') throw new TypeError('Provide demonstration settings');
    var a = percent(options.survivalPercent, 'survivalPercent');
    var q = percent(options.retainedPercent, 'retainedPercent');
    if (options.model !== 'fixed' && options.model !== 'proportional') {
      throw new RangeError('model must be fixed or proportional');
    }

    // Same invented starting state and same linear contraction in both orders.
    // Resistant survival is fixed at 1; no growth, mutation, delay or extinction.
    var afterContraction = burden(90 * a, 10);
    var target = 100 * q;
    var first = burden(q * afterContraction.sensitive, q * afterContraction.resistant);
    // A target above available burden never adds material.
    var retainSecond = options.model === 'fixed' ? Math.min(1, target / afterContraction.total) : q;
    var second = burden(retainSecond * afterContraction.sensitive, retainSecond * afterContraction.resistant);
    return {
      model: options.model,
      survivalPercent: options.survivalPercent,
      retainedPercent: options.retainedPercent,
      first: first,
      second: second,
      resistantFractionPercent: 100 * afterContraction.resistant / afterContraction.total,
      resistantRatio: second.resistant / first.resistant,
      chartMaximum: Math.max(first.total, second.total),
      target: target,
      capped: options.model === 'fixed' && target > afterContraction.total
    };
  }

  function explanation(result) {
    if (result.model === 'proportional') {
      return 'Same final burden in both orders. In this artificial linear model, removing the same fraction commutes with contraction. This is a mathematical null case, not evidence that treatment order is equivalent in people.';
    }
    if (Math.abs(result.resistantRatio - 1) < 1e-12) {
      return 'Same final burden at these settings. The fixed-target rule produces no order difference here. Both orders have the same final resistant fraction in this artificial model.';
    }
    return 'Different final burdens, identical resistant fractions. The absolute-target removal rule creates this order difference under the stated artificial assumptions.' +
      (result.capped ? ' The target exceeds the burden available after contraction, so the second removal leaves that burden unchanged.' : '');
  }

  function mount(element) {
    if (element.classList.contains('lab-ready')) return true;
    var find = function (selector) { return element.querySelector(selector); };
    var survival = find('[data-lab-survival]');
    var retain = find('[data-lab-retain]');
    var controls = find('[data-lab-controls]');
    var reset = find('[data-lab-reset]');
    var fixed = find('input[name="removal-model"][value="fixed"]');
    var proportional = find('input[name="removal-model"][value="proportional"]');
    var keys = ['survival-label', 'retain-label', 'first-sensitive', 'first-resistant', 'first-total',
      'second-sensitive', 'second-resistant', 'second-total', 'fraction', 'ratio', 'scale', 'interpretation'];
    var outputs = {};
    keys.forEach(function (key) { outputs[key] = find('[data-lab-' + key + ']'); });
    var barKeys = ['first-sensitive', 'first-resistant', 'second-sensitive', 'second-resistant'];
    var bars = {};
    barKeys.forEach(function (key) { bars[key] = find('[data-lab-bar="' + key + '"]'); });
    // Progressive enhancement: incomplete markup leaves the static example intact.
    if (!survival || !retain || !controls || !reset || !fixed || !proportional ||
        keys.some(function (key) { return !outputs[key]; }) ||
        barKeys.some(function (key) { return !bars[key]; })) return false;

    function readPercent(input) {
      var value = Number(input.value);
      if (!Number.isFinite(value)) value = 10;
      value = Math.min(100, Math.max(1, value));
      input.value = String(value);
      return value;
    }

    function render(announce) {
      if (!fixed.checked && !proportional.checked) fixed.checked = true;
      var result = calculate({ survivalPercent: readPercent(survival),
        retainedPercent: readPercent(retain), model: proportional.checked ? 'proportional' : 'fixed' });
      outputs['survival-label'].textContent = result.survivalPercent + '%';
      outputs['retain-label'].textContent = result.retainedPercent + '%';
      survival.setAttribute('aria-valuetext', result.survivalPercent + ' percent');
      retain.setAttribute('aria-valuetext', result.retainedPercent + ' percent');
      ['first', 'second'].forEach(function (order) {
        ['sensitive', 'resistant', 'total'].forEach(function (part) {
          outputs[order + '-' + part].textContent = result[order][part].toFixed(2);
          if (part !== 'total') bars[order + '-' + part].style.width =
            (100 * result[order][part] / result.chartMaximum).toFixed(6) + '%';
        });
      });
      outputs.fraction.textContent = result.resistantFractionPercent.toFixed(2) + '%';
      outputs.ratio.textContent = result.resistantRatio.toFixed(2) + '×';
      outputs.scale.textContent = result.chartMaximum.toFixed(2) + ' artificial burden units';
      if (announce) outputs.interpretation.textContent = explanation(result);
    }

    try {
      render(true);
    } catch (error) {
      return false;
    }
    [survival, retain].forEach(function (input) {
      input.addEventListener('input', function () { render(false); });
      input.addEventListener('change', function () { render(true); });
    });
    [fixed, proportional].forEach(function (input) {
      input.addEventListener('change', function () { render(true); });
    });
    reset.addEventListener('click', function () {
      survival.value = '10';
      retain.value = '10';
      fixed.checked = true;
      proportional.checked = false;
      render(true);
    });
    controls.disabled = false;
    element.classList.add('lab-ready');
    return true;
  }

  return { calculate: calculate, mount: mount };
});
