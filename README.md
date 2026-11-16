<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="Nikhil Chandrakanti — full-stack engineer who ships software real people use" src="assets/banner-dark.svg" width="100%">
</picture>

<p align="center">
  <a href="https://hostelconnect-o8e6.onrender.com"><img src="https://img.shields.io/badge/HostelConnect-live%20%26%20in%20use-34D399?style=flat-square&logo=render&logoColor=white" alt="HostelConnect live"></a>
  <a href="https://www.linkedin.com/in/nnikhilc97/"><img src="https://img.shields.io/badge/LinkedIn-connect-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="https://leetcode.com/u/nikku-2004"><img src="https://img.shields.io/badge/LeetCode-daily%20DSA-F5A524?style=flat-square&logo=leetcode&logoColor=white" alt="LeetCode"></a>
  <img src="https://img.shields.io/badge/open%20to-SDE%20%2F%20Full--Stack%20roles%20·%202027-14182A?style=flat-square" alt="Open to SDE roles, 2027 graduate">
</p>

```ts
const nikhil = {
  studying:   "CS & IT, MVSR Engineering College (final year)",
  focus:      ["full-stack web", "backend reliability", "dev tools"],
  shipped:    "HostelConnect: runs my own 200-student hostel",
  building:   "Repository Intelligence (final-year project)",
  lookingFor: "SDE / Full-Stack roles, graduating 2027",
};
```

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/divider-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/divider-light.svg">
  <img alt="" src="assets/divider-dark.svg" width="100%">
</picture>

## 🚀 Shipped

<table>
<tr>
<td width="50%" valign="top">

### [HostelConnect](https://github.com/nick10-05/HOSTELCONNECT)
`🟢 live · real users`

My hostel ran on a WhatsApp group: complaints got buried, the same issue came back daily, and the owner locked the group. I replaced it with an owner-first app for complaints, announcements, fee tracking with UPI, and post-holiday return polls.

- **200 students**, two buildings, **₹0/month** on free tiers
- **20+ merged PRs**: every change shipped from its own branch
- Per-account login limits, sessions revoked on password change
- Photos compressed in the browser and auto-deleted after 48 h

`React` `TypeScript` `Express` `PostgreSQL` `Supabase` `Vitest` `GitHub Actions`

**[Live app →](https://hostelconnect-o8e6.onrender.com)**

</td>
<td width="50%" valign="top">

### [RelayForge](https://github.com/nick10-05/RelayForge)
`⚙️ backend reliability · 41 test files`

Webhooks fail silently. RelayForge sits in between: it stores every event before acknowledging it, delivers it with retries, crash recovery and a dead-letter state, and lets you replay anything from a dashboard.

- **At-least-once delivery:** transactional outbox, Postgres queue with `SKIP LOCKED` + leases, fenced completion
- **Security:** SSRF-safe outbound client, Standard Webhooks signing, AES-GCM secrets at rest
- **Proven by tests:** concurrency, crash recovery and poison payloads against a chaos receiver, on real Postgres in CI
- One Docker image, **₹0/month** on Render + Neon

`Node.js 24` `TypeScript` `Fastify` `PostgreSQL` `Drizzle` `React` `Docker`

**[Design & README →](https://github.com/nick10-05/RelayForge#readme)**

</td>
</tr>
<tr>
<td width="50%" valign="top">

### [Sundara Kanda](https://github.com/nick10-05/sundara-sara-sangam)
`🎧 audio · 6 languages`

Explore verses 11–20 of the Sundara Kanda with chanted audio, word-by-word meanings, and summaries in six languages.

`React` `TypeScript` `Vite` `shadcn/ui` `Supabase`

</td>
<td width="50%" valign="top">

### Repository Intelligence
`🔨 in progress · final-year project`

Point it at a codebase and see how it fits together: architecture, dependency graphs, and the files a change is likely to break *before* you merge it.

`Static analysis` `Dependency graphs` `Change impact`

</td>
</tr>
</table>

## 📡 Live from my commits

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/terminal-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/terminal-light.svg">
  <img alt="My six most recent commits across my public repositories" src="assets/terminal-dark.svg" width="100%">
</picture>

<sub>Rebuilt every day by a <a href=".github/workflows/build-profile.yml">GitHub Action</a> that reads the GitHub API and redraws these SVGs, banner included. This profile ships the same way my projects do.</sub>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/divider-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/divider-light.svg">
  <img alt="" src="assets/divider-dark.svg" width="100%">
</picture>

## 🧭 How I build

| Habit | Where you can check it |
|---|---|
| Every change goes through a pull request | HostelConnect's PR history |
| Tests run in CI on every push | RelayForge: lint → typecheck → tests on real Postgres → Docker build |
| Security from day one, not bolted on | Login limits, session revocation, no secrets in git |
| Design for real constraints | HostelConnect runs 200 users for ₹0 a month |
| READMEs explain *why*, not only *how* | Start with HostelConnect's "Why it exists" |

## 🛠️ Toolbox

<p>
  <img src="https://skillicons.dev/icons?i=ts,js,py,java,cpp" alt="Languages" height="40"><br>
  <img src="https://skillicons.dev/icons?i=react,vite,tailwind,nodejs,express,postgres,supabase" alt="Frontend, backend and data" height="40"><br>
  <img src="https://skillicons.dev/icons?i=git,githubactions,docker,linux,vscode" alt="Shipping and tooling" height="40">
</p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/divider-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/divider-light.svg">
  <img alt="" src="assets/divider-dark.svg" width="100%">
</picture>

## 📍 Now

- 🔨 **Building** Repository Intelligence, my final-year project
- 🚀 **Up next:** DriveRadar, a placement-notice tracker for my batch
- 🧠 **Daily:** data structures and algorithms on [LeetCode](https://leetcode.com/u/nikku-2004)

<p align="center"><sub><code>git commit -m "thanks for reading this far"</code></sub></p>
