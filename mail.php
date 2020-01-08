<?php

header('Content-type: text/html; charset=utf-8');

if($_POST["trap"]) {
    
    echo json_encode([
        "status" => false
    ]);
    
    exit();

} else if ($_POST["email"]) {
    
    $name = $_POST["name"];
    $mail = $_POST["email"];
    $text = $_POST["text"];
    $check = $_POST["check"];
    
    $mail = array (
        'to' => "autozona54@mail.ru",
        'subject' => "Заявка с сайта MKlines",
        'message' => "<html><body><p>Имя: ".$name."</p><p>Почта: ".$mail."</p><p>Услуга: ".$check."</p><p>Сообщение: ".$text."</p></body></html>",
        'headers' => "MIME-Version: 1.0\r\n"."Content-type: text/html; charset=utf-8\r\n"."From: Заявка с сайта <MKlines>\r\n"
    );
    
    mail($mail['to'], $mail['subject'], $mail['message'], iconv ('utf-8', 'windows-1251', $mail['headers']));
    
    echo json_encode([
        "status" => true
    ]);

    
}; /*else {
    
    echo json_encode([
        "status" => false
    ]);
    
};*/


?>
