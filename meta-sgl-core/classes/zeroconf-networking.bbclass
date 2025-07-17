#
# This bbclass allows an image to optionally
# install packages which enable "zeroconf" networking
# (mDNS and DNS-SD)
#

IMAGE_FEATURES[validitems] += " zeroconf-networking"

python __anonymous() {
    features = d.getVar('IMAGE_FEATURES').split()
    if 'zeroconf-networking' in features:
        pkgs = d.getVar('IMAGE_INSTALL') or ""
        pkgs += " avahi-daemon avahi-utils libnss-mdns"
        d.setVar('IMAGE_INSTALL', pkgs)
}
