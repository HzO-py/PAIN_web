var method={
    msg_layer:function(obj){
        //弹框
        $(".msg-layer-bg,.msg-layer").remove();
       $("body").append( '<div class="msg-layer-bg"></div><div class="msg-layer showAlert"><h5></h5><div class="msg-con"></div><div class="layer-close">&times;</div><div class="layer-btn"><div class="layer-cancel"></div><div class="layer-commit"></div></div></div>');
        var _layerBg=$(".msg-layer-bg"),_layer=$(".msg-layer"),_close=$(".layer-close"),_cansel=$(".layer-cancel"),_commit=$(".layer-commit");
        _layer.attr("data-animation",obj.type);
        var winH=$(window).height(),winW=$(window).width();
        if(obj.title){
            _layer.find("h5").html(obj.title);
        }else{
            _layer.find("h5").css("display","none")
        }
        _layer.find($(".msg-con")).html(obj.content);
        _layerBg.css({"display":"block"});
        if(!obj.close  || obj.close == "true"){
            //关闭按钮
            _close.css("display","block");
            _close.on("click",function(){
                method.msg_close();
            })
        }else{
            _close.css("display","none");
        }
        if(obj.area){
            //宽高
            if(obj.area[0] != "auto" && obj.area[1] != "auto"){
                _layer.css({"width":obj.area[0],"height":obj.area[1],"left":winW/2-parseFloat(obj.area[0])/2,"top":winH/2-parseFloat(obj.area[1])/2});
            }else if(obj.area[0] != "auto" && obj.area[1] === "auto"){
                _layer.css({"width":obj.area[0],"height":obj.area[1],"left":winW/2-parseFloat(obj.area[0])/2,"top":winH/2-(_layer.height()+20)/2});
            }else if(obj.area[0] === "auto" && obj.area[1] != "auto"){
                _layer.css({"width":_layer.width()+20,"height":obj.area[1],"left":winW/2-(_layer.width()+20)/2,"top":winH/2-parseFloat(obj.area[1])/2});
            }

        }else{
            _layer.css({"width":_layer.width()+20,"height":_layer.height()+30,"left":winW/2-(_layer.width()+20)/2,"top":winH/2-(_layer.height()+30)/2});
        }
        if(obj.btn){
            //按钮
            if(obj.btn[0] != 0){
                _cansel.css("display","inline-block");
                _cansel.html(obj.btn[0]);
                _cansel.on("click",function(){
                    method.msg_close();
                })
            }
            if(obj.btn[1] != 0){
                _commit.css("display","inline-block");
                _commit.html(obj.btn[1]);
                _commit.on("click",function(){
                    window.location.href="/interviewreview";
                })
            }
        }
    },
    msg_close:function(){
        //关闭弹框
        var timer=null;
        $(".msg-layer").removeClass('showAlert').addClass("hideAlert");
        timer=setTimeout(function(){
            clearTimeout(timer);
            $(".msg-layer-bg").remove();
            $(".msg-layer").remove();
        },200);
    }
};
