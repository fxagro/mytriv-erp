# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
import werkzeug.exceptions

_logger = logging.getLogger(__name__)


class AuthController(http.Controller):
    """
    Authentication REST API controller for MyTriv ERP.
    
    Provides endpoints for user authentication, session management, and user info.
    Supports both session cookie and token-based authentication.
    """

    @http.route('/api/v1/auth/login', type='http', auth='none', methods=['POST'], csrf=False)
    def login(self):
        """
        Authenticate user and create session.
        
        Expects JSON payload:
        {
            "login": "user@example.com",
            "password": "password123",
            "db": "mytriv_erp"  // optional, defaults to request.db
        }
        
        Returns:
        {
            "user": {
                "id": 1,
                "name": "John Doe",
                "login": "user@example.com",
                "partner_id": 1,
                "company_id": 1,
                "company_name": "My Company"
            },
            "session_id": "session123...",
            "message": "Login successful"
        }
        
        On failure, returns 401 with error message.
        """
        try:
            # Parse JSON data
            try:
                data = json.loads(request.httprequest.data)
            except json.JSONDecodeError:
                return self._error_response("Invalid JSON data in request body", 400)

            if not isinstance(data, dict):
                return self._error_response("Request body must be a JSON object", 400)

            # Validate required fields
            if not data.get('login') or not data.get('password'):
                return self._error_response("Login and password are required", 400)

            login = data.get('login').strip()
            password = data.get('password')
            db = data.get('db')

            # Authenticate user
            try:
                uid = request.session.authenticate(db, login, password)
                if not uid:
                    return self._error_response("Invalid login credentials", 401)
            except Exception as e:
                _logger.error(f"Authentication error for user {login}: {str(e)}")
                return self._error_response("Authentication failed", 401)

            # Get user info
            user = request.env['res.users'].browse(uid)
            if not user.exists():
                return self._error_response("User not found", 401)

            # Get company info
            company = user.company_id
            company_info = {
                'id': company.id,
                'name': company.name
            } if company else None

            # Get partner info
            partner = user.partner_id
            partner_info = {
                'id': partner.id,
                'name': partner.name,
                'email': partner.email
            } if partner else None

            user_data = {
                'id': user.id,
                'name': user.name,
                'login': user.login,
                'partner_id': partner.id if partner else None,
                'company_id': company.id if company else None,
                'company_name': company.name if company else None,
                'partner': partner_info
            }

            response_data = {
                'user': user_data,
                'session_id': request.session.sid,
                'message': 'Login successful',
                'success': True
            }

            return self._success_response(response_data)

        except Exception as e:
            _logger.error(f"Unexpected error in login: {str(e)}")
            return self._error_response(f"Login failed: {str(e)}", 500)

    @http.route('/api/v1/auth/logout', type='http', auth='user', methods=['POST'], csrf=False)
    def logout(self):
        """
        Logout user and destroy session.
        
        Returns:
        {
            "message": "Logout successful",
            "success": true
        }
        """
        try:
            # Clear session
            request.session.logout()

            return self._success_response({
                'message': 'Logout successful',
                'success': True
            })

        except Exception as e:
            _logger.error(f"Error in logout: {str(e)}")
            return self._error_response(f"Logout failed: {str(e)}", 500)

    @http.route('/api/v1/auth/me', type='http', auth='user', methods=['GET'], csrf=False)
    def get_current_user(self):
        """
        Get current authenticated user information.
        
        Returns:
        {
            "user": {
                "id": 1,
                "name": "John Doe",
                "login": "user@example.com",
                "partner_id": 1,
                "company_id": 1,
                "company_name": "My Company"
            },
            "session_id": "session123..."
        }
        
        Returns 401 if no authenticated user.
        """
        try:
            user = request.env.user

            # Check if user is authenticated (not public user)
            if user.id == request.env.ref('base.public_user').id:
                return self._error_response("Not authenticated", 401)

            # Get company info
            company = user.company_id
            company_info = {
                'id': company.id,
                'name': company.name
            } if company else None

            # Get partner info
            partner = user.partner_id
            partner_info = {
                'id': partner.id,
                'name': partner.name,
                'email': partner.email
            } if partner else None

            user_data = {
                'id': user.id,
                'name': user.name,
                'login': user.login,
                'partner_id': partner.id if partner else None,
                'company_id': company.id if company else None,
                'company_name': company.name if company else None,
                'partner': partner_info,
                'groups': [group.name for group in user.groups_id],
                'active': user.active,
                'last_login': user.login_date.isoformat() if user.login_date else None
            }

            response_data = {
                'user': user_data,
                'session_id': request.session.sid,
                'authenticated': True
            }

            return self._success_response(response_data)

        except Exception as e:
            _logger.error(f"Error in get_current_user: {str(e)}")
            return self._error_response(f"Error retrieving user info: {str(e)}", 500)

    @http.route('/api/v1/auth/session', type='http', auth='none', methods=['GET'], csrf=False)
    def check_session(self):
        """
        Check if current session is valid and return user info if authenticated.
        
        Returns:
        {
            "authenticated": true,
            "user": { ... }  // if authenticated
        }
        
        Returns:
        {
            "authenticated": false,
            "message": "No active session"
        }
        """
        try:
            user = request.env.user

            # Check if user is authenticated (not public user)
            if user.id == request.env.ref('base.public_user').id:
                return self._success_response({
                    'authenticated': False,
                    'message': 'No active session'
                })

            # Get company info
            company = user.company_id
            company_info = {
                'id': company.id,
                'name': company.name
            } if company else None

            # Get partner info
            partner = user.partner_id
            partner_info = {
                'id': partner.id,
                'name': partner.name,
                'email': partner.email
            } if partner else None

            user_data = {
                'id': user.id,
                'name': user.name,
                'login': user.login,
                'partner_id': partner.id if partner else None,
                'company_id': company.id if company else None,
                'company_name': company.name if company else None,
                'partner': partner_info
            }

            response_data = {
                'authenticated': True,
                'user': user_data,
                'session_id': request.session.sid
            }

            return self._success_response(response_data)

        except Exception as e:
            _logger.error(f"Error in check_session: {str(e)}")
            return self._error_response(f"Error checking session: {str(e)}", 500)

    def _success_response(self, data, status=200):
        """Return successful JSON response"""
        response = Response(
            json.dumps(data, default=str, indent=2),
            content_type='application/json',
            status=status
        )
        return response

    def _error_response(self, message, status=400):
        """Return error JSON response"""
        return self._success_response({
            'error': message,
            'success': False
        }, status)