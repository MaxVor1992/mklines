$(function(){
    
    $('.js-fancybox').fancybox();
    
    $('.mailmask').inputmask({
        alias:'email'
    });
    
    $('.menu').on('click', function(){
        $('.main-menu').toggleClass('main-menu__deactive');
    });
    
    ymaps.ready(function(){
        var geolocation = ymaps.geolocation;
        $('#tow').html(geolocation.city);
    });
    
    $('.result-tabs').on('click', '.js-result-item:not(.active)', function() {
        $(this)
          .addClass('active')
          .siblings()
          .removeClass('active')
          .closest('div.result-block')
          .find('div.result-tabs-content')
          .removeClass('active')
          .eq($(this).index())
          .addClass('active');
    });
    
    $('.tariff-tabs').on('click', '.js-tariff-item:not(.active)', function() {
        $(this)
          .addClass('active')
          .siblings()
          .removeClass('active')
          .closest('div.tariff-block')
          .find('div.tariff-tabs-content')
          .removeClass('active')
          .eq($(this).index())
          .addClass('active');
    });
    
    $('.js-faq-item').on('click', function() {
        $(this).toggleClass('active');
    });
    
    //forms
    var dataDescription = "";
    
    $(document).on('click', '.js-form-popup', function(){
        dataDescription = $(this).attr('data-description');
        $('input[name=check]').val(dataDescription);
    });
    
    $(document).on('click', '.audit-submit', function(){
        dataDescription = $(this).attr('data-description');
        $('input[name=check]').val(dataDescription);
    });
    
    $(document).on('click', '.cosmos-submit', function(){
        dataDescription = $(this).attr('data-description');
        $('input[name=check]').val(dataDescription);
    });
    
    
    //forms
    $(".form-popup").submit(function(event) {
        event.preventDefault();
        $.ajax ({
            url: 'mail.php',
            type: 'POST',
            dataType: "json",
            data: $('.form-popup').serialize(),
            success: function(data) {
                if(data['status'] === true) {
                    $(".form-popup").trigger('reset');
                } else if (data['status'] === false) {
                    window.location.replace("https://yandex.ru/");
                }
            },
        });
    });
    
    $(".form-audit").submit(function(event) {
        event.preventDefault();
        $.ajax ({
            url: 'mail.php',
            type: 'POST',
            dataType: "json",
            data: $('.form-audit').serialize(),
            success: function(data) {
                if(data['status'] === true) {
                    $(".form-audit").trigger('reset');
                } else if (data['status'] === false) {
                    window.location.replace("https://yandex.ru/");
                }
            },
        });
    });  
    
    $(".form-cosmos").submit(function(event) {
        event.preventDefault();
        $.ajax ({
            url: 'mail.php',
            type: 'POST',
            dataType: "json",
            data: $('.form-cosmos').serialize(),
            success: function(data) {
                if(data['status'] === true) {
                    $(".form-cosmos").trigger('reset');
                } else if (data['status'] === false) {
                    window.location.replace("https://yandex.ru/");
                }
            },
        });
    });
    
});