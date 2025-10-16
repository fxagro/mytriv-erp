# -*- coding: utf-8 -*-
"""
Main controller for MyTriv ERP

This module handles the main web interface and routing.
"""

import json
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class Home(http.Controller):
    """Main home controller"""

    @http.route('/', type='http', auth='none')
    def index(self):
        """Main index page"""
        return request.render('base.index')

    @http.route('/web/login', type='http', auth='none')
    def web_login(self, **kw):
        """Login page"""
        return request.render('base.login')

    @http.route('/web/logout', type='http', auth='user')
    def web_logout(self):
        """Logout and redirect to login page"""
        request.session.logout()
        return request.redirect('/web/login')


class WebClient(http.Controller):
    """Web client controller"""

    @http.route('/web', type='http', auth='user')
    def web_client(self):
        """Main web client interface"""
        return request.render('base.web_client')

    @http.route('/web/action/load', type='json', auth='user')
    def load_action(self, action_id=None, **kw):
        """Load action data"""
        if action_id:
            action = request.env['ir.actions.act_window'].browse(int(action_id))
            return {
                'id': action.id,
                'name': action.name,
                'res_model': action.res_model,
                'view_mode': action.view_mode,
                'domain': action.domain,
                'context': action.context,
            }
        return {}

    @http.route('/web/dataset/search_read', type='json', auth='user')
    def search_read(self, model, fields=None, domain=None, offset=0, limit=80, sort=None):
        """Search and read records"""
        Model = request.env[model]
        records = Model.search_read(
            domain=domain or [],
            fields=fields,
            offset=offset,
            limit=limit,
            order=sort
        )
        return {
            'records': records,
            'length': len(records)
        }


class DatabaseController(http.Controller):
    """Database management controller"""

    @http.route('/web/database/selector', type='http', auth='none')
    def database_selector(self):
        """Database selection page"""
        return request.render('base.database_selector')

    @http.route('/web/database/create', type='http', auth='none', methods=['POST'])
    def create_database(self, master_password=None, name=None, **kw):
        """Create new database"""
        if not master_password or master_password != 'admin':
            raise UserError(_("Invalid master password"))

        if not name:
            raise UserError(_("Database name is required"))

        # Database creation logic would go here
        return request.redirect('/web/login')

    @http.route('/web/database/backup', type='http', auth='user')
    def backup_database(self):
        """Backup current database"""
        # Backup logic would go here
        return request.render('base.database_backup')


class SessionController(http.Controller):
    """Session management controller"""

    @http.route('/web/session/authenticate', type='json', auth='none')
    def authenticate(self, login, password, db=None):
        """Authenticate user session"""
        try:
            uid = request.session.authenticate(db, login, password)
            return {
                'uid': uid,
                'user_context': request.env['res.users'].context_get(),
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/web/session/logout', type='json', auth='user')
    def logout(self):
        """Logout user session"""
        request.session.logout()
        return True

    @http.route('/web/session/get_session_info', type='json', auth='user')
    def get_session_info(self):
        """Get current session information"""
        return request.env['ir.http'].get_session_info()


class MenuController(http.Controller):
    """Menu management controller"""

    @http.route('/web/menu/load', type='json', auth='user')
    def load_menus(self):
        """Load user menus"""
        menus = request.env['ir.ui.menu'].load_menus(request.session.debug)
        return menus

    @http.route('/web/menu/get', type='json', auth='user')
    def get_menu(self, menu_id=None):
        """Get specific menu"""
        if menu_id:
            menu = request.env['ir.ui.menu'].browse(int(menu_id))
            return {
                'id': menu.id,
                'name': menu.name,
                'action': menu.action,
                'children': menu.child_id.mapped(lambda m: {
                    'id': m.id,
                    'name': m.name,
                    'action': m.action,
                })
            }
        return {}


class ViewController(http.Controller):
    """View management controller"""

    @http.route('/web/view/load', type='json', auth='user')
    def load_views(self, views):
        """Load view definitions"""
        result = []
        for view in views:
            view_data = request.env['ir.ui.view'].browse(view['view_id']).read()
            result.append(view_data)
        return result

    @http.route('/web/view/edit_custom', type='json', auth='user')
    def edit_custom_view(self, view_id, arch):
        """Edit custom view"""
        view = request.env['ir.ui.view'].browse(view_id)
        view.arch = arch
        return True


class BinaryController(http.Controller):
    """Binary data controller"""

    @http.route('/web/binary/upload', type='http', auth='user', methods=['POST'])
    def upload_binary(self, file, **kw):
        """Upload binary file"""
        # File upload logic would go here
        return json.dumps({'success': True})

    @http.route('/web/binary/download', type='http', auth='user')
    def download_binary(self, file_id):
        """Download binary file"""
        attachment = request.env['ir.attachment'].browse(int(file_id))
        if attachment:
            return request.make_response(
                attachment.datas,
                headers=[('Content-Type', attachment.mimetype)]
            )
        return request.not_found()


class ReportController(http.Controller):
    """Report controller"""

    @http.route('/web/report/download', type='http', auth='user')
    def download_report(self, report_name, **kw):
        """Download report"""
        # Report generation logic would go here
        return request.render('base.report_template')


class TranslationController(http.Controller):
    """Translation controller"""

    @http.route('/web/translate', type='json', auth='user')
    def translate(self, lang, terms):
        """Translate terms"""
        translations = {}
        for term in terms:
            translation = request.env['ir.translation']._get_source(
                term, 'code', lang
            )
            translations[term] = translation or term
        return translations