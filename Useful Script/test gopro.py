from dronekit import connect

MAVLINK_GIMBAL_SYSTEM_ID = 1
MAVLINK_GIMBAL_COMPONENT_ID = 154

vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)

from pymavlink import mavutil

msg = vehicle.message_factory.gopro_set_request_encode(1, 154, mavutil.mavlink.GOPRO_COMMAND_SHUTTER, (1, 0, 0, 0))
vehicle.send_mavlink(msg)
vehicle.commands.upload()
vehicle.close()
print vehicle
print vehicle.battery.level
