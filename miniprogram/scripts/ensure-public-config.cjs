#!/usr/bin/env node

const fs = require('node:fs')
const path = require('node:path')

const rootDir = path.resolve(__dirname, '..')

const templatePairs = [
  {
    target: 'project.config.json',
    template: 'project.config.json.template'
  },
  {
    target: 'project.private.config.json',
    template: 'project.private.config.json.template'
  },
  {
    target: path.join('src', 'manifest.json'),
    template: path.join('src', 'manifest.json.template')
  }
]

const createdFiles = []

for (const pair of templatePairs) {
  const targetPath = path.join(rootDir, pair.target)
  const templatePath = path.join(rootDir, pair.template)

  if (fs.existsSync(targetPath)) {
    continue
  }

  if (!fs.existsSync(templatePath)) {
    console.error(`[public-config] Missing template: ${pair.template}`)
    process.exit(1)
  }

  fs.copyFileSync(templatePath, targetPath)
  createdFiles.push(pair.target)
}

if (createdFiles.length === 0) {
  console.log('[public-config] Local config files already exist; nothing changed.')
  process.exit(0)
}

console.log('[public-config] Created local config files from templates:')
for (const file of createdFiles) {
  console.log(`- ${file}`)
}
console.log('[public-config] Replace placeholder AppID values before opening the project in WeChat DevTools.')
