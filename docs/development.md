# Development Setup

This guide covers optional image features useful for development and testing with Space Grade Linux.

## Optional Image Features

SGL supports optional image features that can be enabled at build time using the `OPTIONAL_FEATURES` environment variable. Multiple features can be enabled by separating them with spaces.

```bash
OPTIONAL_FEATURES="feature1 feature2" kas build kas/sgl-scarthgap-qemuarm64.yml
```

## Enabling SSH Access

To enable SSH server access on your image, add the `ssh-server-openssh` feature:

```bash
OPTIONAL_FEATURES="ssh-server-openssh" kas build kas/sgl-scarthgap-qemuarm64.yml
```

This will include the OpenSSH server in your image, allowing you to connect remotely.

::: info
The default login is `root` without a password.
:::

## Zeroconf Networking (mDNS/DNS-SD)

Zeroconf networking allows your device to be discoverable on the local network using a human-readable hostname (e.g., `hostname.local`) without requiring DNS configuration.

### Enabling Zeroconf

To enable zeroconf networking, add the `zeroconf-networking` feature:

```bash
OPTIONAL_FEATURES="zeroconf-networking" kas build kas/sgl-scarthgap-qemuarm64.yml
```

This installs:
- **avahi-daemon**: mDNS/DNS-SD service daemon
- **avahi-utils**: Command-line utilities for browsing services
- **libnss-mdns**: NSS plugin for mDNS hostname resolution

### Development Build with SSH and Zeroconf

For a full development setup with both SSH and zeroconf, combine the features:

```bash
OPTIONAL_FEATURES="ssh-server-openssh zeroconf-networking" kas build kas/sgl-scarthgap-qemuarm64.yml
```

### Connecting to Your Device

Once your device is running with zeroconf enabled, you can connect using the hostname:

```bash
ssh root@<hostname>.local
```

For example, if your device's hostname is `qemuriscv64`:

```bash
ssh root@qemuriscv64.local
```

### Discovering Devices on the Network

From another machine with Avahi installed, you can discover SGL devices advertising SSH:

```bash
avahi-browse -at | grep SSH
```

Example output:
```
+   eth0 IPv6 mydevice SSH Server    _ssh._tcp    local
+   eth0 IPv4 mydevice SSH Server    _ssh._tcp    local
```

### Verifying Zeroconf on the Device

On the target device, verify that Avahi is running and advertising services:

```bash
avahi-browse -at
```

You can also test mDNS resolution locally:

```bash
ping $(hostname).local
```

## Feature Reference

| Feature | Description |
|---------|-------------|
| `ssh-server-openssh` | OpenSSH server for remote access |
| `ssh-server-dropbear` | Dropbear SSH server (lightweight alternative) |
| `zeroconf-networking` | mDNS/DNS-SD support via Avahi |
