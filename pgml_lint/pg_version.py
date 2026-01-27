# Standard Library
import re


DEFAULT_PG_VERSION = "2.17"
VERSION_RX = re.compile(r"^\s*(\d+)(?:\.(\d+))?")


#============================================


def normalize_pg_version(version: str | None) -> str:
	"""
	Normalize the PG version string or fall back to the default.
	"""
	if version is None:
		return DEFAULT_PG_VERSION
	normalized = str(version).strip()
	if not normalized:
		return DEFAULT_PG_VERSION
	return normalized


#============================================


def parse_pg_version(version: str) -> tuple[int, int]:
	"""
	Parse a PG version string like 2.17 into a (major, minor) tuple.
	"""
	match = VERSION_RX.match(str(version))
	if not match:
		raise ValueError(f"Invalid PG version: {version}")
	major = int(match.group(1))
	minor = int(match.group(2) or 0)
	return (major, minor)
