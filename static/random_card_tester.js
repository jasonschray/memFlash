// var scriptvar = document.createElement('script');
// scriptvar.src = 'https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.2.1.min.js';

function updateTester(){
    side_names = $('select[name="test_name"]').children()
    // side_names.removeClass(active)
    for (var i = 0; i < side_names.length; i++) {
        console.log(side_names[i].value)
        $('#'+side_names[i].value).addClass('de-activate')
    }
    for (var i = 0; i < side_names.length; i++) {
        console.log(side_names[i].value)
        search_string = '#'+  side_names[i].value
        console.log(search_string)
        if (side_names[i].value == $('select[name="test_name"]').val())
        {
            $(search_string).removeClass('de-activate')
        }
    }
   
}
function showSides(){
    $('.show-sides').toggleClass('de-activate');
    // $('.collapse').collapse('toggle');
    // $('.test-cards').toggleClass('active');
}

function updateButtonLink(){
    split_string ='&selected_side=';
    link = $('#nextCardButton').attr('href').split(split_string)[0] + split_string + encodeURIComponent($('#test_name').find(":selected").val());
    $('#nextCardButton').attr('href',link)
    // console.log($('#test_name').find(":selected").val())
    // console.log($('#nextCardButton'))
}


    $( document ).ready(function() {
        if(typeof $ !== 'undefined'){
            updateTester();
            $('select[name="test_name"]').change(updateTester);
            $('select[name="test_name"]').change(updateButtonLink);
            $('#show-sides').click(showSides)
        }
    });
// };