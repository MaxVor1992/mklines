$(function() {
    // Инициализация fancybox
    $(".js-fancybox").fancybox();
    
    // Маска для email
    $(".mailmask").inputmask({alias: "email"});
    
    // Переключение городов
    $(".js-hover").on("click", function(e) {
        e.preventDefault();
        var t = $(this).attr("href");
        $(this).parent(".city-list").find(t).toggleClass("city-hide");
    });
    
    // Показать больше работ
    $(".js-open-example").on("click", function() {
        $(this).text("Скрыть работы" == $(this).text() ? "Показать больше" : "Скрыть работы");
        $(this).parent(".example-block").toggleClass("active");
    });
    
    // Переключение тарифов
    $(".tariff-tabs").on("click", ".js-tariff-item:not(.active)", function() {
        $(this).addClass("active").siblings().removeClass("active")
            .closest("div.tariff-block").find("div.tariff-tabs-content")
            .removeClass("active").eq($(this).index()).addClass("active");
    });
    
    // FAQ accordion
    $(".js-faq-item").on("click", function() {
        $(this).toggleClass("active");
    });
    
    // Toggle items
    $(".js-toggle-item").on("click", function() {
        $(this).toggleClass("active");
    });
    
    // Form popup
    var e = "";
    $(document).on("click", ".js-form-popup", function() {
        e = $(this).attr("data-description");
        $("input[name=check]").val(e);
    });
    
    $(document).on("click", ".cosmos-submit", function() {
        e = $(this).attr("data-description");
        $("input[name=check]").val(e);
    });
    
    $(".form-popup").submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: "mail.php",
            type: "POST",
            dataType: "json",
            data: $(".form-popup").serialize(),
            success: function(e) {
                !0 === e.status ? $(".form-popup").trigger("reset") : !1 === e.status && window.location.replace("https://yandex.ru/")
            }
        });
    });
    
    $(".form-cosmos").submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: "mail.php",
            type: "POST",
            dataType: "json",
            data: $(".form-cosmos").serialize(),
            success: function(e) {
                !0 === e.status ? $(".form-cosmos").trigger("reset") : !1 === e.status && window.location.replace("https://yandex.ru/")
            }
        });
    });
    
    // Swiper результат
    if (0 < $(".swiper-result").length) {
        new Swiper(".swiper-result", {
            direction: "horizontal",
            loop: !1,
            slidesPerGroup: 1,
            grabCursor: !0,
            pagination: {el: ".swiper-pagination-result", clickable: !0},
            navigation: {prevEl: ".swiper-button-prev", nextEl: ".swiper-button-next"},
            breakpoints: {
                980: {slidesPerView: 2, spaceBetween: 60},
                300: {slidesPerView: 1, spaceBetween: 0}
            }
        });
    }
    
    // Swiper about
    if (0 < $(".swiper-about").length) {
        new Swiper(".swiper-about", {
            direction: "horizontal",
            loop: !1,
            slidesPerView: 1,
            spaceBetween: 20,
            grabCursor: !0,
            autoplay: {delay: 8e3, stopOnLastSlide: !1},
            pagination: {el: ".swiper-pagination-about"}
        });
    }
    
    // Chosen select
    $(".js-chosen").chosen({
        no_results_text: "Совпадений не найдено",
        placeholder_text_single: "Выберите город"
    });
    
    // Смена поисковой системы
    $(".select_engine").on("change", function() {
        var e = $(".select_engine option:selected").data("search");
        $(".js-city-y").addClass("none");
        $(".js-city-g").addClass("none");
        $("." + e).removeClass("none").children(".chosen-container").attr("style", "");
    });
    
    // Пункт 7: Индикация прогресса при парсинге
    $(".parser-submit").on("click", function() {
        $("body").removeClass("loaded");
        $(".progress-text").show();
    });
    
    // Подсветка одинаковых URL
    $(".answer-table .table-body td").hover(
        function() {
            var i = $(this).find(".js-site-link").text();
            $(".answer-table .js-site-link").each(function(e, t) {
                i === $(this).text() && $(this).closest("tr").addClass("td__identical");
            });
        },
        function() {
            $(".answer-table .js-site-link").each(function(e, t) {
                $(this).closest("tr").removeClass("td__identical");
            });
        }
    );
    
    // Подсветка агрегаторов
    $(".button-lighting-agregator").on("click", function(e) {
        e.preventDefault();
        $.each([
            "2gis.ru", "zoon.ru", "abc.ru", "AliExpress.ru", "activizm.ru", "aport.ru",
            "Avito.ru", "berito.ru", "beru.ru", "bigum.ru", "blizko.ru", "cdek.market",
            "centromall.ru", "cosmeticpoint.ru", "cleaning.firmika.ru", "e-katalog.ru",
            "gde-nedorogo.ru", "goods.ru", "joom.com", "kelkoo.ru", "lamoda.ru",
            "LeroyMerlin.ru", "magazilla.ru", "marketguru.ru", "marketmio.ru",
            "market.yandex.ru", "pokupki.market.yandex.ru", "millionpodarkov.ru",
            "mixmarket.biz", "mixprice.ru", "mobigru.ru", "mobisoto.ru", "nadavi.ru",
            "nbprice.ru", "OZON.ru", "oknazavr.ru", "profi.ru", "pandao.ru", "podarki.ru",
            "poisk-podbor.ru", "pokupaj.ru", "price.ru", "priceok.ru", "pulscen.ru",
            "regmarkets.ru", "robo.market", "saleplus.ru", "sotoguide.ru", "spravker",
            "stolica.ru", "techGuru.ru", "technoportal.ru", "televizor-x.ru", "tiu.ru",
            "topadvert.ru", "vseinstrumenti.ru", "WildBerries.ru", "ymall.ru", "yandex.ru",
            "uslugio.com"
        ], function(e, t) {
            $(".js-site-link:contains(" + t + ")").closest("tr").toggleClass("td__agregator");
        });
    });
    
    // Подсветка главных страниц
    $(".button-lighting-main").on("click", function(e) {
        e.preventDefault();
        $(".js-site-link").each(function() {
            1 == $(this).attr("mainpage") && $(this).closest("tr").toggleClass("td__main");
        });
    });
    
    // Подсветка своих доменов
    $(".btn_url_on").on("click", function(e) {
        e.preventDefault();
        var t = $(".list_url").val().split("\n");
        $.each(t, function(e, t) {
            $(".js-site-link:contains(" + t + ")").closest("tr").addClass("td__url");
        });
        $.fancybox.close();
    });
    
    $(".btn_url_off").on("click", function(e) {
        e.preventDefault();
        var t = $(".list_url").val().split("\n");
        $.each(t, function(e, t) {
            $(".js-site-link:contains(" + t + ")").closest("tr").removeClass("td__url");
        });
        $.fancybox.close();
    });
    
    // Переключение колонок
    $(".js-column-format").on("click", function() {
        $(".js-column-format").each(function(e) {
            $(this).removeClass("active");
        });
        $("#answer").removeClass("col-3");
        $("#answer").removeClass("col-4");
        $("#answer").removeClass("col-5");
        $(this).toggleClass("active");
        $(".js-column-format").each(function(e) {
            $(this).hasClass("active") && $("#answer").addClass($(this).data("view"));
        });
    });
    
    // Пункт 11: Копирование URL в буфер обмена
    $(".clipboard").off("click");
    $(".clipboard").on("click", function() {
        var e = [];
        $(this).closest("table").find(".js-site-link").each(function() {
            e.push($(this).text());
        });
        if (0 < e.length) {
            var t = $("<textarea>");
            $("body").append(t);
            t.val(e.join("\n")).select();
            document.execCommand("copy");
            t.remove();
            
            // Визуальное подтверждение копирования
            var originalText = $(this).html();
            $(this).html(" ✓ Скопировано!");
            setTimeout(() => {
                $(this).html(originalText);
            }, 2000);
        }
    });
    
    // Переключение табов методов
    $(".method-tabs").on("click", ".js-method-item:not(.active)", function() {
        $(this).addClass("active").siblings().removeClass("active")
            .closest("div.method-block").find(".method-content")
            .removeClass("js-method-parsing").attr("disabled", !0)
            .eq($(this).index()).addClass("js-method-parsing").attr("disabled", !1);
    });
    
    // Переключатель удаления слов
    $(".js-word-del").on("click", function(e) {
        e.preventDefault();
        $(".word_del").slideToggle(300);
    });
});

// Загрузка страницы
$(window).on("load", function() {
    $("body").addClass("loaded_hiding");
    window.setTimeout(function() {
        $("body").addClass("loaded");
        $("body").removeClass("loaded_hiding");
    }, 500);
});
