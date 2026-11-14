/* ============================================================
   SecurityAPPCR - 02_crear_tablas.sql
   Crea las tablas, restricciones, relaciones e índices.
   El script se puede ejecutar más de una vez.
   ============================================================ */

USE [tiusr9pl_SecurityAPP];
GO

/* ------------------------- Configuración ------------------------- */
IF OBJECT_ID(N'dbo.Configuracion', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Configuracion
    (
        id                       INT             NOT NULL,
        nombre_zona              NVARCHAR(100)   NOT NULL,
        limite_personas          INT             NOT NULL,
        segundos_permanencia     INT             NOT NULL,
        zona_restringida_activa  BIT             NOT NULL CONSTRAINT DF_Configuracion_ZonaActiva DEFAULT (0),
        zona_x1                  FLOAT           NOT NULL,
        zona_y1                  FLOAT           NOT NULL,
        zona_x2                  FLOAT           NOT NULL,
        zona_y2                  FLOAT           NOT NULL,
        horario_activo           BIT             NOT NULL CONSTRAINT DF_Configuracion_HorarioActivo DEFAULT (0),
        hora_inicio              CHAR(5)         NOT NULL,
        hora_fin                 CHAR(5)         NOT NULL,
        alertas_activas          BIT             NOT NULL CONSTRAINT DF_Configuracion_AlertasActivas DEFAULT (1),
        cooldown_segundos        INT             NOT NULL,
        confianza_minima         FLOAT           NOT NULL,
        actualizado_en           DATETIME2(0)    NOT NULL CONSTRAINT DF_Configuracion_Actualizado DEFAULT (SYSDATETIME()),

        CONSTRAINT PK_Configuracion PRIMARY KEY (id),
        CONSTRAINT CK_Configuracion_Unica CHECK (id = 1),
        CONSTRAINT CK_Configuracion_LimitePersonas CHECK (limite_personas BETWEEN 1 AND 50),
        CONSTRAINT CK_Configuracion_Permanencia CHECK (segundos_permanencia BETWEEN 2 AND 3600),
        CONSTRAINT CK_Configuracion_Cooldown CHECK (cooldown_segundos BETWEEN 5 AND 3600),
        CONSTRAINT CK_Configuracion_Confianza CHECK (confianza_minima BETWEEN 0.10 AND 0.95),
        CONSTRAINT CK_Configuracion_ZonaX1 CHECK (zona_x1 BETWEEN 0 AND 1),
        CONSTRAINT CK_Configuracion_ZonaY1 CHECK (zona_y1 BETWEEN 0 AND 1),
        CONSTRAINT CK_Configuracion_ZonaX2 CHECK (zona_x2 BETWEEN 0 AND 1),
        CONSTRAINT CK_Configuracion_ZonaY2 CHECK (zona_y2 BETWEEN 0 AND 1),
        CONSTRAINT CK_Configuracion_OrdenZona CHECK (zona_x1 < zona_x2 AND zona_y1 < zona_y2),
        CONSTRAINT CK_Configuracion_HoraInicio CHECK (TRY_CONVERT(TIME(0), hora_inicio) IS NOT NULL),
        CONSTRAINT CK_Configuracion_HoraFin CHECK (TRY_CONVERT(TIME(0), hora_fin) IS NOT NULL)
    );
END;
GO

/* ------------------------- Destinatarios ------------------------- */
IF OBJECT_ID(N'dbo.Destinatarios', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Destinatarios
    (
        id          INT             IDENTITY(1,1) NOT NULL,
        nombre      NVARCHAR(100)   NOT NULL,
        correo      NVARCHAR(254)   NOT NULL,
        activo      BIT             NOT NULL CONSTRAINT DF_Destinatarios_Activo DEFAULT (1),
        creado_en   DATETIME2(0)    NOT NULL CONSTRAINT DF_Destinatarios_Creado DEFAULT (SYSDATETIME()),

        CONSTRAINT PK_Destinatarios PRIMARY KEY (id),
        CONSTRAINT UQ_Destinatarios_Correo UNIQUE (correo),
        CONSTRAINT CK_Destinatarios_Nombre CHECK (LEN(LTRIM(RTRIM(nombre))) BETWEEN 2 AND 100),
        CONSTRAINT CK_Destinatarios_Correo CHECK (correo LIKE N'%_@_%._%')
    );
END;
GO

/* ---------------------------- Alertas ---------------------------- */
IF OBJECT_ID(N'dbo.Alertas', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Alertas
    (
        id                    INT              IDENTITY(1,1) NOT NULL,
        tipo                  VARCHAR(40)      NOT NULL,
        titulo                NVARCHAR(150)    NOT NULL,
        mensaje               NVARCHAR(600)    NOT NULL,
        nivel                 VARCHAR(15)      NOT NULL,
        cantidad_personas     INT              NOT NULL CONSTRAINT DF_Alertas_Cantidad DEFAULT (0),
        limite_personas       INT              NULL,
        id_seguimiento        INT              NULL,
        confianza_promedio    FLOAT            NULL,
        fecha_hora            DATETIMEOFFSET(0) NOT NULL,
        estado                VARCHAR(15)      NOT NULL CONSTRAINT DF_Alertas_Estado DEFAULT ('PENDIENTE'),
        zona                  NVARCHAR(100)    NOT NULL,
        captura_ruta          NVARCHAR(300)    NULL,
        correo_enviado        BIT              NOT NULL CONSTRAINT DF_Alertas_CorreoEnviado DEFAULT (0),
        estado_correo         NVARCHAR(300)    NOT NULL CONSTRAINT DF_Alertas_EstadoCorreo DEFAULT (N'PENDIENTE'),
        detalle_json          NVARCHAR(MAX)    NULL,
        creado_en             DATETIME2(0)     NOT NULL CONSTRAINT DF_Alertas_Creado DEFAULT (SYSDATETIME()),

        CONSTRAINT PK_Alertas PRIMARY KEY (id),
        CONSTRAINT CK_Alertas_Tipo CHECK
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
        ),
        CONSTRAINT CK_Alertas_Nivel CHECK (nivel IN ('BAJO', 'MEDIO', 'ALTO')),
        CONSTRAINT CK_Alertas_Estado CHECK (estado IN ('PENDIENTE', 'REVISADA', 'DESCARTADA')),
        CONSTRAINT CK_Alertas_Cantidad CHECK (cantidad_personas >= 0),
        CONSTRAINT CK_Alertas_Limite CHECK (limite_personas IS NULL OR limite_personas >= 1),
        CONSTRAINT CK_Alertas_Confianza CHECK
        (
            confianza_promedio IS NULL OR confianza_promedio BETWEEN 0 AND 1
        ),
        CONSTRAINT CK_Alertas_DetalleJson CHECK
        (
            detalle_json IS NULL OR ISJSON(detalle_json) = 1
        )
    );
END;
GO

/* ---------------------------- Capturas --------------------------- */
IF OBJECT_ID(N'dbo.Capturas', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Capturas
    (
        id           INT               IDENTITY(1,1) NOT NULL,
        alerta_id    INT               NOT NULL,
        ruta         NVARCHAR(300)     NOT NULL,
        fecha_hora   DATETIMEOFFSET(0) NOT NULL,
        creado_en    DATETIME2(0)      NOT NULL CONSTRAINT DF_Capturas_Creado DEFAULT (SYSDATETIME()),

        CONSTRAINT PK_Capturas PRIMARY KEY (id),
        CONSTRAINT FK_Capturas_Alertas
            FOREIGN KEY (alerta_id) REFERENCES dbo.Alertas(id) ON DELETE CASCADE
    );
END;
GO

/* ----------------------------- Índices --------------------------- */
IF NOT EXISTS
(
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_Destinatarios_Activo'
      AND object_id = OBJECT_ID(N'dbo.Destinatarios')
)
BEGIN
    CREATE INDEX IX_Destinatarios_Activo
        ON dbo.Destinatarios (activo, id DESC)
        INCLUDE (nombre, correo, creado_en);
END;
GO

IF NOT EXISTS
(
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_Alertas_FechaHora'
      AND object_id = OBJECT_ID(N'dbo.Alertas')
)
BEGIN
    CREATE INDEX IX_Alertas_FechaHora
        ON dbo.Alertas (fecha_hora DESC, id DESC);
END;
GO

IF NOT EXISTS
(
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_Alertas_EstadoTipo'
      AND object_id = OBJECT_ID(N'dbo.Alertas')
)
BEGIN
    CREATE INDEX IX_Alertas_EstadoTipo
        ON dbo.Alertas (estado, tipo, id DESC)
        INCLUDE (titulo, nivel, cantidad_personas, fecha_hora, zona, correo_enviado);
END;
GO

IF NOT EXISTS
(
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_Capturas_Alerta'
      AND object_id = OBJECT_ID(N'dbo.Capturas')
)
BEGIN
    CREATE INDEX IX_Capturas_Alerta
        ON dbo.Capturas (alerta_id, id DESC)
        INCLUDE (ruta, fecha_hora);
END;
GO

/* ------------------------- Actualizaciones ------------------------- */
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.Configuracion') AND name = 'caida_activa')
BEGIN
    ALTER TABLE dbo.Configuracion ADD caida_activa BIT NOT NULL CONSTRAINT DF_Configuracion_CaidaActiva DEFAULT (0);
END
GO
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.Configuracion') AND name = 'tiempo_riesgo_caida')
BEGIN
    ALTER TABLE dbo.Configuracion ADD tiempo_riesgo_caida INT NOT NULL CONSTRAINT DF_Configuracion_TiempoRiesgo DEFAULT (10);
END
GO
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.Configuracion') AND name = 'fuego_activo')
BEGIN
    ALTER TABLE dbo.Configuracion ADD fuego_activo BIT NOT NULL CONSTRAINT DF_Configuracion_FuegoActivo DEFAULT (0);
END
GO

PRINT N'Tablas, restricciones e índices listos.';
GO
