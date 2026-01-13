-- Script event_tags.sql don't changed file

DECLARE @game INT;


SELECT
    -- Match
    e.matchID,

    -- Event
    e.eventRecordID,
    e.matchPeriod,
    e.eventSec,

    -- Event name
    en.eventName,
    en.subEventName,

    -- Team & Player
    t.teamName,
    CONCAT(p.Fname, ' ', p.Lname) AS playerName,

    -- Tag info
    tg.tagID,
    tg.Description

FROM EVENTTAGS et
JOIN EVENTS e
    ON et.eventRecordID = e.eventRecordID
JOIN TAGSNAME tg
    ON et.tagID = tg.tagID
JOIN EVENTSNAME en
    ON e.subEventID = en.subEventID
JOIN PLAYERS p
    ON e.playerID = p.playerID
JOIN TEAMS t
    ON e.teamID = t.teamID

WHERE e.matchID = @game

ORDER BY
    e.matchPeriod,
    e.eventSec,
    tg.tagID;
