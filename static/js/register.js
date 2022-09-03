//验证码倒计时
//发送验证码时添加cookie
function addCookie(name,value,expiresHours){
    var cookieString=name+"="+escape(value);
    //判断是否设置过期时间,0代表关闭浏览器时失效
    if(expiresHours>0){
        var date=new Date();
        date.setTime(date.getTime()+expiresHours*1000);
        cookieString=cookieString+";expires=" + date.toUTCString();
    }
        document.cookie=cookieString;
}
//修改cookie的值
function editCookie(name,value,expiresHours){
    var cookieString=name+"="+escape(value);
    if(expiresHours>0){
      var date=new Date();
      date.setTime(date.getTime()+expiresHours*1000); //单位是毫秒
      cookieString=cookieString+";expires=" + date.toGMTString();
    }
      document.cookie=cookieString;
}
//根据名字获取cookie的值
function getCookieValue(name){
      var strCookie=document.cookie;
      var arrCookie=strCookie.split("; ");
      for(var i=0;i<arrCookie.length;i++){
        var arr=arrCookie[i].split("=");
        if(arr[0]==name){
          return unescape(arr[1]);
          break;
        }else{
             return "";
             break;
         }
      }

}
$(function(){
    $("#second").click(function (){
        sendCode($("#second"));
    });
    v = getCookieValue("secondsremained");//获取cookie值
    if(v>0){
        settime($("#second"));//开始倒计时
    }
})
//发送验证码
function sendCode(obj){
    var phoneNum = $("#phoneNum").val();
    var result = isPhoneNum();
    if(result){
        doPostBack('/verifycode/',backFunc1,{"phoneNum":phoneNum, "sendtype":"register"});
        addCookie("secondsremained",10,10);//添加cookie记录,有效时间10s
        settime(obj);//开始倒计时
    }
}
//将手机利用ajax提交到后台的发短信接口
function doPostBack(url,backFunc,queryParam) {
    $.ajax({
        async : true,
        cache : false,
        type : 'POST',
        url : url,// 请求的action路径
        data:queryParam,
        error : function() {// 请求失败处理函数
        },
        success : function (response){backFunc1(response);}
    });
}
function backFunc1(data){
    if(data=='账号已存在')
        alert('该账号已存在！');

}
//开始倒计时
var countdown;
function settime(obj) {
    countdown=getCookieValue("secondsremained");
    var mes = document.getElementById('second');
    if (countdown == 0) {
        obj.removeAttr("disabled");
        obj.val("获取验证码");
        mes.style.color='white';
        return;
    } else {
        obj.attr("disabled", true);
        obj.val("重新发送(" + countdown + ")");
        mes.style.color='grey';
        countdown--;
        editCookie("secondsremained",countdown,countdown+1);
    }
    setTimeout(function() { settime(obj) },1000) //每6000毫秒执行一次
}
//校验手机号是否合法
function isPhoneNum(){
    var phonenum = $("#phoneNum").val();
    var myreg = /^(((13[0-9]{1})|(15[0-9]{1})|(18[0-9]{1}))+\d{8})$/;
    if(!myreg.test(phonenum)){
        alert('请输入有效的手机号码！');
        return false;
    }else{
        return true;
    }
}
// 解决csrf问题
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
	var csrftoken = getCookie('csrftoken');
	if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }

});

