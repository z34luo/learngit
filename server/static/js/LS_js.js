$(document).ready(function($){ 
    var $form_modal = $('.cd-user-modal'), 
        $form_login = $form_modal.find('#cd-login'), 
        $form_signup = $form_modal.find('#cd-signup'), 
        $form_modal_tab = $('.cd-switcher'), 
        $tab_login = $form_modal_tab.children('li').eq(0).children('a'), 
        $tab_signup = $form_modal_tab.children('li').eq(1).children('a'), 
        $main_nav = $('.navbar-form'); 
 
    //pop window
    $main_nav.on('click', function(event){ 
 
        if( $(event.target).is($main_nav) ) { 
            // on mobile open the submenu 
            $(this).children('ul').toggleClass('is-visible'); 
          console.log("I am here");
        } else { 
            // on mobile close submenu 
            $main_nav.children('ul').removeClass('is-visible'); 
            //show modal layer 
            $form_modal.addClass('is-visible');     
            //show the selected form 
            ( $(event.target).is('.cd-signup') ) ? signup_selected() : login_selected(); 
        } 
 
    }); 
 
    //close pop window
    $('.cd-user-modal').on('click', function(event){ 
        if( $(event.target).is($form_modal) || $(event.target).is('.cd-close-form') ) { 
            $form_modal.removeClass('is-visible'); 
        }     
    }); 
    //use Esc to close the pop window
    $(document).keyup(function(event){ 
        if(event.which=='27'){ 
            $form_modal.removeClass('is-visible'); 
        } 
    }); 
 
    //switch between forms
    $form_modal_tab.on('click', function(event) { 
        event.preventDefault(); 
        ( $(event.target).is( $tab_login ) ) ? login_selected() : signup_selected(); 
    }); 
 
    function login_selected(){ 
        $form_login.addClass('is-selected'); 
        $form_signup.removeClass('is-selected'); 
        //$form_forgot_password.removeClass('is-selected'); 
        $tab_login.addClass('selected'); 
        $tab_signup.removeClass('selected'); 
    } 
 
    function signup_selected(){ 
        $form_login.removeClass('is-selected'); 
        $form_signup.addClass('is-selected'); 
       // $form_forgot_password.removeClass('is-selected'); 
        $tab_login.removeClass('selected'); 
        $tab_signup.addClass('selected'); 
    } 
 
}); 