# Third party
import pytest

# Local modules
import pgml_lint.plugins
import pgml_lint.registry


#============================================

def test_register_and_list_plugins_order() -> None:
	registry = pgml_lint.registry.Registry()
	registry.register({"id": "a", "name": "A", "run": lambda _ctx: []})
	registry.register({"id": "b", "name": "B", "run": lambda _ctx: []})
	plugins = registry.list_plugins()
	assert [plugin["id"] for plugin in plugins] == ["a", "b"]


#============================================

def test_register_duplicate_id_raises() -> None:
	registry = pgml_lint.registry.Registry()
	registry.register({"id": "a", "name": "A", "run": lambda _ctx: []})
	with pytest.raises(ValueError):
		registry.register({"id": "a", "name": "A2", "run": lambda _ctx: []})


#============================================

def test_resolve_plugins_default_and_overrides() -> None:
	registry = pgml_lint.registry.Registry()
	registry.register({"id": "a", "name": "A", "run": lambda _ctx: [], "default_enabled": True})
	registry.register({"id": "b", "name": "B", "run": lambda _ctx: [], "default_enabled": False})
	registry.register({"id": "c", "name": "C", "run": lambda _ctx: [], "default_enabled": True})

	default_ids = [plugin["id"] for plugin in registry.resolve_plugins(set(), set(), set())]
	assert default_ids == ["a", "c"]

	enabled_ids = [
		plugin["id"]
		for plugin in registry.resolve_plugins(set(), {"b"}, {"c"})
	]
	assert enabled_ids == ["a", "b"]

	only_ids = [plugin["id"] for plugin in registry.resolve_plugins({"b"}, set(), set())]
	assert only_ids == ["b"]


#============================================

def test_build_registry_matches_builtin_plugins() -> None:
	registry = pgml_lint.registry.build_registry()
	plugins = registry.list_plugins()
	assert len(plugins) == len(pgml_lint.plugins.BUILTIN_PLUGINS)
	plugin_ids = [plugin["id"] for plugin in plugins]
	assert len(plugin_ids) == len(set(plugin_ids))


#============================================

def test_load_plugin_path_skipped() -> None:
	pytest.skip("load_plugin_path reads plugin files from disk, which is not allowed in unit tests", allow_module_level=False)
