# Permission of 600 recommended for this file

# SYSTEM
salt_version: 0.10.4-1

# SERVERS
servers:

  rackspacev2-salt-arch201208-b:
    public_ip: 64.49.226.155
    private_ip: 10.181.2.99
    roles: ['application']


# SSH
ssh_port: 30000

# PACMAN
pacman_extra_repos:
  archlinuxfr:
    url: http://repo.archlinux.fr

# SALT
saltmaster_hostname: rackspacev2-salt-arch201208-b

saltmaster_private_ip: 10.181.2.99

saltmaster_public_ip: 64.49.226.155

saltminion_private_ips:

  - 10.181.2.99



# USERS
users:

  rizumu:
    fullname: bootmachine
    uid: 1000
    gid: 1000
    group: rizumu
    extra_groups: [sshers, wheel, ops]
    ssh_auth:
      keys: [

       ecdsa-sha2-nistp521 AAAAE2VjZHNhLXNoYTItbmlzdHA1MjEAAAAIbmlzdHA1MjEAAACFBADi72bdOTzSJdIPqizfZvkWAhU+3YRpJ/B2ezfHESPM+po2BWmKhadgDYVa7acrx0K/UiijQyjZObV7nc54izWJ5ADZIjxEpV4/Bru7m+8MN5MisNMr+dShf59BYBKWLIcCZTPhiiC8lgXBMl8sIGDCd2BTBUWW3/MR9s6iYjD7VHKO+w== bootmachine.key,

      ]
