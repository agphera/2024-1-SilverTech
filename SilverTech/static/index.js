import { showPopup, hidePopup} from './popup.js';

  //도움말 버튼 전체 동작 관리
  document.getElementById("helpButton").addEventListener("click", function() {
    showPopup("helpPopup");
  });

  document.getElementById("one").addEventListener("click", function() {
    showPopup("onePopup");
  });

  document.getElementById("two").addEventListener("click", function() {
      showPopup("twoPopup");
  });

  document.getElementById("three").addEventListener("click", function() {
      showPopup("threePopup");
  });

  document.getElementById("four").addEventListener("click", function() {
      showPopup("fourPopup");
  });

  document.getElementById("back").addEventListener("click", function() {
      hidePopup("helpPopup");
  });

  document.getElementById("bbackOne").addEventListener("click", function() {
      hidePopup("onePopup");
  });

  document.getElementById("bbackTwo").addEventListener("click", function() {
      hidePopup("twoPopup");
  });

  document.getElementById("bbackThree").addEventListener("click", function() {
      hidePopup("threePopup");
  });

  document.getElementById("bbackFour").addEventListener("click", function() {
      hidePopup("fourPopup");
  });
//도움말 버튼 완료

  
  //모든 학습파일
  function visible(current, total){
    var arr = [];
    for(let k = 0; k< total; k++){
      arr[k] = k+"text";
    }
    var con = document.getElementById(arr[current]);
    for(let j = 0; j<arr.length; j++){
      var hid = document.getElementById(arr[j]);
      hid.style.display = 'none';
    }   
    con.style.display = 'block';    
    
  }
  
  
  
  console.log("보내기");console.log("보내기");console.log("보내기");console.log("보내기");
  
  
