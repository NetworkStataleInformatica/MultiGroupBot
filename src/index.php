<?php
include_once "../vendor/autoload.php";

if (!isset($_GET["token"])) {
    http_response_code(403);
    echo "<h1>403 Forbidden</h1>";
    die();
}

use TuriBot\Client;

$client = new Client($_GET["token"], true, "https://botapi.giuseppem99.xyz/bot");
$update = $client->getUpdate();

if (!isset($update->message)) {
    die();
}
$message = $update->message;
$sender = $message->from;
$chat = $message->chat;

include_once "db.php";
$db = new Database();

$g_exists = $db->query("SELECT 1 FROM groups WHERE group_id=:gid;", ["gid" => $update->message->chat->id]);
if (!$g_exists)
    die();

$db->query(
    "INSERT INTO users(user_id, first_name, last_name, username, last_seen) 
    VALUES(:id, :fn, :ln, :un, NOW())
    ON CONFLICT(user_id) DO UPDATE SET first_name=:fn, last_name=:ln, username=:un, last_seen=NOW()",
    ["id" => $sender->id, "fn" => $sender->first_name, "ln" => $sender->last_name, "un" => $sender->username]
);
$db->query(
    "INSERT INTO users_groups(user_id, group_id, last_seen) VALUES(:id, :gid, NOW())
    ON CONFLICT(user_id, group_id) DO UPDATE SET user_id=:id, group_id=:gid",
    ["id" => $sender->id, "gid" => $chat->id]
);

include_once "modules/reputation.php";
