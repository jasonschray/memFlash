
function updateTesterForm(){
    question_side = $('select[name="question_side"]')
    answer_side = $('select[name="answer_side"]')
    if (question_side.val() == answer_side.val() && question_side.val() == '0')
    {
        answer_side.val('1');
    }
    else if (question_side.val() == answer_side.val())
    {
        answer_side.val('0');
    }
    answer_side.children().removeAttr('disabled')
    answer_side.children('option[value="'+question_side.val()+'"]').attr('disabled',true)

}


$( document ).ready(function() {
    updateTesterForm();
    $('select[name="question_side"]').change(updateTesterForm);
});
