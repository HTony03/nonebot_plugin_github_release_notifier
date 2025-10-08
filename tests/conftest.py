"""
Configuration file for pytest test execution.

This module provides test fixtures and configuration for the
nonebot_plugin_github_release_notifier plugin testing suite.
It sets up the test environment, configures async test execution,
and initializes the NoneBot framework with required adapters.
"""

import os

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter
import pytest
from pytest_asyncio import is_async_test

# Set environment to test mode to prevent production side effects
os.environ["ENVIRONMENT"] = "test"


def pytest_collection_modifyitems(items: list[pytest.Item]):
    """
    Modify pytest items to configure async test execution.
    
    This hook function automatically adds session-scoped asyncio markers
    to all async test functions, ensuring proper async test execution
    within a shared event loop session.
    
    Args:
        items: List of pytest test items collected during test discovery
    """
    # Filter async test items
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope="session", autouse=True)
async def after_nonebot_init(after_nonebot_init: None):
    """
    Auto-used session fixture for NoneBot initialization.
    
    This fixture runs automatically before all tests in the session
    and sets up the NoneBot framework with the required OneBot v11
    adapter and loads the plugin from the project configuration.
    
    Args:
        after_nonebot_init: Dependency on NoneBot initialization completion
    """
    # Register OneBot v11 adapter for QQ bot communication
    driver = nonebot.get_driver()
    driver.register_adapter(OnebotV11Adapter)

    # Load plugin from pyproject.toml configuration
    nonebot.load_from_toml("pyproject.toml")
