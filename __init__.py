"""
# Плагин управления пользователями

Упрощает управление учетными записями пользователей. 
Плагин предоставляет администратору полный контроль над пользовательскими данными,
позволяя легко вносить изменения и управлять доступом.   
"""

import os
from settings import Config
from app.core.main.BasePlugin import BasePlugin
from app.core.models.Users import User
from app.core.lib.object import setProperty, getProperty
from app.core.lib.object import getObjectsByClass, addObject, getObject, deleteObject
from flask import redirect, jsonify, url_for
from flask import current_app
from app.authentication.handlers import handle_admin_required

class Permissions(BasePlugin):

    def __init__(self,app):
        super().__init__(app,__name__)
        self.title = "Permissions"
        self.description = """This is a plugin edit permissions"""
        self.version = "0.1"
        self.category = "System"

    def initialization(self):
        pass

    def admin(self, request):

        content = {
        }

        return self.render('permissions.html', content)

    def route_index(self):
        @self.blueprint.route('/Permissions/list', methods=['GET'])
        @handle_admin_required
        def getPermissions():

            # Словарь для хранения маршрутов, сгруппированных по blueprint
            grouped_routes = {}

            def generate_url(rule):
                try:
                    return url_for(rule.endpoint)
                except Exception:
                    return rule.rule
            
            for rule in self._app.url_map.iter_rules():
                #if rule.endpoint in ['static', 'login', 'logout']:
                #    continue  # Пропускаем системные маршруты

                # Извлекаем имя blueprint из endpoint
                parts = rule.endpoint.split('.')
                if len(parts) > 1:
                    blueprint_name = parts[0]  # Имя blueprint
                    endpoint = parts[1]  # Имя маршрута внутри blueprint
                else:
                    blueprint_name = "core"  # Маршрут не принадлежит ни к одному blueprint
                    endpoint = rule.endpoint

                # if blueprint_name in ['dashboard']:
                #     continue  # Пропускаем системные маршруты

                methods = []

                permissions = getProperty("_permissions." + rule.endpoint.replace(".", ":"))

                for method in rule.methods:
                    if method.lower() not in ['get','post','put','delete']:
                        continue

                    # Находим функцию-обработчик для текущего маршрута
                    view_func = current_app.view_functions.get(rule.endpoint)

                    # Проверяем, является ли view_func экземпляром класса Resource
                    if hasattr(view_func, 'view_class'):
                        # Получаем класс Resource
                        resource_class = view_func.view_class

                        # Находим метод, соответствующий HTTP-методу
                        method_name = method.lower()
                        if hasattr(resource_class, method_name):
                            method = getattr(resource_class, method_name)

                            # Получаем обязательные роли (если есть)
                            required_roles = getattr(method, 'required_roles', None)
                        else:
                            required_roles = None
                    else:
                        # Для обычных функций-обработчиков
                        method_name = method.lower()
                        required_roles = getattr(view_func, 'required_roles', None)
                    
                    method_permissions = {}
                    if permissions and method_name in permissions:
                        method_permissions = permissions[method_name]

                    methods.append({
                        'method': method_name,
                        'required_roles':required_roles,
                        'permissions': method_permissions
                    })

                # Создаем запись для маршрута
                route_info = {
                    'endpoint': endpoint,
                    'methods': methods,
                    'url': generate_url(rule),
                }

                # Добавляем маршрут в соответствующую группу
                if blueprint_name not in grouped_routes:
                    bl_permissions = getProperty("_permissions.blueprint:" + blueprint_name)
                    grouped_routes[blueprint_name] = {
                        "endpoints":[],
                        "permissions":bl_permissions,
                    }
                    
                grouped_routes[blueprint_name]["endpoints"].append(route_info)

            return grouped_routes, 200
