SUMMARY = "Minimal Space Grade Linux image"
DESCRIPTION = "A minimal image with custom tweaks tailored to Space Grade Linux"

inherit core-image sgl-image-common
require recipes-core/images/core-image-minimal.bb

IMAGE_FEATURES:append = " \
   ssh-server-openssh \
"

# TODO: License
