<?php
global $client, $db;
global $update, $message, $chat, $sender;

if (!isset($message->reply_to_message) || !isset($message->text)) {
    return;
}
if ($message->text != "+" && $message->text != "^") {
    return;
}
$db_sender = $db->query("SELECT permissions_level FROM users WHERE user_id=:id", ["id" => $sender->id]);
if ($db_sender["permissions_level"] < 1) {  // if the user is not an admin
    return;
}

$target = $message->reply_to_message->from;
$db->query("UPDATE users SET reputation=reputation+1 WHERE user_id=:id", ["id" => $target->id]);

$new_rep = $db->query("SELECT reputation FROM users WHERE user_id=:id", ["id" => $target->id]);

$client->sendMessage(
    $chat->id,
    "➕ <b>Reputazione di " . $target->first_name . " aumentata</b> [" . $new_rep["reputation"] . "]",
    "html",
);
die();

