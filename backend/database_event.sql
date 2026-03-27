-- =============================================
-- Baza danych dla trybu Dyskoteka (Event)
-- =============================================

-- Utworzenie bazy danych (jeśli nie istnieje)
-- CREATE DATABASE RadioGorkaEvent;
-- GO

-- USE RadioGorkaEvent;
-- GO

-- =============================================
-- Tabela eventów
-- =============================================
CREATE TABLE events (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL DEFAULT 'Dyskoteka',
    playlist_id NVARCHAR(50) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);

-- =============================================
-- Tabela tracks dla eventów (dyskoteka)
-- =============================================
CREATE TABLE tracks_event (
    id INT IDENTITY(1,1) PRIMARY KEY,
    videoID NVARCHAR(20) NOT NULL UNIQUE,
    event_id INT NOT NULL DEFAULT 1,
    status NVARCHAR(20) NOT NULL DEFAULT 'check',  -- 'check', 'accepted', 'declined'
    reason NVARCHAR(500) NULL,
    added_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

-- =============================================
-- Domyślny event - Dyskoteka
-- =============================================
INSERT INTO events (name, playlist_id, is_active)
VALUES ('Dyskoteka', 'PLJhSTAItRjxLS10EQ7dNbeUOPcnIW2m6r', 1);

-- =============================================
-- Procedury składowane dla tracks_event
-- =============================================
CREATE PROCEDURE add_music_event
    @videoID NVARCHAR(20),
    @event_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Sprawdź czy utwór już istnieje
    IF EXISTS (SELECT 1 FROM tracks_event WHERE videoID = @videoID AND event_id = @event_id)
    BEGIN
        -- Sprawdź status istniejącego utworu
        SELECT 
            CASE 
                WHEN status = 'check' THEN 'check'
                WHEN status = 'accepted' THEN 'accepted'
                WHEN status = 'declined' THEN 'declined'
            END AS result,
            CASE 
                WHEN status = 'check' THEN 'Utwór czeka na weryfikację'
                WHEN status = 'accepted' THEN 'Utwór został już dodany'
                WHEN status = 'declined' THEN 'Utwór został odrzucony'
            END AS message
        FROM tracks_event 
        WHERE videoID = @videoID AND event_id = @event_id;
        RETURN;
    END
    
    -- Dodaj nowy utwór
    INSERT INTO tracks_event (videoID, event_id, status)
    VALUES (@videoID, @event_id, 'check');
    
    SELECT 'inserted' AS result, 'Utwór dodany do kolejki' AS message;
END
GO

-- =============================================
-- Widok do pobierania utworów do weryfikacji
-- =============================================
CREATE PROCEDURE get_pending_tracks_event
    @event_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT * FROM tracks_event 
    WHERE event_id = @event_id AND status = 'check'
    ORDER BY added_at DESC;
END
GO

-- =============================================
-- Procedura akceptacji utworu
-- =============================================
CREATE PROCEDURE accept_track_event
    @videoID NVARCHAR(20),
    @event_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE tracks_event 
    SET status = 'accepted' 
    WHERE videoID = @videoID AND event_id = @event_id;
END
GO

-- =============================================
-- Procedura odrzucenia utworu
-- =============================================
CREATE PROCEDURE decline_track_event
    @videoID NVARCHAR(20),
    @reason NVARCHAR(500),
    @event_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE tracks_event 
    SET status = 'declined', reason = @reason
    WHERE videoID = @videoID AND event_id = @event_id;
END
GO
