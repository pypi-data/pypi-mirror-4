from mainapp import models
import json
import logging
import httplib
import sys
import platform
import os
import re
import multiprocessing
import time
import plistlib
import socket
import subprocess


LOGGER = logging.getLogger(__name__)
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOG_LEVEL = logging.WARNING
XSAN_CONFIG_DIR = ''
XSAN_VOLUME_CONFIG_REGEX = r'(.+)\.cfg'
XSAN_CONFIG_NODE_REGEX = r'Node \"(.+)\" \d+'
CLIENT_UPDATE_DELAY = 2.0


class process_launcher():
    """Launches multiple PROCESSES.
    Watches if they're alive.
    If any of them exits, terminates the whole bunch

    """
    PROCESSES = []
    ALL_PROCESSES_ALIVE = True

    def add_process(self, process):
        self.PROCESSES.append(process)

    def run(self):
        for process in self.PROCESSES:
            process.start()

        while True:
            #   Check if all processes are alive
            for process in self.PROCESSES:
                process.join(0.5)
                if not process.is_alive():
                    LOGGER.info(
                        "Process %s had unhandled exception, exiting",
                        process.name)
                    self.ALL_PROCESSES_ALIVE = False

            if not self.ALL_PROCESSES_ALIVE:
                #   Kill everyone and exit
                for process in self.PROCESSES:
                    LOGGER.info(
                        "Killing process %s",
                        process.name)
                    process.terminate()

                #   Exit the loop, terminate the program
                break


def get_xsan_config_dir():
    """Gets Xsan config directory path based on the OS version

    """
    config_path = ''

    if platform.system() == 'Darwin':
        releaseVersion = int(platform.release()[0:2])
        if releaseVersion == 12:
            #  Masao Laaa
            LOGGER.info('We seem to run of OS X Mountain Lion')
            config_path = r'/Library/Preferences/Xsan/'
        elif releaseVersion == 11:
            #   Lion
            LOGGER.info('We seem to run of OS X Lion')
            config_path = r'/Library/Preferences/Xsan/'
        elif releaseVersion == 10:
            #   Snow Leo
            LOGGER.info('We seem to run on OS X Snow Leopard')
            config_path = r'/Library/Filesystems/Xsan/config/'
        else:
            LOGGER.error('Unsupported OS X release')
            sys.exit(10)

    LOGGER.info('Configuration path prefix: %s', config_path)
    return config_path


def update_volume_list(xsan_config_path, xsan_config_regex, config_node_regex):
    """Parses Xsan volume config files to fetch the following data:
        1) List of volumes on MDC
        2) List of LUNs that each volume consists of

    This data is then added to the database (models are xsan_volume and xsan_volume_lun)

    """
    if os.path.isdir(xsan_config_path):
        #   flush all volume definitions first
        LOGGER.info('Flushing all volume and LUN records from DB')
        models.xsan_volume.objects.all().delete()
        models.xsan_volume_lun.objects.all().delete()

        config_file_list = os.listdir(xsan_config_path)

        for config_file_name in config_file_list:
            #   We'll add the volume only if it looks like a real volume config
            #   We consider it a volume config, if any line there matches config_node_regex
            #   If any line matched, we change is_a_volume config to True and add a new record to DB model xsan_volume
            is_a_volume_config = False

            if re.match(xsan_config_regex, config_file_name):
                #   Save our volume
                volume_name = os.path.splitext(config_file_name)[0]

                volume = models.xsan_volume(
                    name=volume_name
                )

                if re.match(xsan_config_regex, config_file_name):
                    config_file_path = os.path.join(xsan_config_path, config_file_name)
                    config_file = open(config_file_path, 'r')

                    for line in config_file:
                        line_match = re.match(config_node_regex, line)
                        if line_match:
                            if not is_a_volume_config:
                                #   Looks like a proper config!
                                #   So, we save the volume record safely
                                is_a_volume_config = True
                                volume.save()

                            nodeName = line_match.groups()[0]
                            lun = models.xsan_volume_lun(
                                label=nodeName,
                                volume=volume
                            )
                            lun.save()

    else:
        LOGGER.warning('We don\'t seem to be running on an MDC!')


def client_ping_response(client):
    """Ping the client.
    True == client is reachable
    False == client is not

    """
    ping_response = -1
    try:
        ping_response = subprocess.call(
            ['/sbin/ping', '-c1', client.ip_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except:
        LOGGER.error('Error while calling /sbin/ping: %s', sys.exc_info()[0])
    return ping_response


def parse_client_io_data(client, io_data):
    """Gotta be careful here, since there should be only one stat entry for each status entry type for each host
    Basically, this function parses client HTTP response and creates stat_entry objects in DB

    """
    #   Getting the cvlabel data
    if 'cvlabel' in io_data:
        cvlabels = io_data['cvlabel']

        #   Clean up old cvlabels
        all_cvlabels = models.cvlabel_entry.objects.filter(
            host=client,
        ).all()

        for cvlabel in all_cvlabels:
            if cvlabel.disk not in cvlabels:
                LOGGER.info('Deleting stale record for %s', cvlabel.disk)
                cvlabel.delete()

        for cvlabel in cvlabels:
            disk_name = cvlabel
            cvlabel_name = cvlabels[cvlabel]
            #   So, we either update existing cvlabel entry or create a new one
            cvlabel_obj = models.cvlabel_entry.objects.filter(
                host=client,
                disk=disk_name,
            ).all()

            if len(cvlabel_obj) == 1:
                LOGGER.info('Updating cvlabel entry for %s', disk_name)
                cvlabel_obj.update(
                    label=cvlabel_name
                )
            elif len(cvlabel_obj) == 0:
                LOGGER.info('Creating a new cvlabel entry for %s', disk_name)
                new_cvlabel_obj = models.cvlabel_entry(
                    host=client,
                    disk=disk_name,
                    label=cvlabel_name
                )
                new_cvlabel_obj.save()
            else:
                LOGGER.critical('Two cvlabel entries for one disk found. Something is TERRIBLY wrong!')
                sys.exit()
    else:
        LOGGER.error('Response from client %s doesn\'t contain cvlabel data', client.host_name)

    #   Getting the disk data
    if 'iodata' in io_data:
        disks = io_data['iodata']

        all_stat_entries = models.stat_entry.objects.filter(
            host=client,
        ).all()
        for stat_entry in all_stat_entries:
            if stat_entry.disk not in disks:
                LOGGER.info('Deleting stale disk entry: %s', stat_entry.disk)
                stat_entry.delete()

        for disk_name in disks:
            LOGGER.info('Updating data for %s', disk_name)
            disk_iodata = disks[disk_name]

            #   Adding a couple of auto-calculated stats
            disk_iodata['io_sec'] = disk_iodata['io_read_sec'] + disk_iodata['io_write_sec']
            disk_iodata['bytes_sec'] = disk_iodata['bytes_read_sec'] + disk_iodata['bytes_write_sec']

            for stat in disk_iodata:
                #   Does an entry already exist?
                stat_type = models.stat_type.objects.filter(name=stat).all()[0]
                stat_entry = models.stat_entry.objects.filter(
                    type=stat_type,
                    host=client,
                    disk=disk_name,
                ).all()

                stat_value = disk_iodata[stat_type.name]

                if len(stat_entry) == 1:
                    LOGGER.info('Updating status entry for %s', stat_type)
                    stat_entry.update(
                        value=stat_value
                    )
                elif len(stat_entry) == 0:
                    LOGGER.info('Creating a new stat entry for %s', stat_type)
                    new_stat_entry = models.stat_entry(
                        type=stat_type,
                        host=client,
                        disk=disk_name,
                        value=stat_value
                    )
                    new_stat_entry.save()
                else:
                    LOGGER.critical('Two stat entries for one host found! This is TERRIBLY wrong!')
                    sys.exit()
    else:
        LOGGER.error('Response from client %s does not contain disk I/O statistics', client.host_name)


def get_stats_from_client(client, update_interval):
    """Shoots the HTTP request. Gets response body and calls parse_client_io_data

    """
    while True:
        io_data = None
        http_response = None

        ping_resp = client_ping_response(client)
        if ping_resp == 0:
            client.is_unreachable = False
            try:
                LOGGER.info('Requesting stats from %s', client.host_name)
                http_conn = httplib.HTTPConnection(host=client.ip_address, port=client.port, timeout=3)
                http_conn.request('GET', '/')
                http_response = http_conn.getresponse()
            except:
                LOGGER.info('Client %s does not have xsanio_client installed', client.host_name)
                client.has_client_installed = False
                client.save()
                time.sleep(update_interval)
                continue

            if http_response.status == 200:
                client.has_client_installed = True
                client.save()
                host_response_data = http_response.read()
                io_data = json.loads(host_response_data)
                parse_client_io_data(client, io_data)
                LOGGER.info('Finished parsing response from %s', client.host_name)
            else:
                LOGGER.info("Client %s responded with %s", client.host_name, http_response.status)
        else:
            client.is_unreachable = True
            LOGGER.info('Client %s responded to ping with %s', client.host_name, ping_resp)
            client.save()

        time.sleep(update_interval)


def discover_clients(xsan_config_dir):
    """Parse config.plist
    Get all client hostnames and IP addresses.

    """
    config_plist_path = os.path.join(xsan_config_dir, 'config.plist')
    plist_data = None

    #   Flush ALL data first!
    models.stat_entry.objects.all().delete()
    models.cvlabel_entry.objects.all().delete()
    models.xsanio_client.objects.all().delete()

    if os.path.isfile(config_plist_path):
        LOGGER.info('Reading plist data')
        plist_data = plistlib.readPlist(config_plist_path)

        computer_list = plist_data['computers']
        for client in computer_list:
            client_hostname = client['legacyHostName']
            client_ipaddr = client['ipAddresses'][0]

            LOGGER.info('Adding client %s', client_hostname)
            new_client = models.xsanio_client(
                host_name=client_hostname,
                ip_address=client_ipaddr,
            )
            new_client.save()

    my_hostname = socket.gethostname()
    my_primary_ip = socket.gethostbyname(my_hostname)

    LOGGER.info('Adding myself as %s with IP %s', my_hostname, my_primary_ip)

    my_client = models.xsanio_client(
        host_name=my_hostname,
        ip_address=my_primary_ip,
    )
    my_client.save()


def update_clients():
    """Calls get_stats_from_clients for all client objects in database.
    All tasks are executed in parallel.

    """
    global XSAN_CONFIG_DIR
    global XSAN_VOLUME_CONFIG_REGEX
    global XSAN_CONFIG_NODE_REGEX
    global CLIENT_UPDATE_DELAY

    while True:
        processes = []

        for client in models.xsanio_client.objects.all():
            LOGGER.info('Getting stats for %s', client)
            processes.append(multiprocessing.Process(
                target=get_stats_from_client,
                args=(client, CLIENT_UPDATE_DELAY, )
            ))

        for process in processes:
            process.start()

        for process in processes:
            process.join(0.5)
            if not process.is_alive():
                LOGGER.error('Process crashed, restarting everyone')
                break

        for process in processes:
            process.terminate()


def main():
    """The logic:

        1) Discover our environment
        2) Discover Xsan configuration (volumes and LUNs)
        3) Discover clients
        4) Grab stats from clients in an endless loop

    """
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

    XSAN_CONFIG_DIR = get_xsan_config_dir()
    update_volume_list(XSAN_CONFIG_DIR, XSAN_VOLUME_CONFIG_REGEX, XSAN_CONFIG_NODE_REGEX)

    discover_clients(XSAN_CONFIG_DIR)

    update_clients()

