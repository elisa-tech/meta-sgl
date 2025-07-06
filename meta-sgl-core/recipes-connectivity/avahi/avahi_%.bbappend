FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += " \
    file://ssh.service \
"

do_install:append() {
    install -d ${D}${sysconfdir}/avahi/services
    install -m 0644 ${WORKDIR}/ssh.service ${D}${sysconfdir}/avahi/services/
}
