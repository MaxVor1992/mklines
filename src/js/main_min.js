$(function(){$(".js-fancybox").fancybox(),$(".mailmask").inputmask({alias:"email"}),$(".menu").on("click",function(){$(".main-menu").toggleClass("main-menu__deactive")}),ymaps.ready(function(){var t=ymaps.geolocation;$("#tow").html(t.city)}),$(".result-tabs").on("click",".js-result-item:not(.active)",function(){$(this).addClass("active").siblings().removeClass("active").closest("div.result-block").find("div.result-tabs-content").removeClass("active").eq($(this).index()).addClass("active")}),$(".tariff-tabs").on("click",".js-tariff-item:not(.active)",function(){$(this).addClass("active").siblings().removeClass("active").closest("div.tariff-block").find("div.tariff-tabs-content").removeClass("active").eq($(this).index()).addClass("active")}),$(".js-faq-item").on("click",function(){$(this).toggleClass("active")});var t="";$(document).on("click",".js-form-popup",function(){t=$(this).attr("data-description"),$("input[name=check]").val(t)}),$(document).on("click",".audit-submit",function(){t=$(this).attr("data-description"),$("input[name=check]").val(t)}),$(document).on("click",".cosmos-submit",function(){t=$(this).attr("data-description"),$("input[name=check]").val(t)}),$(".form-popup").submit(function(t){t.preventDefault(),$.ajax({url:"mail.php",type:"POST",dataType:"json",data:$(".form-popup").serialize(),success:function(t){!0===t.status?$(".form-popup").trigger("reset"):!1===t.status&&window.location.replace("https://yandex.ru/")}})}),$(".form-audit").submit(function(t){t.preventDefault(),$.ajax({url:"mail.php",type:"POST",dataType:"json",data:$(".form-audit").serialize(),success:function(t){!0===t.status?$(".form-audit").trigger("reset"):!1===t.status&&window.location.replace("https://yandex.ru/")}})}),$(".form-cosmos").submit(function(t){t.preventDefault(),$.ajax({url:"mail.php",type:"POST",dataType:"json",data:$(".form-cosmos").serialize(),success:function(t){!0===t.status?$(".form-cosmos").trigger("reset"):!1===t.status&&window.location.replace("https://yandex.ru/")}})})});