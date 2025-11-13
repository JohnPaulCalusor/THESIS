import fs from "fs/promises";
import path from "path";

const ROOT = process.cwd();
const SRC = path.join(ROOT, "src");
const OUT_JSON = path.join(ROOT, "design-map.json");
const OUT_MD = path.join(ROOT, "DESIGN_MAP.md");

const EXPECTED_CSS_ORDER = [
  "./index.css",
  "./styles/election.css",
];

const TOKEN_VARS = ["--brand", "--card", "--surface", "--muted", "--border", "--ring"];
const CLASS_REGEX = {
  btn: /\bbtn\b/gi,
  btnPrimary: /\bbtn-primary\b/gi,
  btnSecondary: /\bbtn-secondary\b/gi,
  card: /\bcard\b/gi,
  badge: /\bbadge\b/gi,
  epAny: /\bep-[a-z0-9-]+\b/gi,
};
const VAR_USAGE_REGEX = /var\(--[a-zA-Z0-9-]+\)/g;
const TEXT_FILE_REGEX = /\.(css|tsx?|jsx?)$/i;
const INLINE_STYLE_EXPRESSION = /style\s*=\s*{{[\s\S]*?}}/gi;
const IGNORE_DIRS = new Set(["node_modules", ".git", "dist", "build", ".next"]);

function rel(p) {
  return path.relative(ROOT, p).replace(/\\/g, "/");
}

async function exists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

async function walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (IGNORE_DIRS.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...await walk(full));
    } else {
      files.push(full);
    }
  }
  return files;
}

async function readFileSafe(p) {
  try {
    return await fs.readFile(p, "utf8");
  } catch {
    return "";
  }
}

function cssImportOrder(source) {
  const order = [];
  const regex = /import\s+(?:.+?\s+from\s+)?["'](.+?\.css)["'];/g;
  for (const match of source.matchAll(regex)) {
    order.push(match[1]);
  }
  return order;
}

function indexCssTailwindOnly(css) {
  const stripped = css.replace(/\/\*[\s\S]*?\*\//g, "").trim();
  const collapsed = stripped.replace(/\s+/g, " ").trim();
  return collapsed === "@tailwind base; @tailwind components; @tailwind utilities;";
}

function tokenAliasStatus(content) {
  const status = {};
  for (const token of TOKEN_VARS) {
    const name = token.replace(/^--/, "");
    const pattern = new RegExp(`--${name}\\s*:\\s*[^;]+;`, "i");
    status[token] = pattern.test(content);
  }
  return status;
}

function firstH1Title(tsx) {
  const match = tsx.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
  if (!match) return null;
  return match[1].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim() || null;
}

function hasEpWrapper(tsx) {
  return /\bclassName\s*=\s*{?\s*["'`][^"'`]*\bep\b/i.test(tsx);
}

function hasEpPage(tsx) {
  return /\bep-page\b/i.test(tsx);
}

function detectScope(tsx) {
  const match = tsx.match(/\b(ep-(?:login|ballot|results|admin))\b/i);
  return match ? match[1] : null;
}

function outerWrapperClasses(tsx) {
  const match = tsx.match(/return\s*\(\s*<[^>]+className\s*=\s*{?\s*["'`]([^"'`]+)["'`]/i);
  return match ? match[1].trim() : null;
}

function inlineStyleMatches(tsx) {
  const matches = [];
  let match;
  while ((match = INLINE_STYLE_EXPRESSION.exec(tsx))) {
    if (/\b(borderColor|background)\b/i.test(match[0])) {
      matches.push(match[0].replace(/\s+/g, " ").trim().slice(0, 160));
    }
  }
  return matches;
}

function perFileClassCounts(content) {
  return Object.fromEntries(
    Object.entries(CLASS_REGEX).map(([key, regex]) => {
      const hits = content.match(regex);
      return [key, hits ? hits.length : 0];
    })
  );
}

function collectVarUsages(content) {
  return [...new Set(content.match(VAR_USAGE_REGEX) || [])].sort();
}

async function main() {
  if (!(await exists(SRC))) {
    throw new Error(`src directory not found at ${SRC}`);
  }

  const allFiles = await walk(SRC);
  const textFiles = allFiles.filter((file) => TEXT_FILE_REGEX.test(file));
  const tsxFiles = textFiles.filter((file) => file.endsWith(".tsx"));

  const fileCache = new Map();
  const classUsageTotals = Object.fromEntries(Object.keys(CLASS_REGEX).map((key) => [key, 0]));
  const globalVarUsages = new Set();
  const inlineStyleHotspots = [];
  const inlineStyleMap = new Map();

  for (const file of textFiles) {
    const content = await readFileSafe(file);
    fileCache.set(file, content);

    for (const [key, regex] of Object.entries(CLASS_REGEX)) {
      const matches = content.match(regex);
      if (matches) classUsageTotals[key] += matches.length;
    }

    const vars = content.match(VAR_USAGE_REGEX);
    if (vars) vars.forEach((v) => globalVarUsages.add(v));

    if (file.endsWith(".tsx")) {
      const inlineMatches = inlineStyleMatches(content);
      inlineStyleMap.set(file, inlineMatches);
      if (inlineMatches.length) {
        inlineStyleHotspots.push({ file: rel(file), matches: inlineMatches });
      }
    }
  }

  const mainPath = path.join(SRC, "main.tsx");
  const mainSrc = fileCache.get(mainPath) ?? await readFileSafe(mainPath);
  const cssOrder = cssImportOrder(mainSrc);
  const cssOrderOk = EXPECTED_CSS_ORDER.every((entry, index) => cssOrder[index] === entry);

  const indexCssPath = path.join(SRC, "index.css");
  const indexCss = fileCache.get(indexCssPath) ?? await readFileSafe(indexCssPath);
  const indexCssOk = indexCssTailwindOnly(indexCss);

  const topbarPath = path.join(SRC, "modules", "components", "Topbar.tsx");
  const topbarSrc = fileCache.get(topbarPath) ?? await readFileSafe(topbarPath);
  const topbarHasEpNav = /\bep-nav\b/.test(topbarSrc);
  const topbarHasInner = /\bep-nav-inner\b/.test(topbarSrc);

  const portalCssPath = path.join(SRC, "styles", "election.css");
  const portalExists = await exists(portalCssPath);
  const portalCss = portalExists ? (fileCache.get(portalCssPath) ?? await readFileSafe(portalCssPath)) : "";
  const tokenStatus = tokenAliasStatus(portalCss);
  const tokensOk = portalExists ? Object.values(tokenStatus).every(Boolean) : false;

  const pageFiles = tsxFiles
    .filter((file) => {
      const normalized = rel(file);
      return normalized.includes("src/modules/pages/") || normalized.includes("src/modules/election/pages/");
    })
    .sort();

  const pages = pageFiles.map((file) => {
    const content = fileCache.get(file) ?? "";
    const inlineMatches = inlineStyleMap.get(file) ?? [];
    return {
      file: rel(file),
      component: path.basename(file, ".tsx"),
      hasEpWrapper: hasEpWrapper(content),
      hasEpPage: hasEpPage(content),
      scope: detectScope(content),
      outerWrapperClasses: outerWrapperClasses(content),
      h1: firstH1Title(content),
      inlineStyleMatches: inlineMatches,
      classCounts: perFileClassCounts(content),
      varsUsed: collectVarUsages(content),
    };
  });

  const adminDupes = pageFiles
    .filter((file) => path.basename(file) === "AdminElectionPage.tsx")
    .map((file) => rel(file));

  const result = {
    generatedAt: new Date().toISOString(),
    css: {
      mainPath: rel(mainPath),
      cssOrder,
      cssOrderOk,
      expectedOrder: EXPECTED_CSS_ORDER,
      indexCssPath: rel(indexCssPath),
      indexCssOk,
      portalCssPath: portalExists ? rel(portalCssPath) : "(missing)",
      portalCssExists: portalExists,
    },
    tokens: {
      path: portalExists ? rel(portalCssPath) : "(missing)",
      status: tokenStatus,
      ok: tokensOk,
    },
    topbar: {
      path: rel(topbarPath),
      hasEpNav: topbarHasEpNav,
      hasEpNavInner: topbarHasInner,
      ok: topbarHasEpNav && topbarHasInner,
    },
    duplicates: {
      adminElectionPages: adminDupes,
    },
    inlineStyleHotspots,
    classUsage: {
      totals: classUsageTotals,
      varUsages: [...globalVarUsages].sort(),
    },
    pages,
  };

  await fs.writeFile(OUT_JSON, JSON.stringify(result, null, 2) + "\n", "utf8");

  const md = [];
  md.push("# PAPSAS Design Map", "");
  md.push(`Generated: ${result.generatedAt}`, "");
  md.push("## Global CSS wiring");
  md.push(`- Import order OK: ${cssOrderOk ? "[OK]" : "[CHECK]"} (current: ${cssOrder.join(" -> ") || "none"})`);
  md.push(`- index.css Tailwind only: ${indexCssOk ? "[OK]" : "[CHECK]"}`);
  md.push(`- Portal stylesheet present: ${result.css.portalCssExists ? "[OK]" : "[CHECK]"} (${result.css.portalCssPath})`);
  md.push(`- Token definitions: ${result.tokens.ok ? "[OK]" : "[CHECK]"} (source: ${result.tokens.path})`);
  md.push(`- Topbar ep-nav hooks: ${result.topbar.ok ? "[OK]" : "[CHECK]"} (ep-nav: ${result.topbar.hasEpNav ? "yes" : "no"}, ep-nav-inner: ${result.topbar.hasEpNavInner ? "yes" : "no"})`);
  md.push("");
  md.push("## Duplicates");
  if (adminDupes.length) {
    adminDupes.forEach((file) => md.push(`- ${file}`));
  } else {
    md.push("- none");
  }
  md.push("");
  md.push("## Inline style overrides");
  if (inlineStyleHotspots.length === 0) {
    md.push("- none detected");
  } else {
    inlineStyleHotspots.forEach((entry) => {
      md.push(`- ${entry.file}`);
      entry.matches.forEach((snippet) => md.push(`  - ${snippet}`));
    });
  }
  md.push("");
  md.push("## Global class usage counts");
  md.push(`- btn: ${classUsageTotals.btn}; btn-primary: ${classUsageTotals.btnPrimary}; btn-secondary: ${classUsageTotals.btnSecondary}`);
  md.push(`- card: ${classUsageTotals.card}; badge: ${classUsageTotals.badge}; ep-* classes: ${classUsageTotals.epAny}`);
  md.push(`- CSS vars in JSX: ${result.classUsage.varUsages.join(", ") || "(none)"}`);
  md.push("");
  md.push("## Pages");
  if (pages.length === 0) {
    md.push("- No page files found.");
  } else {
    pages.forEach((page) => {
      md.push(`### ${page.component}`);
      md.push(`- File: \`${page.file}\``);
      md.push(`- Wrapper classes: ${page.outerWrapperClasses || "(not detected)"}`);
      md.push(`- Has .ep: ${page.hasEpWrapper ? "[OK]" : "[MISS]"}; Has .ep-page: ${page.hasEpPage ? "[OK]" : "[MISS]"}; Scope: ${page.scope || "(none)"}`);
      md.push(`- <h1>: ${page.h1 || "(none)"}`);
      md.push(`- Inline style matches (bg/border): ${page.inlineStyleMatches.length}`);
      md.push(`- CSS vars: ${page.varsUsed.join(", ") || "(none)"}`);
      md.push(`- Class counts: btn=${page.classCounts.btn}, btn-primary=${page.classCounts.btnPrimary}, btn-secondary=${page.classCounts.btnSecondary}, card=${page.classCounts.card}, badge=${page.classCounts.badge}, ep-*=${page.classCounts.epAny}`);
      md.push("");
    });
  }

  await fs.writeFile(OUT_MD, md.join("\n"), "utf8");

  console.log("Design scan complete.");
  console.log(`- ${rel(OUT_JSON)}`);
  console.log(`- ${rel(OUT_MD)}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
