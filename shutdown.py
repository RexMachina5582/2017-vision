import dbus
sys_bus = dbus.SystemBus()
ck_srv = sys_bus.get_object('org.freedesktop.ConsoleKit',
                                '/org/freedesktop/ConsoleKit/Manager')
ck_iface = dbus.Interface(ck_srv, 'org.freedesktop.ConsoleKit.Manager')
stop_method = ck_iface.get_dbus_method("Stop")
stop_method()
