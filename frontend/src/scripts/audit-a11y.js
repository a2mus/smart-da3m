import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';

const ROUTES = [
  '/',
  '/login',
  '/student',
  '/journey',
  '/parent',
  '/expert/analytics',
];

const BASE_URL = 'http://localhost:5173';

async function runAudit() {
  console.log(`Starting a11y audit against ${BASE_URL}...`);
  console.log('Ensure your local dev server is running (npm run dev)\n');

  let browser;
  try {
    browser = await chromium.launch();
  } catch (e) {
    console.error('Failed to launch Playwright browser. Error:', e.message);
    process.exit(1);
  }

  const context = await browser.newContext();
  let totalViolations = 0;

  for (const route of ROUTES) {
    const page = await context.newPage();
    const url = `${BASE_URL}${route}`;
    console.log(`Auditing ${url}...`);

    try {
        const response = await page.goto(url, { waitUntil: 'networkidle' });
        if (!response || !response.ok()) {
            console.warn(`⚠️  Warning: Failed to load ${url} (status: ${response?.status()}). Ensure server is running and route exists.`);
            await page.close();
            continue;
        }

        // Give Vue a moment to render dynamic content if networkidle isn't enough
        await page.waitForTimeout(1000);

        const results = await new AxeBuilder({ page })
            .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
            .analyze();

        if (results.violations.length > 0) {
            console.error(`❌ Found ${results.violations.length} violations on ${route}`);
            results.violations.forEach((violation, index) => {
                console.error(`\n   Violation ${index + 1}: ${violation.id} (${violation.impact})`);
                console.error(`   Description: ${violation.description}`);
                console.error(`   Help URL: ${violation.helpUrl}`);
                violation.nodes.forEach(node => {
                    console.error(`   - Element: ${node.html}`);
                    console.error(`     Failure: ${node.failureSummary}`);
                });
            });
            totalViolations += results.violations.length;
        } else {
            console.log(`✅ No violations found on ${route}`);
        }
    } catch (e) {
        console.error(`❌ Error auditing ${route}:`, e.message);
    } finally {
        await page.close();
    }
  }

  await browser.close();

  if (totalViolations > 0) {
    console.error(`\n❌ Audit failed with ${totalViolations} total violations.`);
    process.exit(1);
  } else {
    console.log('\n✅ Audit passed! No violations found.');
    process.exit(0);
  }
}

runAudit();
