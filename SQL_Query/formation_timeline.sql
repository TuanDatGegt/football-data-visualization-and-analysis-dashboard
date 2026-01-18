-- Script information_timeline.sql don't changed file

DECLARE @game INT;

SELECT
    -- Match
    f.matchID,

    -- Team
    f.teamID,
    t.teamName,

    -- Player
    f.playerID,
    p.Sname AS playerName,
    p.Prole AS playerRole,

    -- Lineup & substitution
    f.lineup,
    f.substituteIn,
    f.substituteOut,

    -- Time on pitch
    f.minuteStart,
    f.minuteEnd,
    f.minutePlayed

FROM FORMATIONS f
JOIN PLAYERS p
    ON f.playerID = p.playerID
JOIN TEAMS t
    ON f.teamID = t.teamID

WHERE f.matchID = @game

ORDER BY
    t.teamName,
    f.minuteStart,
    playerName;

