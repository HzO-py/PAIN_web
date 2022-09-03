
/* Playground Demo: Login */

/*
  
  This playground demo is still in production
  
  I will improve this shortly and add the options to recover and reset the password
  
  Let me know if you have questions or ideas how to improve this login modal:
  
  stephanwagner.me@gmail.com
  
*/


// We are ssetting up a global variable where we can adjust html and texts
var verifytime=10;//验证码倒计时
var jBoxLogin = {
  jBox: null,
  
  
  // The html of each of the content containers
  
  html: {
    //login: '<div id="LoginContainer-login" class="login-container" ><div class="login-body"><input type="text" id="loginUsername" class="login-textfield" placeholder="手机号" autocorrect="off" autocapitalize="off" spellcheck="false"><input type="password" id="loginPassword" class="login-textfield" placeholder="密码" autocorrect="off" autocapitalize="off" spellcheck="false"><div class="login-remember"><div class="login-checkbox"><div class="login-checkbox-check"></div></div><div class="login-checkbox-label">7天内自动登录</div><input type="hidden" name="login-remember" value="1"></div><button class="login-button">登录</button></div><div class="login-footer"><span onclick="localStorage.setItem(\'pagetype\',\'register\');jBoxLogin.jBox.showContent(\'register\');">注册账号</span><span style="margin-left:120px" onclick="localStorage.setItem(\'pagetype\',\'reset\');jBoxLogin.jBox.showContent(\'register\')">忘记密码?</span></div></div>',
    //login: '<div id="LoginContainer-login" class="login-container" ><div class="login-body"><input type="text" id="loginUsername" class="login-textfield" placeholder="用户名" autocorrect="off" autocapitalize="off" spellcheck="false"><input type="password" id="loginPassword" class="login-textfield" placeholder="密码" autocorrect="off" autocapitalize="off" spellcheck="false"><div class="login-remember"><input type="hidden" name="login-remember" value="1"></div><button class="login-button">登录</button></div><div class="login-footer"><span onclick="localStorage.setItem(\'pagetype\',\'register\');jBoxLogin.jBox.showContent(\'register\');">注册账号</span><span style="margin-left:120px" onclick="localStorage.setItem(\'pagetype\',\'reset\');jBoxLogin.jBox.showContent(\'register\')">忘记密码?</span></div></div>',
    login: '<div id="LoginContainer-login" class="login-container" ><div class="login-body"><input type="text" id="loginUsername" class="login-textfield" placeholder="账号" autocorrect="off" autocapitalize="off" spellcheck="false"><input type="password" id="loginPassword" class="login-textfield" placeholder="密码" autocorrect="off" autocapitalize="off" spellcheck="false"><div class="login-remember"><input type="hidden" name="login-remember" value="1"></div><button class="login-button">登录</button></div>',
    register: '<div id="LoginContainer-register" class="login-container"><div class="login-body"><input type="text" id="registerUsername" class="login-textfield" placeholder="请输入手机号注册" maxlength="24" autocorrect="off" autocapitalize="off" spellcheck="false"><button class="login-button">下一步</button></div><div class="login-footer"><span onclick="jBoxLogin.jBox.showContent(\'login\')">已有账号？立即登录</span></div></div>',
    verifycode: '<div id="LoginContainer-verifycode" class="login-container"><div class="login-body"><input type="text" id="registerVerifycode" class="login-textfield" placeholder="请输入验证码" maxlength="24" autocorrect="off" autocapitalize="off" spellcheck="false"><a  id="sendverifycode" onclick="">重新发送验证码</a><button class="login-button">下一步</button></div><div class="login-footer"><span onclick="jBoxLogin.jBox.showContent(\'login\')">已有账号？立即登录</span></div></div>',
    passwordReset: '' ,// TODO '<div id="LoginContainer-password-reset" class="login-container"><div class="login-body"><input type="text" placeholder="Recovery Code"><input type="password" placeholder="Password" autocorrect="off" autocapitalize="off" spellcheck="false"><button class="login-button">Reset password</button></div><div class="login-footer"><span onclick="jBoxLogin.jBox.showContent(\'login\')">Already registered? Login!</span></div></div>'
    setpwd:'<div id="LoginContainer-setpwd" class="login-container"><div class="login-body"><input id="password" type="password" placeholder="设置您的密码" class="login-textfield"><input id="repassword" class="login-textfield" type="password" placeholder="确认密码" autocorrect="off" autocapitalize="off" spellcheck="false"><button class="login-button">注册</button></div><div class="login-footer"><span onclick="jBoxLogin.jBox.showContent(\'login\')">已有账号？立即登录</span></div></div>'
  },
  
  
  // Corresponding titles for content elements
  
  title: {
    login: 'AI HR系统登录',
    register: '注册AI HR账号',
    verifycode: '注册AI HR账号',
    setpwd: '设置密码'
    // TODO passwordRecovery: 'Recover password',
    // TODO passwordReset: 'Reset password'
  },
  
  
  // These tooltips will show when a textelemet gets focus
  
  textfieldTooltips: {
    loginUsername: '请输入您的账号',
    loginPassword: '请输入您的密码',
    registerUsername: '请入您的手机号',
    password:'请设置您的密码',
    repassword:'重复输入密码',
    registerVerifycode:'请输入收到的验证码'
  }
  
};


$(document).ready(function() {
  
  
  // On domready create the login modal

  jBoxLogin.jBox = new jBox('Modal', {
    
    // Unique id for CSS access
    id: 'jBoxLogin',
    
    // Dimensions
    width: 320,  // TODO move to global var
    height: 350,
    
    // Attach to elements
    attach: '#DemoLogin',
    
    // Create the content with the html provided in global var
    content: '<div id="LoginWrapper">' + jBoxLogin.html.login + jBoxLogin.html.register +jBoxLogin.html.verifycode + jBoxLogin.html.passwordReset +jBoxLogin.html.setpwd+ '</div>',
    
    // When the jBox is being initialized add internal functions
    onInit: function () {
      
      // Internal function to show content
      this.showContent = function (id, force) {

        // Abort if an ajax call is loading
        if (!force && $('#LoginWrapper').hasClass('request-running')) return null;

        // Set the title depending on id
        this.setTitle(jBoxLogin.title[id]);
        var pagetype = localStorage.getItem('pagetype');

        if(jBoxLogin.title[id] == jBoxLogin.title['register']||jBoxLogin.title[id] == jBoxLogin.title['verifycode']){
          document.getElementsByClassName('jBox-content')[0].style.height='220px';
          if(pagetype=='reset'){
            document.getElementsByClassName("jBox-title")[0].textContent='找回密码';
            document.getElementById("registerUsername").placeholder='请输入手机号找回密码';
          }
          else{
            document.getElementsByClassName("jBox-title")[0].textContent='注册AI HR账号';
            document.getElementById("registerUsername").placeholder='请输入手机号注册';
          }
        }
        else if(jBoxLogin.title[id] == jBoxLogin.title['login']){
          document.getElementsByClassName("jBox-title")[0].textContent='AI HR系统登录';
          document.getElementsByClassName('jBox-content')[0].style.height='350px';
        }
        else if(jBoxLogin.title[id] == jBoxLogin.title['setpwd']){
          document.getElementsByClassName("jBox-title")[0].textContent='设置密码';
          document.getElementsByClassName('jBox-content')[0].style.height='300px';
          if(pagetype=='reset'){
            document.querySelector("#LoginContainer-setpwd .login-button").innerText='确认修改'
          }
          else{
            document.querySelector("#LoginContainer-setpwd .login-button").innerText='注册'
          }
        }
        // Show content depending on id
        $('.login-container.active').removeClass('active');
        $('#LoginContainer-' + id).addClass('active');
        
        // Remove error tooltips
        // TODO only loop through active elements or store tooltips in global var rather than on the element
        $.each(jBoxLogin.textfieldTooltips, function (id, tt) {
          $('#' + id).data('jBoxTextfieldError') && $('#' + id).data('jBoxTextfieldError').close();
        });
      };
      
      // Initially show content for login
      this.showContent('login', true);
      
      // Add focus and blur events to textfields
      $.each(jBoxLogin.textfieldTooltips, function (id, tt) {
        
        // Focus an textelement
        $('#' + id).on('focus', function () {
          
          // When there is an error tooltip close it
          $(this).data('jBoxTextfieldError') && $(this).data('jBoxTextfieldError').close();
          
          // Remove the error state from the textfield
          $(this).removeClass('textfield-error');
          
          // Store the tooltip jBox in the elements data
          if (!$(this).data('jBoxTextfieldTooltip')) {
            
            // TODO create a small jbox plugin
            
            $(this).data('jBoxTextfieldTooltip', new jBox('Tooltip', {
              width: 310, // TODO use modal width - 10
              theme: 'TooltipSmall',
              addClass: 'LoginTooltipSmall',
              target: $(this),
              position: {
                x: 'left',
                y: 'top'
              },
              outside: 'y',
              offset: {
                y: 6,
                x: 8
              },
              pointer: 'left:17',
              content: tt,
              animation: 'move'
            }));
          }
          $(this).data('jBoxTextfieldTooltip').open();
          
        // Loose focus of textelement
        }).on('blur', function () {
          $(this).data('jBoxTextfieldTooltip').close();
        });
      });
      
      // Internal function to show errors
      this.showError = function (element, message) {
        
        if (!element.data('errorTooltip')) {
          
          // TODO add the error class here
          
          element.data('errorTooltip', new jBox('Tooltip', {
            width: 310,
            theme: 'TooltipError',
            addClass: 'LoginTooltipError',
            target: element,
            position: {
              x: 'left',
              y: 'top'
            },
            outside: 'y',
            offset: {
              y: 6
            },
            pointer: 'left:9',
            content: message,
            animation: 'move'
          }));
        }
        
        element.data('errorTooltip').open();
      };
      
      // Internal function to change checkbox state
      this.toggleCheckbox = function () {
        // Abort if an ajax call is loading
        if ($('#LoginWrapper').hasClass('request-running')) return null;
        
        $('.login-checkbox').toggleClass('login-checkbox-active');
      };
      
      // Add checkbox events to checkbox and label
      $('.login-checkbox, .login-checkbox-label').on('click', function () {
        this.toggleCheckbox();
      }.bind(this));
      
      // Parse an ajax repsonse
      this.parseResponse = function(response) {
      	try {
      		response = JSON.parse(response.responseText || response);
      	} catch (e) {}
      	return response;
      };
      
      // Show a global error
      this.globalError = function () {
        new jBox('Notice', {
          color: 'red',
          content: '请求错误',
          attributes: {
            x: 'right',
            y: 'bottom'
          }
        });
      };
      
      // Internal function to disable or enable the form while request is running
      this.startRequest = function() {
        this.toggleRequest();
      }.bind(this);
      
      this.completeRequest = function() {
        this.toggleRequest(true);
      }.bind(this);
      
      this.toggleRequest = function (enable) {
        $('#LoginWrapper')[enable ? 'removeClass' : 'addClass']('request-running');
        $('#LoginWrapper button')[enable ? 'removeClass' : 'addClass']('loading-bar');
        $('#LoginWrapper input, #LoginWrapper button').attr('disabled', enable ? false : 'disabled');
      }.bind(this);
      
      // Bind ajax login function to login button
      $('#LoginContainer-login button').on('click', function () {
        $.ajax({
          url: '/loginajax/',
          data: {
            username: $('#loginUsername').val(),
            password: $('#loginPassword').val(),
            remember: $('.login-checkbox').hasClass('login-checkbox-active') ? 1 : 0
          },
          method: 'post',
          beforeSend: function () {
            this.startRequest();
          }.bind(this),
          
          // Ajax call successfull
          success: function (response) {
            console.log(response)
            this.completeRequest();
            response = this.parseResponse(response);
            
            // Login successfull
            if (response.success) {

              
              new jBox('Notice', {
                color: 'green',
                content: '登录成功,正在跳转',
                attributes: {
                  x: 'right',
                  y: 'bottom'
                }
              });
              window.setTimeout(
                  "window.location.href='/index'",1000
              )
            // Login failed
            } else {
                // Shake submit button
                this.animate('shake', {element: $('#LoginContainer-login button')});
                // Backend error
                $('#loginUsername, #loginPassword').addClass('textfield-error');
                new jBox('Notice', {
                  color: 'red',
                  content: '用户名或密码错误',
                  attributes: {
                  x: 'right',
                  y: 'bottom'
                  }
                });
            }
          }.bind(this),
          
          // Ajax call failed
          error: function () {
            this.completeRequest();
            this.animate('shake', {element: $('#LoginContainer-login button')});
            this.globalError();
          }.bind(this)
        });
      
      }.bind(this));
      
      // Bind ajax register function to register button
      $('#LoginContainer-register button').on('click', function () {
        var pagetype = localStorage.getItem('pagetype');
        var myreg = /^(((13[0-9]{1})|(15[0-9]{1})|(18[0-9]{1}))+\d{8})$/;
        var phonenum = $('#registerUsername').val()
        if(!myreg.test(phonenum)){
            new jBox('Notice', {
              color: 'red',
              content: '手机号格式错误',
              attributes: {
                x: 'right',
                y: 'bottom'
              }
            });
        }
        else {
          $.ajax({
            url: '/registerajax/',
            data: {
              sendtype:pagetype,
              username: phonenum,
            },
            method: 'post',
            beforeSend: function () {
              this.startRequest();
            }.bind(this),

            success: function (response) {
              this.completeRequest();
              response = this.parseResponse(response);

              // Registration successfull
              if (response.success) {

                jBoxLogin.jBox.showContent('verifycode')
                settime();//开始倒计时

                new jBox('Notice', {
                  color: 'green',
                  content: '验证码已发送',
                  attributes: {
                    x: 'right',
                    y: 'bottom'
                  }
                });
                // Redirect or own register behavior here
                // Registration failed
              } else {
                // Shake submit button
                this.animate('shake', {element: $('#LoginContainer-register button')});
                $('#registerUsername').addClass('textfield-error');
                new jBox('Notice', {
                  color: 'red',
                  content: response.desc,
                  attributes: {
                    x: 'right',
                    y: 'bottom'
                  }
                });
              }
            }.bind(this),

            // Ajax call failed
            error: function () {
              this.completeRequest();
              this.animate('shake', {element: $('#LoginContainer-register button')});
              this.globalError();
            }.bind(this)
          });
        }
      }.bind(this));

      $('#LoginContainer-verifycode button').on('click', function () {
        $.ajax({
          url: '/verifyajax/',
          data: {
            username: $('#registerUsername').val(),
            userVerify: $('#registerVerifycode').val(),
          },
          method: 'post',
          beforeSend: function () {
            this.startRequest();
          }.bind(this),

          success: function (response) {
            this.completeRequest();
            response = this.parseResponse(response);

            // Registration successfull
            if (response.success) {

              jBoxLogin.jBox.showContent('setpwd')

            // Registration failed
            } else {
              // Shake submit button
              this.animate('shake', {element: $('#LoginContainer-verifycode button')});
              $('#registerVerifycode').addClass('textfield-error');
              new jBox('Notice', {
                  color: 'red',
                  content: '验证码错误',
                  attributes: {
                  x: 'right',
                  y: 'bottom'
                  }
                });
            }
          }.bind(this),

          // Ajax call failed
          error: function () {
            this.completeRequest();
            this.animate('shake', {element: $('#LoginContainer-verifycode button')});
            this.globalError();
          }.bind(this)
        });

      }.bind(this));

      $('#LoginContainer-setpwd button').on('click', function () {
        var pagetype = localStorage.getItem('pagetype');
        if($('#password').val()!=$('#repassword').val()){
              this.animate('shake', {element: $('#LoginContainer-setpwd button')});
              $('#password, #repassword').addClass('textfield-error');
              new jBox('Notice', {
                  color: 'red',
                  content: '两次密码不一致',
                  attributes: {
                  x: 'right',
                  y: 'bottom'
                  }
                });
        }
        else {
          $.ajax({
            url: '/postregisterajax/',
            data: {
              sendtype: pagetype,
              username: $('#registerUsername').val(),
              password: $('#password').val(),
            },
            method: 'post',
            beforeSend: function () {
              this.startRequest();
            }.bind(this),

            success: function (response) {
              this.completeRequest();
              response = this.parseResponse(response);

              // Registration successfull
              if (response.success) {
                new jBox('Notice', {
                  color: 'green',
                  content: response.desc,
                  attributes: {
                    x: 'right',
                    y: 'bottom'
                  }
                });
                window.setTimeout(
                    "window.location.href='/index'",1000
                )
                // Registration failed
              } else {
                // Shake submit button
                this.animate('shake', {element: $('#LoginContainer-verifycode button')});
                $('#registerVerifycode').addClass('textfield-error');
                new jBox('Notice', {
                  color: 'red',
                  content: '系统拒绝注册',
                  attributes: {
                    x: 'right',
                    y: 'bottom'
                  }
                });
              }
            }.bind(this),

            // Ajax call failed
            error: function () {
              this.completeRequest();
              this.animate('shake', {element: $('#LoginContainer-verifycode button')});
              this.globalError();
            }.bind(this)
          });
        }
      }.bind(this));
    },

    onOpen: function () {
      
      // Go back to login when we open the modal
      this.showContent('login', true);
      
    },
    onClose: function () {
        
        // TODO reset form completely
        // TODO only close jBox with close button, not on overlay click
        
        // Remove error tooltips
        // TODO Better to reset the form, this loop is also in showContent
        $.each(jBoxLogin.textfieldTooltips, function (id, tt) {
          $('#' + id).data('jBoxTextfieldError') && $('#' + id).data('jBoxTextfieldError').close();
        });
        
    }
  });
});

function settime() {
  var text = document.getElementById('sendverifycode');
  text.text='重新发送('+verifytime+')'
  verifytime--;
  if(verifytime>-1)
    setTimeout('settime()',1000)
  else{
    text.text='重新发送验证码';
    text.setAttribute('onclick','resendverifycode()');
    text.setAttribute('href',"javascript:void(0);");
  }
}
function resendverifycode() {
  verifytime=10;
  var text = document.getElementById('sendverifycode');
  text.removeAttribute('onclick');
  text.removeAttribute('href');
  settime();
  sendcode();
}
function sendcode() {
  var phonenum = $('#registerUsername').val()

  $.ajax({
    url: '/registerajax/',
    data: {
      sendtype:localStorage.getItem('pagetype'),
      username: phonenum,
    },
    method: 'post',
    success: function (response) {
      response = JSON.parse(response.responseText || response);
      // Registration successfull
      if (response.success) {
        new jBox('Notice', {
          color: 'green',
          content: '验证码已发送',
          attributes: {
            x: 'right',
            y: 'bottom'
          }
        });
        // Redirect or own register behavior here
        // Registration failed
      } else {
        // Shake submit button
        this.animate('shake', {element: $('#LoginContainer-register button')});
        $('#registerUsername').addClass('textfield-error');
        new jBox('Notice', {
          color: 'red',
          content: '发送失败',
          attributes: {
            x: 'right',
            y: 'bottom'
          }
        });
      }
    }.bind(this),

    // Ajax call failed
    error: function () {
      this.completeRequest();
      this.animate('shake', {element: $('#LoginContainer-register button')});
      this.globalError();
    }.bind(this)
  });
}