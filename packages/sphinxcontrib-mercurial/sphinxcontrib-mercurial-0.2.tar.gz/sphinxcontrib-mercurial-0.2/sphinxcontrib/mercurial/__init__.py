import hg_changelog
import hg_version

def setup(app):
    app.add_directive('hg_changelog', hg_changelog.HgChangeLog)
    app.add_directive('hg_version', hg_version.HgVersion)
