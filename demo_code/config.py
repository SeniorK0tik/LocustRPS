from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import WriteOptions
import logging


class Config:
    conf_name = 'KotikLocustConfig'
    pacing_sec = 0.1
    api_host = 'http://localhost:9090'
    kafka_hosts = ['localhost:29092']
    influx_bucket = 'demo_bucket'
    influx_org = 'demo_org'
    influx_client = InfluxDBClient(
        url="http://localhost:8086",
        token='demo_token',
        org=influx_org
    )
    influxdb = influx_client.write_api(
        write_options=WriteOptions(
        batch_size=10,              # размер пакета (batch)
        flush_interval=10_000,      # интервал (в миллисекундах), с которым пакеты данных будут автоматически сбрасываться на сервер InfluxDB.
        jitter_interval=2_000,      # интервал (в миллисекундах) смещения, который добавляется к flush_interval
        retry_interval=5_000        # интервал (в миллисекундах) повторной попытки отправки данных в случае ошибки
        )
    )
    products = [
        {"Code": 111, "Name": "Молоко для котиков", "Price": 1150},
        {"Code": 123, "Name": "Кефир для котиков", "Price": 1000},
        {"Code": 124, "Name": "Сметана для котиков", "Price": 800},
        {"Code": 125, "Name": "Творог для котиков", "Price": 1200},
        {"Code": 126, "Name": "Сгущёнка для котиков", "Price": 1700},
    ]


class LogConfig():
    logger = logging.getLogger('demo_logger')
    logger.setLevel('DEBUG')
    file = logging.FileHandler(filename='test_logs.log')
    file.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(file)
    logger.propagate = False


logger = LogConfig().logger
cfg = Config()
