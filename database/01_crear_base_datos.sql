/* ============================================================
   SecurityAPPCR - 01_crear_base_datos.sql
   Crea la base de datos si todavía no existe.
   Ejecutar con una cuenta que pueda crear bases de datos.
   ============================================================ */

USE [master];
GO

IF DB_ID(N'BD-SecurityAPPCR') IS NULL
BEGIN
    PRINT N'Creando base de datos [BD-SecurityAPPCR]...';
    CREATE DATABASE [BD-SecurityAPPCR];
END
ELSE
BEGIN
    PRINT N'La base de datos [BD-SecurityAPPCR] ya existe.';
END;
GO

ALTER DATABASE [BD-SecurityAPPCR] SET RECOVERY SIMPLE;
GO

USE [BD-SecurityAPPCR];
GO

PRINT N'Base de datos lista.';
GO
