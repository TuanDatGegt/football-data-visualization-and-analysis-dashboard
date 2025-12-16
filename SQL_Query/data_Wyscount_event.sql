SELECT 
    E.eventRecordID,
    E.matchID,
    E.matchPeriod,
    E.eventSec,
    EN.eventName,
    EN.subEventName,
    E.teamID,
    E.posOrigX,
    E.posOrigY,
    E.posDestX,
    E.posDestY,
    E.playerID,
    P.Sname,
    P.pRole,
    P.foot,
    home.teamID AS homeTeamID,
    away.teamID AS awayTeamID,
    JSON_QUERY(
        '[' + STRING_AGG(CAST(T.tagID AS VARCHAR(10)), ',') + ']'
    ) AS tagIDs
FROM EVENTS AS E
JOIN EVENTSNAME AS EN 
    ON E.subEventID = EN.subEventID
JOIN PLAYERS AS P
    ON P.playerID = E.playerID
JOIN MATCHTEAMS AS home
    ON E.matchID = home.matchID AND home.side = 'home'
JOIN MATCHTEAMS AS away
    ON E.matchID = away.matchID AND away.side = 'away'
LEFT JOIN (
    SELECT DISTINCT eventRecordID, tagID
    FROM EVENTTAGS
) AS T
    ON E.eventRecordID = T.eventRecordID
GROUP BY
    E.eventRecordID,
    E.matchID,
    E.matchPeriod,
    E.eventSec,
    EN.eventName,
    EN.subEventName,
    E.teamID,
    E.posOrigX,
    E.posOrigY,
    E.posDestX,
    E.posDestY,
    E.playerID,
    P.Sname,
    P.pRole,
    P.foot,
    home.teamID,
    away.teamID
ORDER BY 
    E.matchID, E.eventSec;
