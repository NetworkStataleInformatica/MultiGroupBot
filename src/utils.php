<?php

function starts_with($haystack, $needle): bool {
    $length = strlen($needle);
    return substr($haystack, 0, $length) === $needle;
}

function debug_to_console($data) {  // TODO: Remove this
    file_put_contents('php://stderr', print_r($data, TRUE));
}

function schedule_deletion($msg): void {
    global $db;
    $db->query("INSERT INTO autodelete_messages(group_id, message_id, delete_time) 
    VALUES(:gid, :mid, NOW() + INTERVAL '5 MINUTES')", ["gid" => $msg->chat->id, "mid" => $msg->message_id]);
}
