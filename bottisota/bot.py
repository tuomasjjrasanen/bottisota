import bottisota
import bottisota.bus
import bottisota.math

"""Convenience API for bot controller programmers."""

class Controller:

    def __init__(self):
        self.botconn = bottisota.bus.BotConnection()
        self.botconn.syscall_clk()

    def move_to(self, destination):
        while True:
            x, y, speed, direction = self.botconn.syscall_pos()
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

            self.botconn.syscall_drv(direction, speed)
