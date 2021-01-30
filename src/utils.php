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

class Command {
    public string $command;
    public array $args;

    public function __construct(string $command, array $args) {
        $this->command = $command;
        $this->args = $args;
    }
}

function parse_command($msg) {
    if (!isset($msg) || !isset($msg->text) || !starts_with($msg->text, "/")) {
        return false;
    }
    $cmd = preg_match("/^\/(\w+)(?:@\w+[Bb][Oo][Tt])?/", $msg->text, $re);
    if (!$cmd || $cmd == 0) {
        return false;
    }
    $command = $re[1];
    $args = array();
    $args_str = substr($msg->text, strlen($re[0]));
    if (strlen($args_str) > 1) {
        $args = explode(" ", substr($args_str, 1));
    }
    return new Command($command, $args);
}
