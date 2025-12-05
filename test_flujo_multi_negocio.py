import unittest
from unittest.mock import MagicMock, patch
import json
import os
from flask import Flask

# Configurar variables de entorno ANTES de cualquier importación
os.environ['TICKETERA_URL'] = 'http://mock-ticketera'
os.environ['BELGRANO_AHORRO_API_KEY'] = 'test-key'
os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/db'  # Dummy URL para pasar validación

# Importar el blueprint
try:
    from api_belgrano_ahorro import api_bp
except ImportError as e:
    print(f"Error importando api_belgrano_ahorro: {e}")
    import sys
    sys.path.append(os.getcwd())
    from api_belgrano_ahorro import api_bp

class TestMultiNegocio(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(api_bp)
        self.client = self.app.test_client()
        
    @patch('api_belgrano_ahorro.get_db_connection')
    @patch('api_belgrano_ahorro.database')
    @patch('requests.post')
    def test_crear_compra_multi_negocio(self, mock_post, mock_database, mock_get_db):
        # Configurar mock de base de datos
        mock_session = MagicMock()
        mock_get_db.return_value = mock_session
        
        # Mock para usuario
        mock_user_result = MagicMock()
        mock_user_result.fetchone.return_value = MagicMock(_mapping={'nombre': 'Test', 'apellido': 'User', 'email': 'test@test.com', 'telefono': '123456'})
        
        # Mock para productos (2 productos de diferentes negocios)
        # Producto 1: Negocio 1
        prod1_row = MagicMock(_mapping={
            'id': 1, 'nombre': 'Prod 1', 'descripcion': 'Desc 1', 'precio': 100, 
            'stock': 10, 'destacado': False, 'negocio_id': 1, 'categoria_id': 1, 'sucursales': '[1]'
        })
        # Producto 2: Negocio 2
        prod2_row = MagicMock(_mapping={
            'id': 2, 'nombre': 'Prod 2', 'descripcion': 'Desc 2', 'precio': 200, 
            'stock': 10, 'destacado': False, 'negocio_id': 2, 'categoria_id': 1, 'sucursales': '[1]'
        })
        
        # Mock para negocios
        neg1_row = MagicMock(_mapping={'nombre': 'Negocio 1'})
        neg2_row = MagicMock(_mapping={'nombre': 'Negocio 2'})
        
        # Configurar side_effect para execute
        def side_effect(query, params=None):
            query_str = str(query)
            if 'SELECT * FROM usuarios' in query_str:
                return mock_user_result
            if 'FROM productos WHERE id = :producto_id' in query_str:
                res = MagicMock()
                if params['producto_id'] == 1:
                    res.fetchone.return_value = prod1_row
                else:
                    res.fetchone.return_value = prod2_row
                return res
            if 'SELECT nombre FROM negocios' in query_str:
                res = MagicMock()
                if params['negocio_id'] == 1:
                    res.fetchone.return_value = neg1_row
                else:
                    res.fetchone.return_value = neg2_row
                return res
            # Default mocks for others
            res = MagicMock()
            res.fetchone.return_value = MagicMock(_mapping={'nombre': 'Generic'})
            return res
            
        mock_session.execute.side_effect = side_effect
        
        # Mock database helpers
        mock_database.guardar_pedido.return_value = 123
        mock_database.actualizar_stock_carrito.return_value = (True, [], [])
        
        # Mock requests.post response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ticket_id': 999, 'productos': []}
        mock_post.return_value = mock_response
        
        # Datos de la compra
        compra_data = {
            'usuario_id': 1,
            'items': [
                {'producto_id': 1, 'cantidad': 1},
                {'producto_id': 2, 'cantidad': 1}
            ],
            'metodo_pago': 'efectivo',
            'direccion_entrega': 'Calle Falsa 123'
        }
        
        # Ejecutar petición
        print("Enviando petición POST a /api/compras...")
        response = self.client.post('/api/compras', 
                                  json=compra_data,
                                  headers={'X-API-Key': 'test-key'})
        
        # Verificaciones
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json, indent=2)}")
        
        self.assertEqual(response.status_code, 201)
        
        # Verificar que se llamó a requests.post 2 veces (una por negocio)
        print(f"Llamadas a Ticketera: {mock_post.call_count}")
        self.assertEqual(mock_post.call_count, 2)
        
        # Verificar payloads
        calls = mock_post.call_args_list
        negocios_enviados = []
        grupos_compra = []
        
        for i, call in enumerate(calls):
            data = call.kwargs['json']
            print(f"Ticket {i+1}: Negocio='{data['negocio_nombre']}', Grupo='{data['grupo_compra']}', Total Grupo={data['tickets_grupo_total']}")
            negocios_enviados.append(data['negocio_nombre'])
            grupos_compra.append(data['grupo_compra'])
            self.assertEqual(data['tickets_grupo_total'], 2)
            
        self.assertIn('Negocio 1', negocios_enviados)
        self.assertIn('Negocio 2', negocios_enviados)
        
        # Verificar que el grupo de compra es el mismo
        self.assertEqual(grupos_compra[0], grupos_compra[1])
        print("✅ PRUEBA EXITOSA: Se generaron 2 tickets separados para 2 negocios diferentes.")

if __name__ == '__main__':
    unittest.main()
