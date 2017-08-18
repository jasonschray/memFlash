// var scriptvar = document.createElement('script');
// scriptvar.src = 'https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.2.1.min.js';



// document.getElementsByTagName('head')[0].appendChild(scriptvar);
// scriptvar.onload = function(e){ 
    $( document ).ready(function() {
        if(typeof $ !== 'undefined'){
            $('select[name="search_type"]').change(function(){
                console.log('changed')
                $('#searchForm').submit();});
        }
        $()
    });
// };