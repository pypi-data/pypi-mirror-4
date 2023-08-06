none ${rootfs}/dev/pts devpts defaults 0 0
none ${rootfs}/proc proc defaults 0 0
none ${rootfs}/sys sysfs defaults 0 0
none ${rootfs}/var/lock tmpfs defaults 0 0
none ${rootfs}/var/run tmpfs defaults 0 0
/etc/resolv.conf ${rootfs}/etc/resolv.conf none bind,ro 0 0
${host_mde_socketdir} ${rootfs}/var/me2/ none bind 0 0