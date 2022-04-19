import asyncio
import os
import psutil

from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

DEBUG = os.getenv("DEBUG", False)
DEVICE = os.getenv("DEVICE", "My Device")
HOST = os.getenv("INFLUX_HOST", "https://us-central1-1.gcp.cloud2.influxdata.com")
TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG")
BUCKET = os.getenv("INFLUX_BUCKET", "system-metrics")


async def main():
    client = InfluxDBClient(url=HOST, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    while True:
        # Collect stats
        cpu = psutil.cpu_percent(interval=1)
        cpufreq = psutil.cpu_freq()
        load = psutil.getloadavg()
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage('/')
        diskio = psutil.disk_io_counters()
        net = psutil.net_io_counters()
        temps = psutil.sensors_temperatures()

        if DEBUG:
            os.system('clear||cls')
            print("-- Sysmetrics --")
            print("")
            # CPU
            print("[cpu]")
            print("cpu_percent", cpu)
            print("cpu_freq", cpufreq.current)
            print("cpu_temp", temps['cpu_thermal'][0].current)
            print("")
            # LOAD
            print("[load]")
            print("load_1m", load[0])
            print("load_5m", load[1])
            print("load_15m", load[2])
            print("")
            # MEM
            print("[mem]")
            print("mem_percent", mem.percent)
            print("mem_used", mem.used)
            print("mem_free", mem.free)
            print("mem_avail", mem.available)
            print("mem_total", mem.total)
            print("")
            # SWAP
            print("[swap]")
            print("swap_percent", swap.percent)
            print("swap_used", swap.used)
            print("swap_free", swap.free)
            print("swap_total", swap.total)
            print("")
            # DISK
            print("[disk]")
            print("disk_percent", disk.percent)
            print("disk_used", disk.used)
            print("disk_free", disk.free)
            print("disk_total", disk.total)
            print("")
            # DISK IO
            print("[disk_io]")
            print("disk_io_read_count", diskio.read_count)
            print("disk_io_write_count", diskio.write_count)
            print("disk_io_read_bytes", diskio.read_bytes)
            print("disk_io_write_bytes", diskio.write_bytes)
            print("disk_io_read_time", diskio.read_time)
            print("disk_io_write_time", diskio.write_time)
            print("")
            # NET
            print("[net]")
            print("net_bytes_sent", net.bytes_sent)
            print("net_bytes_recv", net.bytes_recv)
            print("net_packets_sent", net.packets_sent)
            print("net_packets_recv", net.packets_recv)
            print("net_err_in", net.errin)
            print("net_err_out", net.errout)
            print("net_drop_in", net.dropin)
            print("net_drop_out", net.dropout)
            print("")

        # Write data to InfluxDB
        POINT = Point("system-metrics") \
            .tag("device", DEVICE) \
            .field("cpu_percent", cpu) \
            .field("cpu_freq", cpufreq.current) \
            .field("cpu_temp", temps['cpu_thermal'][0].current) \
            .field("load_1m", load[0]) \
            .field("load_5m", load[1]) \
            .field("load_15m", load[2]) \
            .field("mem_percent", mem.percent) \
            .field("mem_used", mem.used) \
            .field("mem_free", mem.free) \
            .field("mem_avail", mem.available) \
            .field("mem_total", mem.total) \
            .field("swap_percent", swap.percent) \
            .field("swap_used", swap.used) \
            .field("swap_free", swap.free) \
            .field("swap_total", swap.total) \
            .field("disk_percent", disk.percent) \
            .field("disk_used", disk.used) \
            .field("disk_free", disk.free) \
            .field("disk_total", disk.total) \
            .field("disk_io_read_count", diskio.read_count) \
            .field("disk_io_write_count", diskio.write_count) \
            .field("disk_io_read_bytes", diskio.read_bytes) \
            .field("disk_io_write_bytes", diskio.write_bytes) \
            .field("disk_io_read_time", diskio.read_time) \
            .field("disk_io_write_time", diskio.write_time) \
            .field("net_bytes_sent", net.bytes_sent) \
            .field("net_bytes_recv", net.bytes_recv) \
            .field("net_packets_sent", net.packets_sent) \
            .field("net_packets_recv", net.packets_recv) \
            .field("net_err_in", net.errin) \
            .field("net_err_out", net.errout) \
            .field("net_drop_in", net.dropin) \
            .field("net_drop_out", net.dropout) \
            .time(datetime.utcnow(), WritePrecision.NS)
        write_api.write(bucket=BUCKET, record=POINT)

        await asyncio.sleep(0.25)  # Pause between updates

if __name__ == "__main__":
    print("Sysmetrics is running...")
    asyncio.run(main())
