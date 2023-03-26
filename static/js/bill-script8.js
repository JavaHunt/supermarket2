
var i = 1;
var incIndex = 1;
var Bill = new Object();
//alert(data);
//console.log(data['102']['pname']);
// Retrieving data:
let text = localStorage.getItem("testJSON");
let data_obj = JSON.parse(text);

function findIndex(name){
  if(name.slice(-2) == '0' || name.slice(-2) == '1' || name.slice(-2) == '2' || name.slice(-2) == '3'  || name.slice(-2) == '4' || name.slice(-2) == '5' || name.slice(-2) == '6' || name.slice(-2) == '7' || name.slice(-2) == '8' || name.slice(-2) == '9'){
    x = name.slice(-2) + name.slice(-1)
    return x;
  }
  return name.slice(-1);
}

function increment(name) {
    document.getElementById(name).stepUp();
    indexofTable1 = findIndex(name);
    indexofTable1 = parseInt(indexofTable1);
    var table = document.getElementById("maintable");
    qnty = table.rows.item(indexofTable1).cells.item(2).innerHTML;
    table.rows.item(indexofTable1).cells.item(2).innerHTML = parseInt(qnty) + 1;
    // updated quantity
    qnty = table.rows.item(indexofTable1).cells.item(2).innerHTML;
    save = table.rows.item(indexofTable1).cells.item(4).innerHTML;
    table.rows.item(indexofTable1).cells.item(4).innerHTML = (save/(qnty-1)) * qnty;
    rate = table.rows.item(indexofTable1).cells.item(3).innerHTML;
    // updated save
    save = table.rows.item(indexofTable1).cells.item(4).innerHTML;
    table.rows.item(indexofTable1).cells.item(5).innerHTML = (qnty * rate)-save;
}
function decrement(name) {
    document.getElementById(name).stepDown();
    indexofTable1 = findIndex(name);
    indexofTable1 = parseInt(indexofTable1);
    var table = document.getElementById("maintable");
    qnty = table.rows.item(indexofTable1).cells.item(2).innerHTML;
    if(qnty != 1){
      table.rows.item(indexofTable1).cells.item(2).innerHTML = parseInt(qnty) - 1;
      // updated quantity
      qnty = table.rows.item(indexofTable1).cells.item(2).innerHTML;
      save = table.rows.item(indexofTable1).cells.item(4).innerHTML;
      // alert("save : "+save);
      table.rows.item(indexofTable1).cells.item(4).innerHTML = (parseFloat(save)/(parseInt(qnty)+1)) * parseInt(qnty);
      rate = table.rows.item(indexofTable1).cells.item(3).innerHTML;
      // updated save
      save = table.rows.item(indexofTable1).cells.item(4).innerHTML;
      table.rows.item(indexofTable1).cells.item(5).innerHTML = (qnty * rate)-save;
    }
    else
      alert("You cant't reduce quantity less than 1");
    
}

function delete_row1(name){
  var row = document.getElementById(name.slice(0,-1));
  if(row){
    row.parentNode.removeChild(row);
  }
  else{
    alert("Deletion of row went wrong");
  }
}

function delete_row2(name){
  var row = document.getElementById(name);
  if(row){
    row.parentNode.removeChild(row);
  }
  else{
    alert("Deletion of row went wrong");
  }
}

function addelement(){
  if(document.getElementById("discount").value == ''){
    document.getElementById("discount").value = document.getElementById("rate").value;
  }
  document.getElementById("save").value = parseInt(document.getElementById("rate").value) - parseInt(document.getElementById("discount").value);
  
  var table =document.getElementById("maintable"),
        item = document.getElementById("product").value,
        newRow=table.insertRow(table.length);
        newRow.setAttribute("id", item),
        cell1=newRow.insertCell(0),
        cell2=newRow.insertCell(1),
        cell3=newRow.insertCell(2),
        cell4=newRow.insertCell(3),
        cell5=newRow.insertCell(4),
        cell6=newRow.insertCell(5),
        id = document.getElementById("Iid").value,
        
        quan = document.getElementById("item").value,
        rate = document.getElementById("rate").value;
        discount = document.getElementById("discount").value;
        save = document.getElementById("save").value;
        //save = document.getElementById("save").value;
        //total = document.getElementById("Iid").value;
        cell1.innerHTML=id;
        cell2.innerHTML=item;
        cell3.innerHTML=quan;
        cell4.innerHTML=rate;
        cell5.innerHTML= save*quan;
        cell6.innerHTML=(quan*rate)-(save*quan);
        //Bill[i] = [i, item, quan, rate, save, (quan*rate)-save]
        //i++;
        //console.log(Bill);

}
function addelement1(){
  var table =document.getElementById("secondtable"),
      item = document.getElementById("product").value,
      table_length = table.rows.length,
      newRow=table.insertRow(table.length);
      newRow.setAttribute("id", item);
      cell1=newRow.insertCell(0),
      cell2=newRow.insertCell(1),
      cell3=newRow.insertCell(2),
      quan = document.getElementById("item").value;
      celldata = `<button onclick=increment("`+item+table_length+`")>+</button> \
      <input id="` + item+table_length + `" type=number min=1 max=1000 value="` + quan +`" class='no-outline'> \
      <button onclick=decrement("`+item+table_length+`")>-</button>`
      cell3_data = `<button onclick="delete_row1('`+item+table_length+`'), delete_row2('`+item+`')">delete</button>`
      incIndex++;
      cell1.innerHTML=item;
      cell2.innerHTML= celldata;
      cell3.innerHTML = cell3_data;
}
function download(){
  var table = document.getElementById("maintable");
  var j = 1, k = 0;
  for(j = 1; j < table.rows.length; j++){
    var Objcells = table.rows.item(j).cells;
    var tempArray = []
    for(k=0; k < Objcells.length; k++){
      tempArray.push(Objcells.item(k).innerHTML);
      //Bill[i] = [i, item, quan, rate, save, (quan*rate)-save]
      //i++;
    }
    Bill[i] = tempArray;
    i++;
  }

  var content = ''
  j = 1;
  while(j != i){
    console.log("content : ", content);
    if(content != undefined && Bill[j] != undefined)
      content = content + Bill[j] + "\n";
    j++;
  }

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,'+encodeURIComponent(content));
  element.setAttribute('download', "sample.txt");

  element.style.display = 'none';
  document.body.appendChild(element);
  
  element.click();
  document.body.removeChild(element);
}


function fill_data(){
    id = document.getElementById("Iid").value;
    console.log(data_obj);
    for(i=0;i<data_obj.length;i++){
      if(data_obj[i]['sid'] == String(id)){
        document.getElementById("rate").value = data_obj[i]["price"];
        document.getElementById("product").value = data_obj[i]["pname"];
      }
    }
    // document.getElementById("rate").value = obj[id]['price'];
}


/*
$(document).ready(function () {
  $("#test").submit(function (event) {
    $.ajax({
      type: "POST",
      url: "data",
      data: {
        'video': $('#test').val() // from form
      },
      success: function () {
        $('#message').html("<h2>Contact Form Submitted!</h2>")
      }
    });
    return false; //<---- move it here
  });

});


function sendData1(){
  alert('send data 1');
  var URL = "{% url 'accountant/bill.html/print-bill.html/' %}";
  var data = {
    'result': 'test data',
  };
  $.get(URL, data);
}
*/
