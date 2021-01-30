<?php
include_once $_SERVER["DOCUMENT_ROOT"] . "/utils.php";

global $client, $db;
global $update, $message, $command, $sender, $chat;

if (!$command || !in_array($command->command, ["ban", "unban", "mute", "unmute"])) {
    return;
}

$db_sender = $db->query("SELECT permissions_level FROM users WHERE user_id=:id", ["id" => $sender->id]);
if ($db_sender["permissions_level"] < 1) {
    return;
}
$action = $command->command;
if (!in_array($action, ["ban", "unban", "mute", "unmute"])) {
    return;
}

if (isset($message->reply_to_message)) {
    $target = $message->reply_to_message->from->id;
} else if (count($command->args) > 0) {
    $target = $command->args[0];
} else {
    return;
}

if ($action == "ban") {
    $db->query("UPDATE users SET banned=true WHERE user_id=:id", ["id" => $target]);
} else if ($action == "unban") {
    $db->query("UPDATE users SET banned=false WHERE user_id=:id", ["id" => $target]);
}

$groups = $db->query("SELECT group_id AS id FROM users_groups WHERE user_id=:id", ["id" => $target], true);
foreach ($groups as $group) {
    if ($action == "ban") {
        $client->kickChatMember(
            $group["id"],
            $target,
        );

    } else if ($action == "mute") {
        $client->restrictChatMember(
            $group["id"],
            $target,
            [
                "can_send_messages" => false,
                "can_invite_users" => false,
            ]
        );
    } else if ($action == "unban" || $action == "unmute") {
        $client->unbanChatMember(
            $group["id"],
            $target,
            true,
        );
        $client->restrictChatMember(
            $group["id"],
            $target,
            [
                "can_send_messages" => true,
                "can_send_media_messages" => true,
                "can_send_polls" => true,
                "can_send_other_messages" => true,
                "can_add_web_page_previews" => true,
                "can_invite_users" => true,
            ]
        );
    }
}

$text = null;
if ($action == "ban") {
    $text = "<b>Utente #$target silurato</b>.";
} else if ($action == "mute") {
    $text = "<b>Utente #$target mutato</b>.";
} else if ($action == "unban") {
    $text = "<b>Utente #$target sbannato</b>.";
} else if ($action == "unmute") {
    $text = "<b>Utente #$target smutato</b>.";
}
$client->sendMessage(
    $chat->id, $text, "html"
);

die();
