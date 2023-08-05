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

class check_xsan_client_interactions(unittest.TestCase):
    """Check that we can properly interact with clients

    """
    LOGGER.info("!!! TO run tests properly, a local xsanio_client should be launched !!!")