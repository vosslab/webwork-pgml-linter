# Standard Library
import importlib
import importlib.util
import os

# Local modules
import pgml_lint.plugins


#============================================


def _register_module(registry: "Registry", module: object) -> None:
	"""
	Register a plugin module by reading its metadata.

	Args:
		registry: Plugin registry.
		module: Imported module object.
	"""
	plugin_id = str(getattr(module, "PLUGIN_ID"))
	plugin_name = str(getattr(module, "PLUGIN_NAME"))
	plugin_run = getattr(module, "run")
	default_enabled = bool(getattr(module, "DEFAULT_ENABLED", True))
	registry.register(
		{
			"id": plugin_id,
			"name": plugin_name,
			"run": plugin_run,
			"default_enabled": default_enabled,
		}
	)


#============================================


class Registry:
	"""Plugin registry."""

	def __init__(self) -> None:
		self._plugins: dict[str, dict[str, object]] = {}
		self._order: list[str] = []

	def register(self, plugin: dict[str, object]) -> None:
		"""
		Register a plugin.

		Args:
			plugin: Plugin metadata dict.
		"""
		plugin_id = str(plugin.get("id"))
		if plugin_id in self._plugins:
			raise ValueError(f"Duplicate plugin id: {plugin_id}")
		self._plugins[plugin_id] = plugin
		self._order.append(plugin_id)

	def list_plugins(self) -> list[dict[str, object]]:
		"""
		Return plugins in registration order.

		Returns:
			list[dict[str, object]]: Plugin metadata.
		"""
		return [self._plugins[plugin_id] for plugin_id in self._order]

	def resolve_plugins(
		self,
		only_ids: set[str],
		enable_ids: set[str],
		disable_ids: set[str],
	) -> list[dict[str, object]]:
		"""
		Resolve the list of enabled plugins.

		Args:
			only_ids: When set, use only these plugin ids.
			enable_ids: Plugin ids to enable in addition to defaults.
			disable_ids: Plugin ids to disable.

		Returns:
			list[dict[str, object]]: Enabled plugins.
		"""
		if only_ids:
			enabled = set(only_ids)
		else:
			enabled = {
				plugin["id"]
				for plugin in self.list_plugins()
				if plugin.get("default_enabled") is True
			}
			enabled.update(enable_ids)
		enabled.difference_update(disable_ids)

		resolved: list[dict[str, object]] = []
		for plugin_id in self._order:
			if plugin_id in enabled:
				resolved.append(self._plugins[plugin_id])
		return resolved

	def load_plugin_path(self, path: str) -> None:
		"""
		Load and register a plugin from a file path.

		Args:
			path: Path to a plugin module.
		"""
		abs_path = os.path.abspath(path)
		module_name = f"pgml_lint_plugin_{len(self._plugins)}"
		spec = importlib.util.spec_from_file_location(module_name, abs_path)
		if spec is None or spec.loader is None:
			raise ValueError(f"Unable to load plugin module: {path}")
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
		_register_module(self, module)


#============================================


def build_registry() -> Registry:
	"""
	Build a registry with built-in plugins.

	Returns:
		Registry: Plugin registry.
	"""
	registry = Registry()
	for module_name in pgml_lint.plugins.BUILTIN_PLUGINS:
		module = importlib.import_module(module_name)
		_register_module(registry, module)
	return registry
