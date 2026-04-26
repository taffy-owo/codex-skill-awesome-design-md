#!/usr/bin/env node

import { copyFile, mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises'
import { execFile } from 'node:child_process'
import { createHash } from 'node:crypto'
import path from 'node:path'
import { promisify } from 'node:util'
import vm from 'node:vm'
import { fileURLToPath } from 'node:url'

const execFileAsync = promisify(execFile)

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const REPO_ROOT = path.resolve(__dirname, '../..')
const DESIGN_MD_ROOT = path.join(REPO_ROOT, 'design-md')
const CLI_PKG_PATH = path.join(REPO_ROOT, 'cli', 'package.json')
const GENERATED_DATA_PATH = path.join(REPO_ROOT, 'app', 'data', 'generated', 'designs.generated.ts')
const TEMPLATES_DIR = path.join(REPO_ROOT, 'cli', 'templates')
const RELEASES_DIR = path.join(REPO_ROOT, 'cli', 'releases')
const MANIFEST_PATH = path.join(TEMPLATES_DIR, 'manifest.json')

function parseDescriptionsFromGeneratedTs(content) {
  const descriptionsByOwner = new Map()

  const entryRegex = /description:\s*('(?:\\.|[^'])*'|"(?:\\.|[^"])*")\s*,[\s\S]*?owner:\s*'([^']+)'/g
  let match

  while ((match = entryRegex.exec(content)) !== null) {
    const rawDescription = match[1]
    const owner = match[2]

    let description = ''
    try {
      description = vm.runInNewContext(rawDescription)
    } catch {
      description = String(rawDescription)
    }

    descriptionsByOwner.set(owner, description)
  }

  return descriptionsByOwner
}

async function ensureDir(dirPath) {
  await mkdir(dirPath, { recursive: true })
}

function computeHash(content) {
  return `sha256:${createHash('sha256').update(content, 'utf8').digest('hex')}`
}

async function getCliVersion() {
  const pkgRaw = await readFile(CLI_PKG_PATH, 'utf8')
  const pkg = JSON.parse(pkgRaw)
  return String(pkg.version)
}

async function getSourceGitMetadata(absSourcePath) {
  const relSourcePath = path.relative(REPO_ROOT, absSourcePath)

  try {
    const { stdout } = await execFileAsync(
      'git',
      ['-C', REPO_ROOT, 'log', '-1', '--format=%H%x1f%cI', '--', relSourcePath],
      { encoding: 'utf8' },
    )

    const trimmed = stdout.trim()
    if (!trimmed) {
      return { sourceCommit: null, sourceUpdatedAt: null }
    }

    const [sourceCommit, sourceUpdatedAt] = trimmed.split('\x1f')
    return {
      sourceCommit: sourceCommit || null,
      sourceUpdatedAt: sourceUpdatedAt || null,
    }
  } catch {
    return { sourceCommit: null, sourceUpdatedAt: null }
  }
}

async function removeStaleTemplates(validTemplateFiles) {
  const existing = await readdir(TEMPLATES_DIR, { withFileTypes: true })

  for (const entry of existing) {
    if (!entry.isFile()) continue
    if (!entry.name.endsWith('.md')) continue
    if (!validTemplateFiles.has(entry.name)) {
      await rm(path.join(TEMPLATES_DIR, entry.name), { force: true })
    }
  }
}

async function main() {
  const cliVersion = await getCliVersion()

  await ensureDir(TEMPLATES_DIR)
  await ensureDir(RELEASES_DIR)

  const generatedSource = await readFile(GENERATED_DATA_PATH, 'utf8')
  const descriptionsByOwner = parseDescriptionsFromGeneratedTs(generatedSource)

  const owners = (await readdir(DESIGN_MD_ROOT, { withFileTypes: true }))
    .filter(entry => entry.isDirectory())
    .map(entry => entry.name)
    .sort((a, b) => a.localeCompare(b))

  const manifest = []
  const validTemplateFiles = new Set()

  for (const owner of owners) {
    const sourceDesignPath = path.join(DESIGN_MD_ROOT, owner, 'DESIGN.md')
    let sourceContent = ''

    try {
      sourceContent = await readFile(sourceDesignPath, 'utf8')
    } catch {
      continue
    }

    const templateFile = `${owner}.md`
    const targetTemplatePath = path.join(TEMPLATES_DIR, templateFile)
    const templateHash = computeHash(sourceContent)
    const { sourceCommit, sourceUpdatedAt } = await getSourceGitMetadata(sourceDesignPath)

    await copyFile(sourceDesignPath, targetTemplatePath)
    validTemplateFiles.add(templateFile)

    manifest.push({
      brand: owner,
      file: templateFile,
      description: descriptionsByOwner.get(owner) ?? `${owner} design system template.`,
      templateHash,
      sourceCommit,
      sourceUpdatedAt,
    })
  }

  await removeStaleTemplates(validTemplateFiles)
  await writeFile(MANIFEST_PATH, JSON.stringify(manifest, null, 2) + '\n', 'utf8')

  const releaseSnapshot = {
    cliVersion,
    generatedAt: new Date().toISOString(),
    templateCount: manifest.length,
    templates: manifest,
  }
  const releasePath = path.join(RELEASES_DIR, `${cliVersion}.json`)
  await writeFile(releasePath, JSON.stringify(releaseSnapshot, null, 2) + '\n', 'utf8')

  console.log(`Synced ${manifest.length} templates to ${TEMPLATES_DIR}`)
  console.log(`Wrote release snapshot: ${releasePath}`)
}

main().catch(error => {
  const message = error instanceof Error ? error.message : String(error)
  console.error(`sync-templates failed: ${message}`)
  process.exit(1)
})
