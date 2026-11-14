import unittest

class TestZonaVisual(unittest.TestCase):
    def test_normalizacion_coordenadas(self):
        # Simula dimensiones de pantalla (640x360) y un recuadro dibujado
        ancho, alto = 640, 360
        x1, y1, x2, y2 = 160, 90, 480, 270

        # Conversión de píxeles a rango 0.0 - 1.0
        norm_x1 = round(x1 / ancho, 2)
        norm_y1 = round(y1 / alto, 2)
        norm_x2 = round(x2 / ancho, 2)
        norm_y2 = round(y2 / alto, 2)

        # Verificación de resultados
        self.assertEqual(norm_x1, 0.25)
        self.assertEqual(norm_y1, 0.25)
        self.assertEqual(norm_x2, 0.75)
        self.assertEqual(norm_y2, 0.75)

if __name__ == '__main__':
    unittest.main()
    

