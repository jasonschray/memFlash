
function go_to_url(url){
    window.location.href = url
}
function test_answer_response(correct){    
    $('.answer_true').css('background-color', 'lightgreen')
    $('.answer_false').css('background-color', 'lightcoral')
    $('.answer_true').off()
    $('.answer_false').off()
    url = window.location.href
    if (correct)
    {
        $('.prompt').text('Correct Answer')
        url = url + '&known=True'
    }
    else
    {
        $('.prompt').text('Incorrect Answer')
        url = url + '&known=False'
    }
    window.setTimeout(go_to_url(url),2000);

}


$( document ).ready(function() {
    $('.answer_true').click(function(){test_answer_response(true);});
    $('.answer_false').click(function(){test_answer_response(false);});

});
