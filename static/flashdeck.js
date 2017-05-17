var scriptvar = document.createElement('script');
scriptvar.src = 'https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.2.1.min.js';
//script.type = 'text/javascript';
 
// document.head.appendChild(s); 

function updateDeckForm(){
    // console.log('undating deck form')
    for (var i = 3; i <= 4; i++) {
                selectContainString = 'label:contains("Side '+i+' Type")'
                nameContainString   = 'label:contains("Side '+i+' Name")'
                // console.log(containString)

                curtypediv = $(selectContainString).parent()
                curnamediv = $(nameContainString).parent()
                // console.log(curdiv)
                if (i <= $('select#sideCount').val())
                {
                    curtypediv.show()
                    curnamediv.show()
                }
                else
                {
                    curtypediv.hide()
                    curnamediv.hide()
                }
            };
}
document.getElementsByTagName('head')[0].appendChild(scriptvar);

scriptvar.onload = function(e){ 
    $( document ).ready(function() {
        // console.log( "ready!" );

        if(typeof $ !== 'undefined'){
            // console.log($('#flashdeckForm'))
            // console.log(($('#flashdeckForm').children("div:contains('Number of Sides')").first()))
            // console.log($('select#sideCount').val())
           updateDeckForm();
           // console.log($('select#sideCount'))
           $('select#sideCount').change(updateDeckForm);
            // curdiv = $("label:contains('Side 4 Type')").parent()
            // console.log($("label:contains('Side 4 Type')").parent())
        }

        $()
    });
};


