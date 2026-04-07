$(function(){
    
    $('.js-fancybox').fancybox();
    
    $('.mailmask').inputmask({
        alias:'email'
    });
    
    $('.js-hover').on('click', function(event) {
        event.preventDefault();
        var hover_link = $(this).attr('href');
        $(this).parent('.city-list').find(hover_link).toggleClass('city-hide');
    });
    
    /*$('.result-tabs').on('click', '.js-result-item:not(.active)', function() {
        $(this)
          .addClass('active')
          .siblings()
          .removeClass('active')
          .closest('div.result-block')
          .find('div.result-tabs-content')
          .removeClass('active')
          .eq($(this).index())
          .addClass('active');
    });*/
    
    $('.js-open-example').on('click', function(){
        $(this).text($(this).text() == "Скрыть работы" ? "Показать больше" : "Скрыть работы");
        $(this).parent('.example-block').toggleClass('active');
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
    
    //список toggle
    $('.js-faq-item').on('click', function() {
        $(this).toggleClass('active');
    });
    
    //список toggle
    $(".js-toggle-item").on("click", function() {
        $(this).toggleClass("active")
    });
    
    //forms
    var dataDescription = "";
    
    $(document).on('click', '.js-form-popup', function(){
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
    
    if ($('.swiper-result').length > 0) {
        //слайдер
        var mySwiper1 = new Swiper ('.swiper-result', {
            direction: 'horizontal',
            loop: false,
            slidesPerGroup: 1,
            grabCursor: true,
            pagination: {
                el: '.swiper-pagination-result',
                clickable: true
            },
            navigation: {
                prevEl: '.swiper-button-prev',
                nextEl: '.swiper-button-next'
            },
            breakpoints: {
                980: {
                    slidesPerView: 2,
                    spaceBetween: 60
                },
                300: {
                    slidesPerView: 1,
                    spaceBetween: 0
                },
            }
        });
    }

    if ($('.swiper-about').length > 0) {
        //слайдер
        var mySwiper1 = new Swiper ('.swiper-about', {
            direction: 'horizontal',
            loop: false,
            slidesPerView: 1,
            spaceBetween: 20,
            grabCursor: true,
            autoplay: {
                delay: 8000,
                stopOnLastSlide: false,
                
            },
            pagination: {
                el: '.swiper-pagination-about',
            },
        });
    } 
    
    /*if ($('.swiper-example').length > 0) {
        //слайдер
        var mySwiper2 = new Swiper ('.swiper-example', {
            direction: 'horizontal',
            loop: false,
            slidesPerView: 2, //слайдов для показа
            slidesPerGroup: 1, //кол-во пролистываемых
            spaceBetween: 30, //отступ
            centeredSlides: true, //центрирование
            pagination: {
                el: '.swiper-pagination-example',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
        });
    } */
    


    
    //parsing

    //инициализация плагина для списка городов
	$('.js-chosen').chosen({
		no_results_text: 'Совпадений не найдено',
		placeholder_text_single: 'Выберите город'
	});
	
	//выбор поисковой системы
    $('.select_engine').on('change', function () {
        var search = $('.select_engine option:selected').data('search');
        $('.js-city-y').addClass('none');
        $('.js-city-g').addClass('none');
        $('.' + search).removeClass('none').children('.chosen-container').attr('style', '');
    });
    
    //прелоадер
    $(".parser-submit").on("click", function() {
        $('body').removeClass('loaded');
    });

    //подсветка идентичных url
    $(".answer-table .table-body td").hover(function () {
        var urlHover = $(this).find(".js-site-link").text();
        $(".answer-table .js-site-link").each(function (index, value) {
            if(urlHover === $(this).text()) {
                $(this).closest("tr").addClass("td__identical");
            }
        });
    }, 
    function () {
        $(".answer-table .js-site-link").each(function (index, value) {
            $(this).closest("tr").removeClass("td__identical");
        });
    });
    
    //подсветка агрегаторов
    $(".button-lighting-agregator").on("click", function(event) {
        event.preventDefault();
        var agregator = ['2gis.ru', 'zoon.ru', 'abc.ru', 'AliExpress.ru', 'activizm.ru', 'aport.ru', 'Avito.ru', 'berito.ru', 'beru.ru', 'bigum.ru', 'blizko.ru', 'cdek.market', 'centromall.ru', 'cosmeticpoint.ru', 'cleaning.firmika.ru', 'e-katalog.ru', 'gde-nedorogo.ru', 'goods.ru', 'joom.com', 'kelkoo.ru', 'lamoda.ru', 'LeroyMerlin.ru', 'magazilla.ru', 'marketguru.ru', 'marketmio.ru', 'market.yandex.ru', 'pokupki.market.yandex.ru', 'millionpodarkov.ru', 'mixmarket.biz', 'mixprice.ru', 'mobigru.ru', 'mobisoto.ru', 'nadavi.ru', 'nbprice.ru', 'OZON.ru', 'oknazavr.ru', 'profi.ru', 'pandao.ru', 'podarki.ru', 'poisk-podbor.ru', 'pokupaj.ru', 'price.ru', 'priceok.ru', 'pulscen.ru', 'regmarkets.ru', 'robo.market', 'saleplus.ru', 'sotoguide.ru', 'sravni.com', 'spravker', 'stolica.ru', 'techGuru.ru', 'technoportal.ru', 'televizor-x.ru', 'tiu.ru', 'topadvert.ru', 'vseinstrumenti.ru', 'WildBerries.ru', 'ymall.ru', 'yandex.ru', 'uslugio.com'];
        $.each(agregator, function(ind, val){
            $('.js-site-link:contains('+val+')').closest('tr').toggleClass("td__agregator");
        });
    });
    
    //подсветка главных страниц
    $(".button-lighting-main").on("click", function(event) {
        event.preventDefault();
        var mainPage = '1';
        $('.js-site-link').each(function(){
            if ($(this).attr('mainpage')==1) {
                $(this).closest('tr').toggleClass('td__main');
            }
        });
    });
    
    //подсветка своих url
    $(".btn_url_on").on("click", function(event) {
        event.preventDefault();
        var myUrl = $('.list_url').val().split('\n');
        $.each(myUrl, function(ind, val){
            $('.js-site-link:contains('+val+')').closest('tr').addClass("td__url");
        });
        $.fancybox.close();
    });
    //снятие подсветки своих url
    $(".btn_url_off").on("click", function(event) {
        event.preventDefault();
        var myUrl = $('.list_url').val().split('\n');
        $.each(myUrl, function(ind, val){
            $('.js-site-link:contains('+val+')').closest('tr').removeClass("td__url");
        });
        $.fancybox.close();
    });
    
    //изменить кол-во столбцов
    $(".js-column-format").on("click", function(){
        
        $(".js-column-format").each(function(index) {
            $(this).removeClass('active');
        });
        
        $("#answer").removeClass("col-3");
        $("#answer").removeClass("col-4");
        $("#answer").removeClass("col-5");
        
        $(this).toggleClass("active");
        
        $(".js-column-format").each(function(index) {
            if ($(this).hasClass('active')) {
                $("#answer").addClass($(this).data("view"));
            }
        });
    });

    //копируем в буфер обмена
    var copytext = function (text) {
        var tmp = $('<textarea>');
        $("body").append(tmp);
        tmp.val(text).select();
        document.execCommand("copy");
        tmp.remove();
    }
        
    $('.clipboard').off('click');
    $('.clipboard').on('click', function () {
        var urls = [];
        $(this).closest('table').find('.js-site-link').each(function () {
            urls.push($(this).text());
        });
        //console.log(urls);
        if (urls.length > 0) copytext(urls.join('\n'));
    });
    
/*
    $('.clipboard').on('click', function() {
        var clipId = $(this).data('clip');
        coppuBlock(clipId);
    })
    
    function coppuBlock(element) {
        var tmp = $('<textarea>');
        $("body").append(tmp);
        tmp.val($(element).text()).select();
        
        if($(element).text()){
            document.execCommand("copy");
            setGoal('TOOLS_COPU');
            tmp.remove();
        }
    }
*/
/*
    $('.clipboard').click(function() {
        var urls = '';
        var id = $(this).attr('data-clip');
        var el = $(id); 
        urls = $(id).html();
        copytext(el);
    });
    function copytext(el) {
        var tmp = $('<textarea>');
        $("body").append(tmp);
        tmp.val($(el).text()).select();
        document.execCommand("copy");
        tmp.remove();
    } 
*/
    
    //analBot
    
    //табы
    $('.method-tabs').on('click', '.js-method-item:not(.active)', function() {
        $(this)
          .addClass('active')
          .siblings()
          .removeClass('active')
          .closest('div.method-block')
          .find('.method-content')
          .removeClass('js-method-parsing')
          .attr("disabled", true)
          .eq($(this).index())
          .addClass('js-method-parsing')
          .attr("disabled", false);
    });
    
    $('.js-word-del').on('click', function(event) {
        event.preventDefault();
        $('.word_del').slideToggle(300);
    });
    
    //тест отправки данных из анал бот
    /*$(".analbot-form").submit(function(event) {
        event.preventDefault();
        $.ajax ({
            url: 'mail.php',
            type: 'POST',
            dataType: "json",
            data: $('.analbot-form').serialize(),
        });
    });*/

});

//progress-bar
$(window).on('load', function () {
    $('body').addClass('loaded_hiding');
    window.setTimeout(function () {
      $('body').addClass('loaded');
      $('body').removeClass('loaded_hiding');
    }, 500);
});