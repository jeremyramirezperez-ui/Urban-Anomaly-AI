/* ============================================================
   SecurityAPPCR - 03_crear_procedimientos.sql
   Procedimientos usados por los repositorios cuando DB_TIPO=sqlserver.
   ============================================================ */

USE [tiusr9pl_SecurityAPP];
GO

/* ============================ CONFIGURACIÓN ============================ */
CREATE OR ALTER PROCEDURE dbo.sp_configuracion_obtener
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        id, nombre_zona, limite_personas, segundos_permanencia,
        zona_restringida_activa, zona_x1, zona_y1, zona_x2, zona_y2,
        horario_activo, hora_inicio, hora_fin, alertas_activas,
        cooldown_segundos, confianza_minima, caida_activa, tiempo_riesgo_caida, fuego_activo, actualizado_en
    FROM dbo.Configuracion
    WHERE id = 1;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_configuracion_actualizar
    @nombre_zona              NVARCHAR(100),
    @limite_personas          INT,
    @segundos_permanencia     INT,
    @zona_restringida_activa  BIT,
    @zona_x1                  FLOAT,
    @zona_y1                  FLOAT,
    @zona_x2                  FLOAT,
    @zona_y2                  FLOAT,
    @horario_activo           BIT,
    @hora_inicio              CHAR(5),
    @hora_fin                 CHAR(5),
    @alertas_activas          BIT,
    @cooldown_segundos        INT,
    @confianza_minima         FLOAT,
    @caida_activa             BIT,
    @tiempo_riesgo_caida      INT,
    @fuego_activo             BIT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE dbo.Configuracion
    SET
        nombre_zona = @nombre_zona,
        limite_personas = @limite_personas,
        segundos_permanencia = @segundos_permanencia,
        zona_restringida_activa = @zona_restringida_activa,
        zona_x1 = @zona_x1,
        zona_y1 = @zona_y1,
        zona_x2 = @zona_x2,
        zona_y2 = @zona_y2,
        horario_activo = @horario_activo,
        hora_inicio = @hora_inicio,
        hora_fin = @hora_fin,
        alertas_activas = @alertas_activas,
        cooldown_segundos = @cooldown_segundos,
        confianza_minima = @confianza_minima,
        caida_activa = @caida_activa,
        tiempo_riesgo_caida = @tiempo_riesgo_caida,
        fuego_activo = @fuego_activo,
        actualizado_en = SYSDATETIME()
    WHERE id = 1;

    EXEC dbo.sp_configuracion_obtener;
END;
GO

/* ============================ DESTINATARIOS ============================ */
CREATE OR ALTER PROCEDURE dbo.sp_destinatario_guardar
    @nombre NVARCHAR(100),
    @correo NVARCHAR(254)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    SET @nombre = LTRIM(RTRIM(@nombre));
    SET @correo = LOWER(LTRIM(RTRIM(@correo)));

    IF EXISTS (SELECT 1 FROM dbo.Destinatarios WHERE correo = @correo)
    BEGIN
        UPDATE dbo.Destinatarios
        SET nombre = @nombre,
            activo = 1
        WHERE correo = @correo;
    END
    ELSE
    BEGIN
        INSERT INTO dbo.Destinatarios (nombre, correo, activo)
        VALUES (@nombre, @correo, 1);
    END;

    SELECT id, nombre, correo, activo, creado_en
    FROM dbo.Destinatarios
    WHERE correo = @correo;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_destinatarios_listar
    @solo_activos BIT = 1
AS
BEGIN
    SET NOCOUNT ON;

    SELECT id, nombre, correo, activo, creado_en
    FROM dbo.Destinatarios
    WHERE @solo_activos = 0 OR activo = 1
    ORDER BY id DESC;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_destinatario_cambiar_estado
    @id INT,
    @activo BIT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE dbo.Destinatarios
    SET activo = @activo
    WHERE id = @id;

    SELECT id, nombre, correo, activo, creado_en
    FROM dbo.Destinatarios
    WHERE id = @id;
END;
GO

/* =============================== ALERTAS =============================== */
CREATE OR ALTER PROCEDURE dbo.sp_alerta_guardar
    @tipo                 VARCHAR(40),
    @titulo               NVARCHAR(150),
    @mensaje              NVARCHAR(600),
    @nivel                VARCHAR(15),
    @cantidad_personas    INT,
    @limite_personas      INT = NULL,
    @id_seguimiento       INT = NULL,
    @confianza_promedio   FLOAT = NULL,
    @fecha_hora           DATETIMEOFFSET(0),
    @zona                 NVARCHAR(100),
    @captura_ruta         NVARCHAR(300) = NULL,
    @detalle_json         NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    INSERT INTO dbo.Alertas
    (
        tipo, titulo, mensaje, nivel, cantidad_personas, limite_personas,
        id_seguimiento, confianza_promedio, fecha_hora, estado, zona,
        captura_ruta, correo_enviado, estado_correo, detalle_json
    )
    VALUES
    (
        @tipo, @titulo, @mensaje, @nivel, @cantidad_personas, @limite_personas,
        @id_seguimiento, @confianza_promedio, @fecha_hora, 'PENDIENTE', @zona,
        @captura_ruta, 0, N'PENDIENTE', @detalle_json
    );

    DECLARE @id INT = CONVERT(INT, SCOPE_IDENTITY());

    SELECT *
    FROM dbo.Alertas
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_alerta_obtener
    @id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT *
    FROM dbo.Alertas
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_alertas_listar
    @estado VARCHAR(15) = NULL,
    @tipo   VARCHAR(40) = NULL,
    @limite INT = 100
AS
BEGIN
    SET NOCOUNT ON;

    IF @limite < 1 SET @limite = 1;
    IF @limite > 500 SET @limite = 500;

    SELECT TOP (@limite) *
    FROM dbo.Alertas
    WHERE (@estado IS NULL OR estado = @estado)
      AND (@tipo IS NULL OR tipo = @tipo)
    ORDER BY id DESC;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_alerta_actualizar_estado
    @id INT,
    @estado VARCHAR(15)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE dbo.Alertas
    SET estado = @estado
    WHERE id = @id;

    SELECT *
    FROM dbo.Alertas
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_alerta_actualizar_correo
    @id INT,
    @correo_enviado BIT,
    @estado_correo NVARCHAR(300)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE dbo.Alertas
    SET correo_enviado = @correo_enviado,
        estado_correo = @estado_correo
    WHERE id = @id;

    SELECT *
    FROM dbo.Alertas
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_alertas_resumen_totales
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        COUNT_BIG(*) AS total,
        SUM(CASE WHEN estado = 'PENDIENTE' THEN CONVERT(BIGINT, 1) ELSE CONVERT(BIGINT, 0) END) AS pendientes
    FROM dbo.Alertas;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_alertas_resumen_por_tipo
AS
BEGIN
    SET NOCOUNT ON;

    SELECT tipo, COUNT_BIG(*) AS cantidad
    FROM dbo.Alertas
    GROUP BY tipo
    ORDER BY cantidad DESC, tipo ASC;
END;
GO

/* =============================== CAPTURAS ============================== */
CREATE OR ALTER PROCEDURE dbo.sp_captura_guardar
    @alerta_id INT,
    @ruta NVARCHAR(300),
    @fecha_hora DATETIMEOFFSET(0)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    INSERT INTO dbo.Capturas (alerta_id, ruta, fecha_hora)
    VALUES (@alerta_id, @ruta, @fecha_hora);

    SELECT CONVERT(INT, SCOPE_IDENTITY()) AS id;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_capturas_por_alerta
    @alerta_id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT id, alerta_id, ruta, fecha_hora, creado_en
    FROM dbo.Capturas
    WHERE alerta_id = @alerta_id
    ORDER BY id DESC;
END;
GO

/* ========================== APOYO PARA PRUEBAS ========================= */
CREATE OR ALTER PROCEDURE dbo.sp_limpiar_datos_demostracion
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRANSACTION;
        DELETE FROM dbo.Capturas;
        DELETE FROM dbo.Alertas;
        DBCC CHECKIDENT ('dbo.Capturas', RESEED, 0) WITH NO_INFOMSGS;
        DBCC CHECKIDENT ('dbo.Alertas', RESEED, 0) WITH NO_INFOMSGS;
    COMMIT TRANSACTION;
END;
GO

/* ==================== DASHBOARD CON FILTRO DE FECHA ==================== */
CREATE OR ALTER PROCEDURE dbo.sp_dashboard_totales
    @fecha_desde NVARCHAR(40) = NULL,
    @fecha_hasta NVARCHAR(40) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @desde DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_desde);
    DECLARE @hasta DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_hasta);

    SELECT
        COUNT_BIG(*) AS total,
        SUM(CASE WHEN estado = 'PENDIENTE' THEN CONVERT(BIGINT, 1) ELSE CONVERT(BIGINT, 0) END) AS pendientes
    FROM dbo.Alertas
    WHERE (@desde IS NULL OR fecha_hora >= @desde)
      AND (@hasta IS NULL OR fecha_hora <= @hasta);
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_dashboard_resumen_por_tipo
    @fecha_desde NVARCHAR(40) = NULL,
    @fecha_hasta NVARCHAR(40) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @desde DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_desde);
    DECLARE @hasta DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_hasta);

    SELECT tipo, COUNT_BIG(*) AS cantidad
    FROM dbo.Alertas
    WHERE (@desde IS NULL OR fecha_hora >= @desde)
      AND (@hasta IS NULL OR fecha_hora <= @hasta)
    GROUP BY tipo
    ORDER BY cantidad DESC, tipo ASC;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_dashboard_resumen_por_estado
    @fecha_desde NVARCHAR(40) = NULL,
    @fecha_hasta NVARCHAR(40) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @desde DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_desde);
    DECLARE @hasta DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_hasta);

    SELECT estado, COUNT_BIG(*) AS cantidad
    FROM dbo.Alertas
    WHERE (@desde IS NULL OR fecha_hora >= @desde)
      AND (@hasta IS NULL OR fecha_hora <= @hasta)
    GROUP BY estado
    ORDER BY cantidad DESC, estado ASC;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_dashboard_resumen_por_nivel
    @fecha_desde NVARCHAR(40) = NULL,
    @fecha_hasta NVARCHAR(40) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @desde DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_desde);
    DECLARE @hasta DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_hasta);

    SELECT nivel, COUNT_BIG(*) AS cantidad
    FROM dbo.Alertas
    WHERE (@desde IS NULL OR fecha_hora >= @desde)
      AND (@hasta IS NULL OR fecha_hora <= @hasta)
    GROUP BY nivel
    ORDER BY
        CASE nivel WHEN 'ALTO' THEN 1 WHEN 'MEDIO' THEN 2 WHEN 'BAJO' THEN 3 ELSE 4 END;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_dashboard_evolucion_diaria
    @fecha_desde NVARCHAR(40) = NULL,
    @fecha_hasta NVARCHAR(40) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @desde DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_desde);
    DECLARE @hasta DATETIMEOFFSET(0) = TRY_CONVERT(DATETIMEOFFSET(0), @fecha_hasta);

    SELECT
        CAST(fecha_hora AS DATE) AS dia,
        COUNT_BIG(*) AS cantidad
    FROM dbo.Alertas
    WHERE (@desde IS NULL OR fecha_hora >= @desde)
      AND (@hasta IS NULL OR fecha_hora <= @hasta)
    GROUP BY CAST(fecha_hora AS DATE)
    ORDER BY dia ASC;
END;
GO

PRINT N'Procedimientos almacenados listos.';
GO