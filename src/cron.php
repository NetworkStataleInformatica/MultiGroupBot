<?php
// Delete messages scheluded for deletion

include_once "../vendor/autoload.php";
include_once "db.php";
include_once "utils.php";

$db = new Database();
$client = new \TuriBot\Client(getenv("BOT_TOKEN"), false, "https://botapi.giuseppem99.xyz/bot");

$messages = $db->query(
    "SELECT group_id, message_id FROM autodelete_messages WHERE delete_time < NOW()",
    [], true
);
if (!$messages) {
    die();
}

$db->query("DELETE FROM autodelete_messages WHERE delete_time < NOW()");
foreach ($messages as $message) {
    debug_to_console($message);
    $res = $client->deleteMessage($message["group_id"], $message["message_id"]);
    var_dump($res);
}
