WITH TAGS AS (
    SELECT 
        ET.eventRecordID,

        -- Flag cho các loại tag:
        MAX(CASE WHEN TN.Description = 'Goal' THEN 1 END) AS Goal,
        MAX(CASE WHEN TN.Description = 'Own goal' THEN 1 END) AS OwnGoal,
        MAX(CASE WHEN TN.Description = 'Counter attack' THEN 1 END) AS CounterAttack,

        -- Body part: lấy tagID (401,402,403) của cú dứt điểm
        MAX(CASE WHEN ET.tagID IN (401, 402, 403) THEN ET.tagID END) AS BodyPartTagID
    FROM EVENTTAGS ET
    LEFT JOIN TAGSNAME TN
        ON ET.tagID = TN.tagID
    GROUP BY ET.eventRecordID
)

SELECT
    EV.matchID,
    EV.matchPeriod,
    EV.eventSec,
    EN.eventName,
    EN.subEventName,
    EV.teamID,
    EV.posOrigX,
    EV.posOrigY,
    EV.posDestX,
    EV.posDestY,

    EV.playerID,
    P.Sname AS playerName,
    P.Prole AS playerPosition,
    P.foot AS playerStrongFoot,

    EV.teamID AS teamPossession,
    MT_home.teamID AS homeTeamId,
    MT_away.teamID AS awayTeamId,

    -- Flags
    ISNULL(T.Goal, 0) AS Goal,
    ISNULL(T.OwnGoal, 0) AS OwnGoal,
    ISNULL(T.CounterAttack, 0) AS CounterAttack,

    -----------------------------------------
    -- Body Part (KHÔNG nhân dòng)
    -----------------------------------------
    CASE
        WHEN T.BodyPartTagID = 401 THEN 'leftFoot'
        WHEN T.BodyPartTagID = 402 THEN 'rightFoot'
        WHEN T.BodyPartTagID = 403 THEN 'head/body'
        ELSE NULL
    END AS bodyPartShot,

    -- Body part code cho xG
    CASE
        WHEN T.BodyPartTagID = 403 THEN 2
        WHEN T.BodyPartTagID = 401 THEN 1
        WHEN T.BodyPartTagID = 402 THEN 3
        ELSE 0
    END AS bodyPartShotCode

FROM EVENTS AS EV

-- Event name
LEFT JOIN EVENTSNAME AS EN
    ON EV.subEventID = EN.subEventID

-- Player
LEFT JOIN PLAYERS AS P
    ON EV.playerID = P.playerID

-- Home / Away teams
LEFT JOIN MATCHTEAMS AS MT_home
    ON EV.matchID = MT_home.matchID AND MT_home.side = 'home'

LEFT JOIN MATCHTEAMS AS MT_away
    ON EV.matchID = MT_away.matchID AND MT_away.side = 'away'

-- JOIN TAGS duy nhất → không bao giờ nhân dòng
LEFT JOIN TAGS AS T
    ON EV.eventRecordID = T.eventRecordID

ORDER BY EV.matchID, EV.eventSec;