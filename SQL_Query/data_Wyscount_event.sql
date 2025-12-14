-- This is version 2 for query
SELECT 
    E.matchID,
	E.matchPeriod,
	E.eventSec,
	EN.eventName,
    E.teamID,
    E.playerID,
	EN.subEventName,
    E.posOrigX,
    E.posOrigY,
    E.posDestX,
    E.posDestY,
	TN.Description
    -- Bạn sẽ cần join thêm bảng TAGSNAME ở bước sau để lấy mô tả của tagID
FROM 
    EVENTS E
JOIN 
    EVENTSNAME EN 
    ON E.subEventID = EN.subEventID
LEFT JOIN 
    EVENTTAGS ET 
    ON E.eventRecordID = ET.eventRecordID
LEFT JOIN
	TAGSNAME AS TN
	ON TN.tagID = ET.tagID;