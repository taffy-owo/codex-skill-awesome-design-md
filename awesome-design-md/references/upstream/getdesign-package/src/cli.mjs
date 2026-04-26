#!/usr/bin/env node

import { access, copyFile, mkdir, readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const PKG_ROOT = path.resolve(__dirname, '..')
const TEMPLATES_DIR = path.join(PKG_ROOT, 'templates')
const MANIFEST_PATH = path.join(TEMPLATES_DIR, 'manifest.json')
const PKG_PATH = path.join(PKG_ROOT, 'package.json')
const DEFAULT_CLI_TELEMETRY_URL = 'https://getdesign.md/api/cli/downloads'
const CLI_TELEMETRY_TIMEOUT_MS = 1500

let packageJsonCache = null

// ANSI colors (zero dependencies)
const c = {
  pink: s => `\x1b[38;2;255;177;238m${s}\x1b[0m`,
  white: s => `\x1b[97m${s}\x1b[0m`,
  green: s => `\x1b[32m${s}\x1b[0m`,
  dim: s => `\x1b[2m${s}\x1b[0m`,
  gray: s => `\x1b[38;2;160;160;160m${s}\x1b[0m`,
  bold: s => `\x1b[1m${s}\x1b[0m`,
}

// Original ANSI Shadow font (6 rows)
const L = {
  G: [' ██████╗ ','██╔════╝ ','██║  ███╗','██║   ██║','╚██████╔╝',' ╚═════╝ '],
  E: ['███████╗','██╔════╝','█████╗  ','██╔══╝  ','███████╗','╚══════╝'],
  T: ['████████╗','╚══██╔══╝','   ██║   ','   ██║   ','   ██║   ','   ╚═╝   '],
  D: ['██████╗ ','██╔══██╗','██║  ██║','██║  ██║','██████╔╝','╚═════╝ '],
  S: ['███████╗','██╔════╝','███████╗','╚════██║','███████║','╚══════╝'],
  I: ['██╗','██║','██║','██║','██║','╚═╝'],
  N: ['███╗   ██╗','████╗  ██║','██╔██╗ ██║','██║╚██╗██║','██║ ╚████║','╚═╝  ╚═══╝'],
  '.':['   ','   ','   ','   ','██╗','╚═╝'],
  M: ['███╗   ███╗','████╗ ████║','██╔████╔██║','██║╚██╔╝██║','██║ ╚═╝ ██║','╚═╝     ╚═╝'],
}

function printBanner() {
  console.log()
  for (let row = 0; row < 6; row++) {
    const line = ['G','E','T'].map(ch => L[ch][row]).join('')
    console.log(`  ${c.white(line)}`)
  }
  for (let row = 0; row < 6; row++) {
    const design = ['D','E','S','I','G','N'].map(ch => L[ch][row]).join('')
    const md     = ['.','M','D'].map(ch => L[ch][row]).join('')
    console.log(`  ${c.pink(design)}${c.white(md)}`)
  }
  console.log()
}

function printSuccess({ brand, filePath, mode }) {
  const relativePath = path.relative(process.cwd(), filePath) || filePath

  printBanner()
  console.log(`  ${c.green('✓')} DESIGN.md inspired by ${c.white(brand)} ${mode === 'updated' ? 'updated' : 'installed'}`)
  console.log(`    ${c.dim('→ ' + relativePath)}`)
  console.log()
  console.log(`  ${c.gray('Tell your coding agent to use this file as')}`)
  console.log(`  ${c.gray('reference before writing any UI.')}`)
  console.log(`  ${c.gray('Customize it as your project evolves.')}`)
  console.log()
}

function printNestedSuccess({ brand, filePath }) {
  const relativePath = path.relative(process.cwd(), filePath) || filePath

  printBanner()
  console.log(`  ${c.green('✓')} DESIGN.md inspired by ${c.white(brand)} saved`)
  console.log(`    ${c.dim('→ ' + relativePath)}`)
  console.log()
  console.log(`  ${c.gray('DESIGN.md already exists at root. To make this one active:')}`)
  console.log(`  ${c.dim('cp ' + brand + '/DESIGN.md ./DESIGN.md')}`)
  console.log()
  console.log(`  ${c.gray('Tell your coding agent to use this file as')}`)
  console.log(`  ${c.gray('reference before writing any UI.')}`)
  console.log(`  ${c.gray('Customize it as your project evolves.')}`)
  console.log()
}

function printHelp() {
  console.log(`getdesign CLI

Usage:
  getdesign add <brand> [--force] [--out <path>]
  getdesign list

Examples:
  npx getdesign add airbnb          # first add → ./DESIGN.md
  npx getdesign add stripe          # already exists → ./stripe/DESIGN.md
  npx getdesign add ibm --force     # overwrite active DESIGN.md
  npx getdesign add ibm --out ./docs/DESIGN.md
  npx getdesign list`)
}

async function pathExists(targetPath) {
  try {
    await access(targetPath)
    return true
  } catch {
    return false
  }
}

async function loadManifest() {
  const raw = await readFile(MANIFEST_PATH, 'utf8')
  const parsed = JSON.parse(raw)

  if (!Array.isArray(parsed)) {
    throw new Error('Invalid manifest format: expected an array')
  }

  return parsed
}

async function loadPackageJson() {
  if (packageJsonCache) {
    return packageJsonCache
  }

  const raw = await readFile(PKG_PATH, 'utf8')
  packageJsonCache = JSON.parse(raw)
  return packageJsonCache
}

async function findProjectRoot(startDir) {
  let current = path.resolve(startDir)

  while (true) {
    const packageJsonPath = path.join(current, 'package.json')
    const gitPath = path.join(current, '.git')

    if ((await pathExists(packageJsonPath)) || (await pathExists(gitPath))) {
      return current
    }

    const parent = path.dirname(current)
    if (parent === current) {
      return null
    }

    current = parent
  }
}

function resolveBrand(input, entries) {
  const exact = entries.find(entry => entry.brand === input)
  if (exact) return exact

  const lower = input.toLowerCase()
  return entries.find(entry => entry.brand.toLowerCase() === lower) ?? null
}

function parseAddOptions(args) {
  let force = false
  let outPath = null

  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i]

    if (arg === '--force' || arg === '-f') {
      force = true
      continue
    }

    if (arg === '--out' || arg === '-o') {
      const next = args[i + 1]
      if (!next || next.startsWith('-')) {
        throw new Error('--out requires a path value')
      }
      outPath = next
      i += 1
      continue
    }

    throw new Error(`Unknown option: ${arg}`)
  }

  return { force, outPath }
}

function isTelemetryEnabled() {
  const disabled = process.env.GETDESIGN_DISABLE_TELEMETRY?.trim().toLowerCase()
  return disabled !== '1' && disabled !== 'true' && disabled !== 'yes'
}

function getTelemetryUrl() {
  const overrideUrl = process.env.GETDESIGN_TELEMETRY_URL?.trim()
  return overrideUrl || DEFAULT_CLI_TELEMETRY_URL
}

async function trackSuccessfulAdd({ brand, installMode }) {
  if (!isTelemetryEnabled()) {
    return
  }

  const pkg = await loadPackageJson()
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), CLI_TELEMETRY_TIMEOUT_MS)

  try {
    await fetch(getTelemetryUrl(), {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        eventId: crypto.randomUUID(),
        brand,
        cliVersion: typeof pkg.version === 'string' ? pkg.version : null,
        command: 'add',
        installMode,
        nodeVersion: process.version,
        platform: process.platform,
      }),
      signal: controller.signal,
    })
  } catch {
    // Ignore telemetry errors; installs should not fail because of analytics.
  } finally {
    clearTimeout(timeoutId)
  }
}

async function runList() {
  const entries = await loadManifest()

  for (const entry of entries) {
    console.log(`${entry.brand} - ${entry.description}`)
  }
}

async function runAdd(commandArgs) {
  const brandArg = commandArgs[0]
  if (!brandArg) {
    throw new Error('Missing brand. Usage: getdesign add <brand>')
  }

  const { force, outPath } = parseAddOptions(commandArgs.slice(1))
  const entries = await loadManifest()
  const selected = resolveBrand(brandArg, entries)

  if (!selected) {
    const available = entries.map(entry => entry.brand).join(', ')
    throw new Error(`Unknown brand: ${brandArg}\nAvailable brands: ${available}`)
  }

  const sourcePath = path.join(TEMPLATES_DIR, selected.file)
  if (!(await pathExists(sourcePath))) {
    throw new Error(`Template file not found for brand '${selected.brand}': ${sourcePath}`)
  }

  const projectRoot = (await findProjectRoot(process.cwd())) ?? process.cwd()

  if (outPath) {
    // Explicit output path — write directly
    const targetPath = path.resolve(process.cwd(), outPath)
    const targetExists = await pathExists(targetPath)
    if (targetExists && !force) {
      throw new Error(`Target already exists: ${targetPath}\nUse --force to overwrite.`)
    }
    await mkdir(path.dirname(targetPath), { recursive: true })
    await copyFile(sourcePath, targetPath)
    await trackSuccessfulAdd({ brand: selected.brand, installMode: 'custom' })
    printSuccess({ brand: selected.brand, filePath: targetPath, mode: targetExists ? 'updated' : 'installed' })
    return
  }

  const rootDesign = path.join(projectRoot, 'DESIGN.md')
  const rootExists = await pathExists(rootDesign)

  if (!rootExists || force) {
    // No DESIGN.md yet (or --force) → write to root
    await copyFile(sourcePath, rootDesign)
    await trackSuccessfulAdd({ brand: selected.brand, installMode: 'root' })
    printSuccess({ brand: selected.brand, filePath: rootDesign, mode: rootExists ? 'updated' : 'installed' })
  } else {
    // DESIGN.md already exists → write to brand subfolder
    const brandDir = path.join(projectRoot, selected.brand)
    const brandDesign = path.join(brandDir, 'DESIGN.md')
    await mkdir(brandDir, { recursive: true })
    await copyFile(sourcePath, brandDesign)
    await trackSuccessfulAdd({ brand: selected.brand, installMode: 'nested' })
    printNestedSuccess({ brand: selected.brand, filePath: brandDesign })
  }
}

async function main() {
  const args = process.argv.slice(2)
  const command = args[0]

  if (!command || command === '--help' || command === '-h') {
    printHelp()
    return
  }

  if (command === '--version' || command === '-v') {
    const pkg = await loadPackageJson()
    console.log(pkg.version)
    return
  }

  if (command === 'list' || command === 'ls') {
    await runList()
    return
  }

  if (command === 'add' || command === 'install') {
    await runAdd(args.slice(1))
    return
  }

  throw new Error(`Unknown command: ${command}`)
}

main().catch(error => {
  const message = error instanceof Error ? error.message : String(error)
  console.error(`Error: ${message}`)
  process.exit(1)
})
