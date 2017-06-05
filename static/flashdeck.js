// var scriptvar = document.createElement('script');
// scriptvar.src = 'https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.2.1.min.js';

function updateDeckForm(){
    for (var i = 3; i <= 4; i++) {


                selectContainString = 'input[name="side_'+i+'_name"]'
                curSelectdiv = $(selectContainString).parent()
                labelContainString = 'select[name="side_'+i+'_type"]'
                curLabeldiv = $(labelContainString).parent()

                if (i <= parseInt($('select[name="side_count"]').val()))
                {
                    curSelectdiv.show()
                    curLabeldiv.show()
                }
                else
                {
                    curSelectdiv.hide()
                    curLabeldiv.hide()
                }
               
            };
}

// document.getElementsByTagName('head')[0].appendChild(scriptvar);
// scriptvar.onload = function(e){ 
    $( document ).ready(function() {
        if(typeof $ !== 'undefined'){
            updateDeckForm();
            $('select[name="side_count"]').change(updateDeckForm);
            document.getElementById("flashdeckForm").style.display="block";
        }
        $()
    });
// };