# How to contribute

To contribute, please send GitHub pull requests to the meta-sgl repository.
Make sure your commits include a Signed-off-by line to comply with the [Developer Certificate of Origin (DCO)](https://developercertificate.org/).

To sign off your commits, use the `-s` flag:

```bash
git commit -sv
```

## Contribute to documentation

The SGL website and documentation is written in Markdown and compiled into a
static website using [VitePress](https://vitepress.dev/).

### Setup the documentation environment

1. Clone the meta-sgl repository and change to the docs/ directory:
```bash
git clone https://github.com/elisa-tech/meta-sgl
cd meta-sgl/docs/
```

2. Install VitePress and generate the website:

Prerequisites: You need Nodejs and npm (Node Package manager) to use VitePress.

```bash
npm ci
npm run docs:build
npm run docs:preview
```

### Running the documentation site locally

To preview the documentation site while you're edit the source:

```bash
npm run docs:dev
```

This will start a local development server, typically at
`http://localhost:5173`. The site will automatically reload when you make
changes to the markdown files.

### Editing documentation

The Markdown files are located in the meta-sgl/docs/. To add or modify
documentation:

1. Edit existing `.md` files or create new ones
2. Test your changes locally using `npm run docs:dev`
3. Submit a pull request with your changes

