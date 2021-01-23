<?php

class Database {
    private PDO $dbh;

    public function __construct() {
        $this->dbh = new PDO('pgsql:host=postgres;dbname=networkstatale', 'networkstatale', 'tarallodomina');
    }

    public function query($statement, $params=[], $fetchall=false): array {
        $q = $this->dbh->prepare($statement);
        foreach ($params as $key => $value)
            if (gettype($value) === "boolean")
                $q->bindValue($key, $value, \PDO::PARAM_BOOL);
            else
                $q->bindValue($key, $value);
        $q->execute();
        return $fetchall ? $q->fetchAll() : $q->fetch();
    }
}
