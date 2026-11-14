from __future__ import annotations

from backend.base_datos import BaseDatos, obtener_base_datos


class DestinatariosRepositorio:
    def __init__(
        self,
        bd: BaseDatos | None = None,
    ) -> None:
        self.bd = bd or obtener_base_datos()

    def guardar(
        self,
        nombre: str,
        correo: str,
    ) -> dict:
        existente = self.bd.consultar_uno(
            """
            SELECT *
            FROM Destinatarios
            WHERE correo = ?
            """,
            (correo,),
        )

        if existente:
            self.bd.ejecutar(
                """
                UPDATE Destinatarios
                SET
                    nombre = ?,
                    activo = 1
                WHERE correo = ?
                """,
                (nombre, correo),
            )

            return (
                self.bd.consultar_uno(
                    """
                    SELECT *
                    FROM Destinatarios
                    WHERE correo = ?
                    """,
                    (correo,),
                )
                or {}
            )

        identificador = self.bd.insertar(
            """
            INSERT INTO Destinatarios (
                nombre,
                correo,
                activo
            )
            VALUES (?, ?, 1)
            """,
            (nombre, correo),
        )

        return (
            self.bd.consultar_uno(
                """
                SELECT *
                FROM Destinatarios
                WHERE id = ?
                """,
                (identificador,),
            )
            or {}
        )

    def listar(
        self,
        solo_activos: bool = True,
    ) -> list[dict]:
        sql = """
            SELECT *
            FROM Destinatarios
        """

        parametros: tuple = ()

        if solo_activos:
            sql += """
                WHERE activo = 1
            """

        sql += """
            ORDER BY id DESC
        """

        return self.bd.consultar_todos(
            sql,
            parametros,
        )

    def desvincular(
        self,
        destinatario_id: int,
    ) -> dict | None:
        existente = self.bd.consultar_uno(
            """
            SELECT *
            FROM Destinatarios
            WHERE id = ?
              AND activo = 1
            """,
            (destinatario_id,),
        )

        if existente is None:
            return None

        self.bd.ejecutar(
            """
            UPDATE Destinatarios
            SET activo = 0
            WHERE id = ?
              AND activo = 1
            """,
            (destinatario_id,),
        )

        return self.bd.consultar_uno(
            """
            SELECT *
            FROM Destinatarios
            WHERE id = ?
            """,
            (destinatario_id,),
        )