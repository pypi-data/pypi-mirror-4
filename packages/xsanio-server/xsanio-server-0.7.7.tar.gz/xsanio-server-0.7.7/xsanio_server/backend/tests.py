from django.utils import unittest
import xsanio_backend
from mainapp import models
import platform
import logging
import os


XSAN_TEST_CONFIGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data/test_xsan_configs')
LOGGER = logging.getLogger(__name__)
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOG_LEVEL = logging.INFO


class check_xsan_config_parsing(unittest.TestCase):
    """Check that xsanio_backend properly parses Xsan configs

    """
    def test_returned_config_dir(self):
        function_result = xsanio_backend.get_xsan_config_dir()

        releaseVersion = int(platform.release()[0:2])
        if platform.system() == 'Darwin':
            if releaseVersion == 12:
                self.assertEqual(function_result, '/Library/Preferences/Xsan/')
            elif releaseVersion == 11:
                self.assertEqual(function_result, '/Library/Preferences/Xsan/')
            elif releaseVersion == 10:
                self.assertEqual(function_result, '/Library/Filesystems/Xsan/config/')
            else:
                self.fail(msg='Not running on supported OS X release')
        else:
            self.fail(msg='Not running on OS X')

    def test_volume_config_parsing(self):
        logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

        XSAN_VOLUME_CONFIG_REGEX = xsanio_backend.XSAN_VOLUME_CONFIG_REGEX
        XSAN_CONFIG_NODE_REGEX = xsanio_backend.XSAN_CONFIG_NODE_REGEX

        LOGGER.info("Using Xsan config path: %s", XSAN_TEST_CONFIGS_DIR)

        xsanio_backend.update_volume_list(
            XSAN_TEST_CONFIGS_DIR,
            XSAN_VOLUME_CONFIG_REGEX,
            XSAN_CONFIG_NODE_REGEX,
        )

        expected_found_volumes = [
            'ActiveVideo',
            'DailyVideo',
            'VENUS'
        ]

        unexpected_found_volumes = [
            'NotAVolume',
        ]

        LOGGER.info("xsan_volume objects in DB: %s", models.xsan_volume.objects.all())

        #   Should put all real volumes into DB
        for expected_volume in expected_found_volumes:
            vol_object = models.xsan_volume.objects.filter(
                name=expected_volume,
            ).all()

            self.assertTrue(vol_object)

        #   Shouldn't put the fake volume config in DB
        for unexpected_found_volume in unexpected_found_volumes:
            vol_object = models.xsan_volume.objects.filter(
                name = unexpected_found_volume,
            ).all()

            self.assertFalse(vol_object)

        #   Okay, now let's check all LUN records are properly created
        volume_luns = {
            'ActiveVideo': [
                'ActiveMD',
                'ActiveVideo01',
                'ActiveVideo02',
                'ActiveVideo03',
                'ActiveVideo04',
                'ActiveVideo05',
                'ActiveVideo06',
                'ActiveVideo07',
                'ActiveVideo08',
                'ActiveOther01',
                'ActiveOther02',
                'ActiveVideo09',
                'ActiveVideo10',
                'ActiveVideo11',
                'ActiveVideo12',
            ],
            'DailyVideo': [
                'Arena25_DailyVideoMD',
                'Arena25_DailyVideoData1',
                'Arena26_DailyVideoData2',
                'Arena27_DailyVideoData3',
                'Arena28_DailyVideoData4',
            ],
            'VENUS': [
                'XsanMeta184',
                'XsanData181',
                'XsanData182',
                'XsanData183',
                'XsanData184',
            ],
        }

        LOGGER.info("Checking Xsan LUNs are added to DB properly")
        for volume_name in volume_luns:
            for lun_name in volume_luns[volume_name]:
                lun_object = models.xsan_volume_lun.objects.filter(
                    label=lun_name,
                    volume=models.xsan_volume.objects.filter(name=volume_name).all()[0],
                ).all()

                self.assertTrue(lun_object)

    def test_client_discovery(self):
        expected_clients = {
            'test-325-2.test.com': '10.11.15.32',
            'test-311.test.com': '10.11.15.12',
            'test-317.test.com': '10.11.15.18',
            'test-320.test.com': '10.11.15.21',
            'test-325-3.test.com': '10.11.15.33',
            'test-303.test.com': '10.11.15.25',
            'test-301v.test.com': '10.11.15.4',
            'test-307.test.com': '10.11.15.8',
            'test-303a.test.com': '10.11.15.23',
            'test-358.local': '10.11.15.11',
            'test-312.test.com': '10.11.15.13',
            'test-319.local': '10.11.15.20',
            'test-309.test.com': '10.11.15.10',
            'test-306.local': '10.11.15.7',
            'test-301g.test.com': '10.11.15.3',
            'test-308.test.com': '10.11.15.9',
            'test-313.local': '10.0.23.29',
            'test-302a.test.com': '10.11.15.6',
            'test-301a.test.com': '10.11.15.1',
            'test-302.test.com': '10.11.15.5',
            'test-304.test.com': '10.0.23.3',
            'test-325-4.test.com': '10.11.15.34',
            'test-325-1.test.com': '10.11.15.31',
            'test-314.test.com': '10.11.15.15',
            'test-318.test.com': '10.11.15.19',
            'test-327.test.com': '10.11.15.37',
            'test-316.test.com': '10.11.15.17',
            'test-326.test.com': '10.11.15.22',
            'test-325-5.test.com': '10.11.15.35',
            'mdc1.test.com': '10.0.0.10'
        }

        xsanio_backend.discover_clients(XSAN_TEST_CONFIGS_DIR)
        LOGGER.info("Testing config.plist parser")

        for expected_client_hostname in expected_clients:
            expected_ip_addr = expected_clients[expected_client_hostname]

            client_obj = models.xsanio_client.objects.filter(
                host_name=expected_client_hostname,
            ).all()[0]

            self.assertEqual(client_obj.ip_address, expected_ip_addr)

class check_xsan_client_interactions(unittest.TestCase):
    """Check that we can properly interact with clients.
    Mostly checks that parser is sane

    """

    def add_test_data(self):
        #   Add a test client
        test_clients = [
            'test1',
            'test2',
            'test3',
        ]

        test_volumes = [
            'VENUS',
            'ActiveVideo',
            'DailyVideo',
        ]

        volume_luns = {
            'ActiveVideo': [
                'ActiveMD',
                'ActiveVideo01',
                'ActiveVideo02',
                'ActiveVideo03',
                'ActiveVideo04',
                'ActiveVideo05',
                'ActiveVideo06',
                'ActiveVideo07',
                'ActiveVideo08',
                'ActiveOther01',
                'ActiveOther02',
                'ActiveVideo09',
                'ActiveVideo10',
                'ActiveVideo11',
                'ActiveVideo12',
                ],
            'DailyVideo': [
                'Arena25_DailyVideoMD',
                'Arena25_DailyVideoData1',
                'Arena26_DailyVideoData2',
                'Arena27_DailyVideoData3',
                'Arena28_DailyVideoData4',
                ],
            'VENUS': [
                'XsanMeta184',
                'XsanData181',
                'XsanData182',
                'XsanData183',
                'XsanData184',
                ],
        }

        #   Populate the database with all the stuff
        for test_client_name in test_clients:
            test_client = models.xsanio_client(
                host_name=test_client_name,
                ip_address='127.0.0.1',
            )
            test_client.save()

        for test_volume_name in test_volumes:
            test_volume = models.xsan_volume(
                name=test_volume_name,
            )
            test_volume.save()

        for test_volume_name in volume_luns:
            for test_lun_name in volume_luns[test_volume_name]:
                test_lun = models.xsan_volume_lun(
                    label=test_lun_name,
                    volume=models.xsan_volume.objects.filter(name=test_volume_name).all()[0],
                )
                test_lun.save()

        #   Also some cvlabel data needs to be added
        for i in range(1,4):
            test_client = models.xsanio_client.objects.get(pk=i)
            test_client_volume = models.xsan_volume.objects.get(pk=i)

            test_client_volume_luns = models.xsan_volume_lun.objects.filter(
                volume=test_client_volume,
            )

            disk_counter = 0
            for test_client_volume_lun in test_client_volume_luns:
                test_cvlabel_entry = models.cvlabel_entry(
                    host=test_client,
                    disk="disk%s" % disk_counter,
                    label=test_client_volume_lun.label,
                )
                test_cvlabel_entry.save()
                disk_counter += 1

    def test_iodata_parser(self):
        logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

        LOGGER.info('Adding test data to DB')
        self.add_test_data()

        test_iodata = [
            {"cvlabel":
                 {
                     "disk8": "XsanMetaSmall184",
                     "disk0": "XsanData184",
                     "disk1": "XsanData182",
                     "disk2": "XsanData181",
                     "disk3": "XsanData183",
                     "disk7": "XsanSmall184"
                 },
             "sample_time": 2.0,
             "iodata":
                 {
                     "disk8": {"bytes_read_sec": 10.0, "io_read_sec": 10.0, "bytes_write_sec": 100.0, "io_write_sec": 1.0},
                     "disk0": {"bytes_read_sec": 20.0, "io_read_sec": 20.0, "bytes_write_sec": 200.0, "io_write_sec": 2.0},
                     "disk1": {"bytes_read_sec": 30.0, "io_read_sec": 30.0, "bytes_write_sec": 300.0, "io_write_sec": 3.0},
                     "disk2": {"bytes_read_sec": 40.0, "io_read_sec": 40.0, "bytes_write_sec": 400.0, "io_write_sec": 4.0},
                     "disk3": {"bytes_read_sec": 50.0, "io_read_sec": 50.0, "bytes_write_sec": 500.0, "io_write_sec": 5.0},
                     "disk4": {"bytes_read_sec": 60.0, "io_read_sec": 60.0, "bytes_write_sec": 600.0, "io_write_sec": 6.0},
                     "disk5": {"bytes_read_sec": 70.0, "io_read_sec": 70.0, "bytes_write_sec": 700.0, "io_write_sec": 7.0},
                     "disk7": {"bytes_read_sec": 80.0, "io_read_sec": 80.0, "bytes_write_sec": 800.0, "io_write_sec": 8.0}
                 }
            },
            {"cvlabel":
                 {
                     "disk8": "ActiveMD",
                     "disk0": "ActiveVideo01",
                     "disk1": "ActiveVideo02",
                     "disk2": "ActiveVideo03",
                     "disk4": "ActiveVideo04",
                     "disk5": "ActiveVideo05",
                 },
             "sample_time": 2.0,
             "iodata":
                 {
                     "disk8": {"bytes_read_sec": 10.0, "io_read_sec": 10.0, "bytes_write_sec": 100.0, "io_write_sec": 1.0},
                     "disk0": {"bytes_read_sec": 20.0, "io_read_sec": 20.0, "bytes_write_sec": 200.0, "io_write_sec": 2.0},
                     "disk1": {"bytes_read_sec": 30.0, "io_read_sec": 30.0, "bytes_write_sec": 300.0, "io_write_sec": 3.0},
                     "disk2": {"bytes_read_sec": 40.0, "io_read_sec": 40.0, "bytes_write_sec": 400.0, "io_write_sec": 4.0},
                     "disk3": {"bytes_read_sec": 50.0, "io_read_sec": 50.0, "bytes_write_sec": 500.0, "io_write_sec": 5.0},
                     "disk4": {"bytes_read_sec": 60.0, "io_read_sec": 60.0, "bytes_write_sec": 600.0, "io_write_sec": 6.0},
                     "disk5": {"bytes_read_sec": 70.0, "io_read_sec": 70.0, "bytes_write_sec": 700.0, "io_write_sec": 7.0},
                     "disk7": {"bytes_read_sec": 80.0, "io_read_sec": 80.0, "bytes_write_sec": 800.0, "io_write_sec": 8.0}
                 }
            },
        ]

#        for test_client in models.xsanio_client.objects.all():
        for i in range(1, len(test_iodata) + 1):
            LOGGER.info("cvalbel_entry dump:\n%s", models.cvlabel_entry.objects.all())
            test_client = models.xsanio_client.objects.get(pk=i)
            xsanio_backend.parse_client_io_data(test_client, test_iodata[i-1])

            #   Now we ensure that all corresponding stat_entry objects were created
            test_client_disk_iodata = test_iodata[i-1]['iodata']
            for disk_name in test_client_disk_iodata:
                iodata = test_client_disk_iodata[disk_name]

                for stat_type_name in iodata:
                    expected_value = iodata[stat_type_name]
                    stat_type = models.stat_type.objects.filter(name=stat_type_name).all()[0]

                    value_in_db = models.stat_entry.objects.filter(
                        type=stat_type,
                        host=test_client,
                        disk=disk_name,
                    ).all()[0].value

                    LOGGER.info("Checking stat entry for %s: %s", test_client, stat_type_name)
                    self.assertEqual(expected_value, value_in_db)

            #   Check cvlabel objects too
            test_client_cvlabel_data = test_iodata[i-1]['cvlabel']
            for disk_name in test_client_cvlabel_data:
                label_name = test_client_cvlabel_data[disk_name]

                cvlabel_entry = models.cvlabel_entry.objects.filter(
                    host=test_client,
                    disk=disk_name,
                ).all()[0]

                LOGGER.info("Checking cvlabel for %s: %s", test_client, disk_name)
                self.assertEqual(label_name, cvlabel_entry.label)


