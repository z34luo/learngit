 var data = " [ {name:'6101',value:'beijing',age:'11'}, {name:'6102',value:'tianjin',age:'11'}, {name:'6103',value:'shanghai',age:'22'}]"; 
  var dataObj = eval("(" + data + ")");    
var $tab1=$('#mytab');
$.each(dataObj,function(index,item){

    var tr=document.createElement("tr");
    $.each(item,function(name,val){
        var td=document.createElement("td");
        td.innerHTML=val;
        tr.appendChild(td);
    });
    console.log(tr);
    var ta = document.getElementById("table");
    console.log(ta);
    ta.appendChild(tr);
});


