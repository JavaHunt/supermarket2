"use strict";

import data from './stocks1.json' assert { type: 'json' };
// export {data};

const myJSON = JSON.stringify(data);
localStorage.setItem("testJSON", myJSON);



/*
function fill_data(){
console.log(data['102']['category']);
document.getElementById("rate").innerHTML = data["102"]['price'];
}
/*
function search(){
    x = document.getElementById("Iid").value;
    document.getElementById("rate").value = data[x][price];
}

function temp(){
    alert("hello");
}
*/