//sidebar toggle button
$(document).ready(function() {
	$('[data-toggle="offcanvas"]').click(function() {
		$('#side-menu').toggleClass('hidden-xs');
	});
});

//news part
$(function() {
            $("#btnHome").click(function(){
                $('#myTabs a:first').tab('show'); //首页
            });
            $("#btnNews").click(function(){
                $('#myTabs li:eq(1) a').tab('show'); //新闻
            });
            $("#btnMoney").click(function(){
                $('#myTabs a[href="#money"]').tab('show'); //财经
            });
            
        });




/*$.ajax({type:"POST",
                    url:"#",
                    data:{'username':$("#txtUID").val(),
                          'password':$("#txtPWD").val(),
                          'usernames':$("#txtUIDS").val(),
                          'passwords':$("#txtPWDS").val(),
                          'emails':$("#txtEmailS").val(),
                          'ages':$("#txtAgeS").val()
                         },
                    success:function(data)
                    { 
                        alert("Hello");
                        window.location.assign('/Main');
                    },
                    error:function()
                    {
                        alert("Your password is not right.");
                    }
        });*/