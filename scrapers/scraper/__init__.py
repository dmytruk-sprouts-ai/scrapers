# =====================================================================
# MONKEY-PATCH FOR UNDETECTED-CHROMEDRIVER PY3.12+ ATTRIBUTE ERROR
# =====================================================================
from packaging.version import Version

# Force the 'version' property to return the standard string representation
if not hasattr(Version, "version"):

    @property
    def get_version_str(self):
        return str(self)

    Version.version = get_version_str
    Version.vstring = get_version_str
# =====================================================================
