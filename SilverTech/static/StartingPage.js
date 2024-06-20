import { showPopup, hidePopup } from "./popup.js";

document.addEventListener("DOMContentLoaded", function () {
  let popup = document.getElementById("GreetingPopup");

  // 3초후 팝업
  setTimeout(function () {
    showPopup("GreetingPopup");
  }, 3000);

  var greetings = [
    "와우~ 반갑습니다!",
    "우와, 안녕하세요!",
    "짝짝짝, 환영합니다!",
    "기다리고 있었어요!",
  ];
  var randomGreeting = greetings[Math.floor(Math.random() * greetings.length)]; // 랜덤인사
  document.getElementById("random-greeting").textContent = randomGreeting;
});

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
