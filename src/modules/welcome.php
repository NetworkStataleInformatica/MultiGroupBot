<?php
include_once $_SERVER["DOCUMENT_ROOT"] . "/utils.php";

global $client, $db;
global $message, $chat, $update;

if (!isset($message->new_chat_members)) {
    return;
}

$db_group = $db->query("SELECT 1 AS exists, welcome_message FROM groups WHERE group_id=:gid",
    ["gid" => $chat->id]);

if (!$db_group || !array_key_exists("exists", $db_group)) {
    return;
}

$client->getMe();  // Dumb fix to an issue in the TuriBot library

$res = $client->sendMessage(
    $chat->id,
    $db_group["welcome_message"],
    "html"
);
schedule_deletion($res->result);
