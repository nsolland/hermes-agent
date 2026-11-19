"""Regression checks for the pinned Salad Technologies model-provider.

No external inference or credential access.
"""
import unittest
from unittest.mock import patch

from providers import get_provider_profile
from providers.base import ProviderProfile


class SaladCloudProviderTests(unittest.TestCase):
    def test_official_profile_is_discovered(self):
        profile = get_provider_profile("saladcloud")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.base_url, "https://ai.salad.cloud/v1")
        self.assertEqual(profile.fallback_models, ("qwen3.6-35b-a3b",))
        self.assertIs(profile, get_provider_profile("salad"))

    def test_dedicated_gateway_credential_takes_precedence(self):
        profile = get_provider_profile("saladcloud")
        self.assertEqual(profile.env_vars[0], "SALAD_AI_GATEWAY_API_KEY")
        self.assertIn("SALAD_API_KEY", profile.env_vars)
        self.assertIn("SALAD_CLOUD_API_KEY", profile.env_vars)

    def test_upstream_model_filter_is_preserved(self):
        profile = get_provider_profile("saladcloud")
        with patch.object(ProviderProfile, "fetch_models",
                          return_value=["qwen3.5-9b", "qwen3.6-35b-a3b"]):
            self.assertEqual(profile.fetch_models(), ["qwen3.6-35b-a3b"])
        with patch.object(ProviderProfile, "fetch_models",
                          return_value=["qwen3.5-9b"]):
            self.assertIsNone(profile.fetch_models())


if __name__ == "__main__":
    unittest.main()
