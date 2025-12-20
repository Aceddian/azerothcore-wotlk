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
-- Delete all content of "game_event_creature" table.
DELETE FROM `game_event_creature`;
-- Delete all content of "game_event_creature_quest" table.
DELETE FROM `game_event_creature_quest`;
-- Delete all content of "game_event_creature" table.
DELETE FROM `game_event_gameobject`;
-- Delete all content of "game_event_creature_quest" table.
DELETE FROM `game_event_gameobject_quest`;
-- Delete all content of "game_event_npcflag" table.
DELETE FROM `game_event_npcflag`;
-- Delete all content of "game_event_npcflag_vendor" table.
DELETE FROM `game_event_npc_vendor`;
-- Delete all content of "game_event_npcflag_vendor" table.
DELETE FROM `game_event_pool`;
-- Delete all content of "pool_creature" table.
DELETE FROM `pool_creature`;
-- Delete all content of "pool_gameobject" table.
DELETE FROM `pool_gameobject`;
-- Delete all content of "pool_pool" table.
DELETE FROM `pool_pool`;
-- Delete all content of "pool_quest" table.
DELETE FROM `pool_quest`;
-- Delete all content of "pool_template" table.
DELETE FROM `pool_template`;
-- Delete all content of "smart_scripts" table.
DELETE FROM `smart_scripts`;
DELETE FROM `creature_addon`;
DELETE FROM `creature_movement_override`;
DELETE FROM `gameobject_addon`;
DELETE FROM `linked_respawn`;
DELETE FROM `creature_queststarter`;
DELETE FROM `creature_questender`;
DELETE FROM `gameobject_queststarter`;
DELETE FROM `gameobject_questender`;
DELETE FROM `npc_vendor`;

-- DELETE FROM ``;

