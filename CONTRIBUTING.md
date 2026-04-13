# Contributing to Space Grade Linux

Space Grade Linux (SGL) is a Yocto layer for building a Linux distribution
targeted at space missions. This document describes how to build the layer,
how to propose changes, the licensing expectations for inbound contributions,
and how the contributor and committer roles work.

## Getting the source

```bash
git clone https://github.com/elisa-tech/meta-sgl
cd meta-sgl
```

The default branch is `main`. All pull requests target `main`.

## Building locally

Builds are driven by [kas](https://kas.readthedocs.io/). The `kas/` directory
contains the configurations for each supported target. The same kas configs
are used by the GitHub Actions workflows in `.github/workflows/`, so a local
build and a CI build produce the same image from the same inputs.

See [`docs/building.md`](docs/building.md) for step-by-step instructions,
including installing kas, picking a target, and running the resulting image
under QEMU.

### Supported Yocto releases

`meta-sgl-core/conf/layer.conf` declares `LAYERSERIES_COMPAT` for the layer.
The current value is:

```
kirkstone scarthgap walnascar whinlatter
```

`scarthgap` is the release exercised in CI and the default for new targets.
If you are adding a new kas configuration, prefer `scarthgap` unless there is
a concrete reason to target a different release, and update the compat list
if you introduce support for a new one.

### Adding a new build target

Walkthroughs for creating a new kas configuration and wiring it into the
reusable GitHub Actions workflow live in
[`docs/contribute.md`](docs/contribute.md).

## Proposing changes

Changes are proposed as GitHub pull requests against `main`.

### Branch naming

Use a short, prefixed branch name. Common prefixes in this repo are:

- `<handle>/<topic>` for contributor-scoped work (for example,
  `{username}/add-contributing`, `{username}/kas-qemux86-64-support`).
- `ci/<topic>` for CI and workflow changes.
- `feature/<topic>` for user-visible features.
- `fix/<topic>` for bug fixes.

Match whichever pattern you have been using in prior PRs. Consistency within
your own history matters more than which prefix you pick.

### Commits

Keep commits small and focused. Write commit messages in the imperative mood
and use a scope prefix that matches the area you are touching, for example:

```
kas: add QEMU SpaceROS and x86-64 build targets
ci: upload build artifacts and bump actions to Node.js 24
meta-sgl-core: add zeroconf networking as optional image feature
```

### Developer Certificate of Origin

All commits must include a `Signed-off-by` trailer, certifying that you wrote
the patch or otherwise have the right to submit it under the project's
licenses. The full text of the DCO is at
[developercertificate.org](https://developercertificate.org/).

Add the trailer automatically by passing `-s` when you commit:

```bash
git commit -s
```

Commits without a sign-off will not be merged.

### Pull requests

- Open the PR against `main`.
- In the description, explain what the change does and why. Link the issue it
  closes, if any.
- Keep the diff reviewable. Split unrelated changes into separate PRs.
- Make sure CI passes on all affected targets before requesting review.
- Respond to review feedback with follow-up commits on the same branch; do
  not force-push over in-flight review unless a maintainer asks you to.

## Licensing of contributions

This repository is dual-licensed. By submitting a contribution you agree to
license it under the terms described below.

### Inbound license

- **Code and metadata** (recipes, classes, configuration, scripts, CI, kas
  files) is contributed under the [MIT License](LICENSE.MIT).
- **Documentation** (files under `docs/`, READMEs, and similar prose) is
  currently contributed under
  [Creative Commons Attribution-ShareAlike 4.0](LICENSE.CC-BY-SA-4.0), as
  stated in [`LICENSE`](LICENSE).

See [`LICENSE`](LICENSE) for the authoritative summary.

### SPDX identifiers

New files should carry an [SPDX License
Identifier](https://spdx.dev/) near the top. Use:

- `SPDX-License-Identifier: MIT` for code, recipes, and configuration.
- The matching SPDX identifier for the documentation license currently in use
  (see [`LICENSE`](LICENSE)) for new prose files.

If a file pulls in third-party material under a different license, record
that license in the file header and, where relevant, in the recipe.

## Contributor and committer roles

SGL uses two roles for participation in this repository.

### Contributors

Anyone who sends a pull request, files an issue, or joins a discussion is a
contributor. There is no paperwork to sign beyond the per-commit DCO sign-off
described above. Contributors do not have write access to the repository;
their changes land through review by a committer.

### Committers

Committers have write access to `meta-sgl` and are responsible for:

- Reviewing and merging pull requests.
- Keeping CI green on `main`.
- Triaging issues and security reports.
- Maintaining the contribution policies in this file.

#### Becoming a committer

A contributor may be proposed as a committer by any existing committer, on
the basis of a track record of sustained, high-quality contributions to this
repository. Proposals are made to the existing committers. A proposal is
accepted if it receives a majority vote of the existing committers. The
proposing committer records the outcome by updating the maintainers list
in this file.

#### Stepping down or removing a committer

A committer may step down at any time by opening a pull request that removes
their entry from the maintainers list.

A committer may be removed for sustained inactivity or for conduct that is
incompatible with this project. Removal is proposed to the existing
committers and takes effect on a majority vote of the existing committers,
excluding the committer under consideration. Removal is recorded by updating
the maintainers list in this file.

### Current maintainers

- Ramón Roche ([@mrpollo](https://github.com/mrpollo)) — project lead
- Philip Balister ([@balister](https://github.com/balister))
- Tim Bird ([@tbird20d](https://github.com/tbird20d))
- Ivan Perez ([@ivanperez-keera](https://github.com/ivanperez-keera))
- Rob Woolley ([@robwoolley](https://github.com/robwoolley))
- Pedro Roque ([@Pedro-Roque](https://github.com/Pedro-Roque))

## Communication

- **Issues**: open a [GitHub issue](https://github.com/elisa-tech/meta-sgl/issues)
  for bugs, build failures, and proposals.
- **Pull requests**: use [GitHub pull requests](https://github.com/elisa-tech/meta-sgl/pulls)
  for code and documentation changes.
- **Mailing list**: [Mailing List](https://lists.elisa.tech/g/space-grade-linux)
- **Chat**: [Discord](https://chat.elisa.tech/)
- **Regular meetings**: [Calendar](https://elisa.tech/community/meetings/)

## Reporting security issues

Please do not file public GitHub issues for suspected security vulnerabilities.

Until a dedicated disclosure channel is in place, contact a maintainer
privately (see the maintainers list above) and allow time for a fix before
any public disclosure.

## Code of Conduct

Participation in this project is governed by the Code of Conduct and policies
published at <https://lfprojects.org/policies/>. By participating, you agree
to uphold them.

<!-- TODO(coc): replace with a project-specific Code of Conduct if one is adopted. -->
