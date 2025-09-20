[1mdiff --git a/app_tickets.py b/app_tickets.py[m
[1mindex ae948bd..48068af 100644[m
[1m--- a/app_tickets.py[m
[1m+++ b/app_tickets.py[m
[36m@@ -329,12 +329,16 @@[m [mtry:[m
         [m
         @app.route('/devops/ofertas')[m
         def _devops_fallback_ofertas():[m
[31m-            from flask import session, jsonify, request, make_response[m
[32m+[m[32m            from flask import session, jsonify, request, make_response, render_template[m
             if not session.get('devops_authenticated'):[m
                 return jsonify({'error': 'No autorizado'}), 401[m
             [m
[31m-            # Si es una petición AJAX, devolver JSON[m
[31m-            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':[m
[32m+[m[32m            # Solo devolver JSON si se solicita explícitamente con todos los parámetros[m
[32m+[m[32m            if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and[m[41m [m
[32m+[m[32m                request.args.get('ajax') == 'true' and[m[41m [m
[32m+[m[32m                request.args.get('format') == 'json' and[m[41m [m
[32m+[m[32m                request.args.get('api') == 'true' and[m
[32m+[m[32m                request.args.get('json') == 'true'):[m
                 try:[m
                     from datetime import datetime[m
                     [m
[36m@@ -380,182 +384,8 @@[m [mtry:[m
                         'source': 'error'[m
                     }), 500[m
             [m
[31m-            # Si no es AJAX, devolver HTML completo[m
[31m-            html = """[m
[31m-            <!DOCTYPE html>[m
[31m-            <html lang="es">[m
[31m-            <head>[m
[31m-                <meta charset="UTF-8">[m
[31m-                <meta name="viewport" content="width=device-width, initial-scale=1.0">[m
[31m-                <title>Gestión de Ofertas - DevOps</title>[m
[31m-                <style>[m
[31m-                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f5f5f5; }[m
[31m-                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }[m
[31m-                    .container { max-width: 1200px; margin: 20px auto; padding: 20px; }[m
[31m-                    .card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }[m
[31m-                    .card-header { background: #f8f9fa; padding: 15px 20px; border-bottom: 1px solid #dee2e6; border-radius: 8px 8px 0 0; }[m
[31m-                    .card-body { padding: 20px; }[m
[31m-                    .btn { padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }[m
[31m-                    .btn-primary { background: #007bff; color: white; }[m
[31m-                    .btn-success { background: #28a745; color: white; }[m
[31m-                    .btn-warning { background: #ffc107; color: black; }[m
[31m-                    .btn-danger { background: #dc3545; color: white; }[m
[31m-                    .btn-secondary { background: #6c757d; color: white; }[m
[31m-                    .btn:hover { opacity: 0.8; }[m
[31m-                    .table { width: 100%; border-collapse: collapse; margin-top: 20px; }[m
[31m-                    .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }[m
[31m-                    .table th { background: #f8f9fa; font-weight: 600; }[m
[31m-                    .form-group { margin-bottom: 15px; }[m
[31m-                    .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }[m
[31m-                    .form-control { width: 100%; padding: 8px 12px; border: 1px solid #ced4da; border-radius: 4px; }[m
[31m-                    .form-row { display: flex; gap: 15px; }[m
[31m-                    .form-row .form-group { flex: 1; }[m
[31m-                    .status-badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500; }[m
[31m-                    .status-active { background: #d4edda; color: #155724; }[m
[31m-                    .status-inactive { background: #f8d7da; color: #721c24; }[m
[31m-                    .loading { text-align: center; padding: 20px; color: #6c757d; }[m
[31m-                    .alert { padding: 12px 16px; border-radius: 4px; margin-bottom: 20px; }[m
[31m-                    .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }[m
[31m-                    .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }[m
[31m-                </style>[m
[31m-            </head>[m
[31m-            <body>[m
[31m-                <div class="header">[m
[31m-                    <h1>🎯 Gestión de Ofertas</h1>[m
[31m-                    <p>Administra las ofertas y promociones del sistema</p>[m
[31m-                </div>[m
[31m-                [m
[31m-                <div class="container">[m
[31m-                    <div class="card">[m
[31m-                        <div class="card-header">[m
[31m-                            <h3>📋 Lista de Ofertas</h3>[m
[31m-                        </div>[m
[31m-                        <div class="card-body">[m
[31m-                            <div style="margin-bottom: 20px;">[m
[31m-                                <button class="btn btn-success" onclick="crearOferta()">➕ Nueva Oferta</button>[m
[31m-                                <button class="btn btn-primary" onclick="cargarOfertas()">🔄 Actualizar</button>[m
[31m-                                <button class="btn btn-secondary" onclick="volverPanel()">← Volver al Panel</button>[m
[31m-                            </div>[m
[31m-                            [m
[31m-                            <div id="loading" class="loading" style="display: none;">[m
[31m-                                Cargando ofertas...[m
[31m-                            </div>[m
[31m-                            [m
[31m-                            <div id="alert-container"></div>[m
[31m-                            [m
[31m-                            <table class="table" id="ofertas-table" style="display: none;">[m
[31m-                                <thead>[m
[31m-                                    <tr>[m
[31m-                                        <th>ID</th>[m
[31m-                                        <th>Título</th>[m
[31m-                                        <th>Descripción</th>[m
[31m-                                        <th>Descuento</th>[m
[31m-                                        <th>Fecha Inicio</th>[m
[31m-                                        <th>Fecha Fin</th>[m
[31m-                                        <th>Estado</th>[m
[31m-                                        <th>Acciones</th>[m
[31m-                                    </tr>[m
[31m-                                </thead>[m
[31m-                                <tbody id="ofertas-tbody">[m
[31m-                                </tbody>[m
[31m-                            </table>[m
[31m-                        </div>[m
[31m-                    </div>[m
[31m-                </div>[m
[31m-                [m
[31m-                <script>[m
[31m-                    function cargarOfertas() {[m
[31m-                        document.getElementById('loading').style.display = 'block';[m
[31m-                        document.getElementById('ofertas-table').style.display = 'none';[m
[31m-                        [m
[31m-                        fetch('/devops/ofertas', {[m
[31m-                            headers: { 'X-Requested-With': 'XMLHttpRequest' }[m
[31m-                        })[m
[31m-                        .then(response => response.json())[m
[31m-                        .then(data => {[m
[31m-                            document.getElementById('loading').style.display = 'none';[m
[31m-                            [m
[31