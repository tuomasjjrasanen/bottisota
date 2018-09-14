import bottisota
import bottisota.net
import bottisota.math
import bottisota.protocol

"""Convenience API for bot controller programmers."""

class Controller:

    def __init__(self):
        self.link = bottisota.net.Link(bottisota.net.connect_socket(),
                                       bottisota.protocol.BotStack())
        self.syscall_clk()

    def syscall_clk(self):
        tick, = self.link.syscall(bottisota.protocol.MSG_CLK)
        return tick

    def syscall_drv(self, direction, speed):
        speed, = self.link.syscall(bottisota.protocol.MSG_DRV, direction, speed)
        return speed

    def syscall_pos(self):
        return self.link.syscall(bottisota.protocol.MSG_POS)

    def syscall_scn(self, direction, resolution):
        return self.link.syscall(bottisota.protocol.MSG_SCN, direction, resolution)

    def syscall_msl(self, direction, distance):
        self.link.syscall(bottisota.protocol.MSG_MSL, direction, distance)

    def move_to(self, destination):
        while True:
            x, y, speed, direction = self.syscall_pos()
            loc = x, y

            distance_to_destination = bottisota.math.distance(loc, destination)

            direction = bottisota.math.direction(loc, destination)

            if distance_to_destination < 5:
                return

            if distance_to_destination < 5 * speed:
                # We are getting closer, slow down.
                speed = max(speed // 2, 1)
            else:
                # Full speed ahead.
                speed = bottisota.DRV_SPEED_MAX

            self.syscall_drv(direction, speed)
