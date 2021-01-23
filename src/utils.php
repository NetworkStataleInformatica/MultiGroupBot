<?php

function starts_with($haystack, $needle): bool {
    $length = strlen($needle);
    return substr($haystack, 0, $length) === $needle;
}

function debug_to_console($data) {  // TODO: Remove this
    file_put_contents('php://stderr', print_r($data, TRUE));
}
