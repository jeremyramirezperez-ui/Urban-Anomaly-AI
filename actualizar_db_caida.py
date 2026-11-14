from backend.base_datos import BaseDatos

def actualizar():
    db = BaseDatos()
    try:
        # Drop existing constraint
        db.ejecutar("ALTER TABLE dbo.Alertas DROP CONSTRAINT CK_Alertas_Tipo")
        # Add new constraint
        db.ejecutar("""
            ALTER TABLE dbo.Alertas ADD CONSTRAINT CK_Alertas_Tipo CHECK
            (
                tipo IN
                (
                    'AGLOMERACION',
                    'PERMANENCIA_PROLONGADA',
                    'ZONA_RESTRINGIDA',
                    'FUERA_DE_HORARIO',
                    'CAMARA_APAGADA',
                    'FALLA_CAMARA',
                    'PRUEBA',
                    'CAIDA_DETECTADA'
                )
            )
        """)
        print("Constraint 'CK_Alertas_Tipo' actualizado exitosamente.")
    except Exception as e:
        print(f"Error actualizando constraint: {e}")

if __name__ == "__main__":
    actualizar()
