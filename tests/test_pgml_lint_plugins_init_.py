# Local modules
import pgml_lint.plugins


#============================================

def test_builtin_plugins_list() -> None:
	plugins = pgml_lint.plugins.BUILTIN_PLUGINS
	assert isinstance(plugins, list)
	assert "pgml_lint.plugins.block_markers" in plugins
	assert "pgml_lint.plugins.pgml_inline" in plugins
	assert all(isinstance(name, str) for name in plugins)
