-- Script event_tracking.sql don't changed file

DECLARE @game INT;

SELECT
    -- Match info
    m.matchID,
    m.labelMatch,
    m.matchDate,
    m.venueName,

    -- Event timing
    e.eventRecordID,
    e.matchPeriod,
    e.eventSec,

    -- Event type
    en.eventName,
    en.subEventName,

    -- Team
    t.teamID,
    t.teamName,
    mt.side,

    -- Player
    p.playerID,
    p.Sname AS playerName,
    p.Prole AS playerPosition,

    -- Spatial data (tracking core)
    e.posOrigX,
    e.posOrigY,
    e.posDestX,
    e.posDestY

FROM EVENTS e
JOIN MATCHES m
    ON e.matchID = m.matchID
JOIN EVENTSNAME en
    ON e.subEventID = en.subEventID
JOIN PLAYERS p
    ON e.playerID = p.playerID
JOIN TEAMS t
    ON e.teamID = t.teamID
JOIN MATCHTEAMS mt
    ON m.matchID = mt.matchID
   AND t.teamID = mt.teamID

-- 🔑 LỌC ĐÚNG 1 TRẬN
WHERE e.matchID = @game

ORDER BY
    e.matchPeriod,
    e.eventSec;

