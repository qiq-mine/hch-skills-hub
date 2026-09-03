import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const target = process.argv[2]
  ? path.resolve(process.cwd(), process.argv[2])
  : path.resolve(scriptDir, '../assets/explainer-starter.html');

function fail(message) {
  throw new Error(message);
}

function requireMatch(source, expression, message) {
  const match = source.match(expression);
  assert.ok(match, message);
  return match;
}

function scriptsIn(html) {
  return [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)].map((match) => ({
    attributes: match[1],
    body: match[2],
  }));
}

function createFakeElement() {
  const classes = new Set();
  const listeners = new Map();
  return {
    dataset: {},
    hidden: false,
    disabled: false,
    tabIndex: -1,
    textContent: '',
    classList: {
      toggle(name, enabled) {
        if (enabled) classes.add(name);
        else classes.delete(name);
      },
      remove(name) {
        classes.delete(name);
      },
      contains(name) {
        return classes.has(name);
      },
    },
    addEventListener(type, listener) {
      listeners.set(type, listener);
    },
    trigger(type, event = {}) {
      const listener = listeners.get(type);
      assert.ok(listener, 'Expected a ' + type + ' event listener.');
      listener({ preventDefault() {}, ...event });
    },
  };
}

function assertSingleActive(steps, expectedIndex) {
  assert.equal(steps.filter((step) => !step.hidden).length, 1, 'Slide mode must expose exactly one stage.');
  assert.equal(steps.filter((step) => step.classList.contains('is-active')).length, 1, 'Slide mode must mark exactly one active stage.');
  assert.equal(steps.findIndex((step) => !step.hidden), expectedIndex, 'Slide mode must reveal the requested index.');
}

function stylesIn(html) {
  return [...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map((match) => match[1]).join('\n');
}

function assertNoExternalStyleDependencies(html) {
  assert.doesNotMatch(html, /<link\b[^>]*>/i, 'Any <link> tag is forbidden in this self-contained starter.');
  const styles = stylesIn(html);
  assert.doesNotMatch(styles, /@import\b/i, 'CSS @import is not allowed.');
  assert.doesNotMatch(styles, /@font-face\b/i, 'CSS @font-face is not allowed.');
  assert.doesNotMatch(styles, /url\(\s*(?!["']?data:)[^)]+\)/i, 'Only data: CSS url() values are allowed.');
  return styles;
}

function assertExternalDependencyMutationsFail(html) {
  const mutations = [
    ['stylesheet link', '<link rel=stylesheet href=theme.css>'],
    ['font preload link', '<link rel=preload as=font href=./font.woff2>'],
    ['font-face source', '<style>@font-face{src:url(font.woff2)}</style>'],
  ];
  for (const [label, injection] of mutations) {
    const mutated = html.replace('</head>', injection + '</head>');
    assert.notEqual(mutated, html, 'Mutation fixture must have a head closing tag.');
    assert.throws(() => assertNoExternalStyleDependencies(mutated), assert.AssertionError, label + ' mutation must be rejected.');
  }
}

function validateDocument(html) {
  assert.match(html, /^\s*<!doctype html>/i, 'Expected one HTML document beginning with <!doctype html>.');
  assert.equal((html.match(/<!doctype html>/gi) ?? []).length, 1, 'Expected exactly one doctype.');
  assert.match(html, /<html\b[^>]*\blang=["']zh-CN["'][^>]*>/i, 'Expected <html lang="zh-CN">.');
  assert.match(html, /<meta\b[^>]*\bcharset=["']?utf-8["']?[^>]*>/i, 'Expected a UTF-8 charset meta tag.');
  assert.match(html, /<meta\b[^>]*\bname=["']viewport["'][^>]*\bcontent=["'][^"']*width=device-width[^"']*["'][^>]*>/i, 'Expected a responsive viewport meta tag.');

  const styles = assertNoExternalStyleDependencies(html);
  assert.ok(styles, 'Expected inline CSS for this single-file starter.');
  assertExternalDependencyMutationsFail(html);
  for (const token of ['--bg:#05091A', '--ink:#E2EEFF', '--cyan:#00CFFF', '--green:#00FF8A', '--orange:#FF7C5C']) {
    assert.ok(styles.includes(token), 'Expected exact HCH token ' + token + ' in the stylesheet.');
  }

  assert.match(html, /<header\b[^>]*>/i, 'Expected a semantic header.');
  assert.match(html, /<main\b[^>]*>/i, 'Expected a semantic main element.');
  assert.match(html, /<h1\b[^>]*>[^<]+<\/h1>/i, 'Expected a page h1.');
  assert.match(html, /<h2\b[^>]*>[^<]+<\/h2>/i, 'Expected a section h2.');
  assert.match(styles, /prefers-reduced-motion/i, 'Expected a prefers-reduced-motion rule.');
  assert.match(styles, /body\s*\{[^}]*overflow-y\s*:\s*(?:auto|scroll)/i, 'Expected the page to remain vertically scrollable.');

  const flowSection = requireMatch(
    html,
    /<section\b(?=[^>]*\bdata-flow-section\b)(?=[^>]*\baria-labelledby=["']([^"']+)["'])[^>]*>/i,
    'Expected a labelled semantic flow section with data-flow-section.'
  );
  const flowHeadingId = flowSection[1];
  assert.match(html, new RegExp("<h2\\b[^>]*\\bid=['\"]" + flowHeadingId + "['\"][^>]*>", 'i'), 'Flow section label must reference its h2.');

  const flowContainer = requireMatch(
    html,
    /<[^>]+\bdata-flow\b(?=[^>]*\bdata-flow-mode(?:=["'][^"']*["'])?)[^>]*>/i,
    'Expected a flow container that records data-flow-mode.'
  )[0];
  const flowBody = html.slice(html.indexOf(flowContainer), html.indexOf('</section>', html.indexOf(flowContainer)));
  const steps = [...flowBody.matchAll(/<article\b(?=[^>]*\bdata-flow-step\b)[^>]*>/gi)];
  assert.ok(steps.length >= 1, 'Expected at least one semantic <article data-flow-step>.');

  const allScripts = scriptsIn(html);
  assert.ok(allScripts.length >= 2, 'Expected dedicated mode and controller scripts.');
  for (const script of allScripts) {
    assert.doesNotMatch(script.attributes, /\bsrc\s*=/i, 'External scripts are not allowed.');
    assert.doesNotMatch(script.attributes, /\btype\s*=\s*["']module["']/i, 'Module scripts are not allowed.');
    assert.doesNotMatch(script.body, /\b(?:import|require)\b|\b(?:React|Vue|Svelte|webpack|vite)\b/i, 'Framework or bundler dependencies are not allowed.');
    new Function(script.body);
  }

  const modeScript = allScripts.find((script) => /\bdata-component\s*=\s*["']flow-mode["']/i.test(script.attributes));
  assert.ok(modeScript, 'Expected a dedicated data-component="flow-mode" script.');
  const sandbox = vm.createContext({});
  new vm.Script(modeScript.body, { filename: 'flow-mode-inline.js' }).runInContext(sandbox);
  assert.equal(typeof sandbox.selectFlowMode, 'function', 'flow-mode script must assign globalThis.selectFlowMode.');
  assert.equal(sandbox.selectFlowMode(1), 'scroll');
  assert.equal(sandbox.selectFlowMode(3), 'scroll');
  assert.equal(sandbox.selectFlowMode(4), 'slides');
  assert.equal(sandbox.selectFlowMode(9), 'slides');

  const controller = allScripts.find((script) => /\bdata-component\s*=\s*["']flow-controller["']/i.test(script.attributes));
  assert.ok(controller, 'Expected a data-component="flow-controller" script.');
  assert.match(controller.body, /globalThis\.createFlowController\s*=/, 'Controller must expose createFlowController for injected-element verification.');
  new vm.Script(controller.body, { filename: 'flow-controller-inline.js' }).runInContext(sandbox);
  assert.equal(typeof sandbox.createFlowController, 'function', 'Controller script must expose createFlowController for injected elements.');

  const slideFlow = createFakeElement();
  const slideSteps = Array.from({ length: 4 }, createFakeElement);
  const slideNav = createFakeElement();
  const slidePrev = createFakeElement();
  const slideNext = createFakeElement();
  const slideCount = createFakeElement();
  const slideController = sandbox.createFlowController({
    flow: slideFlow,
    steps: slideSteps,
    nav: slideNav,
    prev: slidePrev,
    next: slideNext,
    count: slideCount,
  });
  assert.equal(slideController.mode, 'slides', 'Four real steps must select slide mode.');
  assert.equal(slideFlow.dataset.flowMode, 'slides', 'Controller must record slide mode on the flow container.');
  assert.equal(slideFlow.dataset.flowDirection, 'next', 'Initial slide direction must use the CSS-facing data-flow-direction property.');
  assert.equal(slideFlow.tabIndex, 0, 'Slide mode flow must be keyboard focusable.');
  assert.equal(slideNav.hidden, false, 'Slide navigation must be visible in slide mode.');
  assert.equal(slideCount.textContent, '1 / 4', 'Slide counter must use the actual step count.');
  assert.equal(slidePrev.disabled, true, 'Previous must be disabled at the first slide.');
  assert.equal(slideNext.disabled, false, 'Next must be enabled before the last slide.');
  assertSingleActive(slideSteps, 0);

  slideNext.trigger('click');
  assert.equal(slideCount.textContent, '2 / 4', 'Next click must advance the real controller index.');
  assert.equal(slideFlow.dataset.flowDirection, 'next', 'Forward navigation must set the CSS-facing direction.');
  assertSingleActive(slideSteps, 1);
  slidePrev.trigger('click');
  assert.equal(slideFlow.dataset.flowDirection, 'previous', 'Previous navigation must set the CSS-facing direction.');
  assertSingleActive(slideSteps, 0);
  slideFlow.trigger('keydown', { key: 'ArrowRight' });
  assertSingleActive(slideSteps, 1);
  slideFlow.trigger('touchstart', { changedTouches: [{ clientX: 200 }] });
  slideFlow.trigger('touchend', { changedTouches: [{ clientX: 80 }] });
  assertSingleActive(slideSteps, 2);
  slideController.move(99);
  assertSingleActive(slideSteps, 3);
  assert.equal(slideNext.disabled, true, 'Next must disable at the last slide.');

  const scrollFlow = createFakeElement();
  const scrollSteps = Array.from({ length: 3 }, createFakeElement);
  const scrollNav = createFakeElement();
  const scrollPrev = createFakeElement();
  const scrollNext = createFakeElement();
  const scrollCount = createFakeElement();
  const scrollController = sandbox.createFlowController({
    flow: scrollFlow,
    steps: scrollSteps,
    nav: scrollNav,
    prev: scrollPrev,
    next: scrollNext,
    count: scrollCount,
  });
  assert.equal(scrollController.mode, 'scroll', 'Three real steps must select scroll mode.');
  assert.equal(scrollFlow.dataset.flowMode, 'scroll', 'Controller must record scroll mode on the flow container.');
  assert.equal(scrollFlow.tabIndex, -1, 'Scroll mode must remove the inert flow container from tab order.');
  assert.equal(scrollNav.hidden, true, 'Scroll mode must hide slide navigation.');
  assert.ok(scrollSteps.every((step) => !step.hidden), 'Scroll mode must leave every stage in document flow.');
  assert.ok(scrollSteps.every((step) => !step.classList.contains('is-active')), 'Scroll mode must not retain an active-only stage.');
  assert.equal(scrollPrev.disabled, true, 'Scroll mode previous navigation must be disabled.');
  assert.equal(scrollNext.disabled, true, 'Scroll mode next navigation must be disabled.');

  const bootstrap = allScripts.find((script) => /\bdata-component\s*=\s*["']flow-bootstrap["']/i.test(script.attributes));
  assert.ok(bootstrap, 'Expected a flow-bootstrap script that uses the injected controller in the page.');
  const bootstrapFlow = createFakeElement();
  const bootstrapSteps = Array.from({ length: 4 }, createFakeElement);
  const bootstrapNodes = {
    '[data-flow-nav]': createFakeElement(),
    '[data-flow-prev]': createFakeElement(),
    '[data-flow-next]': createFakeElement(),
    '[data-flow-count]': createFakeElement(),
  };
  bootstrapFlow.querySelectorAll = (selector) => {
    assert.equal(selector, '[data-flow-step]', 'Bootstrap must read real flow steps.');
    return bootstrapSteps;
  };
  bootstrapFlow.querySelector = (selector) => {
    assert.ok(bootstrapNodes[selector], 'Bootstrap requested an unknown flow control.');
    return bootstrapNodes[selector];
  };
  sandbox.document = {
    querySelector(selector) {
      assert.equal(selector, '[data-flow]', 'Bootstrap must bind the real flow container.');
      return bootstrapFlow;
    },
  };
  new vm.Script(bootstrap.body, { filename: 'flow-bootstrap-inline.js' }).runInContext(sandbox);
  assert.equal(bootstrapFlow.dataset.flowMode, 'slides', 'The page bootstrap must initialize the executable controller.');
  assertSingleActive(bootstrapSteps, 0);

  assert.match(flowBody, /<nav\b(?=[^>]*\bdata-flow-nav\b)[^>]*>/i, 'Expected a real slide navigation landmark.');
  assert.match(flowBody, /<button\b(?=[^>]*\bdata-flow-prev\b)[^>]*>/i, 'Expected a previous button.');
  assert.match(flowBody, /<button\b(?=[^>]*\bdata-flow-next\b)[^>]*>/i, 'Expected a next button.');
  assert.match(flowBody, /<[^>]+\bdata-flow-count\b[^>]*\baria-live=["']polite["'][^>]*>/i, 'Expected an aria-live polite slide counter.');
  assert.match(styles, /\[data-flow-nav\][^{]*\{[^}]*opacity\s*:\s*\.6/i, 'Navigation must default to 60% opacity.');
  assert.match(styles, /\[data-flow-nav\]:hover[\s\S]{0,180}?opacity\s*:\s*1/i, 'Navigation must reach full opacity on hover.');
  assert.match(styles, /\[data-flow-nav\]:focus-within[\s\S]{0,180}?opacity\s*:\s*1/i, 'Navigation must reach full opacity on keyboard focus.');
  const directionAttribute = 'data-' + 'flowDirection'.replace(/[A-Z]/g, (letter) => '-' + letter.toLowerCase());
  assert.equal(directionAttribute, 'data-flow-direction', 'Controller direction property must map to the CSS attribute.');
  assert.match(styles, new RegExp('\\[' + directionAttribute + '=["' + "'" + ']next["' + "'" + ']\\]', 'i'), 'Expected direction-aware next transition styling.');
  assert.match(styles, new RegExp('\\[' + directionAttribute + '=["' + "'" + ']previous["' + "'" + ']\\]', 'i'), 'Expected direction-aware previous transition styling.');
  assert.match(controller.body, /dataset\.flowDirection/, 'Controller must update the same data-flow-direction attribute used by CSS.');
  assert.match(styles, /@media\s*\(max-width:\s*680px\)[\s\S]{0,800}?\[data-flow-nav\]\s*\{[^}]*position\s*:\s*static/i, 'Mobile navigation must enter normal document flow instead of covering stage content.');
}

try {
  if (!fs.existsSync(target)) fail('Target HTML file not found: ' + target);
  validateDocument(fs.readFileSync(target, 'utf8'));
  console.log('architecture web explainer contract: PASS');
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
