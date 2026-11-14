/* ============================================================
   SecurityAPPCR - 04_insertar_datos_iniciales.sql
   Inserta la configuración mínima y verifica la instalación.
   No agrega correos de ejemplo: se registran desde la web.
   ============================================================ */

USE [tiusr9pl_SecurityAPP];
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Configuracion WHERE id = 1)
BEGIN
    INSERT INTO dbo.Configuracion
    (
        id,
        nombre_zona,
        limite_personas,
        segundos_permanencia,
        zona_restringida_activa,
        zona_x1,
        zona_y1,
        zona_x2,
        zona_y2,
        horario_activo,
        hora_inicio,
        hora_fin,
        alertas_activas,
        cooldown_segundos,
        confianza_minima
    )
    VALUES
    (
        1,
        N'Aula de demostración',
        2,
        8,
        0,
        0.35,
        0.20,
        0.65,
        0.85,
        0,
        '06:00',
        '22:00',
        1,
        20,
        0.45
    );
END;
GO

PRINT N'Configuración inicial lista.';
GO

/* Verificación final */
SELECT DB_NAME() AS base_datos_actual;

SELECT
    t.name AS tabla,
    SUM(p.rows) AS filas
FROM sys.tables AS t
INNER JOIN sys.partitions AS p
    ON p.object_id = t.object_id
   AND p.index_id IN (0, 1)
WHERE t.schema_id = SCHEMA_ID(N'dbo')
GROUP BY t.name
ORDER BY t.name;

SELECT
    p.name AS procedimiento
FROM sys.procedures AS p
WHERE p.schema_id = SCHEMA_ID(N'dbo')
ORDER BY p.name;

EXEC dbo.sp_configuracion_obtener;
GO
