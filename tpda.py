from settpa import setNode
import time

def adjust_transmit_power(car, rssi, current_power, min_power, max_power, power_step):
    # Thresholds for RSSI
    rssi_min = -80
    rssi_max = -20

    # Adjust the transmit power based on RSSI
    if rssi < rssi_min:
        current_power += power_step  # Increase power
        print(f"Increasing power: RSSI {rssi} < {rssi_min}")
    elif rssi > rssi_max:
        current_power -= power_step  # Decrease power
        print(f"Decreasing power: RSSI {rssi} > {rssi_max}")

    # Ensure power is within acceptable range
    current_power = max(min(current_power, max_power), min_power)
    print(f"Setting transmit power to: {current_power} dBm")

    # Set the transmit power on the car
    car.wintfs[0].txpower = current_power

    return current_power
    
def collect_rssi_and_adjust_power(car, duration, interval, min_power, max_power, power_step):
    rssi_values = []
    power_values = []

    current_power = car.wintfs[0].txpower

    for _ in range(int(duration / interval)):
        # Get RSSI value from the first wireless interface
        rssi = car.wintfs[0].rssi
        print(f"Current RSSI: {rssi} dBm")

        # Adjust the transmit power based on RSSI
        current_power = adjust_transmit_power(car, rssi, current_power, min_power, max_power, power_step)

        # Store the RSSI and transmit power values
        rssi_values.append(rssi)
        power_values.append(current_power)

        # Wait for the next interval
        time.sleep(interval)

    return rssi_values, power_values

