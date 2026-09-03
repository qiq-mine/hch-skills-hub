import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const root = path.resolve(import.meta.dirname, '..');
const skill = fs.readFileSync(path.join(root, 'SKILL.md'), 'utf8');
const integrationPath = path.join(root, 'references', 'archscribe-integration.md');
const failures = [];

const requireText = (source, text, label) => {
  if (!source.includes(text)) failures.push(`${label}: missing ${JSON.stringify(text)}`);
};

requireText(skill, 'Web only', 'artifact routing');
requireText(skill, 'Archscribe only', 'artifact routing');
requireText(skill, 'Hybrid', 'artifact routing');
requireText(skill, 'references/archscribe-integration.md', 'integration reference');

if (!fs.existsSync(integrationPath)) {
  failures.push('integration reference: references/archscribe-integration.md does not exist');
} else {
  const integration = fs.readFileSync(integrationPath, 'utf8');
  for (const text of ['共享内容模型', '稳定 ID', '1–3', '4 个及以上', 'inline SVG', 'iframe']) {
    requireText(integration, text, 'integration contract');
  }
}

if (failures.length) {
  console.error(`Skill integration validation failed (${failures.length})`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('Skill integration validation passed');
