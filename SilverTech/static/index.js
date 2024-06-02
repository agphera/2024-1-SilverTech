import { showPopup, hidePopup } from "./popup.js";



//모든 학습파일
function visible(current, total) {
  var arr = [];
  for (let k = 0; k < total; k++) {
    arr[k] = k + "text";
  }
  var con = document.getElementById(arr[current]);
  for (let j = 0; j < arr.length; j++) {
    var hid = document.getElementById(arr[j]);
    hid.style.display = "none";
  }
  con.style.display = "block";
}

console.log("보내기");
console.log("보내기");
console.log("보내기");
console.log("보내기");
