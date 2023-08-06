import re

from pkg_resources import resource_filename

from trac.core import *
from trac.admin import IAdminPanelProvider
from trac.db import DatabaseManager
from trac.env import IEnvironmentSetupParticipant
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider, add_notice

from trac.util.translation import _, ngettext

import db_default

class Redirects(Component):
    """
    With this component you can define server-side redirects in Trac.
    """

    implements(IEnvironmentSetupParticipant, IAdminPanelProvider, IRequestHandler, ITemplateProvider)

    # IEnvironmentSetupParticipant methods

    def environment_created(self):
        """Called when a new Trac environment is created."""

        self.found_db_version = 0
        self.upgrade_environment(self.env.get_db_cnx())

    def environment_needs_upgrade(self, db):
        """Called when Trac checks whether the environment needs to be upgraded."""

        cursor = db.cursor()
        cursor.execute("SELECT value FROM system WHERE name=%s", (db_default.name,))
        value = cursor.fetchone()
        if not value:
            self.found_db_version = 0
            return True
        else:
            self.found_db_version = int(value[0])
            if self.found_db_version < db_default.version:
                return True
        
        return False

    def upgrade_environment(self, db):
        """Actually perform an environment upgrade."""

        connector, _ = DatabaseManager(self.env)._get_connector()

        cursor = db.cursor()
        for table in db_default.schema:
            for stmt in connector.to_sql(table):
                cursor.execute(stmt)

        if not self.found_db_version:
            cursor.execute("INSERT INTO system (name, value) VALUES (%s, %s)", (db_default.name, db_default.version))
        else:
            cursor.execute("UPDATE system SET value=%s WHERE name=%s", (db_default.version, db_default.name))

        db.commit()

        self.log.info('Upgraded %s schema version from %d to %d', db_default.name, self.found_db_version, db_default.version)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        """Return a list of available admin panels."""

        if req.perm.has_permission('TRAC_ADMIN'):
            yield ('general', _('General'), 'redirects', _('Redirects'))

    def render_admin_panel(self, req, category, page, path_info):
        """Process a request for an admin panel."""

        db = self.env.get_db_cnx()
        cursor = db.cursor()

        if req.method == 'POST':
            if req.args.get('add'):
                f = req.args.get('from').strip()
                t = req.args.get('to').strip()
                enabled = req.args.get('enabled', "").strip()
                enabled = enabled and (enabled != "0")
                self._add_redirect(cursor, f, t, enabled)
                db.commit()
                add_notice(req, _('Redirect from "%(frompath)s" to "%(topath)s" has been added.', frompath=f, topath=t))
            elif req.args.get('remove'):
                selected = req.args.get('selected')
                if selected:
                    if not isinstance(selected, list):
                        selected = [selected]
                    for redirect in selected:
                        self._remove_redirect(cursor, redirect)
                    db.commit()
                    msg = ngettext('Selected redirect has been removed.', 'Selected redirects have been removed.', len(selected))
                    add_notice(req, msg)
            elif req.args.get('enable'):
                selected = req.args.get('selected')
                if selected:
                    if not isinstance(selected, list):
                        selected = [selected]
                    for redirect in selected:
                        self._enable_redirect(cursor, redirect)
                    db.commit()
                    msg = ngettext('Selected redirect has been enabled.', 'Selected redirects have been enabled.', len(selected))
                    add_notice(req, msg)
            elif req.args.get('disable'):
                selected = req.args.get('selected')
                if selected:
                    if not isinstance(selected, list):
                        selected = [selected]
                    for redirect in selected:
                        self._disable_redirect(cursor, redirect)
                    db.commit()
                    msg = ngettext('Selected redirect has been disabled.', 'Selected redirects have been disabled.', len(selected))
                    add_notice(req, msg)

            req.redirect(req.href.admin(category, page))

        cursor.execute("SELECT frompath, topath, enabled FROM redirects ORDER BY frompath, topath")
        redirects = cursor.fetchall()

        return ('admin_redirects.html', {
                'redirects': redirects,
            })

    def _add_redirect(self, cursor, f, t, enabled):
        if not f or not t:
            raise TracError(_('Invalid command argument.'))

        cursor.execute("INSERT INTO redirects (frompath, topath, enabled) VALUES (%s, %s, %s)", (f, t, 1 if enabled else 0))

    def _remove_redirect(self, cursor, redirect):
        cursor.execute("DELETE FROM redirects WHERE frompath=%s", (redirect,))

    def _enable_redirect(self, cursor, redirect):
        cursor.execute("UPDATE redirects SET enabled=1 WHERE frompath=%s", (redirect,))

    def _disable_redirect(self, cursor, redirect):
        cursor.execute("UPDATE redirects SET enabled=0 WHERE frompath=%s", (redirect,))

    # IRequestHandler methods

    def match_request(self, req):
        """Return whether the handler wants to process the given request."""

        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("SELECT frompath, topath FROM redirects WHERE enabled=1 ORDER BY frompath, topath")
        for f, t in cursor:
            pattern = re.compile(f)
            if pattern.match(req.path_info):
                self.to = pattern.sub(t, req.path_info)
                return True

        return False

    def process_request(self, req):
        """Process the request."""

        self.log.debug('Redirecting to "%s"', self.to)
        req.redirect(self.to)

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """Return a list of directories with static resources (such as style
        sheets, images, etc.)"""

        return []

    def get_templates_dirs(self):
        """Return a list of directories containing the provided template files."""

        yield resource_filename(__name__, 'templates')
