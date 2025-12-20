-- This is to remove extra information from other things, creatures, objects, waypoints, etc.
-- Delete all content of "creature_formations" table.
DELETE FROM `creature_formations`;
-- Delete all content of "conditions" table.
DELETE FROM `conditions`;
-- Delete all content of "event_scripts" table.
DELETE FROM `event_scripts`;
-- Delete all content of "script_waypoint" table.
DELETE FROM `script_waypoint`;
-- Delete all content of "waypoints" table.
DELETE FROM `waypoints`;
-- Delete all content of "waypoint_data" table.
DELETE FROM `waypoint_data`;
-- Delete all content of "waypoint_scripts" table.
DELETE FROM `waypoint_scripts`;
-- Removes any SmartAI or C++ scripts from the creatures.
UPDATE `creature_template` SET `AIName` = "", `ScriptName` = "";
