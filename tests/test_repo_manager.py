from unittest import mock, TestCase

from mort.file_utils import get_absolute_path
from tests.data import JOB_ID, JOB_DETAIL, GIT_HASH_CURR, GIT_HASH_REF, PATH, TARGETS
from mort.repo_manager import extract_urls_from_job_details, get_screenshot_path, get_screenshot, load_screenshots


class TestRepoManager(TestCase):
    @mock.patch('os.path.join', return_value=get_absolute_path("tests/resources/manifest.json"))
    def test_find_all_screenshots(self, _):
        self.assertIsNone(get_screenshot(GIT_HASH_CURR, PATH, {"browser": "ie", "browser_version": "100"}))
        screen_shot = get_screenshot(GIT_HASH_CURR, PATH, {"browser": "ie", "browser_version": "11"})
        self.assertIn("740d33a68b06a04dd07dd5756824a11669740de/win10_ie_11.0.jpg", screen_shot['image_url'])

    def test_extract_urls_from_job_details(self):
        urls = extract_urls_from_job_details(JOB_DETAIL)
        self.assertEqual(len(urls), 1)
        self.assertIn('android_Google-Nexus-6_5.0_portrait', urls[0])

    def test_get_screenshot_path(self):
        path = get_screenshot_path(GIT_HASH_CURR, JOB_DETAIL["screenshots"][0])
        self.assertIn(JOB_ID, path)
        self.assertIn("/fdd01e6683e0474ede370b753f870542f364f8ba/android_Google-Nexus-6_5.0_portrait.jpg", path)

    @mock.patch('mort.repo_manager.get_screenshot')
    @mock.patch('mort.repo_manager.get_screenshot_path')
    def test_load_screenshots(self, get_screenshot_path, get_screenshot):
        get_screenshot.return_value = None
        no_images = load_screenshots([PATH], TARGETS, GIT_HASH_CURR, GIT_HASH_REF)
        self.assertEqual(0, len(no_images))
        self.assertEqual(0, get_screenshot_path.call_count)

        get_screenshot.return_value = TARGETS[0]
        get_screenshot_path.return_value = "path"
        two_images = load_screenshots([PATH], TARGETS, GIT_HASH_CURR, GIT_HASH_REF)
        self.assertEqual(2, len(two_images))
